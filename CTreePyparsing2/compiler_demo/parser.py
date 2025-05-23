import inspect

import pyparsing as pp
from pyparsing import pyparsing_common as ppc

from .ast import *


def _make_parser():
    IF = pp.Keyword('if')
    FOR = pp.Keyword('for')
    WHILE = pp.Keyword('while')
    RETURN = pp.Keyword('return')
    SWITCH = pp.Keyword('switch')
    CASE = pp.Keyword('case')
    DEFAULT = pp.Keyword('default')
    BREAK = pp.Keyword('break')
    CONTINUE = pp.Keyword('continue')

    keywords = IF | FOR | WHILE | RETURN | SWITCH | CASE | DEFAULT | BREAK | CONTINUE

    num = pp.Regex('[+-]?(\\d+\\.\\d*|\\.\\d+)([eE][+-]?\\d+)?[fFdD]?|[+-]?\\d+([eE][+-]?\\d+)?[fFdD]?')
    str_ = pp.QuotedString('"', escChar='\\', unquoteResults=False, convertWhitespaceEscapes=False)
    char = pp.Regex(r"'(\\.|[^\\'])'")
    literal = num | char | str_ | pp.Regex('true|false')

    ident = (ppc.identifier.copy()).setName('ident')
    ident = pp.Word(pp.alphas + "_$", pp.alphanums + "_$").setName('ident')

    type_ = ident.copy().setName('type')

    COLON = pp.Literal(':').suppress()
    LPAR, RPAR = pp.Literal('(').suppress(), pp.Literal(')').suppress()
    LBRACK, RBRACK = pp.Literal("[").suppress(), pp.Literal("]").suppress()
    LBRACE, RBRACE = pp.Literal("{").suppress(), pp.Literal("}").suppress()
    SEMI, COMMA = pp.Literal(';').suppress(), pp.Literal(',').suppress()
    ASSIGN = pp.Literal('=')

    ADD_ASSIGN = pp.Literal('+=')
    SUB_ASSIGN = pp.Literal('-=')
    MUL_ASSIGN = pp.Literal('*=')
    DIV_ASSIGN = pp.Literal('/=')
    MOD_ASSIGN = pp.Literal('%=')

    ADD, SUB = pp.Literal('+'), pp.Literal('-')
    MUL, DIV, MOD = pp.Literal('*'), pp.Literal('/'), pp.Literal('%')
    AND = pp.Literal('&&')
    OR = pp.Literal('||')
    BIT_AND = pp.Literal('&')
    BIT_OR = pp.Literal('|')
    GE, LE, GT, LT = pp.Literal('>='), pp.Literal('<='), pp.Literal('>'), pp.Literal('<')
    NEQUALS, EQUALS = pp.Literal('!='), pp.Literal('==')

    add = pp.Forward()
    expr = pp.Forward()
    stmt = pp.Forward()
    stmt_list = pp.Forward()

    call = ident + LPAR + pp.Optional(expr + pp.ZeroOrMore(COMMA + expr)) + RPAR

    group = (
        literal |
        call |
        ident |
        LPAR + expr + RPAR
    )

    mult = pp.Group(group + pp.ZeroOrMore((MUL | DIV | MOD) + group)).setName('bin_op')
    add << pp.Group(mult + pp.ZeroOrMore((ADD | SUB) + mult)).setName('bin_op')
    compare1 = pp.Group(add + pp.Optional((GE | LE | GT | LT) + add)).setName('bin_op')
    compare2 = pp.Group(compare1 + pp.Optional((EQUALS | NEQUALS) + compare1)).setName('bin_op')
    logical_and = pp.Group(compare2 + pp.ZeroOrMore(AND + compare2)).setName('bin_op')
    logical_or = pp.Group(logical_and + pp.ZeroOrMore(OR + logical_and)).setName('bin_op')

    expr << (logical_or)

    assign = (
            ident + pp.Optional((ASSIGN | ADD_ASSIGN | SUB_ASSIGN | MUL_ASSIGN | DIV_ASSIGN | MOD_ASSIGN) + expr)
    ).setName('assign')
    simple_stmt = assign | call

    simple_assign = ((ident + pp.Optional(ASSIGN + expr))).setName('assign')

    var_inner = simple_assign | ident
    vars_ = type_ + var_inner + pp.ZeroOrMore(COMMA + var_inner)

    for_stmt_list0 = (pp.Optional(simple_stmt + pp.ZeroOrMore(COMMA + simple_stmt))).setName('stmt_list')
    for_stmt_list = vars_ | for_stmt_list0
    for_cond = expr | pp.Group(pp.empty).setName('stmt_list')
    for_body = stmt | pp.Group(SEMI).setName('stmt_list')


    case_ = CASE.suppress() + ((LPAR + expr + RPAR) | literal) + COLON + for_body
    default_ = DEFAULT.suppress() + COLON + for_body
    cases_list = pp.Optional(pp.ZeroOrMore(case_) + pp.Optional(default_))

    if_ = IF.suppress() + LPAR + expr + RPAR + stmt + pp.Optional(pp.Keyword("else").suppress() + stmt)
    for_ = FOR.suppress() + LPAR + for_stmt_list + SEMI + for_cond + SEMI + for_stmt_list + RPAR + for_body
    return_ = RETURN.suppress() + expr
    while_ = WHILE.suppress() + LPAR + expr + RPAR + stmt
    switch_ = SWITCH.suppress() + LPAR + ident + RPAR + LBRACE + cases_list + RBRACE
    composite = LBRACE + stmt_list + RBRACE

    param = type_ + ident
    params = pp.Optional(param + pp.ZeroOrMore(COMMA + param))
    func = type_ + ident + LPAR + params + RPAR + LBRACE + stmt_list + RBRACE

    break_ = BREAK.suppress()
    continue_ = CONTINUE.suppress()

    stmt << (
        break_ |
        continue_ |
        if_ |
        for_ |
        while_ |
        switch_ |
        return_ |
        simple_stmt + SEMI |
        vars_ + SEMI |
        composite |
        func
    )

    stmt_list << (pp.ZeroOrMore(stmt + pp.ZeroOrMore(SEMI)))

    program = stmt_list.ignore(pp.cStyleComment).ignore(pp.dblSlashComment) + pp.StringEnd()

    start = program

    def set_parse_action_magic(rule_name: str, parser: pp.ParserElement) -> None:
        if rule_name == rule_name.upper():
            return
        if getattr(parser, 'name', None) and parser.name.isidentifier():
            rule_name = parser.name
        if rule_name in ('bin_op', ):
            def bin_op_parse_action(s, loc, tocs):
                node = tocs[0]
                if not isinstance(node, AstNode):
                    node = bin_op_parse_action(s, loc, node)
                for i in range(1, len(tocs) - 1, 2):
                    secondNode = tocs[i + 1]
                    if not isinstance(secondNode, AstNode):
                        secondNode = bin_op_parse_action(s, loc, secondNode)
                    node = BinOpNode(BinOp(tocs[i]), node, secondNode, loc=loc)
                return node
            parser.setParseAction(bin_op_parse_action)
        else:
            cls = ''.join(x.capitalize() for x in rule_name.split('_')) + 'Node'
            with suppress(NameError):
                cls = eval(cls)

                if not inspect.isabstract(cls):
                    def parse_action(s, loc, tocs):
                        if cls is FuncNode:
                            return FuncNode(tocs[0], tocs[1], tocs[2:-1], tocs[-1], loc=loc)
                        if cls is StmtListNode:
                            print()
                        if cls is AssignNode:
                            return AssignNode(AssignOp(tocs[1]), tocs[0], tocs[2], loc=loc)
                        else:
                            return cls(*tocs, loc=loc)
                    parser.setParseAction(parse_action)

    for var_name, value in locals().copy().items():
        if isinstance(value, pp.ParserElement):
            value.setDebug(True)
            set_parse_action_magic(var_name, value)

    return start


parser = _make_parser()


def parse(prog: str) -> StmtListNode:
    locs = []
    row, col = 0, 0
    for ch in prog:
        if ch == '\n':
            row += 1
            col = 0
        elif ch == '\r':
            pass
        else:
            col += 1
        locs.append((row, col))

    old_init_action = AstNode.init_action

    def init_action(node: AstNode) -> None:
        loc = getattr(node, 'loc', None)
        if isinstance(loc, int):
            node.row = locs[loc][0] + 1
            node.col = locs[loc][1] + 1

    AstNode.init_action = init_action
    try:
        prog: StmtListNode = parser.parseString(str(prog))[0]
        prog.program = True
        return prog
    finally:
        AstNode.init_action = old_init_action
