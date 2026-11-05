Usage
=====

Command line
------------

Install the package (see the README) and compile a ``.pass`` file::

    uv run pass style.pass

The result is written next to the source file with a ``.css`` extension.
Useful options::

    uv run pass --help

.. list-table::
   :header-rows: 1

   * - Option
     - Description
   * - ``-V, --version``
     - show program's version number and exit
   * - ``-i, --inherit``
     - use selector inheritance, rather than property duplication
   * - ``-c, --formatted``
     - pretty format result ``.css`` file
   * - ``-e, --empty-selectors``
     - keep empty selectors
   * - ``-r, --respect-indents``
     - respect indents in inherited selector names
   * - ``-n, --newlines``
     - use newlines
   * - ``-I, --indent INDENT``
     - ``.pass`` file indentation, default 2 breaks
   * - ``-C, --css-indent CSS_INDENT``
     - ``.css`` file indentation, default 4 breaks

Library
-------

.. code-block:: python

    import Pass

    Pass('style.pass', inherit_selectors=True, compressed=True)

The :class:`Pass.Pass` constructor accepts the same options as the CLI
and writes the ``.css`` file next to the source file. Syntax and
indentation errors are reported with the file name and line number.

Demos
-----

The ``demo/`` directory contains runnable examples::

    uv run python demo/make.py
