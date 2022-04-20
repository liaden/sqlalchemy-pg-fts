import pytest

from sqlalchemy_pg_fts.websearch import websearch
from sqlalchemy_pg_fts.tsvector import to_tsvector
from tests.util import to_sql

from sqlalchemy import select


def test_english_to_tsvector():
    vector = select([to_tsvector("english", "dinosaur & stomp")])

    assert to_sql(vector).startswith(
        "SELECT to_tsvector('english', 'dinosaur & stomp')"
    )


def test_nolang_to_tsvector():
    vector = select([to_tsvector("dinosaur & stomp")])

    assert to_sql(vector).startswith("SELECT to_tsvector('dinosaur & stomp')")


def test_websearch_to_tsvector():
    vector = select([to_tsvector("english", websearch("dinosaur stomp"))])

    assert to_sql(vector).startswith(
        "SELECT to_tsvector('english', 'dinosaur & stomp')"
    )
