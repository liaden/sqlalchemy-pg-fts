import pytest

from sqlalchemy import select
from sqlalchemy_pg_fts import websearch, websearch_to_tsquery
from tests.integration.conftest import connection, session
from tests.integration.model import create_item, Item
from tests.util import to_sql


DINO_WEBSEARCH_QUERIES = [
    ("Dinosaurs lived a long, long time ago.", "dinosaur lived"),
    ("Dinosaurs lived a long, long time ago.", '"dinosaur lived"'),
    ("Dinosaurs lived a long, long time ago.", '"dino* lived"'),
    ("Dinosaurs lived a long, long time ago.", "dino* lived"),
    ("Dinosaurs lived a long, long time ago.", 'dino* "long time"'),
    ("Dinosaurs lived a long, long time ago.", 'dino* "long long"'),
]


@pytest.mark.parametrize("item_body,query", DINO_WEBSEARCH_QUERIES)
def test_websearch_to_tsquery_matches(item_body, query, session):
    item = create_item(session, item_body)
    items = (
        session.query(Item).filter(Item.body.match(websearch_to_tsquery(query))).all()
    )
    assert items == [item]


@pytest.mark.parametrize("item_body,query", DINO_WEBSEARCH_QUERIES)
def test_websearch_matches(item_body, query, session):
    item = create_item(session, item_body)
    items = session.query(Item).filter(Item.body.match(websearch(query))).all()
    assert items == [item]


def test_compile_websearch(session):
    websearch_query = "dinosaur stomp"
    query = session.query(Item).filter(Item.body.match(websearch(websearch_query)))
    assert to_sql(query) == (
        "SELECT item.id, item.body \n"
        "FROM item \n"
        "WHERE item.body @@ to_tsquery('dinosaur & stomp')"
    )
