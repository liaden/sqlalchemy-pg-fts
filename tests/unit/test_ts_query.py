import pytest

from sqlalcehmy_pg_fts.tsquery import _filter, websearch


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
def test_websearch(query, tsquery):
    assert websearch(query) == tsquery
