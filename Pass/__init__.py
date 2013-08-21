import os
import sys
from base import read_from_file, read_from_string, write_to_file, write_to_stdout, process_pass

__version__ = (1, 0, 4)


class Pass(object):

    def __init__(self, filename, compressed=True, empty_selectors=True, respect_indents=False,
                 inherit_selectors=False, indent='  ', css_indent='    ', newlines=True):
        try:
            process_pass(filename, compressed, empty_selectors, respect_indents,
                         inherit_selectors, indent, css_indent, newlines)
        except (SyntaxError, IndentationError) as e:
            self.print_error(e, e.filename, e.lineno, getattr(e, 'msg', e.message))
        except (ValueError, IOError) as e:
            try:
                self.print_error(e, e.args[1][0], e.args[1][1], e.args[0])
            except IndexError:
                print e.args

    def print_error(self, e, filename, n, msg):
        name = e.__class__.__name__
        with open(filename) as f:
            margin = 1
            lines = []
            for i, line in enumerate(f):
                if n - margin <= i + 1 <= n + margin:
                    lines.append(line)
            m = len(lines)/2 + 1
            tab = lines[m][:len(lines[m]) - len(lines[m].lstrip())]
            lines = ''.join(lines[:m] + [tab + '^\n'] + lines[m:])
            sys.stderr.write('File "%s", line %s\n%s%s: %s\n' % (os.path.normpath(filename), n, lines, name, msg))


def get_version():
    return '.'.join(map(str, __version__))