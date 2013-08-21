====
Pass
====
http://githab.com/rimvaliulin/pass

The **pythonic awesome** stylesheet language.

About
=====
Pass is a dynamic stylesheet language and css preprocessor for web-developers that makes ccs coding simple and
beautiful by having dynamic behavior such as variables, inheritance, operations and functions with python like indented syntax.

Installation
------------

::

    pip install pass

Command-line usage
------------------

::

    pass style.pass

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

+------------------------------------------+------------------------------------------+
|::                                        |::                                        |
|                                          |                                          |
|    // Pass                               |    /* Compiled CSS */                    |
|    link_active = #1f6ba2                 |    .menu-item {                          |
|    link_hover = #ccc                     |        color: #1f6ba2;                   |
|    link_height = 32px                    |        line-height: 16px                 |
|    link_size = 1em                       |    }                                     |
|                                          |    a:hover {                             |
|    .menu-item                            |        color: #ccc                       |
|      color link_active                   |        font-size: 1.5em                  |
|      line-height link_height / 2         |        background: #000                  |
|                                          |    }                                     |
|    a:hover                               |                                          |
|      color link_hover                    |                                          |
|      font-size link_size + 0.5           |                                          |
|      background #000                     |                                          |
|                                          |                                          |
+------------------------------------------+------------------------------------------+

Nested selectors
----------------
Rather than constructing long selector names to specify inheritance, you can simply nest selectors
inside other selectors.

+------------------------------------------+------------------------------------------+
|::                                        |::                                        |
|                                          |                                          |
|    // Pass                               |    /* Compiled CSS */                    |
|    line_height = 16px                    |    .menu {                               |
|    .menu                                 |        margin-bottom 8px                 |
|      margin-bottom line_height/2         |    }                                     |
|      -item                               |    .menu-item {                          |
|        float left                        |        float left                        |
|        color #fff                        |        color #fff                        |
|        :visited                          |    }                                     |
|          color #eee                      |    .menu-item:visited {                  |
|        _active                           |        color #eee                        |
|        :hover                            |    }                                     |
|          color #ccc                      |    .menu-item_active, .menu-item:hover { |
|      span                                |       color #ccc                         |
|        background-color #ccc             |    }                                     |
|                                          |    .menu span {                          |
|                                          |        background-color #ccc             |
|                                          |    }                                     |
|                                          |                                          |
+------------------------------------------+------------------------------------------+

Selector inheritance
--------------------
Class naming scheme::

             block-[element]
    [child_]parent-[[parent]_child]

+------------------------------------------+------------------------------------------+
|::                                        |::                                        |
|                                          |                                          |
|    // Pass                               |    /* Compiled CSS */                    |
|    ._foo                                 |    ._foo,.foo,.сhild_foo,.new_child_foo{}|
|      pass                                |    .foo{}                                |
|                                          |    .child_foo,.new_child_foo{}           |
|    .foo                                  |    .new_child_foo{}                      |
|      pass                                |                                          |
|                                          |                                          |
|    .сhild_foo                            |                                          |
|      pass                                |                                          |
|                                          |                                          |
|    .new_child_foo                        |                                          |
|      pass                                |    .bar-link,bar-link_active{}           |
|                                          |    bar-link_active{}                     |
|    .bar                                  |                                          |
|      -link                               |                                          |
|        pass                              |                                          |
|        _acive                            |                                          |
|          pass                            |                                          |
+------------------------------------------+------------------------------------------+


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

-a         Output all.
-b         Output both (this description is
           quite long).
-c arg     Output just arg.
--long     Output all day long.

-p         This option has two paragraphs in the description.
           This is the first.

           This is the second.  Blank lines may be omitted between
           options (as above) or left in (as here and below).

--very-long-option  A VMS-style option.  Note the adjustment for
                    the required two spaces.

--an-even-longer-option
           The description can also start on the next line.

-2, --two  This option has two variants.

-f FILE, --file=FILE  These two options are synonyms; both have
                      arguments.

/V         A VMS/DOS-style option.

License
=======

See ``LICENSE`` file.
::

> Copyright (c) 2012 Rim Valiulin


:Author: Rim Valiulin
:Version: 1.0.4 of 2013/07/21
:Dedication: To my wife.
