from src.exc import EOF
from src.interp import Interpreter
import sys


def run(filename):

    if not filename:
        return

    interp = Interpreter().read(filename, is_file=True)

    with open(".debug", "w") as log:
        try:
            while True:
                log.write(str(Interpreter.Snapshot(interp)) + "/n")
                interp.exec_next()
        except EOF:
            exit(0)


if __name__ == "__main__":
    run(sys.argv[1])
