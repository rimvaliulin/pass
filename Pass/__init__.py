"""Pass — the pythonic awesome stylesheet language.

A CSS preprocessor with an indented, Python-like syntax: variables,
nested selectors, selector inheritance, operations and color functions.
"""

import os
import sys
from .base import read_from_file, read_from_string, write_to_file, write_to_stdout, process_pass

__version__ = (1, 0, 5)

__all__ = ['Pass', 'get_version', 'read_from_file', 'read_from_string',
           'write_to_file', 'write_to_stdout', 'process_pass']


class Pass(object):
    """Compile a ``.pass`` file into a ``.css`` file next to it.

    On a syntax or indentation error the error is reported with the
    source location and the process exits with status 1.
    """

    def __init__(self, filename, compressed=True, empty_selectors=True, respect_indents=False,
                 inherit_selectors=False, indent='  ', css_indent='    ', newlines=True):
        """Compile ``filename`` with the given options.

        :param filename: path to the ``.pass`` source file
        :param compressed: emit minified CSS (default), otherwise pretty format
        :param empty_selectors: keep selectors without declarations
        :param respect_indents: keep the ``.pass`` indentation in inherited selector names
        :param inherit_selectors: merge selectors instead of duplicating properties
        :param indent: indentation unit of the ``.pass`` file
        :param css_indent: indentation unit of the generated ``.css`` file
        :param newlines: terminate output lines with newlines
        """
        try:
            process_pass(filename, compressed, empty_selectors, respect_indents,
                         inherit_selectors, indent, css_indent, newlines)
        except (SyntaxError, IndentationError) as e:
            self._print_error(e, e.filename, e.lineno, getattr(e, 'msg', str(e)))
        except (ValueError, IOError) as e:
            try:
                self._print_error(e, e.args[1][0], e.args[1][1], e.args[0])
            except IndexError:
                print(e.args)

    def _print_error(self, e, filename, n, msg):
        """Print a compiler error with the offending source line and exit with status 1."""
        name = e.__class__.__name__
        try:
            with open(filename) as f:
                margin = 1
                lines = []
                for i, line in enumerate(f):
                    if n - margin <= i + 1 <= n + margin:
                        lines.append(line)
                m = len(lines)//2
                tab = lines[m][:len(lines[m]) - len(lines[m].lstrip())]
                lines = ''.join(lines[:m] + [tab + '^\n'] + lines[m:])
                sys.stderr.write('File "%s", line %s\n%s%s: %s\n' % (os.path.normpath(filename), n, lines, name, msg))
                sys.exit(1)
        except IOError:
            sys.stderr.write('File "%s", line %s\n%s%s: %s\n' % (os.path.normpath(filename), n, None, name, msg))
            sys.exit(1)

def get_version():
    """Return the package version as a dotted string, e.g. ``'1.0.5'``."""
    return '.'.join(map(str, __version__))