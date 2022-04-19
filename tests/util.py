from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Query


def to_sql(query):
    statement = query.statement if isinstance(query, Query) else query

    return str(
        statement.compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": "true"}
        )
    )
