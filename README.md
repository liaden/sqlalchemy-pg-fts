# SqlAlchemy Postgres Full Text Search

This provides the `websearch_to_tsquery` functionality that postgres
provides out of the box, but it adds support for using `*` as a wildcard.

## Usage

### Saving a TSQuery

```python
class Query(Base):
    __tablename__ = 'query'
    query = Column(TSQuery) # english query by default
    spanish_query = Column(TSQuery(language = 'spanish'))
    simple_query = Column(TSQuery(language = None)) # or 'simple'
```

### Saving a TSVector

Note: there isn't much value in doing this as opposed to creating the
indexes on a `TEXT` column unless the original text does not matter.

```python
class Vector(Base):
    __tablename__ = 'vector'
    vector = Column(TSVector) # english by default
    spanish_vector = Column(TSVector(language = 'spanish'))
    simple_vector = Column(TSVector(language = None)) # or 'simple'
```

### Filtering with `to_tsquery`

```python
from sql_alchemy_fts import to_tsquery

vecs = session.
    query(Vector).
    filter(
        Vector.vector.op("@@")(to_tsquery('english', 'dinosaur & extinction')),
    ).all()

```

Note: `vector` is a `TSVector`. This will also work as text, but it will
not give a chance to specify language (so will be `'simple'` by default,
unless postgres has been configured otherwise).

### Filtering with `websearch`

```python
from sql_alchemy_fts import to_tsquery, websearch
query = websearch('dinosaur "long time" -"jurassic park"')
vecs = session.
    query(Vector).
    filter(
        Vector.vector.op("@@")(to_tsquery('english', query),
    ).all()
```

### Creating a TSVector index

```python
from sql_alchemy_fts import to_tsvector

class Document(Base):
    __tablename__ = 'document'
    body = Column(Text)
    # track language so we can create partial indexes for language matches
    language = Column(Text)

    __tableargs__ = [Index("ix_document_body_english_gin_tsvector", to_tsvector(
        # Create english language index
        Index(
            "ix_document_body_english_gin_tsvec",
            text("to_tsvector('english', body)"),
            postgresql_using="gin",
            postgresql_where=text("language = 'english'"),
        ),
        # Create spanish language index
        Index(
            "ix_document_body_spanish_gin_tsvec",
            text("to_tsvector('spanish', body)"),
            postgresql_using="gin",
            postgresql_where=text("language = 'spanish'"),
        ),
    ]

# querying spanish docs:
session.
    query(Document).
    filter(
        # convert the text type to_tsvector to match the index
        to_tsvector('spanish', Document.body).
            op("@@")(to_tsquery("spanish", "dinosaurios & vivieron"))
    ).
    # required for postgres to match the index to be used
    filter(Document.language == "spanish").
    all()

```

Note: an index is likely going to be useful even if the `TEXT` was dropped
and only a `TSVector` was saved on the table.


### Websearch Syntax

This is inspired by the `websearch_to_tsquery` function that is defined in
postgres, but it does not allow a `"*"` to wildcard after a prefix,
despite that `tsquery` supports it. Therefore, to make this work, the
entire websearch to tsquery has to be done within python.

1. `websearch("dinosaur stomp")`: Dinosaur and stomp both must show up.
1. `websearch("dinosaur or stomp")`: Either must show up.
1. `websearch("dinosaur "long time ago")`: Dinosaur must show up and the
   phrase "long time ago" must show up.
1. `websearch("the of a an by dinosaur")`: Dinosaur must show up and the
   other words are of no value so they are filtered (by postgres itself).
1. `websearch("super*")`: Word with the prefix of super* is required such
   as superman, superb, or superior.
1. `websearch("-dinosaur")` Anything without the word dinosaur.
1. `websearch("dinosuar -"jurassic park")`: The phrase jurassic park must
   not be present, but dinosaur must show up.

The `websearch` class only renders out a tsquery text fragment. It is
intended to be composed with `to_tsquery`.

## Development

### Setup

1. Install [asdf](https://asdf-vm.com/guide/getting-started.html#_1-install-dependencies).
1. Add python plugin: `asdf plugin-add python`.
    1. Add a `$HOME/.default-python-packages` containing `poetry`.
1. Optionally, add postgres plugin: `asdf plugin-add postgres.
1. `asdf install` to install python and postgres.

### Tests

Run `poetry run tox` or `poetry run tox --asdf-install` if some versions of python are missing.

Note: make sure postgres is running. If installed through asdf, it needs to be started with `pg_ctl`.

