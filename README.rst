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
|    ._wrapper                             |    ._wrapper                             |
|      pass                                |      pass                                |
|                                          |                                          |
|    .wrapper                              |    .wrapper                              |
|      pass                                |      pass                                |
|                                          |                                          |
|    .header                               |    .header                               |
|      pass                                |      pass                                |
|    .content                              |    .content                              |
|      pass                                |      pass                                |
|    .footer                               |    .footer                               |
|      pass                                |      pass                                |
|                                          |                                          |
|    .main                                 |    .main                                 |
|      pass                                |      pass                                |
|      _header                             |      _header                             |
|        pass                              |        pass                              |
|      _content                            |      _content                            |
|        pass                              |        pass                              |
|      _footer                             |      _footer                             |
|        pass                              |        pass                              |
|                                          |                                          |
|    .page                                 |    .page                                 |
|      pass                                |      pass                                |
|      _header                             |      _header                             |
|        pass                              |        pass                              |
|      _content                            |      _content                            |
|        pass                              |        pass                              |
|      _footer                             |      _footer                             |
|        pass                              |        pass                              |
|                                          |                                          |
+------------------------------------------+------------------------------------------+

Functions
---------

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
:Version: 0.9.beta.0 of 2013/06/02
:Dedication: To my wife.
