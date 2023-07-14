from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import *


class Connection:
    engine = create_engine(database_addr)
    DB = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()


class Parsed_data(Connection.DB):
    __tablename__ = 'parsed_data'

    Id = Column(Integer, primary_key=True)
    file_name = Column(String)


class Keys(Connection.DB):
    __tablename__ = "keys_to_make_new_json"

    id = Column(Integer, primary_key=True, unique=True)
    main_keys = Column(String, unique=True)


Connection.DB.metadata.create_all(Connection.engine)
