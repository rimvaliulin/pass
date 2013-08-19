from StringIO import StringIO
from token import NUMBER, NAME, OP, STRING
from tokenize import generate_tokens, untokenize
from Pass.utils import consumer


def decistmt(s):
    """Substitute Decimals for floats in a string of statements.

    >>> from decimal import Decimal
    >>> s = 'print +21.3e-5*-.1234/81.7'
    >>> decistmt(s)
    "print +Decimal ('21.3e-5')*-Decimal ('.1234')/Decimal ('81.7')"

    >>> exec(s)
    -3.21716034272e-007
    >>> exec(decistmt(s))
    -3.217160342717258261933904529E-7

    """
    result = []
    g = generate_tokens(StringIO(s).readline)   # tokenize the string
    for toknum, tokval, _, _, _ in g:
        print toknum, tokval
        if toknum == NUMBER and '.' in tokval:  # replace NUMBER tokens
            result.extend([
                (NAME, 'Decimal'),
                (OP, '('),
                (STRING, repr(tokval)),
                (OP, ')')
            ])
        else:
            result.append((toknum, tokval))
    return untokenize(result)


#print decistmt('a, b = 1, 2')


@consumer
def getter(lines):
    yield
    for line in lines:
        data = yield line
        if data is not None:
            print '=>', data,
            yield line


def iterator(lines):
    for line in lines:
        yield line


def iterator1(lines):
    for line in lines:
        if line == 5:
            lines.send(line)
            break
        yield line


def generator():
    for line in range(10):
        yield line


lines = generator()
lines = getter(lines)
#lines = iterator(lines)
lines = iterator1(lines)
lines = getter(lines)
lines = iterator1(lines)
for line in lines:
    print line
