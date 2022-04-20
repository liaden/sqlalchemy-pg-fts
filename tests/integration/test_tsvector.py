import pytest

from sqlalchemy import select
from sqlalchemy.dialects import postgresql
from sqlalchemy_pg_fts.tsvector import to_tsvector
from sqlalchemy_pg_fts.tsquery import to_tsquery
from tests.integration.conftest import connection, session
from tests.integration.model import create_document, Document, SavedVector


VECTOR_TEXT = "Dinosaurs lived a long, long time ago."
SPANISH_VECTOR_TEXT = "Los dinosaurios vivieron hace mucho, mucho tiempo."


def create_vector(session, **kwargs):
    v = SavedVector(**kwargs)
    session.add_all([v])
    session.commit()
    return v


def test_vector(session):
    v = create_vector(session, vector=VECTOR_TEXT)
    saved_vec = session.query(SavedVector).filter(SavedVector.id == v.id).all()[0]
    assert saved_vec.vector != VECTOR_TEXT
    assert "'dinosaur':1" in saved_vec.vector
    assert "'long':4,5" in saved_vec.vector
    assert "'a'" not in saved_vec.vector


def test_null_vector(session):
    v = create_vector(session)
    saved_vec = session.query(SavedVector).filter(SavedVector.id == v.id).all()[0]
    assert saved_vec.vector is None


def test_vector_language(session):
    v = create_vector(session, vector="extinction", no_lang_vector="extinction")
    saved_vec = session.query(SavedVector).filter(SavedVector.id == v.id).all()[0]
    assert saved_vec.vector != saved_vec.no_lang_vector
    assert saved_vec.vector == "'extinct':1"
    assert saved_vec.no_lang_vector == "'extinction':1"


def test_find_vector_by_vector(session):
    v = create_vector(session, vector=VECTOR_TEXT)
    found_vec = (
        session.query(SavedVector)
        .filter(SavedVector.vector == to_tsvector(VECTOR_TEXT))
        .all()
    )


def test_find_vectory_by_query(session):
    v = create_vector(session, vector=VECTOR_TEXT)
    found_vec = (
        session.query(SavedVector)
        .filter(SavedVector.vector.op("@@")(to_tsquery("dinosaur & long")))
        .all()
    )[0]
    assert found_vec.id == v.id


def test_to_tsvector_index(session):
    english_doc = create_document(session, VECTOR_TEXT, "english")
    spanish_doc = create_document(session, SPANISH_VECTOR_TEXT, "spanish")
    no_lang_doc = create_document(session, VECTOR_TEXT)

    # english tsquery finds english doc when filtering against language as well
    found_docs = (
        session.query(Document)
        .filter(
            to_tsvector("english", Document.body).op("@@")(
                to_tsquery("english", "dinosaur & long")
            )
        )
        .filter(Document.language == "english")
        .all()
    )
    assert [english_doc] == found_docs

    # simple tsquery finds no lang doc and english doc when
    found_docs = (
        session.query(Document)
        .filter(
            to_tsvector("english", Document.body).op("@@")(
                to_tsquery("dinosaur & long")
            )
        )
        .all()
    )
    assert [english_doc, no_lang_doc] == found_docs

    # spanish tsquery finds spansih doc regardless of filtering against the language
    found_docs = (
        session.query(Document)
        .filter(
            to_tsvector("spanish", Document.body).op("@@")(
                to_tsquery("spanish", "dinosaurios & vivieron")
            )
        )
        .all()
    )
    assert [spanish_doc] == found_docs
