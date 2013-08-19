from __future__ import absolute_import
import unittest
from Pass.units import Em, Ex, Pr, Mm, Cm, In, Pt, Pc, Px, unit_pattern


class TestUnits(unittest.TestCase):

    def test_units_string_formating(self):
        self.assertEqual(unit_pattern('1px'), 'Px(1)')
        self.assertEqual(unit_pattern('1%'), 'Pr(1)')
        self.assertEqual(unit_pattern('1.Px'), 'Px(1.)')
        self.assertEqual(unit_pattern('1.1px'), 'Px(1.1)')
        self.assertEqual(unit_pattern('.1px'), 'Px(.1)')
        self.assertEqual(unit_pattern('0.1px'), 'Px(0.1)')

    def test_units_conversion_fails(self):
        self.assertRaises(ValueError, Em, Px(1))

    def test_absolute_units_conversion(self):
        self.assertEqual(Cm(In(1)), 2.54)
        self.assertEqual(Cm(Mm(10)), 1)
        self.assertEqual(Mm(Cm(1)), 10)
        self.assertEqual(Pt(Pc(1)), 12)
        self.assertEqual(Pt(Px(1)), .75)

    def test_absolute_units_equality(self):
        self.assertEqual(Cm(1), Mm(10))
        self.assertEqual(Cm(2.54), In(1))
        self.assertEqual(Pt(1), In(1 / 72.))
        self.assertEqual(Pc(1), Pt(12))
        self.assertEqual(Px(1), Pt(0.75))
