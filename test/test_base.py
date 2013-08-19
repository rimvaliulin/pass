from __future__ import unicode_literals
import unittest
from Pass.base import (read_and_write_file, read_from_string, ignore_empty_lines,
                       ignore_line_comments, ignore_block_comments, define_variables,
                       tokenize_selectors_and_properties, check_indentation_errors,
                       check_imports_syntax, filter_properties, evaluate_properties,
                       _locals, check_media_queries_syntax, combine_selectors,
                       make_statements_list, inherit_statements, make_css_from_statements)
from Pass.utils import consumer


def _in(first, start=0):
    is_str = True
    try:
        first = (i[8:] for i in first.splitlines()[1:-1])
    except AttributeError:
        is_str = False
    for i, line in enumerate(first, start=1):
        if line == '---':
            continue
        if is_str:
            line = (line,)
        if start == 0:
            line = (None, i) + line
        elif start == 1:
            line = (None,) + line
        elif start == 2:
            line = (i,) + line
        yield line


def _out(first, start=1):
    return [line[start:] for line in first]


def _plain(first):
    first = '\n' + '\n'.join(first) + '\n'
    return first.replace('\n', '\n        ')


def _print(first):
    for i in first:
        print i


class TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.indent = '  '

    @consumer
    def target(self):
        temp = []
        try:
            while True:
                temp.append((yield))
        except GeneratorExit:
            self.first = temp

    def test_load_from_file(self):
        read_and_write_file('there_no_such_file.pass')
        #with self.assertRaises(IOError):
        #    read_and_write_file('there_no_such_file.pass')

    def test_load_from_string(self):
        for first in ('\n', '\n', '\r\n', '\na\r\nb\nc\n \n    \n'):
            second = [(None, i, x.rstrip()) for i, x in enumerate(first.splitlines(), start=1)]
            first = list(read_from_string(first))
            self.assertListEqual(first, second)

    def test_ignore_empty_lines(self):
        first = '''
        ---
        hello world
        a\n\n
        \t
         \t
        \r\n \t
        ---
         \n \r \t
         \r\n
        \r
        '''
        second = [
            (2, 'hello world'),
            (3, 'a'),
        ]
        first = _out(ignore_empty_lines(_in(first)))
        self.assertEqual(first, second)

    def test_ignore_line_comments(self):
        first = '''
        color #fff //comment
        ---
        background white url("http://ya.ru/i.gif") top left repeat
         //comment
        ---
        background white url("https://yandex.ru/empty.gif") top left x-repeat
        \t  // comment
        '''
        second = [
            (1, 'color #fff //comment'),
            (3, 'background white url("http://ya.ru/i.gif") top left repeat'),
            (6, 'background white url("https://yandex.ru/empty.gif") top left x-repeat'),
        ]
        first = _out(ignore_line_comments(_in(first), self.target()))
        self.assertEqual(first, second)

    def test_ignore_block_comments(self):
        first = '''
        ---
        /* inline comment */a
        ---
        /* inline comment */b/* inline /* comment */c/* block comment starts
        block comment body
        block comment body
        ---
        block comment ends */d/* inline comment *//* inline comment *//* inline comment */
        e
        ---
        \t
        /* inline comment */ \t  /* inline comment */
        ---
        f/* inline comment */g/* inline comment */
        '''
        second = [
            (2, 'a'),
            (4, 'bc'),
            (8, 'd'),
            (9, 'e'),
            (11, '\t'),
            (14, 'fg'),
        ]
        first = _out(ignore_block_comments(_in(first), self.target()))
        self.assertListEqual(first, second)

    def test_define_variables(self):
        first = '''
        a = 1
        b = 2
        ---
        input["type"="radio"]
        ---
        e = 'string'
        '''
        second = [
            (4, 'input["type"="radio"]'),
        ]
        second1 = [
            (1, 'a = 1'),
            (2, 'b = 2'),
            (6, "e = 'string'"),
        ]
        first = _out(define_variables(_in(first), self.target()))
        self.assertDictContainsSubset({'a': 1, 'b': 2, 'e': 'string'}, _locals)
        self.assertEqual(first, second)
        self.assertListEqual(_out(self.first), second1)

    def test_define_variables_on_syntax_error(self):
        first = '''
        =
        ---
        a=
        ---
        =b
        ---
        1a = 1
        ---
        a, b = 2, 3
        ---
        auto = 1
        ---
        none = 1
        ---
        Px = 1
        '''
        for first in first.split('---'):
            with self.assertRaises(SyntaxError):
                _out(define_variables(_in(first), self.target()))

    def test_define_variables_on_indentation_error(self):
        first = '''
         a = 1
        ---
          b = 2
        ---
           c = 3
        ---
        \td = 4
        ---
        \t e = 5
        '''
        for first in first.split('---'):
            with self.assertRaises(IndentationError):
                _out(define_variables(_in(first), self.target()))

    def test_tokenize_selectors_and_properties(self):
        first = '''
        .menu
          pass
          color red
          margin 0
          -item
            color blue
            float left
            _selected
              color green
              border none
        '''
        second = [
            (1, '.menu', 0, 1, True, True),
            (2, 'pass', 1, 1, False, True),
            (3, ('color', 'red'), 1, 0, False, False),
            (4, ('margin', '0'), 1, 0, False, False),
            (5, '-item', 1, 0, True, False),
            (6, ('color', 'blue'), 2, 1, False, True),
            (7, ('float', 'left'), 2, 0, False, False),
            (8, '_selected', 2, 0, True, False),
            (9, ('color', 'green'), 3, 1, False, True),
            (10, ('border', 'none'), 3, 0, False, False),
            (0, '', 0, -3, True, False)]
        first = _out(tokenize_selectors_and_properties(_in(first), self.indent))
        self.assertEquals(first, second)

    def test_tokenize_selectors_and_properties_for_empty_input(self):
        first = '''
        '''
        first = _out(tokenize_selectors_and_properties(_in(first), self.indent))
        self.assertEquals(first, [])

    def test_check_indentation_errors(self):
        first = '''
         .foo
        ---
          .bar
        ---
        \t.baz
        ---
        div
           input
        ---
        div
            input
        ---
        div
        \t input
        ---
        margin-bottom 1px
        ---
        div
          div.sidebar
          margin-bottom 0px
        ---
        div
          div
        ---
        div
          .menu
        input
          pass
        ---
        .menu
          .item
            span
          float left
        ---
        .menu
          float left
            margin-bottom 0px
        ---
        .menu
          #item
            float left
          margin-bottom 0px
        ---
        @media screen
          @media screen
        '''
        for first in first.split('---'):
            first = tokenize_selectors_and_properties(_in(first), self.indent)
            with self.assertRaises(IndentationError):
                _out(check_indentation_errors(first))

    def test_check_imports_syntax_error(self):
        first = '''
        @import
        '''
        for first in first.split('---'):
            first = tokenize_selectors_and_properties(_in(first), self.indent)
            with self.assertRaises(SyntaxError):
                _out(check_imports_syntax(first))

    def test_check_imports_syntax_for_indentation_error(self):
        first = '''
        @import foo.css
          foo
            pass
        ---
        div
        span
        @import foo.css
        '''
        for first in first.split('---'):
            first = tokenize_selectors_and_properties(_in(first), self.indent)
            with self.assertRaises(IndentationError):
                _out(check_imports_syntax(first))

    def test_filter_properties(self):
        first = '''
        foo
          color green
        bar
          margin 0
          margin 0 0
          margin 0 0 0
          margin 0 0 0 0
        baz
          pass
        div
          pass
          pass
        span
          pass
          margin 0
          pass
        '''
        second = [
            (1, 'foo', 0, 1, True, True ),
            (2, ('color', 'green'), 1, 1, False, True ),
            (3, 'bar', 0, -1, True, False),
            (7, ('margin', '0 0 0 0'), 1, 1, False, True ),
            (8, 'baz', 0, -1, True, False),
            (10, 'pass', 1, 1, False, True ),
            (10, 'div', 0, -1, True, False),
            (13, 'pass', 1, 1, False, True ),
            (13, 'span', 0, -1, True, False),
            (15, ('margin', '0'), 1, 0, False, False),
            (0, '', 0, -1, True, False)]
        first = tokenize_selectors_and_properties(_in(first), self.indent)
        first = _out(filter_properties(first))
        self.assertEquals(first, second)

    def test_evaluate_properties_for_name_errors(self):
        first = (
            (None, 1, ('margin-bottom', 'a a'), 1, 0, False, False),
            (None, 1, ('margin', 'a a+1 auto 2*2 1'), 1, 0, False, False),
            (None, 1, ('margin', 'not_defined_var'), 1, 0, False, False),
        )
        for first in first:
            with self.assertRaises(NameError):
                _out(evaluate_properties([first]))

    def test_evaluate_properties(self):
        _locals['a'] = 2
        first = (
            (None, 1, ('margin-bottom', 'a*2'), 1, 0, False, False),
            (None, 1, ('margin', 'a a+1 auto 2*2'), 1, 0, False, False),
            (None, 1, ('margin', 'a a+1'), 1, 0, False, False),
            (None, 1, ('margin', 'a'), 1, 0, False, False),
        )
        second = (
            (('margin-bottom', '4'), 1, 0, False, False),
            (('margin', '2 3 auto 4'), 1, 0, False, False),
            (('margin', '2 3'), 1, 0, False, False),
            (('margin', '2'), 1, 0, False, False),
        )
        for first, second in zip(first, second):
            first = list(evaluate_properties([first]))
            self.assertEqual(first, [second])

    def test_check_media_queries_syntax(self):
        first = '''
        div
          pass
        @media
        ---
        @media
          margin 0
        ---
        @media
        div
          pass
        ---
        div
        span
        @media
        ---
        @media
        @media
          margin 0
        ---
        @media
        '''
        for first in first.split('---'):
            first = tokenize_selectors_and_properties(_in(first), self.indent)
            with self.assertRaises(IndentationError):
                _out(check_media_queries_syntax(first))

    def test_combine_selectors(self):
        first = '''
        .last
          _menu
            pass
            -item
              pass
              _selected
                color green
                _modified
                  pass
                  :hover
                  :active
                    color green
                    font serif
              _last
                color green
                font serif
                width 100%
        '''
        second = [
            (['.last', '_menu'], True, True),
            ('pass', False, True),
            (['.last', '_menu', '-item'], True, False),
            ('pass', False, True),
            (['.last', '_menu', '-item', '_selected'], True, False),
            (('color', 'green'), False, True),
            (['.last', '_menu', '-item', '_selected', '_modified'], True, False),
            ('pass', False, True),
            (['.last', '_menu', '-item', '_selected', '_modified', ':hover'], True, False),
            (['.last', '_menu', '-item', '_selected', '_modified', ':active'], True, True),
            (('color', 'green'), False, True),
            (('font', 'serif'), False, False),
            (['.last', '_menu', '-item', '_last'], True, False),
            (('color', 'green'), False, True),
            (('font', 'serif'), False, False),
            (('width', '100%'), False, False),
        ]
        first = tokenize_selectors_and_properties(_in(first), self.indent)
        first = list(combine_selectors(_out(first, 2)))
        self.assertEquals(first, second)

    def test_combine_selectors1(self):
        first = '''
        foo
        foo1
          bar
            baz
            baz1
              pass
            dum
            dum1
              div
                pass
          must
          must1
            div
              pass
        qalandar
        qalandar1
          div
            pass
        '''
        second = [
            (['foo', 'bar', 'baz'], True, True),
            (['foo1', 'bar', 'baz'], True, True),
            (['foo', 'bar', 'baz1'], True, True),
            (['foo1', 'bar', 'baz1'], True, True),
            ('pass', False, True),
            (['foo', 'bar', 'dum', 'div'], True, False),
            (['foo1', 'bar', 'dum', 'div'], True, True),
            (['foo', 'bar', 'dum1', 'div'], True, True),
            (['foo1', 'bar', 'dum1', 'div'], True, True),
            ('pass', False, True),
            (['foo', 'must', 'div'], True, False),
            (['foo1', 'must', 'div'], True, True),
            (['foo', 'must1', 'div'], True, True),
            (['foo1', 'must1', 'div'], True, True),
            ('pass', False, True),
            (['qalandar', 'div'], True, False),
            (['qalandar1', 'div'], True, True),
            ('pass', False, True),
        ]
        first = tokenize_selectors_and_properties(_in(first), self.indent)
        first = list(combine_selectors(_out(first, 2)))
        self.assertEquals(first, second)

    def test_make_statements_list(self):
        first = [
            (['.last', '_menu'], True, True),
            ('pass', False, True),
            (['.last', '_menu', '-item'], True, False),
            (('float', 'left'), False, True),
            (['.last', '_menu', '-item', '_selected'], True, False),
            (('color', 'green'), False, True),
            (('background', 'black'), False, False),
            (['.last', '_menu', '-item', '_selected', '_modified'], True, False),
            (('margin', '0'), False, True),
            (['.last', '_menu', '-item', '_selected', '_modified', ':hover'], True, False),
            (['.last', '_menu', '-item', '_selected', '_modified', ':active'], True, True),
            ('pass', False, True),
            (['.last', '_menu', '-item', '_last'], True, False),
            ('pass', False, True),
            (['.last', '_menu'], True, False),
            ('pass', False, True),
        ]
        second = [
            ([['.last', '_menu']], []),
            ([['.last', '_menu', '-item']], [('float', 'left')]),
            ([['.last', '_menu', '-item', '_selected']], [('color', 'green'), ('background', 'black')]),
            ([['.last', '_menu', '-item', '_selected', '_modified']], [('margin', '0')]),
            ([['.last', '_menu', '-item', '_selected', '_modified', ':hover'],
              ['.last', '_menu', '-item', '_selected', '_modified', ':active']], []),
            ([['.last', '_menu', '-item', '_last']], []),
            ([['.last', '_menu']], []),
        ]
        first = list(make_statements_list(first))
        self.assertEqual(first, second)

    def test_make_statements_list1(self):
        first = '''
        .header
        .footer
          a
            .left
            .right
              pass
            .banner
              div
                pass
          :hover
          :active
            div
              pass
        @import print
          .header
          .footer
            div
              pass
        '''
        second = [
            ([['.header', 'a', '.left'],
              ['.footer', 'a', '.left'],
              ['.header', 'a', '.right'],
              ['.footer', 'a', '.right']],
                []),
            ([['.header', 'a', '.banner', 'div'],
              ['.footer', 'a', '.banner', 'div']],
                []),
            ([['.header', ':hover', 'div'],
              ['.footer', ':hover', 'div'],
              ['.header', ':active', 'div'],
              ['.footer', ':active', 'div']],
                []),
            ([['@import print', '.header', 'div'],
              ['@import print', '.footer', 'div']],
                []),
        ]
        first = tokenize_selectors_and_properties(_in(first), self.indent)
        first = combine_selectors(_out(first, 2))
        first = list(make_statements_list(first))
        self.assertEqual(first, second)

    def test_inherit_statements(self):
        first = [
            ([['.menu']], [('a', 1)]),
            ([['.menu', '-item']], [('b', 1)]),
            ([['.menu', '-item', '_selected']], [('c', 1)]),
            ([['.menu', '-item', '_selected', ':active'], ['.menu', '-item', '_selected', ':hover']], [('d', 1)]),
            ([['.menu', '-item', '_selected', '_last']], [('e', 1)]),
            ([['.top', '_menu']], [('a1', 1)]),
            ([['.top', '_menu', '-item']], [('b1', 1)]),
            ([['.top', '_menu', '-item', '_selected']], [('c1', 1)]),
            ([['.top', '_menu', '-item', '_selected', ':hover']], [('d1', 1)]),
            ([['.top', '_menu', '-item', '_selected', '_last']], [('e1', 1)]),
            ([['.detail', '_top', '_menu']], [('a', 3)]),
            ([['.detail', '_top', '_menu', '-item']], [('a', 4)]),
            ([['.detail', '_top', '_menu', '-item', '_selected']], []),
            ([['.detail', '_top', '_menu', '-item', '_selected', ':active']], [('d', 3)]),
            ([['.detail', '_top', '_menu', '-item', '_selected', '_last']], [('e', 3)]),
        ]
        second = [
            ([['.menu']], [('a', 1)]),
            ([['.menu', '-item']], [('b', 1)]),
            ([['.menu', '-item', '_selected']], [('b', 1), ('c', 1)]),
            ([['.menu', '-item', '_selected', ':active'], ['.menu', '-item', '_selected', ':hover']], [('d', 1)]),
            ([['.menu', '-item', '_selected', '_last']], [('b', 1), ('c', 1), ('e', 1)]),
            ([['.top', '_menu']], [('a', 1), ('a1', 1)]),
            ([['.top', '_menu', '-item']], [('b', 1), ('b1', 1)]),
            ([['.top', '_menu', '-item', '_selected']], [('c', 1), ('b', 1), ('b1', 1), ('c1', 1)]),
            ([['.top', '_menu', '-item', '_selected', ':hover']], [('d', 1), ('d1', 1)]),
            ([['.top', '_menu', '-item', '_selected', '_last']],
             [('e', 1), ('c', 1), ('b', 1), ('b1', 1), ('c1', 1), ('e1', 1)]),
            ([['.detail', '_top', '_menu']], [('a1', 1), ('a', 3)]),
            ([['.detail', '_top', '_menu', '-item']], [('b', 1), ('b1', 1), ('a', 4)]),
            ([['.detail', '_top', '_menu', '-item', '_selected']], [('c', 1), ('c1', 1), ('b', 1), ('b1', 1), ('a', 4)]),
            ([['.detail', '_top', '_menu', '-item', '_selected', ':active']], [('d', 3)]),
            ([['.detail', '_top', '_menu', '-item', '_selected', '_last']],
             [('e1', 1), ('c', 1), ('c1', 1), ('b', 1), ('b1', 1), ('a', 4), ('e', 3)]),
        ]
        temp = list(inherit_statements(first, True, False))
        self.assertEqual(temp, second)
        second = [
            ([['.menu'],
              ['.top', '_menu'],
              ['.detail', '_top', '_menu']], [('a', 1)]),
            ([['.menu', '-item'],
              ['.menu', '-item', '_selected'],
              ['.top', '_menu', '-item'],
              ['.detail', '_top', '_menu', '-item']], [('b', 1)]),
            ([['.menu', '-item', '_selected'],
              ['.menu', '-item', '_selected', '_last'],
              ['.top', '_menu', '-item', '_selected'],
              ['.detail', '_top', '_menu', '-item', '_selected']], [('c', 1)]),
            ([['.menu', '-item', '_selected', ':active'],
              ['.menu', '-item', '_selected', ':hover'],
              ['.top', '_menu', '-item', '_selected', ':hover'],
              ['.detail', '_top', '_menu', '-item', '_selected', ':active']], [('d', 1)]),
            ([['.menu', '-item', '_selected', '_last'],
              ['.top', '_menu', '-item', '_selected', '_last'],
              ['.detail', '_top', '_menu', '-item', '_selected', '_last']], [('e', 1)]),
            ([['.top', '_menu'],
              ['.detail', '_top', '_menu']], [('a1', 1)]),
            ([['.top', '_menu', '-item'],
              ['.top', '_menu', '-item', '_selected'],
              ['.detail', '_top', '_menu', '-item']], [('b1', 1)]),
            ([['.top', '_menu', '-item', '_selected'],
              ['.top', '_menu', '-item', '_selected', '_last'],
              ['.detail', '_top', '_menu', '-item', '_selected']], [('c1', 1)]),
            ([['.top', '_menu', '-item', '_selected', ':hover']], [('d1', 1)]),
            ([['.top', '_menu', '-item', '_selected', '_last'],
              ['.detail', '_top', '_menu', '-item', '_selected', '_last']], [('e1', 1)]),
            ([['.detail', '_top', '_menu']], [('a', 3)]),
            ([['.detail', '_top', '_menu', '-item'],
              ['.detail', '_top', '_menu', '-item', '_selected']], [('a', 4)]),
            ([['.detail', '_top', '_menu', '-item', '_selected'],
              ['.detail', '_top', '_menu', '-item', '_selected', '_last']], []),
            ([['.detail', '_top', '_menu', '-item', '_selected', ':active']], [('d', 3)]),
            ([['.detail', '_top', '_menu', '-item', '_selected', '_last']], [('e', 3)]),
        ]
        temp = list(inherit_statements(first, True, True))
        self.assertEqual(temp, second)

    def test_make_css_from_statements(self):
        first = [
            ([], ['.menu'], [('a', 1)]),
            ([], ['.menu-item'], [('b', 1)]),
            ([], ['.menu-item_selected'], [('c', 1)]),
            ([], ['.menu-item_selected:active', '.menu-item_selected:hover'], [('d', 1)]),
            (['@media print'], ['.menu-item_selected_last'], [('e', 1)]),
        ]
        second = '''
        .menu{a:1;}
        .menu-item{b:1;}
        .menu-item_selected{c:1;}
        .menu-item_selected:active,.menu-item_selected:hover{d:1;}
        @media print{
        .menu-item_selected_last{e:1;}
        }
        '''
        temp = make_css_from_statements(first, compressed=True, empty_selectors=True, indent='    ')
        self.assertEqual(_plain(temp), second)
        second = '''
        .menu {
          a: 1;
        }
        .menu-item {
          b: 1;
        }
        .menu-item_selected {
          c: 1;
        }
        .menu-item_selected:active,
        .menu-item_selected:hover {
          d: 1;
        }
        @media print {
          .menu-item_selected_last {
            e: 1;
          }
        }
        '''
        temp = make_css_from_statements(first, compressed=False, empty_selectors=True, indent='  ')
        self.assertEqual(_plain(temp), second)

    def test_make_css_from_statements_show_empty_selectors(self):
        first = [
            ([], ['.empty'], []),
            (['@media print'], [], []),
        ]
        second = '''
        .empty{}
        @media print{
        }
        '''
        temp = make_css_from_statements(first, compressed=True, empty_selectors=True, indent='  ')
        self.assertEqual(_plain(temp), second)
        second = '''
        .empty {
        \n        }
        @media print {
        }
        '''
        temp = make_css_from_statements(first, compressed=False, empty_selectors=True, indent='  ')
        self.assertEqual(_plain(temp), second)

    def test_make_css_from_statements_hide_empty_selectors(self):
        first = [
            ([], ['.empty'], []),
            (['@media print'], [], []),
        ]
        second = '''\n'''
        temp = make_css_from_statements(first, compressed=True, empty_selectors=False, indent='  ')
        self.assertEqual(_plain(temp), second)
        second = '''\n'''
        temp = make_css_from_statements(first, compressed=False, empty_selectors=False, indent='  ')
        self.assertEqual(_plain(temp), second)


if __name__ == '__main__':
    unittest.main(verbosity=2)
