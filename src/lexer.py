from io import BytesIO
import re


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
        self.nline = 0
        self.nchar = 0

    def __exit__(self):
        self.src.close()

    def backtrack(self, n=1):
        self.src.seek(-n, 1)
        return self

    def scan(self):

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
                    self.backtrack(1)
                    break

        # char is newline
        # TODO: fix newlines getting tangled with numbers
        if re.match(self.syntax.r_newline, char):
            self.nchar = 0
            self.nline = self.nline + 1
        else:
            self.nchar = self.nchar + 1

        word = "".join(self.token) if len(self.token) > 0 else None

        if word is None:
            return None

        return self.Token(word, line=self.nline, char=self.nchar)

    def next(self):

        tree = self.syntax.symbols
        word = []

        while True:
            # get next symbol
            token = self.scan()
            # info,symbol = self.scan()

            # EOF
            if token is None:
                return False

            # search in syntax tree
            for regexp in tree:
                match = None
                if regexp is None:
                    self.backtrack(1)
                    continue

                try:
                    if re.match(regexp, token.word):
                        word.append(token.word)
                        # move forward in tree
                        tree = tree[regexp]
                        match = token.word
                        break

                except TypeError as err:
                    print(token)
                    print(err)
                    exit(1)

            if match is not None:
                # there is a possible continuation to this symbol
                if isinstance(tree, dict):
                    continue
            else:
                tree = tree.get(None)

            if len(word) == 0:
                # move to tree root
                tree = self.syntax.symbols
                continue

            token.word = "".join(word)

            # return a typed lexeme
            return tree(token.word, (token.line, token.char))
