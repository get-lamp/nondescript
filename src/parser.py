import src.lang.data
from src.lang.base import (
    Keyword,
    Lexeme,
    Space,
    Tab,
    NewLine,
    Comma,
    DoubleQuote,
    SingleQuote,
    Bracket,
    Parentheses,
    Delimiter,
    Identifier,
)
from src.lang.control import Block
from src.lang.data import Constant
from src.lang.operator import Operator, UnaryOperator, UnaryPostOperator
from src.lang import data
from src.lexer import Lexer, Token
from src.exc import UnexpectedEOF, UnexpectedSymbol


BLOCK_MAIN = "<main>"


class Parser:
    """
    The parser
    """

    def __init__(self, lang, source, is_file=False):
        self.count = 0
        self.lang = lang
        self.lexer = Lexer(lang, source, is_file)
        self.tree = []
        self.pending = []
        self.blocks: [Block] = [BLOCK_MAIN]

    def set_source(self, source, is_file=False):
        self.lexer = Lexer(self.lang, source, is_file)

    def _EOF(self):
        if len(self.blocks) > 1:
            pass
            # print self.blocks
            # raise Exception('Missing end statement')

        return False

    @staticmethod
    def _unnest(s, stop):
        n = []
        while True and len(s) > 0:
            i = s.pop(-1)
            if isinstance(i, stop):
                break
            else:
                n.insert(0, i)

        return s, n

    def seek_ahead(self, needle):
        now = self.lexer.src.tell()

        try:
            while lex := self.next():
                if lex.word == needle:
                    return lex
        finally:
            self.lexer.jump_to(now)

    def push_block(self, block):
        self.blocks.append(block)

    def pull_block(self) -> Block:
        if len(self.blocks) <= 1:
            raise Exception("Cannot pull main block")
        return self.blocks.pop()

    def get_block(self, type_=None):
        if type_ is None:
            return self.blocks[-1]
        else:
            for _, block in reversed(self.blocks):
                if isinstance(block, type_):
                    return block

    def _verbatim(self, stop, **kwargs):
        verbatim = []

        while True:
            lexeme = self.lexer.next()

            # EOF
            if not lexeme or lexeme is None:
                break

            # is lexeme the stop token?
            if isinstance(lexeme, stop):
                found = True
                # has lexeme the properties we are looking for?
                for p in kwargs:
                    # it doesn't
                    if p not in lexeme.__dict__:
                        found = False
                    # has property but different value?
                    elif kwargs[p] != lexeme.__dict__[p]:
                        found = False
                        # reject lexeme as the stop mark
                        break
                if found:
                    return "".join(verbatim)
            else:
                verbatim.append(lexeme.word)

        return False

    def next(self, ignore=None) -> Lexeme | bool:

        ignore = (Space, Tab) if ignore is None else ignore

        while True:
            lexeme = self.pending.pop() if len(self.pending) > 0 else self.lexer.next()

            # EOF
            if lexeme is False:
                return False

            # preprocessor directives
            if isinstance(lexeme, self.lang.Preprocessor):
                if isinstance(lexeme, self.lang.CommentLine):
                    # skips until newline
                    self._verbatim(NewLine)
                    continue

                if isinstance(lexeme, self.lang.CommentBlock):
                    # skips until closed comment block
                    self._verbatim(self.lang.CommentBlock, open=False)
                    continue

            if isinstance(lexeme, ignore):
                continue

            break

        return lexeme

    def list(self, s):
        ll = []
        e = []
        while True and len(s) > 0:
            i = s.pop(0)
            if isinstance(i, Comma):
                ll.append(e)
                e = []
                continue
            elif isinstance(i, Bracket):
                if i.open:
                    e = self.list(s)
                else:
                    if len(e) > 0:
                        ll.append(e)
                    return ll
            else:
                e.append(i)

        ll.append(e)

        return ll

    def parse_block(self, until=None, leave=False):

        block = []

        while True:
            # parse.Stop if found delimiter
            i = self.parse(until=until)

            # EOF
            if i is False:
                # EOF before expected delimiter
                if until is not None:
                    raise UnexpectedEOF(f"Unexpected EOF at block {block}")
                # return last statement
                elif len(block) > 0:
                    return block
                else:
                    return False
            # stop at delimiter
            if isinstance(i, until):
                # leave delimiter for further parsing
                if leave is True:
                    self.pending.append(i)
                return block
            # add instruction to block
            else:
                block.append(i)

    def parse_expression(self, until=None):
        # Collects tokens belonging to an expression.
        # It expects an expression and would fail on tokens unexpected on an expression

        expression = self.lang.Expression()

        while True:
            lexeme = self.next()

            # EOF
            if lexeme is False:
                # return last parse_expression
                if len(expression) > 0:
                    return expression
                else:
                    return False

            # commit parse_expression on newline
            if isinstance(lexeme, NewLine):
                return expression

            if until is not None and isinstance(lexeme, until):
                return expression

            # literals
            if isinstance(lexeme, (DoubleQuote, SingleQuote)):
                if isinstance(lexeme, DoubleQuote):
                    word = self._verbatim(DoubleQuote)
                else:
                    word = self._verbatim(SingleQuote)

                ll = data.String(Token(word, lexeme.line, lexeme.char, lexeme.byte))
                expression.push(ll)
                continue

            if self.lang.Grammar.is_legal(expression + [lexeme], self.lang.expression):
                expression.push(lexeme)
            else:
                raise UnexpectedSymbol(
                    f'Unexpected "{lexeme.word}" at ({lexeme.line}:{lexeme.char}). '
                    f"Expecting: {', '.join(expression.hint())}"
                )

        return expression

    def clause(self, expecting):

        clause = self.lang.Clause()

        while True:
            lexeme = self.next()

            if len(clause) == 0 and not isinstance(lexeme, expecting):
                self.pending.append(lexeme)
                return clause

            # EOF
            if lexeme is False:
                # return last parse_expression
                if len(clause) > 0:
                    return clause
                else:
                    return False

            if not clause.push(lexeme):
                self.pending.append(lexeme)
                break

        return clause

    def parse(self, until=None):

        lexeme = self.next()

        if lexeme is False:
            return self._EOF()

        if until is not None and isinstance(lexeme, until):
            return lexeme

        if isinstance(lexeme, Keyword):
            if isinstance(lexeme, Block):
                self.push_block((self.count, lexeme))

            elif isinstance(lexeme, Delimiter):
                p0, b = self.pull_block()
                lexeme.owner, b.length = (b, self.count - p0 - 1)

            # add to instruction counter
            self.count += 1
            return lexeme.parse(self)

        elif isinstance(lexeme, (Delimiter, Constant, Identifier, UnaryOperator)):
            self.pending.append(lexeme)

            # add to instruction counter
            self.count += 1
            return self.parse_expression()
        elif isinstance(lexeme, self.lang.Parameter):
            raise Exception("Misplaced parameter")
        else:
            # newline, tab & beyond
            return self.parse(until=until)

    def build_ast(self, s):

        # n as the node we are building
        n = []

        # get rid of superfluous nesting
        if isinstance(s, list) and len(s) == 1 and isinstance(s[0], list):
            s = s.pop()

        while s and len(s) > 0:
            i = s.pop(0)
            # parentheses grouping
            if isinstance(i, Parentheses):
                if i.open:
                    # n is the i(n)ner node while s is the remaining (i)nstruction
                    n, s = self._unnest(s, Parentheses)
                    if len(n) > 0:
                        n = self.build_ast(n)
                else:
                    raise Exception("Unexpected parentheses at %s" % i.line)

            # list without brackets. Like arguments list
            elif isinstance(i, Comma):
                return src.lang.data.List(self.list(n + [i] + s))

            # list with brackets
            elif isinstance(i, Bracket):
                if i.open:
                    n.append(src.lang.data.List(self.list(s)))
                # closing brackets are disposed by self.list, so they shouldn't come up here
                else:
                    raise Exception("Unexpected bracket at %s" % i.line)

            # parameter
            elif isinstance(i, self.lang.Parameter):
                return [i, self.build_ast(s)]

            # operator delimits terms
            elif isinstance(i, Operator):
                if isinstance(i, UnaryOperator):
                    # unary operator
                    return [i, self.build_ast(s)]

                elif isinstance(i, UnaryPostOperator):
                    # unary post operator
                    return [i, n]
                # binary operator
                else:
                    return [n, i, self.build_ast(s)]
            else:
                n.append(i)

        return n
