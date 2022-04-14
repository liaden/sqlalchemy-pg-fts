import pytest

from sqlalcehmy_pg_fts import websearch
from tests.integration.conftest import connection, session
from tests.integration.model import Item


@pytest.mark.parametrize(
    "item_body,query",
    [
        ("Dinosaurs lived a long, long time ago.", "dinosaur lived"),
        ("Dinosaurs lived a long, long time ago.", '"dinosaur lived"'),
        ("Dinosaurs lived a long, long time ago.", '"dino* lived"'),
        ("Dinosaurs lived a long, long time ago.", "dino* lived"),
        ("Dinosaurs lived a long, long time ago.", 'dino* "long time"'),
        ("Dinosaurs lived a long, long time ago.", 'dino* "long long"'),
    ],
)
def test_websearch_tsquery_matches(item_body, query, session):
    missed_item = Item(body="a lot of us like dinos")
    item = Item(body=item_body)
    session.add_all([missed_item, item])
    session.commit()
    items = session.query(Item).filter(Item.body.match(websearch(query))).all()
    assert items == [item]
