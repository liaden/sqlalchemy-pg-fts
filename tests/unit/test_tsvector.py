import pytest

from sqlalchemy_pg_fts.websearch import websearch
from sqlalchemy_pg_fts.tsvector import to_tsvector
from sqlalchemy_pg_fts.errors import ArgumentError
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


def test_to_tsvector_no_args():
    query = select([to_tsvector()])

    with pytest.raises(ArgumentError):
        to_sql(query)


def test_to_tsvector_too_many_args():
    query = select([to_tsvector("a", "b", "c")])

    with pytest.raises(ArgumentError):
        to_sql(query)
