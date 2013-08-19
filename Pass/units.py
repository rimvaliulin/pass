# encoding: utf-8
from __future__ import unicode_literals, division

import re
import functools
from operator import mul, div, add, sub

relative = ['em', 'ex', '%']
absolute = ['mm', 'cm', 'in', 'pt', 'pc', 'px']

p = re.compile(r'([\d.]+)(' + '|'.join(relative + absolute) + ')')


def unit_replace(match):
    unit_name = match.group(2).replace('%', 'pr')
    return unit_name.title() + '(' + match.group(1) + ')'


def unit_pattern(string):
    return p.sub(unit_replace, string)


class Unit(object):

    __slots__ = ('type', 'value')

    def __init__(self, value):
        self.type = self.__class__.__name__.replace('Pr', '%').lower()
        self.value = self.convert(value)

    def convert(self, value):
        try:
            if self.type == value.type:
                return value.value
            elif self.type in relative and value.type in absolute:
                raise ValueError('can\'t convert relative types to absolute')
            elif value.type in absolute and value.type in relative:
                raise ValueError('can\'t convert absolute types to relative')
            elif self.type in relative and value.type in relative:
                if self.type != value.type:
                    raise ValueError("conversion not supported in relative types")
                return value.value
            elif self.type in absolute and value.type in absolute:
                value = value.value
                for _type, op in ((self.type, div), (value.type, mul)):
                    if _type == 'mm':
                        value = op(value, 720 / 254.)
                    elif _type == 'cm':
                        value = op(value, 7200 / 254.)
                    elif _type == 'in':
                        value = op(value, 72.)
                    elif _type == 'pc':
                        value = op(value, 12.)
                    elif _type == 'px':
                        value = op(value, 0.75)
                return value
            else:
                raise TypeError("Undefined type")
        except AttributeError:
            if self.type == '%':
                if not 0 <= value <= 100:
                    raise ValueError('percent type must be in 0..100')
            return value

    def percent(self, other, operator):
        if self.type != "%":
            raise ValueError("left operand must be unit type")
        return operator(other, other*self.value)

    def __lt__(self, other):
        return self.value < self.convert(other)

    def __le__(self, other):
        return self.value <= self.convert(other)

    def __eq__(self, other):
        return self.value == self.convert(other)

    def __ne__(self, other):
        return self.value != self.convert(other)

    def __gt__(self, other):
        return self.value > self.convert(other)

    def __ge__(self, other):
        return self.value >= self.convert(other)

    def __int__(self):
        return int(self.value)

    def __long__(self):
        return long(self.value)

    def __float__(self):
        return float(self.value)

    def __add__(self, other):
        return self.__class__(self.value + self.convert(other))

    def __sub__(self, other):
        return self.__class__(self.value - self.convert(other))

    def __mul__(self, other):
        return self.__class__(self.value*self.convert(other))

    def __div__(self, other):
        return self.__class__(self.value/self.convert(other))

    def __radd__(self, other):
        return self.percent(other, add)

    def __rsub__(self, other):
        return self.percent(other, sub)

    def __rmul__(self, other):
        return self.percent(other, lambda x, y: y)

    def __rdiv__(self, other):
        return self.percent(other, lambda x, y: x - y)

    def __iadd__(self, other):
        return self.__add__(other)

    def __isub__(self, other):
        return self.__sub__(other)

    def __imul__(self, other):
        return self.__mul__(other)

    def __idiv__(self, other):
        return self.__div__(other)

    def __neg__(self):
        return self.__class__(-self.value)

    def __pos__(self):
        return self.__class__(+self.value)

    def __abs__(self):
        return abs(self.value)

    def __oct__(self):
        return oct(self.value)

    def __hex__(self):
        return hex(self.value)[2:]

    def __str__(self):
        value = str(self.value)
        if value[-2:] == '.0':
            value = value[:-2]
        return value + self.type

    def __repr__(self):
        return "'" + self.type + '(' + self.value + ')' + "'"


class Em(Unit):
    pass


class Ex(Unit):
    pass


class Pr(Unit):
    pass


class Mm(Unit):
    pass


class Cm(Unit):
    pass


class In(Unit):
    pass


class Pt(Unit):
    pass


class Pc(Unit):
    pass


class Px(Unit):
    pass


def unitdispatcher(func):
    @functools.wraps(func)
    def wrapper(*args):
        try:
            if func in ('min_', 'max_'):
                temp = [arg.value for arg in args]
                value = func(*temp)
                index = temp.index(value)
                args[index].value = value
                return args[index]
            else:
                args[0].value = func(args[0].value, *args[1:])
                return args[0]
        except AttributeError:
            return func(*args)
    return wrapper


if __name__ == "__main__":
    print Px(980) - Px(630)