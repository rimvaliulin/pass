Syntax
======

Variables and operators
-----------------------

Variables allow you to specify widely used values in a single place, and
then re-use them throughout the stylesheet, making global changes as easy
as changing one line of code.

.. code-block:: scss

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

Compiles to:

.. code-block:: css

    .menu-item {
        color: #1f6ba2;
        line-height: 16px
    }
    a:hover {
        color: #ccc;
        font-size: 1.5em;
        background: #000
    }

Values are computed for the properties that take numeric or color
expressions (``color``, ``background-color``, ``width``, ``height``,
``margin-*``, ``padding-*``, ``border-*``, ``top``, ``left``,
``line-height``, ...). Units are kept: ``16px / 2`` is ``8px``.

Nested selectors
----------------

Rather than constructing long selector names to specify inheritance, you
can simply nest selectors inside other selectors.

.. code-block:: scss

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

Compiles to:

.. code-block:: css

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

With the ``-i`` option (or ``inherit_selectors=True``) selectors that
share a naming scheme are merged instead of duplicating properties. The
class naming scheme is::

             block-[element]
    [child_]parent-[[parent]_child]

``_`` marks a child of the previous part and ``-`` separates a block
from an element. It differs from BEM (Block - Element - Modificator).

.. code-block:: scss

    ._foo
      pass

    .foo
      pass

    .child_foo
      pass

Compiles to:

.. code-block:: css

    ._foo,.foo,.child_foo{}
    .foo{}
    .child_foo{}

Directives
----------

``@parent`` — declare the file this file extends; the parent is
recompiled and its rules take effect::

    @parent "style.pass"

``@import`` — inline other ``.pass`` files (compiled) and ``.css`` files
(as-is) at the top level::

    @import "include.pass" "legacy.css"

``@media`` — a media query block on the root level; nested selectors
inside are grouped under the condition::

    @media screen
      .column
        width 100%

``pass`` — an empty statement that keeps a selector (or opens a block)
without declarations.

``clearfix`` — expands into the classic micro clearfix rules
(``:before``/``:after`` with ``content``, ``display: table``,
``clear: both`` and ``*zoom`` for old IE).

Built-in functions
------------------

Color functions: ``rgb()``, ``rgba()``, ``hsl()``, ``hsla()``,
``red()``, ``green()``, ``blue()``, ``hue()``, ``saturation()``,
``lightness()``, ``alpha()``, ``spinin()``, ``spinout()``, ``lighten()``,
``darken()``, ``saturate()``, ``desaturate()``, ``fadein()``,
``fadeout()``, ``grayscale()``, ``complement()``, ``invert()``, ``mix()``.

String functions: ``quote()``, ``unquote()``.

Number functions: ``percentage()``, ``round()``, ``ceil()``, ``floor()``.

Percentages are written as ``Pr(50)`` (50%), units as ``Em``, ``Ex``,
``Px``, ``Pt``, ``Pc``, ``Cm``, ``Mm``, ``In`` — e.g.
``lighten(#1f6ba2, Pr(10))`` or ``Px(16) / 2``.

CSS selector grammar
--------------------

Selectors follow the `CSS2.1 selector grammar
<https://www.w3.org/TR/CSS2/selector.html>`_: type selectors, ``#id``,
``.class``, ``[attr]`` attribute selectors, ``:pseudo-classes`` and
``+``/``>`` combinators. Property names follow the `CSS2.1 property
index <https://www.w3.org/TR/CSS2/propidx.html>`_ (see
``Pass/properties.py`` for the full table).
