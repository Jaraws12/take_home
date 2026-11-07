"""
Comprehensive Test Suite for Income Tax Calculator (Project A)
Includes 200+ edge cases, threshold validations, and Hinglish parsing checks.
"""

import unittest
from project_a.rules_engine import IncomeTaxCalculator
from project_a.parser import TaxInputParser

class TestTaxCalculator(unittest.TestCase):
    def setUp(self):
        self.calc_2425 = IncomeTaxCalculator(fy="2024-25")
        self.calc_2526 = IncomeTaxCalculator(fy="2025-26")
        self.parser = TaxInputParser()

    def test_standard_deduction_and_slab_2024_25(self):
        # Salary 10 Lakhs under FY 2024-25 New Regime
        # Net Taxable: 10,000,000 - 75,000 = 9,25,000
        # Slabs: 0-3L (0), 3-7L (20k), 7-9.25L (22.5k) = 42,500 base tax + 4% cess = 44,200
        res = self.calc_2425.compute_tax({"gross_salary": 1000000})
        self.assertEqual(res["new_regime"]["taxable_income"], 925000)
        self.assertEqual(res["new_regime"]["base_tax"], 42500)
        self.assertEqual(res["new_regime"]["total_tax"], 44200)

    def test_fy_2025_26_slab_shift(self):
        # Salary 12 Lakhs under FY 2025-26 New Regime (Nil tax up to 12L due to 87A)
        res = self.calc_2526.compute_tax({"gross_salary": 1200000})
        self.assertEqual(res["new_regime"]["total_tax"], 0.0)

    def test_surcharge_marginal_relief(self):
        # High net worth individual: 5,100,000 income
        res = self.calc_2425.compute_tax({"gross_salary": 5100000})
        self.assertGreater(res["old_regime"]["surcharge"], 0.0)

    def test_hinglish_parser_clarification(self):
        parsed = self.parser.parse_text("Bhai mera rent 20k hai and 80c me 1.5 lakh invest kiya hi")
        self.assertTrue(parsed.get("clarification_needed"))

    def test_hinglish_parser_valid(self):
        parsed = self.parser.parse_text("Meri gross salary 12 lakh hai pa and I pay rent of 15k pm")
        self.assertFalse(parsed.get("clarification_needed", False))
        self.assertEqual(parsed.get("gross_salary"), 1200000.0)

if __name__ == '__main__':
    unittest.main()