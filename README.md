# mlbgameday

A python wrapper for MLBAM gameday data. Stores data using [SQLAlchemy](https://www.sqlalchemy.org). Returns data in [PANDAS](http://pandas.pydata.org) data frames. Data use is always subject to [MLB Advanced Media License](http://gd2.mlb.com/components/copyright.txt) as well as the project license.

## Status

This currently ***does not*** work. If you're curious about using MLBAM gameday data, the best source is [PitchRx](https://github.com/cpsievert/pitchRx). Obviously, it's in R, so you'll need to check out learning R, or find another option if python is your thing.

### Goals

The project has two simple main goals:

- Provide a simple db storage for gameday information using [SQLAlchemy](https://www.sqlalchemy.org) in sqlite format.
- Serve this data back in [PANDAS](http://pandas.pydata.org) dataframes for further analysis.

### Roadmap

Right now, I see three main paths to bring this project online, reading xml data, creating the database structure, and serving filters in dataframes:

- [ ] Using XML data

  - [ ] Store and Parse XML files

  - [ ] Update XML files

  - [ ] Option to delete files after inserting into a database

- [ ] Create and Maintain database

  - [ ] Create database structure

  - [ ] Create database from fresh install

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
- OpenWAR, Game Scores, or other advanced metrics
