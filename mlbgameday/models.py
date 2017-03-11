from sqlalchemy import Column, Date, DateTime, Float, Integer, SmallInteger, String, func, ForeignKey
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

Base = declarative_base()

class GameModel(Base):
    __tablename__ = 'game'
    game_pk = Column(Integer, primary_key=True)
    gid = Column(String(20))
    venue = Column(String(50))
    venue_id = Column(Integer)
    location = Column(String())
    time_date = Column(DateTime)
    home_time = Column(DateTime)
    home_time_zone = Column(String(2))
    day = Column(String(3))
    game_type = Column(String(1))
    away_name_abbrev = Column(String(3))
    away_code = Column(String(3))
    away_file_code = Column(String(5))
    away_team_id = Column(Integer)
    away_team_city = Column(String(20))
    away_team_name = Column(String(30))
    away_division = Column(String(2))
    away_league_id = Column(Integer)
    away_sport_code = Column(String(3))
    home_name_abbrev = Column(String(3))
    home_code = Column(String(3))
    home_file_code = Column(String(5))
    home_team_id = Column(Integer)
    home_team_city = Column(String(20))
    home_team_name = Column(String(30))
    home_division = Column(String(2))
    home_league_id = Column(Integer)
    home_sport_code = Column(String(3))
    gameday_sw = Column(String(1))
    away_games_back = Column(Float)
    home_games_back = Column(Float)
    away_games_back_wildcard = Column(Float)
    home_games_back_wildcard = Column(Float)
    away_win = Column(Integer)
    away_loss = Column(Integer)
    home_win = Column(Integer)
    home_loss = Column(Integer)
    league = Column(String(4))
    status = Column(String(15))
    ind = Column(String(2))
    away_team_runs = Column(Integer)
    home_team_runs = Column(Integer)
    away_team_hits = Column(Integer)
    home_team_hits = Column(Integer)
    away_team_errors = Column(Integer)
    home_team_errors = Column(Integer)
    reason = Column(String(17))
    description = Column(String)
    original_date = Column(Date)
    double_header_sw = Column(String(1))
    game_nbr = Column(Integer)
    tbd_flag = Column(String(1))
    away_team_hr = Column(Integer)
    home_team_hr = Column(Integer)
    away_team_sb = Column(Integer)
    home_team_sb = Column(Integer)
    away_team_so = Column(Integer)
    home_team_so = Column(Integer)
    resume_date = Column(Date)
    series = Column(String(12))
    series_num = Column(Integer)
    ser_home_nbr = Column(Integer)
    ser_games = Column(Integer)

    def __repr__(self):
        return '<GameModel(gid = %s)>' % (self.gid)

class PlayerModel(Base):
    __tablename__ = 'player'
    gid = Column(String, primary_key = True, ForeignKey('game.gid'))
    player_id = Column(Integer, primary_key = True)

class CoachModel(Base):
    __tablename__ = 'coach'
    gid = Column(String, primary_key = True, ForeignKey('game.gid'))
    coach_id = Column(Integer, primary_key = True)

class UmpireModel(Base):
    __tablename__ = 'coach'
    gid = Column(String, primary_key = True, ForeignKey('game.gid'))
    umpire_id = Column(Integer, primary_key = True)

class HIPModel(Base):
    __tablename__ = 'hip'
    gid = Column(String, primary_key = True, ForeignKey('game.gid'))
    umpire_id = Column(Integer, primary_key = True)

class AtBatModel(Base):
    __tablename__ = 'atbat'
    game_pk = Column(Integer, primary_key = True, ForeignKey('game.game_pk'))
    gid = Column(String)
    atbat_num = Column(Integer, primary_key = True)
    inning = Column(Integer)
    inning_topbot = Column(String(3))
    b = Column(Integer)
    s = Column(Integer)
    o = Column(Integer)
    start_tfs = Column(Integer)
    start_tfs_zulu = Column(DateTime)
    batter = Column(Integer, ForeignKey('player.player_id'))
    stand = Column(String(1))
    b_height = Column(String(4))
    pitcher = Column(Integer, ForeignKey('player.player_id'))
    p_throws = Column(String(1))
    des = Column(String(100))
    des_es = Column(String(100))
    event_num = Column(Integer)
    event = Column(Integer(15))
    event_es = Column(Integer(15))
    play_guid = Column(String(40))
    home_team_runs = Column(Integer)
    away_team_runs = Column(Integer)
    score = Column(String(1))
    event2 = Column(Integer(15))
    event2_es = Column(Integer(15))

    def __repr__(self):
        return '<AtBatModel(gid = %s, atbat_num = %s, inning = %s)>' % \
               (self.gid, self.atbat_num, self.inning)

class PitchModel(Base):
    __tablename__ = 'pitch'
    game_pk = Column(Integer, primary_key = True, ForeignKey('game.game_pk'), ForeignKey('atbat.game_pk'))
    gid = Column(String)
    pitch_num = Column(Integer, primary_key = True)
    inning = Column(Integer)
    inning_topbot = Column(String(3))
    atbat_num = Column(Integer, ForeignKey('atbat.atbat_num'))
    des = Column(String(20))
    pitch_id = Column(Integer)
    pitch_type = Column(String(1))
    tfs = Column(DateTime)
    tfs_zulu = Column(DateTime)
    x = Column(Float)
    y = Column(Float)
    event_num = Column(Integer)
    sv_id = Column(DateTime)
    play_guid = Column(String(40))
    start_speed = Column(Float)
    end_speed = Column(Float)
    sz_top = Column(Float)
    sz_bot = Column(Float)
    pfx_x = Column(Float)
    pfx_z = Column(Float)
    px = Column(Float)
    py = Column(Float)
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

    def __repr__(self):
        return '<PitchModel(gid = %s, pitch_num = %s, pitch_type = %s)>' % \
               (self.gid, self.pitch_num, self.pitch_type)


class RunnerModel(Base):
    __tablename__ = 'runner'
    game_pk = Column(Integer, primary_key = True, ForeignKey('game.game_pk'))
    gid = Column(String)
    event_num = Column(Integer, primary_key = True)
    inning_topbot = Column(String(3))
    inning = Column(Integer)
    bat_num = Column(Integer, ForeignKey('atbat.bat_num'))
    runner_id = Column(Integer)
    start = Column(String(2))
    end = Column(String(2))
    event = Column(String(10))
    score = Column(String(1))
    rbi = Column(String(1))
    earned = Column(String(1))

class PickoffModel(Base):
    __tablename__ = 'pickoff'
    gid = Column(String, primary_key = True, ForeignKey('game.gid'))
    pickoff_num = Column(Integer, primary_key = True)

class TrajectoryModel(Base):
    __tablename__ = 'trajectory'
    game_pk = Column(Integer, primary_key = True, ForeignKey('game.gid'), ForeignKey('pitch.gid'))
    pitch_type = Column(String(2))
    pitch_id = Column(Integer, primary_key = True, ForeignKey('pitch.pitch_id'))
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
        return '<TrajectoryModel(game_pk = %s, pitcher = %s, game_date = %s)>' % \
               (str(self.game_pk), str(self.player_name), str(self.game_date))

class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    # Use default=func.now() to set the default hiring time
    # of an Employee to be the current time when an
    # Employee record was created
    hired_on = Column(DateTime, default=func.now())
    department_id = Column(Integer, ForeignKey('department.id'))
    role_id = Column(Integer, ForeignKey('roles.role_id'))
    # Use cascade='delete,all' to propagate the deletion of a Department onto its Employees
    department = relationship(
        Department,
        backref=backref('employees',
                        uselist=True,
                        cascade='delete,all'))
    role = relationship(
        Role,
        backref=backref('roles',
                        uselist=True,
                        cascade='delete,all'))
