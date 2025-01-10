import pkgutil as _pu

import lark as _lark

from pytrnsys_process import deck


def _create_parser() -> _lark.Lark:
    data = _pu.get_data(deck.__name__, "ddck.lark")
    assert data, "Could not find ddck Lark grammar file."
    grammar = data.decode()
    parser = _lark.Lark(grammar, parser="earley", propagate_positions=True)
    return parser


def parse_dck(ddck_content: str) -> _lark.Tree:
    tree = _create_parser().parse(ddck_content)
    return tree
