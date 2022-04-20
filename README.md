# SqlAlchemy Postgres Full Text Search

This provides the `websearch_to_tsquery` functionality that postgres
provides out of the box, but it adds support for using `*` as a wildcard.


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

