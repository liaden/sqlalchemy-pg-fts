import pytest

from sqlalchemy import select
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Query
from sqlalcehmy_pg_fts import websearch, websearch_to_tsquery
from tests.integration.conftest import connection, session
from tests.integration.model import Item


def create_item(session, item_body):
    missed_item = Item(body="a lot of us like dinos")
    item = Item(body=item_body)
    session.add_all([missed_item, item])
    session.commit()
    return item


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


def to_sql(query):
    print(query.__class__)
    statement = query.statement if isinstance(query, Query) else query

    return str(
        statement.compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": "true"}
        )
    )
