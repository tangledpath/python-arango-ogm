from copy import copy
import re
import textwrap

from enum import StrEnum, auto
from typing import Iterable

CR = '\n'
LF = '\n'
EMPTY = ''
INDENT = '  '
QUOTE = '"'
SPACE = ' '
SCORE = '_'

RE_COMBINE_WHITESPACE = re.compile(r"\s+")
RE_ENCLOSE_WS_BEFORE = re.compile(r"(\s+)([\{\[\(])")
RE_ENCLOSE_NO_WS_BEFORE = re.compile(r"(\S)([\}\]\)])")
RE_ENCLOSE_NO_WS_AFTER = re.compile(r"([\{\[\(\}\]\)])(\S)")
RE_ENCLOSEEMPTY = re.compile(r"([\{\[\(])(\s+)([\}\]\)])")
RE_TOSNAKECASE = re.compile(r"(?:(?<=[a-z])(?=[A-Z]))|[^a-zA-Z]")
RE_CAPITALIZED = re.compile(r"(\s+)([A-Z])")
RE_CAPITAL = re.compile(r"([A-Z]+)")
RE_NOT_ALPHNUM_SCORE = re.compile(r"[^\w+]")

RE_NOT_ALPHNUM = re.compile(r"[^\w]+")
RE_NOT_ALPHNUM_SPACE = re.compile(r"[^a-zA-Z0-9\s]+")
RE_NOT_ALPHNUM_STRICT = re.compile(r"[^a-zA-Z0-9]+")


class QuoteEnum(StrEnum):
    """ Quote Enum """
    SINGLE = auto()
    DOUBLE = auto()
    TRIPLE = auto()


QUOTE_TYPES = {
    QuoteEnum.SINGLE: "'",
    QuoteEnum.DOUBLE: '"',
    QuoteEnum.TRIPLE: '"""',
}


class SurroundEnum(StrEnum):
    QUOTE_SINGLE = auto()
    QUOTE_DOUBLE = auto()
    QUOTE_TRIPLE = auto()
    BRACE = auto()
    BRACKET = auto()
    PARENS = auto()


SURROUND_TYPES = {
    SurroundEnum.QUOTE_SINGLE: ("'", "'"),
    SurroundEnum.QUOTE_DOUBLE: ('"', '"'),
    SurroundEnum.QUOTE_TRIPLE: ('"""', '"""'),
    SurroundEnum.BRACE: ('{', '}'),
    SurroundEnum.BRACKET: ('[', ']'),
    SurroundEnum.PARENS: ('(', ')'),
}


def indent(text, amount=4, pre=''):
    txt = f"{pre} {text}" if pre else str(text)
    return textwrap.indent(txt, INDENT * amount)


def prefix(text, pre):
    return f"{pre}{text}" if text else copy(EMPTY)


def pluralize(val):
    s = str(val).strip()

    if s:
        last_char = s[-1]
        if last_char == 'y':
            p = s[:-1] + 'ies'
        elif last_char == 's':
            p = s + 'es'
        else:
            p = s + 's'
    else:
        p = copy(EMPTY)

    return p


def collapse(ary, join_char=LF):
    return join_char.join(ary)


def surround(text: str, surround_with: SurroundEnum = SurroundEnum.PARENS):
    if not text:
        return copy(EMPTY)

    stype = SURROUND_TYPES[surround_with]
    return "{o}{text}{c}".format(o=stype[0], c=stype[1], text=text)


def surround_all(iterable: Iterable, surround_with: SurroundEnum = SurroundEnum.PARENS) -> Iterable:
    return [surround(t, surround_with=surround_with) for t in iterable]


def squish_text(text, format_braces=True):
    squished = RE_COMBINE_WHITESPACE.sub(SPACE, text).strip()
    if format_braces:
        squished = RE_ENCLOSE_WS_BEFORE.sub(r'\g<2>', squished)
        squished = RE_ENCLOSE_NO_WS_BEFORE.sub(r'\g<1> \g<2>', squished)
        squished = RE_ENCLOSE_NO_WS_AFTER.sub(r'\g<1> \g<2>', squished)
        squished = RE_ENCLOSEEMPTY.sub(r'\g<1>\g<3>', squished)
        squished = RE_COMBINE_WHITESPACE.sub(SPACE, squished).strip()

    return squished


def score_text(text):
    return RE_COMBINE_WHITESPACE.sub('_', text.strip()).lower()


def combine_space(text):
    return RE_COMBINE_WHITESPACE.sub(SPACE, text.strip())


def snake_text(text, lower: bool = True):
    def score_cap(txt: str, position:int):
        return txt if not (txt.isupper() and position) else f"_{txt}"
    # Separate capitalized words:
    terms = RE_CAPITAL.split(text)
    terms.remove('')

    snaked = [score_cap(t, i) for i, t in enumerate(terms) if t]
    txt = "".join(snaked)
    return txt.lower() if lower else txt


def capitalize_text(text):
    txt = str(text).strip()
    return txt if txt.isupper() else txt.capitalize()


def title_text(text):
    txt = RE_CAPITAL.sub(r" \1", text)
    terms = RE_NOT_ALPHNUM_STRICT.split(txt)
    clean_terms = filter(None, terms)

    words = [capitalize_text(t) for t in clean_terms]
    return SPACE.join(words)
