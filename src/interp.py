from .parser import Parser
from .lang import Lang
from .exc import EOF

OPERAND_L = 0
OPERATOR = 1
OPERAND_R = 2


class Interpreter:
    lang = Lang

    class Snapshot(dict):
        """
        Takes a snapshot of interpreter state. Print human-readable dump
        """

        def __init__(self, *args, **kwargs):

            interp = args[0]

            d = {
                "Pointer": interp.pntr,
                "Block stack": interp.block_stack,
                "Scope": interp.memory.scope,
                "Stack": interp.memory.stack,
                "Ctrl stack": interp.ctrl_stack,
                "Instruction": interp.memory.instr[interp.pntr] if interp.pntr < len(interp.memory.instr) else None,
                "Last result": interp.last,
            }

            super(Interpreter.Snapshot, self).__init__(d, **kwargs)

        def __str__(self):
            # one-liner aligning with spaces
            return "\n" + "\n".join(["%s %s %s" % (k, " " * (16 - len(k)), v) for k, v in self.items()])

    """
    Reads language and executes it, handling values stored in memory, etc
    """

    class Memory:
        def __init__(self):
            self.instr = []
            self.stack = []
            self.scope = [{}]

    def __init__(self, source=None):
        self.parser = Parser(self.lang, source)
        self.lang = self.parser.lang
        self.memory = Interpreter.Memory()
        self.ctrl_stack = [True]
        self.block_stack = ["<main>"]
        self.pntr = 0
        self.last = None

    def read(self, source, is_file=False):
        """
        Feeds parser with command
        """
        self.parser.set_source(source, is_file)
        self._load()
        return self

    def _load(self):
        """
        Build grammar tree for all instructions loaded in parser and stores
        it into memory for later execution
        """

        while True:
            instr = self.parser.parse()

            if instr is False or instr is None:
                return False

            # build grammar tree
            gtree = self.parser.build(instr)

            # append to instruction memory block
            self.memory.instr.append(gtree)

    def _exec_all(self, source=None, build=True):
        """
        Execute all lines in source code
        """
        r = None

        for i in source or []:
            r = self.eval(i) if build is None else self.eval(self.parser.build(i))
            self.last = r

        return r

    def exec_next(self):
        """
        Executes one line at a time
        """
        try:
            # eval the instructions
            r = self.eval(self.memory.instr[self.pntr])
            self.last = r

        except IndexError:
            raise EOF

        self.pntr += 1
        return r

    def scope(self):
        """
        Current scope
        """
        return self.memory.scope[-1]

    def bind(self, i, v):
        """
        Bind a variable with a value
        """
        if isinstance(i, self.lang.Identifier):
            i = i.word
        self.scope()[i] = v

    def fetch(self, i):
        """
        Get a value from a variable in scope
        """
        if isinstance(i, self.lang.Identifier):
            i = i.word
        return self.scope().get(i, None)

    def push_scope(self, namespace={}):
        """
        Open a scope
        """
        scp = namespace.copy()
        scp.update(self.scope())
        self.memory.scope.append(scp)

    def pull_scope(self):
        """
        Remove a scope
        """
        return self.memory.scope.pop()

    # absolute addressing
    def goto(self, n):
        """
        Goto absolute address
        """
        self.pntr = n

    # relative addressing
    def move(self, i):
        """
        Move interpreter instruction pointer. Relative address from current pointer position
        """
        self.pntr += i

    def call(self, routine, arguments):
        """
        Handle procedure calls
        """
        print("Calling routine %s" % (routine.get_identifier()))

        # push block
        self.push_block(routine)

        # address & get signarure
        address = routine.address
        signature = routine.get_signature()

        # check signature match with arguments
        if len(signature) != len(arguments):
            raise Exception("Function expects %s arguments. Given %s" % (len(signature), len(arguments)))

        self.push_scope()

        if len(signature) > 0:
            # assign calling args to routine signature
            for k, v in enumerate(self.getval(signature)):
                self.bind(signature[k][0], arguments[k])

        # is function. Return last statement eval
        if isinstance(routine, self.lang.Def):
            ret = self._exec_all(routine.block)
            # print(ret)
            self.endcall()
            return ret
        # is procedure. Return nothing. Move instruction pointer
        else:
            # push return address to stack
            self.stack_push({"ret_addr": self.pntr})
            self.goto(address)

    def endcall(self):
        """
        Handle procedure call ending
        """
        ret_addr = None

        if len(self.memory.stack) > 0:
            stack = self.stack_pull()
            ret_addr = stack.get("ret_addr", None)

        self.endblock()
        self.pull_scope()

        if ret_addr is None:
            return

        self.goto(ret_addr)

    def endblock(self):
        """
        Close a code of block
        """
        self.pull_block()

    def endif(self):
        """
        Close an IF statement
        """
        self.pull_read_enabled()
        self.endblock()

    def block(self):
        """
        Get current block
        """
        return self.block_stack[-1]

    def push_block(self, block):
        """
        Open a block of code
        """
        if not isinstance(block, self.lang.Block):
            raise Exception("Tried to push a non-block statement")
        self.block_stack.append(block)

    def pull_block(self):
        """
        Close a block of code
        """
        return self.block_stack.pop()

    def stack(self):
        return self.memory.stack[-1]

    def stack_push(self, v):
        self.memory.stack.append(v)

    def stack_pull(self):
        return self.memory.stack.pop()

    def is_read_enabled(self):
        """
        Returns whether the interpreter is set to execute instructions or to ignore them
        """
        return self.ctrl_stack[-1]

    def toggle_read_enabled(self):
        """
        Toggle read enable. Used in IF/ELSE blocks
        """
        # if parent block isn't executable, child blocks aren't neither
        if not self.ctrl_stack[-2:-1][0]:
            self.ctrl_stack[-1] = False
        else:
            self.ctrl_stack[-1] = not self.ctrl_stack[-1]

    def push_read_enabled(self, boolean):
        """
        Set a block to be read enabled or not
        """
        # if parent block isn't executable, child blocks aren't neither
        if not self.is_read_enabled():
            self.ctrl_stack.append(False)
        else:
            self.ctrl_stack.append(boolean)

    def pull_read_enabled(self):
        """
        Remove read enabled property in block
        """
        return self.ctrl_stack.pop()

    """
    Eval variables, lists. Handle references
    """

    def getval(self, i, **kwargs):

        # it's nested
        if isinstance(i, list) and not isinstance(i, self.lang.List):
            return self.getval(i.pop(), **kwargs)
        # identifiers
        if isinstance(i, self.lang.Identifier):
            # return memory address identifier
            if kwargs.get("ref", None) is not None:
                return i
            # return value in memory
            else:
                return i.eval(self.scope())

        # structs
        elif isinstance(i, self.lang.Vector):
            return i

        # constants
        elif isinstance(i, self.lang.Constant):
            return i.eval()
        # a value
        else:
            return i

    """
    Eval sentences
    """

    def eval(self, i, ref=False):

        if isinstance(i, self.lang.List):
            for k, v in enumerate(i):
                i[k] = self.eval(v) if ref is True else self.getval(self.eval(v))
            return i

        if isinstance(i, list) and len(i) > 0:
            # a control struct
            if isinstance(i[OPERAND_L], self.lang.Control):
                return i[OPERAND_L].eval(self, i[1:])

            # ignore is read is not enabled
            if not self.is_read_enabled():
                return None

            # a keyword
            if isinstance(i[OPERAND_L], self.lang.Keyword):
                return i[OPERAND_L].eval(self, i[1:])

            # expressions
            for k, v in enumerate(i):
                if isinstance(v, list):
                    i[k] = self.eval(v)

            # a value
            if len(i) < 2:
                ii = i.pop()
                if isinstance(ii, self.lang.Constant):
                    return ii.eval()
                else:
                    return ii

            # unary operation
            if len(i) < 3:
                return i.pop(0).eval(self.scope(), arguments=i.pop(0), interp=self)

            # assign operations
            if isinstance(i[OPERATOR], self.lang.Assign):
                return i[OPERATOR].eval(i[OPERAND_L], self.getval(i[OPERAND_R]), self.scope())
            # any other binary operation
            else:
                return i[OPERATOR].eval(self.getval(i[OPERAND_L]), self.getval(i[OPERAND_R]), self.scope())

        else:
            return i
