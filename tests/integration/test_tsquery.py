import pytest

from sqlalchemy import select
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Query
from sqlalchemy_pg_fts.websearch import Websearch
from sqlalchemy_pg_fts.tsquery import to_tsquery
from tests.integration.conftest import connection, session
from tests.integration.model import SavedQuery


def create_query(session, **kwargs):
    q = SavedQuery(**kwargs)
    session.add_all([q])
    session.commit()
    return q


def test_query(session):
    q = create_query(session, query="stegasaurus & plesiosaurus")
    saved_query = session.query(SavedQuery).filter(SavedQuery.id == q.id).all()[0]
    assert saved_query.query == "'stegasaurus' & 'plesiosaurus'"


def test_query_simplification(session):
    original_query = "(stegasaurus & plesiosaurus)"
    q = create_query(session, query=original_query)
    assert original_query != q.query


def test_query_language(session):
    q = create_query(session, query="extinction", no_lang_query="extinction")
    saved_query = session.query(SavedQuery).filter(SavedQuery.id == q.id).all()[0]
    assert saved_query.query != saved_query.no_lang_query


def test_complex_query(session):
    q = create_query(session, query="dino:* & (extinction <-> event)")
    saved_query = session.query(SavedQuery).filter(SavedQuery.id == q.id).all()[0]
    assert saved_query.query == "'dino':* & 'extinct' <-> 'event'"
    assert saved_query.query == q.query


def test_null_query(session):
    q = create_query(session)
    saved_query = session.query(SavedQuery).filter(SavedQuery.id == q.id).all()[0]
    assert saved_query.query is None


def test_websearch_query(session):
    q = create_query(session, query=Websearch('dino* "extinction event"'))
    saved_query = session.query(SavedQuery).filter(SavedQuery.id == q.id).all()[0]
    assert saved_query.query == "'dino':* & 'extinct' <-> 'event'"


def test_find_query(session):
    q = create_query(session, query="stegasaurus & plesiosaurus")
    found = (
        session.query(SavedQuery)
        .filter(SavedQuery.query == to_tsquery("stegasaurus & plesiosaurus"))
        .all()[0]
    )
    assert found == q
