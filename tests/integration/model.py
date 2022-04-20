from sqlalchemy_pg_fts.tsquery import TSQuery
from sqlalchemy_pg_fts.tsvector import TSVector
from sqlalchemy import text, Column, Index, Integer, String, TEXT
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


class Document(Base):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True)
    body = Column(TEXT)
    language = Column(String)
    __tableargs__ = [
        Index(
            "ix_document_body_english_gin_tsvec",
            text("to_tsvector('english', body)"),
            postgresql_using="gin",
            postgresql_where=text("language = 'english'"),
        ),
        Index(
            "ix_document_body_spanish_gin_tsvec",
            text("to_tsvector('spanish', body)"),
            postgresql_using="gin",
            postgresql_where=text("language = 'spanish'"),
        ),
    ]


def create_document(session, body, language=None):
    doc = Document(body=body, language=language)
    session.add_all([doc])
    session.commit()
    return doc


class SavedQuery(Base):
    __tablename__ = "saved_query"
    id = Column(Integer, primary_key=True)
    query = Column(TSQuery)
    no_lang_query = Column(TSQuery(language=None))


class SavedVector(Base):
    __tablename__ = "saved_vector"
    id = Column(Integer, primary_key=True)
    vector = Column(TSVector)
    no_lang_vector = Column(TSVector(language=None))
