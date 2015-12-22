# encoding: utf-8
from __future__ import unicode_literals, with_statement

import os
import re
import sys
import codecs
from itertools import cycle, chain
from copy import deepcopy

from utils import last, consumer, vendor_prefixed_properties
from units import Em, Pr, Pt, Cm, Mm, Px, Pc, Ex, In, unit_pattern
from colors import color_pattern, Color
from functions import round_, lighten, darken, desaturate, saturate

IMPORT_TOKEN = 2
MEDIA_TOKEN = 3

_globals = {'__builtins__': None}
_reserved = {
    'auto': 'auto', 'none': 'none', 'solid': 'solid', 'dotted': 'dotted',
    'inherit': 'inherit',
    'transparent': 'transparent',
    'abs': abs, 'min': min, 'max': max, 'map': map, 'any': any, 'all': all, 'float': float, 'int': int,
    'round': round_, 'lighten': lighten, 'darken': darken, 'saturate': saturate, 'desaturate': desaturate,
    'Em': Em, 'Pr': Pr, 'Pt': Pt, 'Cm': Cm, 'Mm': Mm, 'Px': Px, 'Pc': Pc, 'Ex': Ex, 'In': In,
    'Color': Color,
}
_locals = deepcopy(_reserved)


@consumer
def null():
    yield
    while True:
        data = yield
        if data is not None:
            yield
            pass


def read_from_file(filename):
    with codecs.open(filename, 'rb+', 'utf-8') as f:
        for n, line in enumerate(f, start=1):
            yield f.name, n, line.rstrip()


def read_from_string(string):
    for n, line in enumerate(string.splitlines(), start=1):
        yield None, n, line.rstrip()


def write_to_file(lines, filename, newlines=True, compressed=True):
    filename, ext = os.path.splitext(filename)
    end_of_line = ('\n' if newlines else '' if compressed else '\n')
    with codecs.open(filename + '.css', 'wb+', 'utf-8') as f:
        for line in lines:
            f.write(line + end_of_line)


def write_to_stdout(lines):
    for line in lines:
        sys.stdout.write(line)


@consumer
def import_pass_file(lines):
    yield
    try:
        while True:
            f, n, line = lines.next()
            data = yield f, n, line
            if data is not None:
                yield f, n, line
                if f != data:
                    lines = chain(read_from_file(data), lines)
    except StopIteration:
        pass


def first_line_update_by_parent(lines, target, *args, **kwargs):
    first = True
    for f, n, line in lines:
        if line[:7] == '@parent':
            if line[7:8] != ' ':
                raise SyntaxError('@parent syntax error', (f, n, None, None))
            if not first:
                continue
            filename = line[8:].strip().strip('"\'')
            if not filename:
                raise SyntaxError('parent file not defined', (f, n, None, None))
            filename, ext = os.path.splitext(filename)
            if ext != '.pass':
                raise IOError('unknown file extension "%s"' % filename, (f, n, None, None))
            filename += ext if ext else '.pass'
            if filename == f:
                raise SyntaxError('parent file is self file', (f, n, None, None))
            path = os.path.join(os.path.dirname(f), filename)
            if not os.path.exists(path):
                raise IOError('file %s not exists' % filename, (f, n, None, None))
            target.send((f, n, line))
            os.remove(os.path.splitext(f)[0] + '.css')
            process_pass(path, *args, **kwargs)
            lines.close()
        else:
            yield f, n, line
        first = False


def ignore_empty_lines(lines, target):
    for f, n, line in lines:
        if line != '' and not line.isspace() or n == 0:
            yield f, n, line
        else:
            target.send((f, n, line))


def ignore_line_comments(lines, target):
    for f, n, line in lines:
        if line.lstrip().startswith('//'):
            target.send((f, n, line))
        else:
            yield f, n, line


def ignore_block_comments(lines, target):
    comment = False
    start = '/*'
    end = '*/'
    iterable = ((True, start, end), (False, end, start))
    for f, n, line in lines:
        if not comment and start in line:
            comment = True
            chunks = ''
            head, tail = line, ''
            for t, a, b in cycle(iterable):
                head, _, tail = head.partition(a)
                if b not in tail:
                    comment = t
                    break
                if t:
                    chunks += head
                head = tail
            line = chunks + (head if comment else tail)
            line = line.rstrip()
            if line:
                yield f, n, line
            target.send((f, n, line))
        elif comment and end in line:
            comment = False
            chunks = ''
            head, tail = line, ''
            for t, a, b in cycle(reversed(iterable)):
                head, _, tail = head.partition(a)
                if b not in tail:
                    comment = t
                    break
                if t:
                    chunks += head
                head = tail
            line = chunks + (head if comment else tail)
            line = line.rstrip()
            if line:
                yield f, n, line
            target.send((f, n, line))
        elif comment:
            target.send((f, n, line))
        else:
            yield f, n, line


def define_variables(lines, target):
    for f, n, line in lines:
        if '=' in line:
            variable, _, value = line.partition('=')
            variable, value = variable.rstrip(), value.lstrip()
            if not variable or not value:
                raise SyntaxError('variable or value not defined', (f, n, None, line))
            elif ',' in variable:
                raise SyntaxError('multiple assignments not allowed', (f, n, None, line))
            elif variable[:1].isspace():
                raise IndentationError('unresolved variable indent', (f, n, None, line))
            elif variable.replace('_', '').isalnum():
                if variable[0].isdigit():
                    raise SyntaxError('variable can\'t start with digit', (f, n, None, line))
                elif variable in _reserved:
                    raise SyntaxError('variable uses reserved word', (f, n, None, line))
                exec_line = variable + ' = ' + color_pattern(unit_pattern(value))
                try:
                    exec exec_line in _globals, _locals
                except (TypeError, SyntaxError, ValueError) as e:
                    raise SyntaxError(e.message + ': %s' % exec_line, (f, n, None, line))
                else:
                    target.send((f, n, line))
            else:
                yield f, n, line
        else:
            yield f, n, line


def tokenize_selectors_and_properties(lines, indent='  '):
    """
    http://www.w3.org/TR/2011/REC-CSS2-20110607/grammar.html
    property token:
    p = re.process(r'^-?(?:[_a-z]|[\240-\377]|\\[0-9a-f]{1,6}(?:\r\n|[ \t\r\n\f])?|\\[^\r\n\f0-9a-f])
    (?:[_a-z0-9-]|[\240-\377]|\\[0-9a-f]{1,6}(?:\r\n|[ \t\r\n\f])?|\\[^\r\n\f0-9a-f])*\s')
    """
    indent_length = len(indent)
    property_pattern = re.compile(r'^-?[_a-z][_a-z0-9-]*\s')
    _level, level = -1, None
    _sel, sel = True, None
    for f, n, line in lines:
        length = len(line) - len(line.lstrip())
        if '\t' in line[:length]:
            _level -= 1
        line = line[length:]
        level = length / indent_length + length % indent_length * indent_length
        behind = level - _level
        if property_pattern.match(line):
            sel = False
            key, _, value = line.partition(' ')
            line = (key, value.lstrip())
        elif line == 'clearfix':
            sel = False
            line = 'clearfix', ''
        elif line == 'pass':
            sel = False
        elif line[:7] == '@import':
            sel = IMPORT_TOKEN
        elif line[:6] == '@media':
            sel = MEDIA_TOKEN
        else:
            sel = True
        yield f, n, line, level, behind, sel, _sel
        _level, _sel = level, sel
    if level is not None:
        yield None, 0, '', 0, -level, True, sel


def check_indentation_errors(lines):
    for f, n, name, level, behind, sel, _sel in lines:
        if n == 0 and (_sel is True or _sel == MEDIA_TOKEN):
            raise IndentationError('expected an indented property 0', (f, n, None, name))
        elif behind > 1:
            raise IndentationError('unindent does not match any outer indentation level', (f, n, None, name))
        elif sel and sel in (IMPORT_TOKEN, MEDIA_TOKEN) and level > 0:
            raise IndentationError('expected %s selector on root level' % name, (f, n, None, name))
        elif sel and _sel and behind < 0:
            raise IndentationError('expected an indented property 1', (f, n, None, name))
        elif sel and not _sel and behind > 0:
            raise IndentationError('expected an indented property 2', (f, n, None, name))
        elif not sel and _sel and (level == 0 or behind <= 0):
            raise IndentationError('expected an indented property 3', (f, n, None, name))
        elif not sel and not _sel and behind != 0:
            raise IndentationError('expected an indented property 4 ', (f, n, None, name))
        yield f, n, name, level, behind, sel, _sel


def check_imports_syntax(lines):
    selector, first = False, True
    for f, n, name, level, behind, sel, _sel in lines:
        if sel == IMPORT_TOKEN:
            if not first and n > 0 and _sel and not selector:
                raise IndentationError('unexpected indented selector 0', (f, n, None, name))
            elif ' ' not in name:
                raise SyntaxError('expected an @import argument', (f, n, None, name))
            selector = True
        elif sel and selector and level > 0:
            raise IndentationError('unexpected indented selector 1', (f, n, None, name))
        elif not sel and selector:
            raise IndentationError('unexpected indented property', (f, n, None, name))
        else:
            selector = False
        yield f, n, name, level, behind, sel, _sel
        first = False


def import_files(lines, target):
    sel_, behind_ = None, None
    for f, n, name, level, behind, sel, _sel in lines:
        if sel == IMPORT_TOKEN:
            temp = []
            for filename in name[7:].lstrip().split():
                filename = filename.strip('"\'')
                _, ext = os.path.splitext(filename)
                full_path = os.path.join(os.path.dirname(f), filename)
                if not ext:
                    filename += '.pass'
                if ext == '.pass':
                    if not os.path.exists(full_path):
                        raise IOError('file %s not exists' % filename, (f, n, None, None))
                    target.send(full_path)
                elif ext == '.css':
                    if not os.path.exists(full_path):
                        raise IOError('file %s not exists' % filename, (f, n, None, None))
                    temp.append(full_path)
                else:
                    raise IOError('unknown file extension "%s"' % filename, (f, n, None, None))
            if temp:
                if _sel == IMPORT_TOKEN:
                    behind, _sel = -1, False
                yield f, n, '@import', 0, behind, True, _sel
                for i, filename in enumerate(temp):
                    yield f, n, ('src' + str(i), filename), 1, 0 if i else 1, False, False if i else True
                _sel, behind = False, -1
            sel_, behind_ = _sel, behind
        elif sel_ is not None:
            yield f, n, name, level, behind_, sel, sel_
            sel_, behind_ = None, None
        else:
            yield f, n, name, level, behind, sel, _sel


def check_media_queries_syntax(lines):
    media, block = False, False
    for f, n, name, level, behind, sel, _sel in lines:
        if sel == MEDIA_TOKEN:
            if not media and _sel and behind == 0:
                raise IndentationError('expected an indented selector 1', (f, n, None, name))
            media = True
        elif sel and media:
            if behind == 0:
                raise IndentationError('expected an indented selector 2', (f, n, None, name))
            media, block = False, True
        elif sel and block and level == 0:
            block = False
        elif not sel and media and name == 'pass':
            media = False
        elif not sel and media:
            raise IndentationError('expected an indented selector', (f, n, None, name))
        yield f, n, name, level, behind, sel, _sel


def filter_properties(lines):
    unique, properties = [], []
    for f, n, name, level, behind, sel, _sel in lines:
        if not sel and name != 'pass':
            prop, expr = name
            try:
                index = unique.index(prop)
            except ValueError:
                pass
            else:
                if index == 0:
                    behind, _sel = properties[index][4], True
                del unique[index], properties[index]
            unique.append(prop)
            properties.append((f, n, name, level, behind, sel, _sel))
        elif sel:
            if not _sel:
                if properties:
                    for prop in properties:
                        yield prop
                else:
                    yield f, n, 'pass', level - behind, 1, False, True
                unique, properties = [], []
            yield f, n, name, level, behind, sel, _sel


def evaluate_properties(lines):
    props = 'width', 'height', 'top', 'left', 'color', 'background-color', 'line-height', 'max-width', 'min-width', 'border-top-color'
    for f, n, name, level, behind, sel, _sel in lines:
        if not sel and name != 'pass':
            prop, expr = name
            if prop.startswith('margin-') or prop.startswith('padding-') or prop in props:
                expr = color_pattern(expr)
                expr = unit_pattern(expr)
                try:
                    expr = str(eval(expr, _globals, _locals))
                except SyntaxError as e:
                    raise SyntaxError(e.msg, (f, n, None, name))
                except (NameError, AttributeError, ValueError) as e:
                    raise SyntaxError(e, (f, n, None, name))
            elif prop in ('margin', 'padding', 'border', 'flex') or prop.startswith('border-'):
                expr = color_pattern(expr)
                expr = unit_pattern(expr)
                for i in range(4):
                    try:
                        expr = ' '.join([str(eval(v, _globals, _locals)) for v in expr.split(None, i)])
                    except (SyntaxError, NameError, ValueError) as e:
                        if i == 3:
                            raise SyntaxError(getattr(e, 'msg', e.message), (f, n, None, name))
                    else:
                        break
            name = prop, expr
        yield f, n, name, level, behind, sel, _sel


def combine_selectors(lines):
    first = True
    stack = []
    selectors = [[]]
    _level, _sel = -1, True
    for f, n, name, level, _, sel, _ in lines:
        behind = level - _level
        if sel and (_sel and behind > 0 or not _sel and behind == 0):
            stack.append(selectors)
            selectors = [s + [name] for s in selectors]
        elif sel and (not _sel and behind < 0 or _sel and behind == 0):
            if not _sel:
                stack = stack[:level + 1]
                selectors = []
            selectors += [s + [name] for s in stack[-1]]
        elif not sel and (_sel and behind > 0 or not _sel and behind == 0):
            if _sel:
                sel_ = first
                for selector in selectors:
                    yield deepcopy(selector), True, sel_
                    sel_ = True
                first = False
            yield name, sel, _sel
        _level, _sel = level, sel


def make_statements_list(lines):
    selectors, declarations = [], []
    for name, sel, _sel in last(lines, (None, True, False)):
        if sel:
            if not _sel and selectors:
                yield selectors, declarations
                selectors, declarations = [], []
            selectors.append(name)
        elif name != 'pass':
            declarations.append(name)


def split_selectors(lines):
    for selectors, declarations in lines:
        _selectors = []
        for selector in selectors:
            chunks = []
            chunks.extend(selector[:1])
            for chunk in selector[1:]:
                if chunk[0] in tuple('.#'):
                    chunks.append(' ' + chunk)
                elif chunk[0] in tuple('_-:'):
                    chunks.append(chunk)
                else:
                    chunks.append(' ' + chunk)
            _selectors.append(chunks)
        yield _selectors, declarations


def inherit_statements(lines, respect_indents=True, inherit_selectors=False):
    """
    # Class naming scheme:
    > block - element
    > child_block _ parent_block - parent_element _ child_element
    It differs from BEM (Block - Element - Modificator), developed by Yandex.
    """
    index = {}
    statements = []
    indent_sep = '/'
    for i, (selectors, declarations) in enumerate(lines):
        parent_selectors = []
        for selector in selectors:
            selector_hash = indent_sep.join(selector)
            block, _, element = selector_hash.partition('-')
            child_block = block
            child_element = element
            while '_' in child_element:
                parent_element, _, child_element = child_element.rpartition('_')
                if child_element.replace('_', '').replace('-', '').isalnum():
                    element_selector = block + '-' + parent_element.rstrip('_') if parent_element else block
                    element_selector = element_selector.rstrip(indent_sep)
                    parent_selectors.append(element_selector)
                    child_element = parent_element
                if not inherit_selectors:
                    break
            while '_' in child_block:
                child_block, _, parent_block = child_block.partition('_')
                prefix = child_block[0]
                parent_block = prefix + parent_block if prefix in ('.', '#') else parent_block
                block_selector = parent_block + '-' + element if element else parent_block
                block_selector = block_selector.lstrip(indent_sep)
                parent_selectors.append(block_selector)
                child_block = parent_block
                if not inherit_selectors:
                    break
            for parent_selector_hash in parent_selectors:
                if not respect_indents:
                    parent_selector_hash = parent_selector_hash.replace(indent_sep, '')
                if parent_selector_hash in index:
                    if inherit_selectors:
                        if parent_selector_hash in index:
                            if selector not in statements[index[parent_selector_hash]][0]:
                                statements[index[parent_selector_hash]][0].append(selector)
                    else:
                        if declarations:
                            keys = zip(*declarations)[0]
                            temp = [i for i in index[parent_selector_hash] if i[0] not in keys]
                            declarations = temp + declarations
                        else:
                            declarations = index[parent_selector_hash]
            if not respect_indents:
                selector_hash = selector_hash.replace(indent_sep, '')
            index[selector_hash] = i if inherit_selectors else declarations
        if inherit_selectors:
            statements.append((selectors, declarations))
        else:
            yield selectors, declarations
    if statements:
        for statement in statements:
            yield statement


def handle_medias(lines):
    for selectors, declarations in lines:
        media, _selectors = [], []
        for selector in selectors:
            if selector[0][:6] == '@media':
                _media = ''.join(selector[:1])
                if _media not in media:
                    media.append(_media)
                _selector = ''.join(selector[1:]).lstrip()
                if _selector not in _selectors:
                    _selectors.append(_selector)
            else:
                _selectors.append(''.join(selector))
        yield media, _selectors, declarations


def add_vendor_prefixes_to_properties(lines):
    for media, selectors, declarations in lines:
        declaration_list = []
        for prop, expression in declarations:
            if prop in vendor_prefixed_properties:
                for prefix in vendor_prefixed_properties[prop].split():
                    declaration_list.append(('-%s-%s' % (prefix, prop), expression))
            declaration_list.append((prop, expression))
        yield media, selectors, declaration_list


def add_clearfix(lines, ie6_7=True):
    for media, selectors, declarations in lines:
        declaration_list = []
        _selectors = []
        for prop, expression in declarations:
            if prop == 'clearfix':
                _selectors = selectors
            else:
                declaration_list.append((prop, expression))
        yield media, selectors, declaration_list
        if _selectors:
            yield media, [selector + ":before" for selector in _selectors], [("content", '" "'), ("display", "table")]
            yield media, [selector + ":after" for selector in _selectors], [("content", '" "'), ("display", "table"), ("clear", "both")]
            if ie6_7:
                yield media, _selectors, [("*zoom", "1")]


def make_css_from_statements(lines, compressed=True, empty_selectors=True, indent='    ', target=None):
    if compressed:
        indent = ''
        try:
            from cssmin import cssmin
        except ImportError:
            def cssmin(css, wrap=None):
                pass
    _media, _indent = [], ''
    for media, selectors, declarations in last(lines, ([], [], [])):
        if media != _media:
            if _media:
                target.send('}')
                yield '}'
                _indent = ''
            if media:
                yield (','.join(media) + '{') if compressed else (', '.join(media) + ' {')
                _indent = indent
        if selectors == ['@import']:
            for _, path in declarations:
                with open(path) as f:
                    content = f.read()
                    if content:
                        yield cssmin(content) if compressed else content
        elif empty_selectors or declarations:
            declarations = [_indent + indent + k + (':' if compressed else ': ') + str(v) + ';' for k, v in declarations]
            if selectors:
                if compressed:
                    line = ','.join(selectors) + '{' + ''.join(declarations) + '}'
                else:
                    line = _indent + (',\n' + _indent).join(selectors)
                    line += ' {\n' + '\n'.join(declarations) + '\n' + _indent + '}'
                if line:
                    yield line
        _media = media


def process_pass(filename, compressed=True, empty_selectors=True, respect_indents=False,
                 inherit_selectors=False, indent='  ', css_indent='    ', newlines=True):
    target = null()
    parents = []
    reader = read_from_file(filename)
    importer = import_pass_file(reader)
    # f, n, line
    lines = first_line_update_by_parent(importer, target, compressed, empty_selectors, respect_indents,
                                        inherit_selectors, indent, css_indent, newlines)
    lines = ignore_empty_lines(lines, target)
    lines = ignore_line_comments(lines, target)
    lines = ignore_block_comments(lines, target)
    lines = define_variables(lines, target)
    lines = tokenize_selectors_and_properties(lines, indent)
    # f, n, name, level, behind, sel, _sel
    lines = check_indentation_errors(lines)
    lines = check_imports_syntax(lines)
    lines = import_files(lines, importer)
    lines = check_media_queries_syntax(lines)
    #lines = filter_properties(lines)
    lines = evaluate_properties(lines)
    ######################
    # Structural changes #
    ######################
    lines = combine_selectors(lines)
    # name, sel, _sel
    lines = make_statements_list(lines)
    # selectors, declarations
    lines = split_selectors(lines)
    lines = inherit_statements(lines, respect_indents, inherit_selectors)
    lines = handle_medias(lines)
    # media, selectors, declaration
    lines = add_vendor_prefixes_to_properties(lines)
    lines = add_clearfix(lines)
    lines = make_css_from_statements(lines, compressed, empty_selectors, css_indent, target)
    write_to_file(lines, filename, newlines, compressed)
