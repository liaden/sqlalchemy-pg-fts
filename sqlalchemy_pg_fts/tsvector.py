from typing import Optional, Union

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import FunctionElement
from sqlalchemy.types import UserDefinedType
from sqlalchemy import func, null


class TSVector(UserDefinedType):
    """
    Represents a postgresql tsvector.
    """

    name = "tsvector"

    def __init__(self, language: Optional[str] = "english"):
        """
        params:
            * language: defaults to "english". Passing none defaults to postgres' default.
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
        return "tsvector"

    def bind_expression(self, value):
        """
            Uses to_tsvector function on postgres to build the query with the language.
        def coerce_compared_value
        """
        if self.language:
            return func.to_tsvector(self.language or "simple", value)
        else:
            return func.to_tsvector(value)

    def bind_processor(self, dialect):
        def process(value):
            return value

        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            return value

        return process


class to_tsvector(FunctionElement):
    name = "to_tsvector"


@compiles(to_tsvector, "postgresql")
def compiles_to_tsvector(element, compiler, **kw) -> str:
    args = list(element.clauses)

    if len(args) > 1:
        language, query = args

        return "to_tsvector(%s, %s)" % (
            compiler.process(language, **kw),
            compiler.process(query, **kw),
        )
    else:
        query = args[0]
        return "to_tsvector(%s)" % compiler.process(query, **kw)
