import tty
import termios
import sys
from src.interp import Interpreter


class Terminal:
    def __init__(self, filename=None):
        self.interp = Interpreter()

        """
		self.source = None
		
		if filename is not None:
			with open(filename, 'r') as source:
				self.source = source.read()
				self.interp.read(self.source)
		"""

    def begin(self):
        """
        if not self.source:
                self.interp.load();
        """

        self.interp.read("tests/sample/sample.dtk", is_file=True)

        while True:
            ch = self.getchar()

            if ch == "q":
                break

            instr = self.interp.exec_next()

            if instr is False:
                print("EOF")
                break

            # print '-' * 80

    def getchar(self):
        # Returns a single character from standard input
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch


T = Terminal()
T.begin()
