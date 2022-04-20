from typing import Optional, Union

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import bindparam, FunctionElement
from sqlalchemy.types import String, UserDefinedType
from sqlalchemy import func, null, type_coerce

from sqlalchemy_pg_fts.websearch import Websearch


class TSQuery(UserDefinedType):
    """
    Represents a postgresql tsquery.

    Defaults to "english" as the language. Check `\dF` via psql for all available
    languages.
    """

    name = "tsquery"

    def __init__(self, language: Optional[str] = "english"):
        """
        params:
            * language: defaults to "english". Passing none sets language to simple.
        """
        self.language = language or "simple"

    class comparator_factory(UserDefinedType.Comparator):
        def __init__(self, expr):
            self.expr = expr
            self.type = expr.type

        def coerce_compared_value(self, op, value):
            return self

    def coerce_compared_value(self, op, value):
        return self

    def get_col_spec(self, **kw):
        return "tsquery"

    def bind_expression(self, value):
        """
            Uses to_tsquery function on postgres to build the query with the language.
        def coerce_compared_value
        """
        return func.to_tsquery(self.language or "simple", value)

    def bind_processor(self, dialect):
        def process(value):
            if isinstance(value, Websearch):
                return value.to_tsquery_text()

            return value

        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            return value

        return process


class to_tsquery(FunctionElement):
    name = "to_tsquery"


@compiles(to_tsquery, "postgresql")
def compiles_to_tsquery(element, compiler, **kw) -> str:
    args = list(element.clauses)

    if len(args) > 1:
        language, query = args

        return "to_tsquery(%s, %s)" % (
            compiler.process(language, **kw),
            compiler.process(query, **kw),
        )
    else:
        query = args[0]
        return "to_tsquery(%s)" % compiler.process(query, **kw)
