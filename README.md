# MLBGame Data

A python API for baseball data working with data from MLBAM Gameday [data](http://gd2.mlb.com/components/game/mlb/), [Baseball Savant](https://baseballsavant.mlb.com), and [Retrosheet](http://www.retrosheet.org). Stores data using [SQLAlchemy](https://www.sqlalchemy.org). Returns data in [PANDAS](http://pandas.pydata.org) data frames.

Data use is always subject to licenses by [MLB Advanced Media License](http://gd2.mlb.com/components/copyright.txt), [retrosheet](http://www.retrosheet.org/notice.txt), and the [project license](https://github.com/toddheitmann/mlbgameday/blob/master/LICENSE).

## Status

This currently ***does not*** work. If you're curious about using MLBAM gameday data, the best source is [PitchRx](https://github.com/cpsievert/pitchRx). Obviously, it's in R, so you'll need to check out learning R, or find another option if python is your thing.

### Goals

The project has two simple main goals:

- Provide a database storage for gameday information using [SQLAlchemy](https://www.sqlalchemy.org) in sqlite format.
- Serve this data back in [PANDAS](http://pandas.pydata.org) dataframes for further analysis.

### Roadmap

Right now, I see three main paths to bring this project online, reading and storing downloaded data, creating the database structure, and serving queries in dataframes:

- [ ] Using Gameday XML data

  - [x] Store XML files

  - [ ] Parse XML files

  - [x] Update XML files

  - [x] Format XML files for database insertion

  - [ ] Option to delete files after inserting into a database

- [ ] Using Baseball Savant data

  - [x] Store and Parse CSV files

  - [ ] Update CSV files

  - [ ] Option to delete files after inserting into a database

- [ ] Using Retrosheet data

  - [x] Download event files

  - [ ] Parse event files using chadwick

    - [x] Windows: include chadwick executables and call to parse

    - [ ] Mac: Require installation via: '''{r, engine='bash', count_lines}brew install chadwick'''

    - [ ] Linux: Provide installation instructions

  - [ ] Store data in database

  - [ ] Update database with new data

  - [ ] Delete files after insertion

- [ ] Create and Maintain database

  - [x] Create database structure

  - [ ] Create database relationships

  - [x] Create database from fresh install

  - [ ] Update database

  - [ ] Create filters and wrappers for joins

- [ ] PANDAS integration

 - [ ] Serve initial queries into dataframes

### Why?

Being a pythonista, I'm slightly jealous of the regularly updated [PitchRx](https://github.com/cpsievert/pitchRx) CRAN package. This will hopefully provide an alternate for use in python development.

### Stretch Goals

While getting initial functionality, I hope to provide added support for:
- different database type (MySQL, PostgreSQL, etc...)
- external data such as travel distances, weather information, etc...
- OpenWAR, cFIP / DRA, or other advanced metrics

### Thank You

Many thanks to MLB Advanced Media for making gameday and pitchf/x data public.

Also, many thanks to all those who support and add to Retrosheet!

The information used here was obtained free of charge from and is copyrighted by Retrosheet.  Interested parties may contact Retrosheet at "www.retrosheet.org".
