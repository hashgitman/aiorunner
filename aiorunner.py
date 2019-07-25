import ast
import asyncio
import sys
import traceback
import uuid

SPACE = " "

class AioRunnerException(Exception):
    def __init__(self, fname, lineno, funcname, text, error, msg):
        self.fname = fname
        self.lineno = lineno
        self.funcname = funcname
        self.text = text
        self.error = error
        self.msg = msg

    def __repr__(self):
        if self.fname:
            return "  File %s, line %d, in %s\n    %s\n%s:%s" % (self.fname,
                                                                 self.lineno,
                                                                 self.fname,
                                                                 self.text,
                                                                 self.error,
                                                                 self.msg)
        else:
            return "%s:%s" % (self.error, self.msg)

    def __str__(self):
        return self.__repr__()

def funcname():
    return "f{}".format(uuid.uuid1().hex)

class AioRunner:
    def __init__(self, script, G={}, filename=funcname(), timeout=60):
        self.G = G
        if asyncio.__name__ not in self.G:
            self.G.setdefault(asyncio.__name__, asyncio)

        self.timeout = timeout
        self.filename = filename

        self.lines = ["async def {}():".format(self.filename)]
        [self.lines.append("%s%s" % (SPACE*4, i)) for i in script.split("\n")]

        self.coroutine = "c%s" % uuid.uuid1().hex
        self.lines.append("%s = %s()" % (self.coroutine, self.filename))

        try:
            self.OBJ = compile(self.script, self.filename, "exec")
        except:
            self._traceback(self.filename, self.script, 1)

    @property
    def script(self):
        return "\n".join(self.lines)

    async def __aenter__(self):
        try:
            exec(self.OBJ, self.G)
        except:
            self._traceback(self.filename, self.script, 1)

        try:
            return await asyncio.wait_for(self.G[self.coroutine], self.timeout)
        except:
            self._traceback(self.filename, self.script, 1)

    def __await__(self):
        return self.__aenter__().__await__()

    @classmethod
    def isAsync(self, script):
        for node in ast.walk(ast.parse(script)):
            if isinstance(node, ast.Await) or \
               isinstance(node, ast.AsyncFunctionDef) or \
               isinstance(node, ast.AsyncFor) or \
               isinstance(node, ast.AsyncWith):
                return True
        return False

    def _traceback(self, filename, script, offset=0):
        info = sys.exc_info()
        tbinfo = traceback.extract_tb(info[2])
        tbinfo.reverse()

        (fname, lineno, func, text) = (None, None, None, None)
        for i in tbinfo:
            if i[0] == filename:
                (fname, lineno, func) = (i[0], i[1], i[2])
                break

        if lineno and offset > 0:
            lineno -= offset
            text = script.split("\n")[lineno]

        raise AioRunnerException(fname, lineno, func, text, info[0].__name__, info[1].__str__())

async def main():
    script = """await asyncio.sleep(1)
print("Hello, asyncio!!")
return "Thanks"
"""
    try:
        response = await AioRunner(script)
        print(response)
    except AioRunnerException as e:
        print(e)

asyncio.run(main())
