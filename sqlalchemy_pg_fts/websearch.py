import re
import platform
from typing import Iterator, List

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import FunctionElement


CHARS_FILTER = re.compile(r"[}{`=,\\?/><\][#@%$^.;|+&!:)(]")
PHRASE_CLEANUP = re.compile(r'"\s*(\w*)\s*"')
AND_OP = "&"
FOL_OP = "<->"
NOT_OP = "!"
OR_OP = "|"


class websearch(FunctionElement):
    """
    Compiles websearch query to tsquery text.

    Example queries:
       * 'super* dinosaur': will match superb/superior/super
           and dinosaur within the document
       * '"super dinosaur" carnivore': will match when the prhase
           'super dinosaur' is present and carnivore is present
       * '-"super dinosaur" carnivore': the phrase must not be
           present while carnivore is
       * 'carnivore or herbivore': either of these words must be present

    Usage:
       * `filter(SomeModel.column.match(websearch("some words -filtered")))`

           Note: This uses SqlAlchemy's match operator which uses '@@' and runs
           to_tsquery underneath; however, it does not convert the column to a
           tsvector which can be problematic.
    """

    name = "websearch"


@compiles(websearch, "postgresql")
def compile_websearch_postgres(element, compiler, **kw):
    websearch_query = list(element.clauses)[0].value
    return "'%s'" % websearch_to_tsquery(websearch_query)


class Websearch:
    def __init__(self, query_text):
        self.query_text = query_text

    def to_tsquery_text(self) -> str:
        return websearch_to_tsquery(self.query_text)


def websearch_to_tsquery(query: str) -> str:
    """
    Similar to postgres' websearch_to_tsquery but also supports prefix* matches.
    """
    result = " ".join(ts_query_tokens(query))
    return result


def ts_query_tokens(query: str) -> List[str]:
    """
    Returns list of tsquery tokens that match the websearch query.
    """
    query = _filter(query).lower()

    tokens = []
    phrase_state = PhraseState()

    for token in _tokenize(query):
        if token == '-"':
            tokens.append("!(")

            phrase_state.invert()
        elif token == '"':
            if len(tokens) > 0 and tokens[-1] == FOL_OP:
                tokens.pop()

            tokens.append(phrase_state.current_paren)
            phrase_state.invert()
        elif token == "-":
            tokens.append(NOT_OP)
        elif token == "or":
            tokens.append(OR_OP)
        elif token == "*":
            tokens[-2] = f"{tokens[-2]}:*"
        else:
            tokens.append(token)
            tokens.append(phrase_state.current_op)

    if len(tokens) > 0 and tokens[-1] == "&":
        tokens.pop()

    return tokens


def _filter(query: str) -> str:
    """
    Filters out degenerate cases.

    `:`, '&', `!`, `|`, `(`, `)`: since we generate them in the tsquery.
    `?`, `!`, `,`, `.`, `;`, `'`: punctuation
    `/`, `\`, `#`, `$`, `%`, `+`, `=`: misc bad characters
    `[`, `]`, `{`, `}`, `<`, `>`: brackets
    `""`, `" "`, etc: degenerate case
    `"word"`: redundant quoting
    `" word "`: redundant quoting with spaces
    """
    return re.sub(PHRASE_CLEANUP, r"\1", re.sub(CHARS_FILTER, r" ", query))


def _tokenize(query: str) -> Iterator[str]:
    """
    Yields one of the following:

       * `"\"": begin/end phrase
       * `"-": signifies not
       * `"or"`: signifies or
       * `word`: a word
    """
    # python 3.7 does not split on empty regex match so the \b boundary doesn't
    # break out all the pieces we need. the solution is to use two splits
    for part in re.split(r"\s", query):
        part = part.strip()
        for token in re.split(r"(\W+)", part):
            if token != "":
                yield token


class PhraseState:
    def __init__(self):
        self.current_op = AND_OP
        self.other_op = FOL_OP
        self.current_paren = "("
        self.next_paren = ")"

    def invert(self) -> None:
        self.current_op, self.other_op = self.other_op, self.current_op
        self.current_paren, self.next_paren = self.next_paren, self.current_paren

    def current_op(self) -> str:
        return self.current_op

    def current_paren(self) -> str:
        return self.current_paren
