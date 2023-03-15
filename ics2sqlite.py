import argparse
import hashlib
from ics import Calendar
import importlib.resources
from pathlib import Path
import sql
import sqlite3


def parse_options():
    parser = argparse.ArgumentParser(
        description=
        'Convert an exported Google Calendar into a sqlite3 database.')
    parser.add_argument('input_calendar',
                        help='path to .ics calendar file',
                        type=Path)
    parser.add_argument('output_database',
                        help='path to sqlite3 database file',
                        type=Path)
    return parser.parse_args()


def parse_calendar(ics_path):
    return Calendar(ics_path.read_text())


def create_tables(db_path):
    sql_text = importlib.resources.read_text(sql, 'tables.sql')
    db = sqlite3.connect(db_path)
    db.executescript(sql_text)
    return db


def populate_database(calendar: Calendar, db: sqlite3.Connection):
    keys = set()
    hashed_keys = {}  # hash -> unhashed key
    for event in calendar.timeline:
        # The primary key of the event is a combination of its "UID" and its
        # start time. Recurring events share a "UID" and each occurrence has a
        # distinct "RECURRENCE-ID", but the latter is considered an "extra"
        # field by our parser, so I'll just use the event start time because
        # it's easier.
        start_iso = event.begin.to('utc').isoformat()
        event_key = f'{event.uid}:{start_iso}'
        if event_key in keys:
            print('Skipping event with duplicate derived key: ', event_key)
            print('\t', repr(event))
            continue
        keys.add(event_key)

        # Replace `event_key` with a prefix of its SHA1 hash, for brevity.
        hasher = hashlib.sha1()
        hasher.update(event_key.encode('utf8'))
        hashed = hasher.hexdigest()[:16]
        already = hashed_keys.get(hashed)
        if already is not None:
            print('Hash collision detected.', hashed, 'is the hash of both',
                  already, 'and', event_key)
            print('\tSkipping', repr(event))
            continue
        event_key = hashed

        # the event itself
        db.execute(
            """
           insert into Event(key, uid, name, organizer_email, begin_iso, begin_unix, end_iso, end_unix, all_day)
           values(:key, :uid, :name, :organizer_email, :begin_iso, :begin_unix, :end_iso, :end_unix, :all_day);
           """, {
                'key': event_key,
                'uid': event.uid,
                'name': event.name,
                'organizer_email': None if event.organizer is None else event.organizer.email,
                'begin_iso': start_iso,
                'begin_unix': event.begin.timestamp(),
                'end_iso': event.end.to('utc').isoformat(),
                'end_unix': event.end.timestamp(),
                'all_day': event.all_day
            })
        # the event's description
        db.execute(
            """insert into EventDescription(event_key, text) values (:event_key, :text);""",
            {
                'event_key': event_key,
                'text': event.description
            })
        # the event's locations
        db.executemany(
            """
           insert into EventLocation(event_key, name)
           values(:event_key, :name);
           """, ({
                'event_key': event_key,
                'name': location
            } for location in event.location.split(',')))
        # the event's invitees
        db.executemany(
            """
           insert into EventInvitee(event_key, email)
           values(:event_key, :email);
           """, ({
                'event_key': event_key,
                'email': invitee.email
            } for invitee in event.attendees))

    db.commit()


if __name__ == '__main__':
    options = parse_options()
    print(f'Creating database tables in {options.output_database} ...')
    db = create_tables(options.output_database)
    print(f'Parsing calendar from {options.input_calendar} ...')
    calendar = parse_calendar(options.input_calendar)
    print(f'Filling database with calendar data ...')
    populate_database(calendar, db)
    print('Done.')
