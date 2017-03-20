"""
This module creates sqlalchemy classes mlbgameday data,
which is subject to the license at http://gd2.mlb.com/components/copyright.txt
"""

from sqlalchemy import Column, Date, DateTime, Float, Integer, SmallInteger, String, func, ForeignKey
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Game(Base):
    __tablename__ = 'game'
    game_pk = Column(Integer, primary_key=True)
    gid = Column(String(26))
    venue = Column(String(50))
    venue_id = Column(Integer)
    location = Column(String(20), default = '')
    game_date = Column(Date)
    datetime_local = Column(DateTime)
    datetime_et = Column(DateTime)
    first_pitch_et = Column(String(5), default = '')
    home_time = Column(String(5))
    home_time_zone = Column(String(3))
    home_ampm = Column(String(2))
    resume_home_time = Column(DateTime, default = None)
    away_time = Column(String(5))
    away_time_zone = Column(String(3))
    away_ampm = Column(String(2))
    resume_away_time = Column(DateTime, default = None)
    day = Column(String(3))
    game_type = Column(String(1))
    home_name_abbrev = Column(String(3))
    home_code = Column(String(3))
    home_file_code = Column(String(5))
    home_team_id = Column(Integer)
    home_team_city = Column(String(25))
    home_team_name = Column(String(30))
    home_division = Column(String(2))
    home_league_id = Column(Integer)
    home_sport_code = Column(String(3))
    home_league_id_spring = Column(String(3), default = '')
    home_split_squad = Column(String(1), default = '')
    away_name_abbrev = Column(String(3))
    away_code = Column(String(3))
    away_file_code = Column(String(5))
    away_team_id = Column(Integer)
    away_team_city = Column(String(25))
    away_team_name = Column(String(30))
    away_division = Column(String(2))
    away_league_id = Column(Integer)
    away_sport_code = Column(String(3))
    away_league_id_spring = Column(String(3), default = '')
    away_split_squad = Column(String(1), default = '')
    gameday_sw = Column(String(1))
    tiebreaker_sw = Column(String(1), default = '')
    home_games_back = Column(Float)
    away_games_back = Column(Float)
    home_games_back_wildcard = Column(Float)
    away_games_back_wildcard = Column(Float)
    home_win = Column(Integer)
    home_loss = Column(Integer)
    away_win = Column(Integer)
    away_loss = Column(Integer)
    league = Column(String(4), default = '')
    status = Column(String(15))
    ind = Column(String(2))
    home_team_runs = Column(Integer)
    away_team_runs = Column(Integer)
    home_team_hits = Column(Integer)
    away_team_hits = Column(Integer)
    home_team_errors = Column(Integer)
    away_team_errors = Column(Integer)
    reason = Column(String(17), default = '')
    description = Column(String(50), default = '')
    original_date = Column(Date)
    double_header_sw = Column(String(1), default = '')
    game_nbr = Column(Integer, default = None)
    tbd_flag = Column(String(1), default = '')
    home_team_hr = Column(Integer, default = None)
    away_team_hr = Column(Integer, default = None)
    home_team_sb = Column(Integer, default = None)
    away_team_sb = Column(Integer, default = None)
    home_team_so = Column(Integer, default = None)
    away_team_so = Column(Integer, default = None)
    resume_date = Column(Date, default = None)
    resume_time_date = Column(DateTime, default = None)
    resume_ampm = Column(String(2), default = '')
    resume_home_ampm = Column(String(2), default = '')
    series = Column(String(12), default = '')
    series_num = Column(Integer, default = None)
    ser_home_nbr = Column(Integer, default = None)
    ser_games = Column(Integer, default = None)
    scheduled_innings = Column(Integer)
    if_necessary = Column(String(1), default = '')
    tv_station = Column(String(60))

    def __repr__(self):
        return '<Game(gid = %s, home = %i, away = %i, venue = %s)>' % \
                (self.gid, self.home_team_runs, self.away_team_runs, self.venue)

class Player(Base):
    __tablename__ = 'player'
    game_pk = Column(Integer, primary_key = True)
    player_id = Column(Integer, primary_key = True)
    gid = Column(String(26))
    first = Column(String(12))
    last = Column(String(15))
    boxname = Column(String(15))
    position = Column(String(2))
    home_flag = Column(Integer, default = None)
    team_id = Column(Integer, default = None)
    team_abbrev = Column(String(3))
    parent_team_id = Column(Integer)
    parent_team_abbrev = Column(String(3))
    num = Column(Integer)
    bats = Column(String(1))
    rl = Column(String(1))
    game_position = Column(String(2), default = '')
    current_position = Column(String(2), default = '')
    bat_order = Column(Integer, default = None)
    status = Column(String(1))
    avg = Column(Float)
    hr = Column(Integer)
    rbi = Column(Integer)
    wins = Column(Integer, default = None)
    losses = Column(Integer, default = None)
    era = Column(Float, default = None)

    def __repr__(self):
        return '<Player(gid = %s, boxname = %s)>' % (self.gid, self.boxname)

class Coach(Base):
    __tablename__ = 'coach'
    game_pk = Column(Integer, primary_key = True)
    coach_id = Column(Integer, primary_key = True)
    gid = Column(String(26))
    home_flag = Column(Integer)
    first = Column(String(10))
    last = Column(String(15))
    num = Column(Integer)
    position = Column(String(25))

    def __repr__(self):
        return '<Coach(gid = %s, last = %s)>' % (self.gid, self.last)

class Umpire(Base):
    __tablename__ = 'umpire'
    game_pk = Column(Integer, primary_key = True)
    umpire_id = Column(Integer, primary_key = True)
    gid = Column(String(26))
    last = Column(String(15), default = '')
    first = Column(String(10), default = '')
    name = Column(String(25))
    position = Column(String(6))

    def __repr__(self):
        return '<Umpire(gid = %s, last = %s)>' % (self.gid, self.last)

class HIP(Base):
    __tablename__ = 'hip'
    game_pk = Column(Integer, primary_key = True)
    pitcher = Column(Integer, primary_key = True)
    batter = Column(Integer, primary_key = True)
    gid = Column(String(26))
    des = Column(String(20))
    x = Column(Float)
    y = Column(Float)
    hip_type = Column(Float)
    team = Column(String(1))
    inning = Column(Integer)

    def __repr__(self):
        return '<HIP(gid = %s, inning = %s, des = %s)>' \
               % (self.gid, self.inning, self.des)

class Event(Base):
    __tablename__ = 'Event'
    game_pk = Column(Integer, primary_key = True)
    game_event_number = Column(Integer, primary_key = True)
    gid = Column(String(26))
    venue_id = Column(Integer)
    event_type = Column(String(6))
    event_num = Column(Integer)
    inning = Column(Integer)
    inning_topbot = Column(String(3))
    play_guid = Column(String(36), default = '')
    pitcher = Column(Integer)
    catcher = Column(Integer)
    battter = Column(Integer)
    umpire = Column(Integer)
    player = Column(Integer, default = None)
    start_outs = Column(Integer)
    start_base_state = Column(String(3))
    start_out_base_state = Column(String(4))
    start_home_team_runs = Column(Integer)
    start_away_team_runs = Column(Integer)
    start_1B = Column(Integer)
    start_2B = Column(Integer)
    start_3B = Column(Integer)
    b = Column(Integer)
    s = Column(Integer)
    o = Column(Integer)
    home_team_runs = Column(Integer, default = None)
    away_team_runs = Column(Integer, default = None)
    pitch = Column(Integer, default = None)
    num = Column(Integer, default = None)
    p_throws = Column(String(1), default = '')
    stand = Column(String(1), default = '')
    b_height = Column(String(4), default = '')
    score = Column(String(1), default = '')
    tfs = Column(String(6), default = '')
    tfs_zulu = Column(String(20), default = '')
    start_tfs = Column(String(6), default = '')
    start_tfs_zulu = Column(String(20), default = '')
    des = Column(String(425))
    des_es = Column(String(400))
    event = Column(String(25))
    event_es = Column(String(50), default = '')
    event2 = Column(String(25), default = '')
    event2_es = Column(String(50), default = '')
    event3 = Column(String(25), default = '')
    event3_es = Column(String(50), default = '')
    event4 = Column(String(25), default = '')
    event4_es = Column(String(50), default = '')
    end_outs = Column(Integer)
    end_base_state = Column(String(3))
    end_out_base_state = Column(String(4))
    end_home_team_runs = Column(Integer)
    end_away_team_runs = Column(Integer)
    end_1B = Column(Integer)
    end_2B = Column(Integer)
    end_3B = Column(Integer)

    def __repr__(self):
        return '<Event(gid = %s, game_event_number = %i, inning = %i, event_type = %s)>' \
               % (self.gid, self.game_event_number, self.inning, self.event_type))

class Pitch(Base):
    __tablename__ = 'pitch'
    game_pk = Column(Integer, primary_key = True)
    pitch_id = Column(Integer, primary_key = True)
    venue_id = Column(Integer)
    gid = Column(String)
    inning = Column(Integer)
    inning_topbot = Column(String(3))
    game_event_number = Column(Integer)
    event_num = Column(Integer)
    event = Column(String(35))
    pitcher = Column(Integer)
    catcher = Column(Integer)
    batter = Column(Integer)
    umpire = Column(Integer)
    start_outs = Column(Integer)
    start_base_state = Column(String(3))
    start_out_base_state = Column(String(4))
    start_home_team_runs = Column(Integer)
    start_away_team_runs = Column(Integer)
    start_1B = Column(Integer)
    start_2B = Column(Integer)
    start_3B = Column(Integer)
    des = Column(String(35))
    des_es = Column(String(35))
    p_type = Column(String(1))
    tfs = Column(String(6))
    tfs_zulu = Column(String(20))
    x = Column(Float)
    y = Column(Float)
    sv_id = Column(DateTime)
    play_guid = Column(String(36))
    start_speed = Column(Float)
    end_speed = Column(Float)
    sz_top = Column(Float)
    sz_bot = Column(Float)
    pfx_x = Column(Float)
    pfx_z = Column(Float)
    px = Column(Float)
    pz = Column(Float)
    x0 = Column(Float)
    y0 = Column(Float)
    z0 = Column(Float)
    vx0 = Column(Float)
    vy0 = Column(Float)
    vz0 = Column(Float)
    ax = Column(Float)
    ay = Column(Float)
    az = Column(Float)
    break_y = Column(Float)
    break_angle = Column(Float)
    break_length = Column(Float)
    pitch_type = Column(String(2))
    type_confidence = Column(Float)
    zone = Column(Integer)
    nasty = Column(Integer)
    spin_dir = Column(Float)
    spin_rate = Column(Float)
    cc = Column(String(200))
    mt = Column(String(1))
    on_1b = Column(Integer, default = None)
    on_2b = Column(Integer, default = None))
    on_3b = Column(Integer, default = None))
    end_outs = Column(Integer)
    end_base_state = Column(String(3))
    end_out_base_state = Column(String(4))
    end_home_team_runs = Column(Integer)
    end_away_team_runs = Column(Integer)
    end_1B = Column(Integer)
    end_2B = Column(Integer)
    end_3B = Column(Integer)

    def __repr__(self):
        return '<Pitch(gid = %s, pitch_num = %i, pitch_type = %s)>' % \
               (self.gid, self.pitch_num, self.pitch_type)


class Runner(Base):
    __tablename__ = 'runner'
    game_pk = Column(Integer, primary_key = True, ForeignKey('game.game_pk'))
    runner_id = Column(Integer, primary_key = True)
    game_event_number = Column(Integer, primary_key = True)
    venue_id = Column(Integer)
    gid = Column(String(26))
    event_num = Column(Integer, default = None))
    inning = Column(Integer)
    inning_topbot = Column(String(3))
    pitcher = Column(Integer)
    catcher = Column(Integer)
    batter = Column(Integer)
    umpire = Column(Integer)
    start_outs = Column(Integer)
    start_base_state = Column(String(3))
    start_out_base_state = Column(String(4))
    start_home_team_runs = Column(Integer)
    start_away_team_runs = Column(Integer)
    start_1B = Column(Integer)
    start_2B = Column(Integer)
    start_3B = Column(Integer)
    event = Column(String(25))
    start = Column(String(2))
    end = Column(String(2))
    score = Column(String(1), default = '')
    rbi = Column(String(1), default = '')
    earned = Column(String(1), default = '')
    end_outs = Column(Integer)
    end_base_state = Column(String(3))
    end_out_base_state = Column(String(4))
    end_home_team_runs = Column(Integer)
    end_away_team_runs = Column(Integer)
    end_1B = Column(Integer)
    end_2B = Column(Integer)
    end_3B = Column(Integer)

    def __repr__(self):
        return '<Runner(game_pk = %s, gid = %s, des = %s)>' % \
               (str(self.game_pk), str(self.event_num), str(self.des))

class Pickoff(Base):
    __tablename__ = 'pickoff'
    game_pk = Column(Integer, primary_key = True, ForeignKey('game.game_pk'))
    game_event_number = Column(Integer, primary_key = True)
    atbat_pickoff_number = Column(Integer, primary_key = True)
    venue_id = Column(Integer)
    gid = Column(String(26))
    event_num = Column(Integer, default = None))
    inning = Column(Integer)
    inning_topbot = Column(String(3))
    pitcher = Column(Integer)
    catcher = Column(Integer)
    batter = Column(Integer)
    umpire = Column(Integer)
    start_outs = Column(Integer)
    start_base_state = Column(String(3))
    start_out_base_state = Column(String(4))
    start_home_team_runs = Column(Integer)
    start_away_team_runs = Column(Integer)
    start_1B = Column(Integer)
    start_2B = Column(Integer)
    start_3B = Column(Integer)
    des = Column(String(20))
    des_es = Column(String(20), default = '')
    play_guid = Column(String(36), default = '')
    end_outs = Column(Integer)
    end_base_state = Column(String(3))
    end_out_base_state = Column(String(4))
    end_home_team_runs = Column(Integer)
    end_away_team_runs = Column(Integer)
    end_1B = Column(Integer)
    end_2B = Column(Integer)
    end_3B = Column(Integer)

    def __repr__(self):
        return '<Pickoff(gid = %s, game_event_number = %i, atbat_pickoff_number = %s)>' \
               % (self.gid, self.game_event_number, self.atbat_pickoff_numbers)


class Trajectory(Base):
    __tablename__ = 'trajectory'
    game_pk = Column(Integer, primary_key = True)
    pitch_id = Column(Integer, primary_key = True)
    pitch_type = Column(String(2))
    game_date = Column(DateTime)
    start_speed = Column(Float)
    x0 = Column(Float)
    z0 = Column(Float)
    player_name = Column(String(30))
    batter = Column(Integer)
    pitcher = Column(Integer)
    events = Column(String(10))
    description = Column(String(20))
    spin_dir = Column(Float)
    spin_rate = Column(Float)
    break_angle = Column(Float)
    break_length = Column(Float)
    zone = Column(Integer)
    des = Column(String(100))
    game_type = Column(String(1))
    stand = Column(String(1))
    p_throws = Column(String(1))
    home_team = Column(String(3))
    away_team = Column(String(3))
    event_type = Column(String(1))
    hit_location = Column(Integer)
    bb_type = Column(Integer)
    balls = Column(Integer)
    strikes = Column(Integer)
    game_year = Column(Integer)
    pfx_x = Column(Float)
    pfx_z = Column(Float)
    px = Column(Float)
    pz = Column(Float)
    on_3b = Column(Integer)
    on_2b = Column(Integer)
    on_1b = Column(Integer)
    outs_when_up = Column(Integer)
    inning = Column(Integer)
    inning_topbot = Column(String(3))
    hc_x = Column(Float)
    hc_y = Column(Float)
    tfs = Column(Integer)
    tfs_zulu = Column(DateTime)
    catcher = Column(Integer)
    umpire = Column(Integer)
    sv_id = Column(String(13))
    vx0 = Column(Float)
    vy0 = Column(Float)
    vz0 = Column(Float)
    ax = Column(Float)
    ay = Column(Float)
    az = Column(Float)
    sz_top = Column(Float)
    sz_bot = Column(Float)
    hit_distance_sc = Column(Float)
    hit_speed = Column(Float)
    hit_angle = Column(Float)
    effective_speed = Column(Float)
    release_spin_rate = Column(Float)
    release_extension = Column(Float)

    def __repr__(self):
        return '<Trajectory(game_pk = %i, pitcher = %s, game_date = %s)>' % \
               (self.game_pk, self.player_name, self.game_date.srftime('%Y-%m-%d'))
