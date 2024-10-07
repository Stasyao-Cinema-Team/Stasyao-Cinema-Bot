from datetime import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.sqlite import INTEGER, TEXT, TIMESTAMP, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


# class Types(Base):
#     __tablename__ = "Types"
#     id = Column(INTEGER, primary_key=True, nullable=False)
#     system = Column(BOOLEAN, nullable=False)
#     value = Column(TEXT, nullable=False)


class Users(Base):
    __tablename__ = "Users"
    id = Column(INTEGER, primary_key=True, nullable=False)
    tg_uname = Column(TEXT, nullable=False, unique=True)
    tg_id = Column(INTEGER, nullable=False, unique=True)
    create_time = Column(TIMESTAMP, nullable=True, default=datetime.now)


class Admins(Base):
    __tablename__ = "Admins"
    id = Column(INTEGER, primary_key=True, nullable=False)
    user_id: Users.id = Column(INTEGER, ForeignKey(Users.id), nullable=False, unique=True)
    create_time = Column(TIMESTAMP, nullable=False, default=datetime.now)
    create_uid: Users.id = Column(INTEGER, ForeignKey(Users.id), nullable=False)
    update_time = Column(TIMESTAMP, nullable=False, default=datetime.now)
    update_uid: Users.id = Column(INTEGER, ForeignKey(Users.id), nullable=False)
    active = Column(BOOLEAN, nullable=False, default=False)


class Events(Base):
    __tablename__ = "Events"
    id = Column(INTEGER, primary_key=True, nullable=False)
    name = Column(TEXT, nullable=False, unique=True)
    create_time = Column(TIMESTAMP, nullable=False, default=datetime.now)
    create_uid: Users.id = Column(INTEGER, ForeignKey(Users.id), nullable=False)
    update_time = Column(TIMESTAMP, nullable=False, default=datetime.now)
    update_uid: Users.id = Column(INTEGER, ForeignKey(Users.id), nullable=False)
    active = Column(BOOLEAN, nullable=False, default=False)


class Actions(Base):
    __tablename__ = "Actions"
    id = Column(INTEGER, primary_key=True, nullable=False)
    name = Column(TEXT, nullable=False, unique=True)
    event_id: Events.id = Column(INTEGER, ForeignKey(Events.id), nullable=False)
    create_time = Column(TIMESTAMP, nullable=False, default=datetime.now)
    create_uid: Users.id = Column(INTEGER, ForeignKey(Users.id), nullable=False)
    update_time = Column(TIMESTAMP, nullable=False, default=datetime.now)
    update_uid: Users.id = Column(INTEGER, ForeignKey(Users.id), nullable=False)
    active = Column(BOOLEAN, nullable=False, default=False)


class Ordering(Base):
    __tablename__ = "Ordering"
    entity_id = Column(TEXT, nullable=False, unique=True)
    order = Column(TEXT, nullable=False)


class Data(Base):
    __tablename__ = "Data"
    id = Column(INTEGER, primary_key=True, nullable=False)
    action_id: Actions.id = Column(INTEGER, ForeignKey(Actions.id), nullable=False)
    create_time = Column(TIMESTAMP, nullable=False, default=datetime.now)
    create_uid: Users.id = Column(INTEGER, ForeignKey(Users.id), nullable=False)
    system = Column(BOOLEAN, nullable=False, default=False)
    type = Column(TEXT, nullable=False)
    active = Column(BOOLEAN, nullable=False, default=True)
    value = Column(TEXT, nullable=False)
