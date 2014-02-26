# encoding: utf-8
from __future__ import unicode_literals, division

import math

from Pass.colors import Color
from Pass.units import Pr, unitdispatcher


########################
# Color initialization #
########################


def rgb(r, g, b):
    """Converts an Rgb(r, g, b) triplet into a color."""
    return Color(r, g, b)


def rgba(r, g, b, a):
    """Converts an Rgba(r, g, b, a) quadruplet into a color."""
    return Color(r, g, b, a)


def hsl(h, s, l):
    """Converts an Hsl(h, s, l) triplet into a color."""
    return Color.from_hsl(h, s, l)


def hsla(h, s, l, a):
    """Converts an Hsla(h, s, l) quadruplet into a color."""
    return Color.from_hsl(h, s, l, a)


############################
# Get/set color components #
############################


def red(color, value=None):
    """Return the red component of the given color."""
    if value is not None:
        color.r = value
    else:
        return color.r


def green(color, value=None):
    """Return the green component of the given color."""
    if value is not None:
        color.g = value
    else:
        return color.g


def blue(color, value=None):
    """Return the blue component of the given color."""
    if value is not None:
        color.b = value
    else:
        return color.b


def hue(color, value=None):
    """Return the hue of the given color."""
    if value is not None:
        color.h = value
    else:
        return color.h


def saturation(color, value=None):
    """Return the saturation of the given color."""
    if value is not None:
        color.s = value
    else:
        return color.s


def lightness(color, value=None):
    """Return the lightness of the given color."""
    if value is not None:
        color.l = value
    else:
        return color.l


def alpha(color, value=None):
    """Return the alpha component of the given color."""
    if value is not None:
        color.a = value
    else:
        return color.a


####################
# Color adjustment #
####################

def spinin(color, value=Pr(10)):
    """Changes the hue of a color."""
    color = Color(color)
    color.h += value
    return color


def spinout(color, value=Pr(10)):
    """Changes the hue of a color."""
    color = Color(color)
    color.h -= value
    return color


def lighten(color, value=Pr(10)):
    """Makes a color lighten."""
    color = Color(color)
    color.l += value
    return color


def darken(color, value=Pr(10)):
    """Makes a color darker."""
    color = Color(color)
    color.l -= value
    return color


def saturate(color, value=Pr(10)):
    """Makes a color more saturated."""
    color = Color(color)
    color.s += value
    return color


def desaturate(color, value=Pr(10)):
    """Makes a color less saturated."""
    color = Color(color)
    color.s -= value
    return color


def fadein(color, value=Pr(10)):
    """Add or change an alpha layer for any color value."""
    color = Color(color)
    color.a += value
    return color


def fadeout(color, value=Pr(10)):
    """Add or change an alpha layer for any color value."""
    color = Color(color)
    color.a -= value
    return color


def grayscale(color):
    """Converts a color to grayscale."""
    color = Color(color)
    color.s = 1
    return color


def complement(color):
    """Returns the complement of a color."""
    color = Color(color)
    return color


def invert(color):
    """Returns the inverse of a color."""
    color = Color(color)
    return color


def mix(color, color1, weight=Pr(50)):
    """Mixes two colors together"""

    p = weight.value/100.0
    w = p * 2 - 1
    a = color.a - color1.a

    w1 = ((w if w * a == -1 else (w + a) / (1 + w * a)) + 1) / 2.0
    w2 = 1 - w1

    r = color.r * w1 + color1.r * w2
    g = color.g * w1 + color1.g * w2
    b = color.b * w1 + color1.b * w2

    a = color.a * p + color1.a * (1 - p)

    return Color(r, g, b, a)


####################
# String Functions #
####################


def quote(s):
    """Removes the quotes from a string."""
    return s.strip('"\'')


def unquote(s):
    """Adds quotes to a string."""
    return '"' + s + '"'


####################
# Number Functions #
####################


def percentage(value):
    """Converts a unitless number to a percentage."""
    return Pr(value)


@unitdispatcher
def round_(value, digits=0):
    """Rounds a number to the nearest whole number."""
    return round(value, digits)


@unitdispatcher
def ceil(value):
    """Rounds a number up to the nearest whole number."""
    return math.ceil(value)


@unitdispatcher
def floor(value):
    """Rounds a number down to the nearest whole number."""
    return math.floor(value)


#def abs(value):
#    """Returns the absolute value of a number."""
#    return abs(value)

#def min(*args):
#    """Finds the minimum of several values."""
#    return min(*args)

#def max(*args):
#    """Finds the maximum of several values."""
#    return max(*args)

##################
# List Functions #
##################

#def len_(list):
#    """Returns the length of a list."""
#    return len(list)

#def nth(list, n):
#    """Returns a specific item in a list."""
#    return list[n]

#def join(list1, list2, separator=None):
#    """Joins together two lists into one."""
#    return

#def append(list1, val, separator=None):
#    """Appends a single value onto the end of a list."""

###########################
# Introspection Functions #
###########################

#def type_of(value):
#    """Returns the type of a value."""

#def unit(number):
#    """Returns the units associated with a number."""

#def unitless(number):
#    """Returns whether a number has units or not."""

#def comparable(number1, number2):
#    """Returns whether two numbers can be added or compared."""

#def url(url):
#    return url