from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import FunctionElement
from sqlalchemy.types import UserDefinedType


class TSQuery(UserDefinedType):
    name = "tsquery"
