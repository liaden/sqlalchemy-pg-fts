import pytest

from sqlalchemy_pg_fts.websearch import websearch
from sqlalchemy_pg_fts.tsquery import to_tsquery
from sqlalchemy_pg_fts.errors import ArgumentError
from tests.util import to_sql

from sqlalchemy import select


def test_english_to_tsquery():
    query = select([to_tsquery("english", "dinosaur & stomp")])

    assert to_sql(query).startswith("SELECT to_tsquery('english', 'dinosaur & stomp')")


def test_nolang_to_tsquery():
    query = select([to_tsquery("dinosaur & stomp")])

    assert to_sql(query).startswith("SELECT to_tsquery('dinosaur & stomp')")


def test_websearch_to_tsquery():
    query = select([to_tsquery("english", websearch("dinosaur stomp"))])

    assert to_sql(query).startswith("SELECT to_tsquery('english', 'dinosaur & stomp')")


def test_to_tsquery_no_args():
    query = select([to_tsquery()])

    with pytest.raises(ArgumentError):
        to_sql(query)


def test_to_tsquery_too_many_args():
    query = select([to_tsquery("a", "b", "c")])

    with pytest.raises(ArgumentError):
        to_sql(query)
