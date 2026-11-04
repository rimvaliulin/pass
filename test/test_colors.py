from __future__ import absolute_import
import unittest
from Pass.colors import Color
from Pass.units import Pr


class TestColors(unittest.TestCase):

    def test_hex_formatting(self):
        self.assertEqual(str(Color('f00')), '#f00')
        self.assertEqual(str(Color('ff0000')), '#f00')
        self.assertEqual(str(Color('123456')), '#123456')

    def test_rgb(self):
        red = Color(255, 0, 0)
        self.assertEqual(red.r, Color('f00').r)
        self.assertEqual(red.g, Color('f00').g)
        self.assertEqual(red.b, Color('f00').b)
        self.assertEqual(Color(Pr(100), Pr(0), Pr(0)).r, red.r)

    def test_hsl(self):
        color = Color('000000')
        color.from_hsl(120, Pr(100), Pr(50))
        self.assertEqual(color.h, 120)
        self.assertEqual(color.s, 1)
        self.assertEqual(color.l, 0.5)
        self.assertEqual(str(color), '#0f0')


if __name__ == '__main__':
    unittest.main(verbosity=2)
