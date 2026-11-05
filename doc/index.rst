Pass — the pythonic awesome stylesheet language
===============================================

Pass is a dynamic stylesheet language and CSS preprocessor with an
indented, Python-like syntax: variables, nested selectors, selector
inheritance, operations and color functions.

Quick example
-------------

.. code-block:: scss

    link_active = #1f6ba2

    .menu-item
      color link_active
      -item
        float left

Compiles to:

.. code-block:: css

    .menu-item{color:#1f6ba2;}
    .menu-item-item{float:left;}

.. note::
   The indentation of the ``.pass`` file is significant: two spaces by
   default (see the ``--indent`` option).

Contents
--------

.. toctree::
   :maxdepth: 2

   usage
   syntax
   api

Indices
-------

* :ref:`genindex`
* :ref:`search`
