"""Compile every ``.pass`` demo in this directory.

Run from the project root::

    uv run python demo/make.py
"""

import os

from Pass import Pass

DEMOS = [
    # (filename, kwargs)
    ('test.pass', dict(inherit_selectors=True)),
    ('variables.pass', dict()),
    ('media.pass', dict()),
    ('imports.pass', dict()),
]

if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    for filename, kwargs in DEMOS:
        print('compiling %s ->' % filename, end=' ')
        Pass(os.path.join(here, filename), **kwargs)
        print(os.path.splitext(filename)[0] + '.css')
