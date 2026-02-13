import re
from io import BytesIO


class Lexer:
    """
    Spit out tokens
    """

    class Token:
        """
        The words
        """

        def __init__(self, word, line, char):
            self.word = word
            self.line = line
            self.char = char

        def __repr__(self):
            return "Token(line=(%s)%s, char=(%s)%s, word=(%s)'%s'" % (
                type(self.line),
                self.line,
                type(self.char),
                self.char,
                type(self.word),
                self.word,
            )

    def __init__(self, syntax, source, is_file=False):
        if is_file:
            with open(source, "rb") as f:
                self.src = BytesIO(f.read())
        else:
            if source is None:
                self.src = BytesIO(b"")
            else:
                self.src = BytesIO(source.encode("utf-8"))
        self.syntax = syntax
        self.token = []
        self.num_line = 0
        self.num_char = 0

    def __exit__(self):
        self.src.close()

    def _backtrack(self, n=1):
        self.src.seek(-n, 1)
        return self

    def _is_newline(self, char):
        return bool(re.match(self.syntax.r_newline, char))

    def _track_line_and_char(self, char, word):
        # char is newline
        if self._is_newline(char) and char == word:
            self.num_char = 0
            self.num_line += 1
        else:
            self.num_char += len(word)

    def _scan(self):

        if self.src.closed:
            # already at EOF
            return None

        self.token = []
        char = ""

        while True:
            # read character
            char_bytes = self.src.read(1)

            if not char_bytes:
                # EOF
                # self.src.close()
                break

            char = char_bytes.decode("utf-8")
            c = re.match(self.syntax.delimiters, char)

            # no delimiter found. Keep reading
            if c is None:
                self.token.append(char)
            else:
                # a delimiter found. A single char to return
                if len(self.token) == 0:
                    self.token = char
                    break
                # a multichar token to return.
                # backtrack 1 to leave pointer in position for next reading
                else:
                    self._backtrack(1)
                    break

        # return None on empty word
        word = "".join(self.token) if len(self.token) > 0 else None
        if word is None:
            return None

        # keep current values before checks for new char & line
        num_char = self.num_char
        num_line = self.num_line

        self._track_line_and_char(char, word)

        return self.Token(word, line=num_line, char=num_char)

    def next(self):

        match = None
        tree = self.syntax.symbols
        tokens = []

        while True:
            # get next symbol
            token = self._scan()

            # EOF
            if token is None:
                if len(tokens) == 0:
                    return False

                elif token in tree.keys():
                    return tree[token](
                        [t.word for t in tokens], (tokens[0].line, tokens[0].char)
                    )

                raise SyntaxError(
                    f"SyntaxError: "
                    f'"{"".join([t.word for t in tokens])}" is unexpected ({self.num_line}:{self.num_char})'
                )

            # search in syntax tree
            for regexp in tree:

                match = None

                if regexp is None:
                    breakpoint()
                    self._backtrack(1)
                    continue

                if re.match(regexp, token.word):
                    tokens.append(token)
                    # move forward in tree
                    tree = tree[regexp]
                    match = token.word
                    break

            if match is not None:
                # there is a possible continuation to this symbol
                if isinstance(tree, dict):
                    continue
            else:
                tree = tree.get(None)

            if len(tokens) == 0:
                # move to tree root
                tree = self.syntax.symbols
                continue

            token.word = "".join([t.word for t in tokens])

            # return a typed lexeme
            return tree(token.word, (token.line, token.char))
