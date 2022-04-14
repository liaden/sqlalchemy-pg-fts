from sqlalchemy import Column, Integer, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()
Session = scoped_session(sessionmaker())


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    body = Column(TEXT)
