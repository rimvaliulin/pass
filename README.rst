====
Pass
====
http://github.com/rimvaliulin/pass

The **pythonic awesome** stylesheet language.

About
=====
Pass is a dynamic stylesheet language and css preprocessor for web-developers that makes ccs coding simple and
beautiful by having dynamic behavior such as variables, inheritance, operations and functions with python like indented syntax.

Installation
------------
Pass requires Python 3.10 or later (tested with Python 3.15). Python 2 is no longer supported.

The project is managed with `uv <https://docs.astral.sh/uv/>`_. To set up the environment and
install the package in editable mode run::

    uv sync

To install the ``pass`` command globally as an isolated tool run::

    uv tool install pass

(or ``uv tool install .`` from a checkout of this repository).

Alternatively, install with pip::

    pip install pass

Documentation
-------------

The full documentation is published on
`GitHub Pages <https://rimvaliulin.github.io/pass/docs/>`_ (Sphinx sources
live in ``doc/``). A landing page with a quick overview is available at
`rimvaliulin.github.io/pass <https://rimvaliulin.github.io/pass/>`_.

Command-line usage
------------------

::

    uv run pass style.pass

Usage in Code
-------------

::

    import Pass

    Pass('style.pass')

Syntax
======
 - Every piece of knowledge must have a single, unambiguous, authoritative representation within a system. `"DRY - don't repeat yourself" <http://en.wikipedia.org/wiki/Don't_repeat_yourself>`_
 - There should be one — and preferably only one — obvious way to do it", from `"The Zen of Python" <http://en.wikipedia.org/wiki/The_Zen_of_Python>`_.

Variables and operators
-----------------------
Variables allow you to specify widely used values in a single place, and then re-use them throughout the stylesheet,
making global changes as easy as changing one line of code.

.. code-block:: scss

    // Pass
    link_active = #1f6ba2
    link_hover = #ccc
    link_height = 32px
    link_size = 1em

    .menu-item
      color link_active
      line-height link_height / 2

    a:hover
      color link_hover
      font-size link_size + 0.5
      background #000

.. code-block:: css

    /* Compiled CSS */
    .menu-item {
        color: #1f6ba2;
        line-height: 16px
    }
    a:hover {
        color: #ccc;
        font-size: 1.5em;
        background: #000
    }

Nested selectors
----------------
Rather than constructing long selector names to specify inheritance, you can simply nest selectors
inside other selectors.

.. code-block:: scss

    // Pass
    line_height = 16px
    .menu
      margin-bottom line_height/2
      -item
        float left
        color #fff
        :visited
          color #eee
        _active
          color #ccc
      span
        background-color #ccc

.. code-block:: css

    /* Compiled CSS */
    .menu {
        margin-bottom: 8px
    }
    .menu-item {
        float: left;
        color: #fff
    }
    .menu-item:visited {
        color: #eee
    }
    .menu-item_active, .menu-item:hover {
        color: #ccc
    }
    .menu span {
        background-color: #ccc
    }

Selector inheritance
--------------------
Class naming scheme::

             block-[element]
    [child_]parent-[[parent]_child]

.. code-block:: scss

    // Pass
    ._foo
      pass

    .foo
      pass

    .child_foo
      pass

    .new_child_foo
      pass

    .bar
      -link
        pass
        _acive
          pass

.. code-block:: css

    /* Compiled CSS */
    ._foo,.foo,.child_foo,.new_child_foo{}
    .foo{}
    .child_foo,.new_child_foo{}
    .new_child_foo{}

    .bar-link,bar-link_active{}
    bar-link_active{}


Parent directive
--------------------
Usage::

    @parent "style.pass"


Functions
---------

Color initialization
####################

rgb(r, g, b) - Converts an Rgb(r, g, b) triplet into a color

rgba(r, g, b, a) - Converts an Rgba(r, g, b, a) quadruplet into a color.

hsl(h, s, l) - Converts an Hsl(h, s, l) triplet into a color.

hsla(h, s, l, a) - Converts an Hsla(h, s, l) quadruplet into a color.


Get/set color components
########################

red(color, value=None) - Return the red component of the given color.

green(color, value=None) - Return the green component of the given color.

blue(color, value=None) - Return the blue component of the given color.

hue(color, value=None) - Return the hue of the given color.

saturation(color, value=None) - Return the saturation of the given color.

lightness(color, value=None) - Return the lightness of the given color.

alpha(color, value=None) - Return the alpha component of the given color.

Color adjustment
################

spinin(color, value=Pr(10)) - Changes the hue of a color.

spinout(color, value=Pr(10)) - Changes the hue of a color.

lighten(color, value=Pr(10)) - Makes a color lighten.

darken(color, value=Pr(10)) - Makes a color darker.

saturate(color, value=Pr(10)) - Makes a color more saturated.

esaturate(color, value=Pr(10)) - Makes a color less saturated.

fadein(color, value=Pr(10)) - Add or change an alpha layer for any color value.

fadeout(color, value=Pr(10)) - Add or change an alpha layer for any color value.

grayscale(color) - Converts a color to grayscale.

complement(color) - Returns the complement of a color.

invert(color) - Returns the inverse of a color.

mix(color, color1, weight=Pr(50)) - Mixes two colors together.

String Functions
################

quote(s) - Removes the quotes from a string.

unquote(s) - Adds quotes to a string.

Number Functions
################

percentage(value) - Converts a unitless number to a percentage.

round_(value, digits=0) - Rounds a number to the nearest whole number.

ceil(value) - Rounds a number up to the nearest whole number.

floor(value) - Rounds a number down to the nearest whole number.


Command-line options
--------------------

-V, --version                           show program's version number and exit
-h, --help                              show this help message and exit
-i, --inherit                           use selector inheritance, rather then property duplication
-c, --formatted                         pretty format result .css file
-e, --empty-selectors                   keep empty selectors
-r, --respect-indents                   respect indentes
-n, --newlines                          use newlines
-I INDENT, --indent=INDENT              .pass file indentation. default 2 breaks
-C CSS_INDENT, --css-indent=CSS_INDENT  .css file indentation. default 4 breaks

Running the tests
-----------------

From the project root run::

    uv run python -m unittest discover -s test

Static checks
-------------

The project uses `ruff <https://docs.astral.sh/ruff/>`_ for linting and `ty <https://docs.astral.sh/ty/>`_
for type checking. Both are installed as dev dependencies by ``uv sync``::

    uv run ruff check .
    uv run ty check .

License
=======

See ``LICENSE`` file.

::

> Copyright (c) 2012 Rim Valiulin


:Author: Rim Valiulin
