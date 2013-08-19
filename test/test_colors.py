from __future__ import absolute_import
import unittest
from Pass.units import Pr
from Pass.colors import Rgb, Hex, Rgba, Hsl, Hsla


class TestUnits(unittest.TestCase):

    def test_colors_formating(self):
        self.assertEqual('#f00', "rgb_(0xf00)")
        self.assertEqual('#ff0000', "rgb_(0xff0000)")
        self.assertEqual('Rgb(255, 0, 0)', 'Rgb(255, 0, 0)')
        self.assertEqual('Rgb(100%, 0%, 0%)', 'Rgb(Pr(100), Pr(0), Pr(0))')

    def test_rgb(self):
        self.assertEqual(Hex('#f00'), Hex('#ff0000'))
        self.assertEqual(Hex('#ff0000'), Rgb(255, 0, 0))
        self.assertEqual(Rgb(255, 0, 0), Rgb(Pr(100), Pr(0), Pr(0)))
        self.assertEqual(Rgb(Pr(100), Pr(0), Pr(0)), Hex('#f00'))
        self.assertEqual(Rgb(255, 0, 0), Rgba(255, 0, 0, 1))
        self.assertEqual(Rgb(Pr(100), Pr(0), Pr(0)), Rgba(255, 0, 0, 1))

    def test_hls(self):
        self.assertEqual(Hsl(120, Pr(100), Pr(50)), Hsla(120, Pr(100), Pr(50), 1))