
create table Event(
    key text primary key not null,
    uid text not null, -- can be duplicated (recurring events)
    name text,
    organizer_email text,
    begin_iso text not null,
    begin_unix real not null,
    end_iso text,
    end_unix real,
    all_day boolean,
    description text);

-- This is a separate table because event descriptions tend to be
-- machine-generated spam.
create table EventDescription(
    event_key text not null,
    text text,
    foreign key(event_key) references Event(key));

create table EventLocation(
    event_key text not null,
    name text,
    foreign key(event_key) references Event(key));

create table EventInvitee(
    event_key text not null,
    email text,
    foreign key(event_key) references Event(key));

create view Meeting as
    select 
        e.key as key,
        e.uid as uid,
        e.name as name,
        e.begin_iso as begin_iso,
        e.end_iso as end_iso,
        e.end_unix - e.begin_unix as duration_seconds,
        strftime('%Y-W%W', begin_iso) as week
    from Event e
    where not e.all_day
        -- I'm using a 23 hour day, so sue me!
        and (e.end_unix - e.begin_unix) / 60 / 60 < 23; 
        