import os
import re
from io import BytesIO


class Token:
    def __init__(self, word, line, char, byte):
        self.word = word
        self.line = line
        self.char = char
        self.byte = byte

    def __eq__(self, other):
        return all(
            [
                self.word == other.word,
                self.line == other.line,
                self.char == other.char,
                self.byte == other.byte,
            ]
        )


class Lexer:
    """
    Spit out tokens
    """

    def __init__(self, syntax, source, is_file=False):

        self.syntax = syntax
        self.chars = []
        self.num_line = 0
        self.num_char = 0
        self.src = None

        if is_file:
            with open(source, "rb") as f:
                self.src = BytesIO(f.read())
        else:
            if source is None:
                self.src = BytesIO(b"")
            else:
                self.src = BytesIO(source.encode("utf-8"))

    def __exit__(self):
        self.src.close()

    def jump_to(self, n):
        self.src.seek(n, os.SEEK_SET)
        return self

    def _backtrack(self, n=1):
        self.src.seek(-n, os.SEEK_CUR)
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

        self.chars = []
        char = ""
        start_byte = self.src.tell()

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
                self.chars.append(char)
            else:
                # a delimiter found. A single char to return
                if len(self.chars) == 0:
                    self.chars = char
                    break
                # a multichar token to return.
                # backtrack 1 to leave pointer in position for next reading
                else:
                    self._backtrack(1)
                    break

        # return None on empty word
        word = "".join(self.chars) if len(self.chars) > 0 else None
        if word is None:
            return None

        # keep current values before checks for new char & line
        num_char = self.num_char
        num_line = self.num_line

        self._track_line_and_char(char, word)

        return Token(word, line=num_line, char=num_char, byte=start_byte)

    def next(self):

        tree = self.syntax.symbols
        tokens = []
        queued = []

        while True:
            match = None

            if len(queued) > 0:
                token = queued.pop(0)
            else:
                token = self._scan()

            if token is None:
                if len(tokens) == 0:
                    return False
                else:
                    return tree[None](
                        Token(
                            "".join([t.word for t in tokens]),
                            tokens[0].line,
                            tokens[0].char,
                            tokens[0].byte,
                        )
                    )

            for regexp in [t for t in tree if t is not None]:
                if re.match(regexp, token.word):
                    tokens.append(token)
                    # move forward in tree
                    tree = tree[regexp]

                    if callable(tree):
                        # It's a terminal symbol. Wrap it up.
                        return tree(
                            Token(
                                "".join([t.word for t in tokens]),
                                tokens[0].line,
                                tokens[0].char,
                                tokens[0].byte,
                            )
                        )
                    elif len(tree) == 1 and None in tree.keys():
                        # Also a terminal
                        return tree[None](
                            Token(
                                "".join([t.word for t in tokens]),
                                tokens[0].line,
                                tokens[0].char,
                                tokens[0].byte,
                            )
                        )

                    match = token.word
                    break

            if match:
                # found something. Collected it in tokens. Get one more and try to match greedily
                continue

            elif (
                not match
                and len(tokens) > 0
                and isinstance(tree, dict)
                and None in tree.keys()
            ):
                self._backtrack(len(token.word))
                self.num_char -= len(token.word)
                return tree[None](
                    Token(
                        "".join([t.word for t in tokens]),
                        tokens[0].line,
                        tokens[0].char,
                        tokens[0].byte,
                    )
                )
            else:
                continue
