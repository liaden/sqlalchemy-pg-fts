import pytest

from sqlalcehmy_pg_fts.websearch import _filter, websearch_to_tsquery


@pytest.mark.parametrize(
    "query,filtered",
    [
        ('""', ""),
        ("!", " "),
        ("|", " "),
        ("&", " "),
        ("(", " "),
        (")", " "),
        ('"word"', "word"),
        ('" "', ""),
        ('" word "', "word"),
        # unchanged
        ("", ""),
        (" ", " "),
        ("word", "word"),
        ('"word word"', '"word word"'),
    ],
)
def test_filter(query, filtered):
    assert _filter(query) == filtered


@pytest.mark.parametrize(
    "query,tsquery",
    [
        ("dinosaurs meteor paleontology", "dinosaurs & meteor & paleontology"),
        ("dino*", "dino:*"),
        ("", ""),
        ('dinosaur -"bird chicken"', "dinosaur & !( bird <-> chicken )"),
        ("dinosaur -bird -chicken", "dinosaur & ! bird & ! chicken"),
        ('dino* "long ago"', "dino:* & ( long <-> ago )"),
    ],
)
def test_websearch_to_tsquery(query, tsquery):
    assert websearch_to_tsquery(query) == tsquery
