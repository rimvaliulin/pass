"""CSS color model: RGB/HSL conversion, descriptors and the ``Color`` class."""

import re
from .units import Pr


class ColorComponent(object):
    """A single color channel value bounded by ``max_value``.

    Supports arithmetic (the result is clamped back into a component)
    and comparison against other components or plain numbers.
    """

    __slots__ = ('max_value', '_value')

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
    """Metaclass that names the ``_r``/``_h``-style storage slots of each descriptor."""

    def __new__(mcs, name, bases, attrs):
        for attr, instance in attrs.items():
            if isinstance(instance, (RgbDescriptor, HslDescriptor)):
                setattr(instance, 'name', '_' + attr)
        return super(InitColorDescriptors, mcs).__new__(mcs, name, bases, attrs)


class ColorDescriptor(object):
    """Descriptor that stores a color channel as a :class:`ColorComponent` on the instance.

    ``name`` (the private storage slot, e.g. ``_r``) is assigned by
    the :class:`InitColorDescriptors` metaclass.
    """

    __slots__ = ('name', 'max_value')

    # assigned by the InitColorDescriptors metaclass
    name: str

    def __init__(self, max_value):
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
    """Descriptor for an RGB channel; converts HSL to RGB on read when HSL was changed last."""

    def __get__(self, instance, owner):
        if getattr(instance, 'hsl_changed', False):
            instance.hsl_to_rgb()
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        instance.rgb_changed = True
        super(RgbDescriptor, self).__set__(instance, value)


class HslDescriptor(ColorDescriptor):
    """Descriptor for an HSL channel; converts RGB to HSL on read when RGB was changed last."""

    def __get__(self, instance, owner):
        if getattr(instance, 'rgb_changed', False):
            instance.rgb_to_hsl()
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        instance.hsl_changed = True
        super(HslDescriptor, self).__set__(instance, value)


class Color(object, metaclass=InitColorDescriptors):
    """A color with lazily synchronized RGB and HSL representations.

    Created from a hex string (``Color('ff9c00')``), another color,
    or up to four channel values (``Color(255, 156, 0)``).
    Channels are exposed as ``r``, ``g``, ``b`` (0..255) and
    ``h`` (0..360), ``s``, ``l`` (0..1) descriptors.
    """

    r, g, b = RgbDescriptor(255), RgbDescriptor(255), RgbDescriptor(255)
    h, s, l = HslDescriptor(360), HslDescriptor(1), HslDescriptor(1)

    __slots__ = ('_r', '_g', '_b', 'rgb_changed',
                 '_h', '_s', '_l', 'hsl_changed', 'a')

    def __init__(self, *args):
        """Initialize from a hex string, another color, or RGB(A) channel values."""
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
        """Copy the RGB channels (and alpha, if present) from another color."""
        self.r, self.g, self.b = color.r, color.g, color.b
        if getattr(color, 'a', False):
            self.a = color.a

    def from_hex(self, hex_string):
        """Initialize the RGB channels from a 3- or 6-digit hex string like ``'f00'``."""
        v = int('0x' + hex_string, 16)
        if len(hex_string) == 3:
            r, g, b = v >> 8, (v >> 4) - (v >> 8 << 4), v - (v >> 4 << 4)
            self.r, self.g, self.b = (r << 4) + r, (g << 4) + g, (b << 4) + b
        else:
            self.r, self.g, self.b = v >> 16, (v >> 8) - (v >> 16 << 8), v - (v >> 8 << 8)

    def from_rgb(self, r, g, b, a=None):
        """Initialize from RGB channels (0..255 or :class:`Pr` percentages) and optional alpha."""
        self.r, self.g, self.b = r, g, b
        self.hsl_changed = False
        if a is not None:
            self.a = a

    def from_hsl(self, h, s, l, a=None):
        """Initialize from HSL channels (h 0..360, s/l 0..1 or :class:`Pr` percentages) and optional alpha."""
        self.h, self.s, self.l = h, s, l
        self.rgb_changed = False
        if a is not None:
            self.a = a

    def rgb_to_hsl(self):
        """Recompute the HSL channels from the current RGB values."""
        r, g, b = self._r.value, self._g.value, self._b.value
        _max = max(r, g, b)
        _min = min(r, g, b)
        l = (_max + _min) / 2
        if _max == _min:
            h = s = 0  # achromatic
        else:
            d = _max - _min
            s = d/(2 - _max - _min) if l > 0.5 else d/(_max + _min)
            if r == _max:
                h = (g - b)/d + (6 if g < b else 0)
            elif g == _max:
                h = (b - r)/d + 2
            else:
                h = (r - g)/d + 4
            h /= 6
        self.rgb_changed = False
        try:
            self._h.value, self._s.value, self._l.value = h, s, l
        except AttributeError:
            self.h, self.s, self.l = 0, 0, 0
            self._h.value, self._s.value, self._l.value = h, s, l

    def hsl_to_rgb(self):
        """Recompute the RGB channels from the current HSL values."""
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
        """Convert a single hue sector into an RGB channel value."""
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
        """Return the color as a hex string, shortened to 3 digits when possible."""
        r, g, b = int(self.r), int(self.g), int(self.b)
        if all(map(lambda x: (x >> 4) == (x - (x >> 4 << 4)), (r, g, b))):
            return '#%x%x%x' % (r >> 4, g >> 4, b >> 4)
        return '#%02x%02x%02x' % (r, g, b)

    def to_rgb(self):
        """Return the color as an ``rgb()`` or ``rgba()`` CSS function string."""
        r, g, b = self.r, self.g, self.b
        try:
            return 'rgba(%s, %s, %s, %s)' % (r, g, b, self.a)
        except AttributeError:
            return 'rgb(%s, %s, %s)' % (r, g, b)

    def to_hsl(self):
        """Return the color as an ``hsl()`` or ``hsla()`` CSS function string."""
        h, s, l = self.h, self.s, self.l
        try:
            return 'hsla(%s, %s, %s, %s)' % (h, s, l, self.a)
        except AttributeError:
            return 'hsl(%s, %s, %s)' % (h, s, l)


p = re.compile(r'#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})')


def color_pattern(string):
    """Replace ``#abc``/``#aabbcc`` hex colors with ``Color("...")`` constructor calls."""
    return p.sub('Color("\\1")', string)

if __name__ == '__main__':
    a = Color('ff9c00')
    #a.l = 0.4
    print(a.to_rgb())
    print(a)
    print('#%02x%02x%02x' % (123, 123, 0))
    #print a.__dict__