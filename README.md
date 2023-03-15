<img alt="screenshot of exporting Google Calendar" src="screenshot.png" />

```console
$ pip install ics
[...]

$ python ics2sqlite.py --help
usage: ics2sqlite.py [-h] input_calendar output_database

Convert an exported Google Calendar into a sqlite3 database.

positional arguments:
  input_calendar   path to .ics calendar file
  output_database  path to sqlite3 database file

options:
  -h, --help       show this help message and exit

$ python ics2sqlite.py calendar.ics calendar.sqlite
Creating database tables in calendar.sqlite ...
Parsing calendar from calendar.ics ...
[...]
Done.

$ sqlite3 calendar.sqlite
sqlite> .headers on
sqlite> .mode columns
sqlite> select key, name, begin_iso, duration_seconds from Meeting where week='2023-W06' limit 4;
key               name                               begin_iso                  duration_seconds
----------------  ---------------------------------  -------------------------  ----------------
563bc89274f2e308  APM Core Lead + PMs                2023-02-07T14:00:00+00:00  2700.0
3fef6f49ff3e8d2a  1:1 David / Bryan                  2023-02-07T15:00:00+00:00  1800.0
ee4a5a2af9d3ea4f  128-Bit TraceId Encoding for Logs  2023-02-07T16:30:00+00:00  1800.0
bdc1301dd36ecd99  C++ Standup                        2023-02-07T22:00:00+00:00  900.0
sqlite>
```
