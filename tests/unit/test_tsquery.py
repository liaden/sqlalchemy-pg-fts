import pytest

from sqlalchemy_pg_fts.websearch import websearch
from sqlalchemy_pg_fts.tsquery import to_tsquery
from tests.util import to_sql

from sqlalchemy import select


def test_english_to_tsquery():
    query = select([to_tsquery("english", "dinosaur & stomp")])

    assert to_sql(query) == (
        "SELECT to_tsquery('english', 'dinosaur & stomp') AS to_tsquery_1"
    )


def test_nolang_to_tsquery():
    query = select([to_tsquery("dinosaur & stomp")])

    assert to_sql(query) == "SELECT to_tsquery('dinosaur & stomp') AS to_tsquery_1"


def test_websearch_to_tsquery():
    query = select([to_tsquery("english", websearch("dinosaur stomp"))])

    assert to_sql(query) == (
        "SELECT to_tsquery('english', 'dinosaur & stomp') AS to_tsquery_1"
    )
