from sqlalchemy_pg_fts.tsquery import TSQuery
from sqlalchemy import Column, Integer, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()
Session = scoped_session(sessionmaker())


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    body = Column(TEXT)


def create_item(session, item_body):
    missed_item = Item(body="a lot of us like dinos")
    item = Item(body=item_body)
    session.add_all([missed_item, item])
    session.commit()
    return item


class SavedQuery(Base):
    __tablename__ = "saved_query"
    id = Column(Integer, primary_key=True)
    query = Column(TSQuery)
    no_lang_query = Column(TSQuery(language=None))
