# MLBGameDay

A python API for baseball data working with data sources from MLBAM Gameday [data](http://gd2.mlb.com/components/game/mlb/), [Baseball Savant](https://baseballsavant.mlb.com), and [Retrosheet](http://www.retrosheet.org). Stores data using [SQLAlchemy](https://www.sqlalchemy.org). Returns data in [PANDAS](http://pandas.pydata.org) data frames.

Data use is always subject to licenses by [MLB Advanced Media License](http://gd2.mlb.com/components/copyright.txt), [retrosheet](http://www.retrosheet.org/notice.txt), and the [project license](https://github.com/toddheitmann/mlbgameday/blob/master/LICENSE).

## Status

This currently ***partially*** works. Expect continued updates and changes to database structure and data models. If you're curious about using MLBAM gameday data, the best source is [PitchRx](https://github.com/cpsievert/pitchRx). Obviously, it's in R, so you'll need to check out learning R, or find another option if python is your thing.

### Goals

The project has two simple main goals:

- Provide a database storage for baseball data using [SQLAlchemy](https://www.sqlalchemy.org).
- Serve this data back for analysis in dataframes using [PANDAS](http://pandas.pydata.org).

### Roadmap

Right now, I see three main paths to bring this project online, reading and storing downloaded data, creating the database structure, and serving queries in dataframes:

- [ ] *Using Gameday XML data*

  - [x] Store XML files

  - [ ] Parse XML files

  - [x] Update XML files

  - [x] Format XML files for database insertion

  - [x] Option to delete files after inserting into a database

- [x] *Using Baseball Savant data*

  - [x] Store and Parse CSV files

  - [x] Delete files after inserting into a database

  - [x] Insert Into database

  - [x] Update Baseball Savant Trajectory Data

- [ ] *Using Retrosheet data*

  - [x] Download event files

  - [ ] Parse event files using chadwick

    - [x] Windows: include chadwick executables and call to parse

    - [x] Mac: Require installation via [homebrew](https://brew.sh):

        ```bash
        brew install chadwick
        ```

    - [ ] Linux: Provide installation instructions

  - [x] Store data in database

  - [x] Update database with new data

  - [x] Delete files after insertion

- [ ] *Create and Maintain Database*

  - [x] Create database structure

  - [ ] Create database relationships

  - [x] Create database from fresh install

  - [ ] Update database

  - [ ] Join different databases (MLBGameDay, Baseball Savant, Retrosheet)

- [ ] *PANDAS integration*

 - [ ] Serve initial queries into dataframes

### Why?

Being a pythonista, I'm slightly jealous of the regularly updated [PitchRx](https://github.com/cpsievert/pitchRx) CRAN package. This will hopefully provide an alternate for use in python development.

### Stretch Goals

While getting initial functionality, I hope to provide added support for:
- different database type (MySQL, PostgreSQL, etc...)
- external data such as travel distances, weather information, etc...
- OpenWAR, cFIP / DRA, or other advanced metrics

### Thank You

Thanks to MLB Advanced Media for making gameday and pitchf/x data public.

Thank you [Daren Willman](https://twitter.com/darenw) for creating [baseball savant](https://baseballsavant.mlb.com).

Many thanks to all those who support and add to Retrosheet!

The information used here was obtained free of charge from and is copyrighted by Retrosheet.  Interested parties may contact Retrosheet at "www.retrosheet.org".
