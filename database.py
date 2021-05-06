from typing import Optional

from sqlalchemy import Column, String, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

import logging

engine: Optional[Engine] = None
session_maker: Optional[sessionmaker] = None
session: Optional[scoped_session] = None

Base = declarative_base()


class DBSession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        session.remove()


class Tag(Base):
    __tablename__ = 'tag'

    def __init__(self, name: str, contents: str):
        self.name = name
        self.contents = contents

    name = Column(String, primary_key=True)
    contents = Column(String)


def load_engine():
    global engine
    engine = create_engine('sqlite:///data.db')
    global session_maker
    session_maker = sessionmaker(bind=engine)
    global session
    session = scoped_session(session_maker)
    Base.metadata.create_all(bind=engine)

    # logging.basicConfig()
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    Base.query = session.query_property()
