# encoding: utf-8
from __future__ import unicode_literals, division

import re
from Pass.units import Pr


class ColorComponent(object):

    __slots__ = ('max_value', '_value', 'value')

    def __init__(self, value, max_value):
        self.max_value = max_value
        self._value = self.convert(value)

    def convert(self, value):
        if isinstance(value, ColorComponent):
            value = value._value
        elif isinstance(value, Pr):
            value = self.max_value*value.value/100.
        if not 0 <= value <= self.max_value:
            raise ValueError('Value %s must be in range 0..%s' % (value, self.max_value))
        return value

    @property
    def value(self):
        return self._value/self.max_value

    @value.setter
    def value(self, value):
        if not 0 <= value <= 1:
            raise ValueError('Value %s must be in range 0..1' % value)
        self._value = self.max_value*value

    def __add__(self, other):
        return ColorComponent(self._value + self.convert(other), self.max_value)

    def __sub__(self, other):
        return ColorComponent(self._value - self.convert(other), self.max_value)

    def __mul__(self, other):
        return ColorComponent(self._value * self.convert(other), self.max_value)

    def __truediv__(self, other):
        return ColorComponent(self._value / self.convert(other), self.max_value)

    def __rshift__(self, other):
        return int(self._value) >> other

    def __lshift__(self, other):
        return int(self._value) << other

    def __int__(self):
        return int(self._value)

    def __float__(self):
        return float(self._value)

    def __str__(self):
        return str(self._value)

    def __eq__(self, other):
        return self._value == self.convert(other)

    def __gt__(self, other):
        return self._value > self.convert(other)

    def __lt__(self, other):
        return self._value < self.convert(other)

    def __ge__(self, other):
        return self._value >= self.convert(other)

    def __le__(self, other):
        return self._value <= self.convert(other)


class InitColorDescriptors(type):

    def __new__(mcs, name, bases, attrs):
        for attr, instance in attrs.items():
            if isinstance(instance, (RgbDescriptor, HslDescriptor)):
                setattr(instance, 'name', '_' + attr)
        return super(InitColorDescriptors, mcs).__new__(mcs, name, bases, attrs)


class ColorDescriptor(object):

    __slots__ = ('name', 'max_value')

    def __init__(self, max_value):
        self.name = None
        self.max_value = max_value

    def __set__(self, instance, value):
        if isinstance(value, ColorComponent):
            value = value._value
        elif isinstance(value, Pr):
            value = self.max_value*value.value/100.
        try:
            getattr(instance, self.name).value = value
        except AttributeError:
            setattr(instance, self.name, ColorComponent(value, self.max_value))


class RgbDescriptor(ColorDescriptor):

    def __get__(self, instance, owner):
        if getattr(instance, 'hsl_changed', False):
            instance.hsl_to_rgb()
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        instance.rgb_changed = True
        super(RgbDescriptor, self).__set__(instance, value)


class HslDescriptor(ColorDescriptor):

    def __get__(self, instance, owner):
        if getattr(instance, 'rgb_changed', False):
            instance.rgb_to_hsl()
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        instance.hsl_changed = True
        super(HslDescriptor, self).__set__(instance, value)


class Color(object):
    __metaclass__ = InitColorDescriptors

    r, g, b = RgbDescriptor(255), RgbDescriptor(255), RgbDescriptor(255)
    h, s, l = HslDescriptor(360), HslDescriptor(1), HslDescriptor(1)

    __slots__ = ('r', 'g', 'b', '_r', '_g', '_b', 'rgb_changed',
                 'h', 's', 'l', '_h', '_s', '_l', 'hsl_changed', 'a')

    def __init__(self, *args):
        if len(args) == 1:
            try:
                self.from_hex(*args)
            except TypeError:
                self.from_color(*args)
        elif 3 <= len(args) <= 4:
            self.from_rgb(*args)
        else:
            raise TypeError

    def from_color(self, color):
        self.r, self.g, self.b = color.r, color.g, color.b
        if getattr(color, 'a', False):
            self.a = color.a

    def from_hex(self, hex_string):
        v = int('0x' + hex_string, 16)
        if len(hex_string) == 3:
            r, g, b = v >> 8, (v >> 4) - (v >> 8 << 4), v - (v >> 4 << 4)
            self.r, self.g, self.b = (r << 4) + r, (g << 4) + g, (b << 4) + b
        else:
            self.r, self.g, self.b = v >> 16, (v >> 8) - (v >> 16 << 8), v - (v >> 8 << 8)

    def from_rgb(self, r, g, b, a=None):
        self.r, self.g, self.b = r, g, b
        if a is not None:
            self.a = a

    def from_hsl(self, h, s, l, a=None):
        self.h, self.s, self.l = h, s, l
        if a is not None:
            self.a = a

    def rgb_to_hsl(self):
        r, g, b = self._r.value, self._g.value, self._b.value
        _max = max(r, g, b)
        _min = min(r, g, b)
        l = (_max + _min) / 2
        if _max == _min:
            h = s = 0  # achromatic
        else:
            d = _max - _min
            s = d/(2 - _max - _min) if l > 0.5 else d/(_max + _min)
            h = None
            if r == _max:
                h = (g - b)/d + (6 if g < b else 0)
            elif g == _max:
                h = (b - r)/d + 2
            elif b == _max:
                h = (r - g)/d + 4
            h /= 6
        self.rgb_changed = False
        try:
            self._h.value, self._s.value, self._l.value = h, s, l
        except AttributeError:
            self.h, self.s, self.l = 0, 0, 0
            self._h.value, self._s.value, self._l.value = h, s, l

    def hsl_to_rgb(self):
        h, s, l = self._h.value, self._s.value, self._l.value
        m2 = l*(s + 1) if l <= 0.5 else l + s - l*s
        m1 = l*2 - m2
        r = self.hue_to_rgb(m1, m2, h + 0.3333333333333333)
        g = self.hue_to_rgb(m1, m2, h)
        b = self.hue_to_rgb(m1, m2, h - 0.3333333333333333)
        self.hsl_changed = False
        try:
            self._r.value, self._g.value, self._b.value = r, g, b
        except AttributeError:
            self.r, self.g, self.b = 0, 0, 0
            self._r.value, self._g.value, self._b.value = r, g, b

    def hue_to_rgb(self, m1, m2, h):
        if h < 0:
            h += 1
        elif h > 1:
            h -= 1
        if h < 0.16666666666666666:
            v = m1 + (m2 - m1)*h*6
        elif h < 0.5:
            v = m2
        elif h < 0.6666666666666666:
            v = m1 + (m2 - m1)*(0.6666666666666666 - h)*6
        else:
            v = m1
        return v

    def __str__(self):
        return self.to_hex()

    def to_hex(self):
        r, g, b = self.r, self.g, self.b
        if all(map(lambda x: (x >> 4) == (x - (x >> 4 << 4)), (r, g, b))):
            return '#%x%x%x' % (r >> 4, g >> 4, b >> 4)
        return '#%02x%02x%02x' % (r, g, b)

    def to_rgb(self):
        r, g, b = self.r, self.g, self.b
        try:
            return 'rgba(%s, %s, %s, %s)' % (r, g, b, self.a)
        except AttributeError:
            return 'rgb(%s, %s, %s)' % (r, g, b)

    def to_hsl(self):
        h, s, l = self.h, self.s, self.l
        try:
            return 'hsla(%s, %s, %s, %s)' % (h, s, l, self.a)
        except AttributeError:
            return 'hsl(%s, %s, %s)' % (h, s, l)


p = re.compile(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})')


def color_pattern(string):
    return p.sub('Color("\\1")', string)

if __name__ == '__main__':
    a = Color('ff9c00')
    #a.l = 0.4
    print a.to_rgb()
    print a
    print '#%02x%02x%02x' % (123, 123, 0)
    #print a.__dict__