import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elementgate import (
    check_formula, check_reaction, molar_mass, parse_formula,
    VALID_FORMULA, INVALID_FORMULA, BALANCED, UNBALANCED, MALFORMED,
)


class TestParse(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(parse_formula("H2O").counts, {"H": 2, "O": 1})

    def test_co2(self):
        self.assertEqual(parse_formula("CO2").counts, {"C": 1, "O": 2})

    def test_two_letter_element(self):
        self.assertEqual(parse_formula("NaCl").counts, {"Na": 1, "Cl": 1})

    def test_nested_group(self):
        self.assertEqual(parse_formula("Ca(OH)2").counts, {"Ca": 1, "O": 2, "H": 2})

    def test_double_nested(self):
        self.assertEqual(parse_formula("Fe2(SO4)3").counts,
                         {"Fe": 2, "S": 3, "O": 12})

    def test_square_brackets(self):
        self.assertEqual(parse_formula("K4[Fe(CN)6]").counts,
                         {"K": 4, "Fe": 1, "C": 6, "N": 6})

    def test_hydrate_middot(self):
        self.assertEqual(parse_formula("CuSO4·5H2O").counts,
                         {"Cu": 1, "S": 1, "O": 9, "H": 10})

    def test_hydrate_dot(self):
        self.assertEqual(parse_formula("Na2CO3.10H2O").counts,
                         {"Na": 2, "C": 1, "O": 13, "H": 20})

    def test_charge_cation(self):
        p = parse_formula("Fe^3+")
        self.assertEqual(p.charge, 3)
        self.assertEqual(p.counts, {"Fe": 1})

    def test_charge_anion(self):
        p = parse_formula("SO4^2-")
        self.assertEqual(p.charge, -2)
        self.assertEqual(p.counts, {"S": 1, "O": 4})

    def test_charge_implicit_one(self):
        self.assertEqual(parse_formula("OH-").charge, -1)
        self.assertEqual(parse_formula("NH4+").charge, 1)

    def test_unknown_element(self):
        p = parse_formula("Xy2")
        self.assertFalse(p.ok)
        self.assertIn("unknown element", p.error)

    def test_lowercase_start_fails(self):
        self.assertFalse(parse_formula("h2o").ok)

    def test_unbalanced_bracket(self):
        self.assertFalse(parse_formula("Ca(OH2").ok)

    def test_empty(self):
        self.assertFalse(parse_formula("").ok)


class TestMolarMass(unittest.TestCase):
    def test_water(self):
        m, _ = molar_mass("H2O")
        self.assertAlmostEqual(m, 18.015, places=3)

    def test_glucose(self):
        m, _ = molar_mass("C6H12O6")
        self.assertAlmostEqual(m, 180.156, places=2)

    def test_calcium_hydroxide(self):
        m, _ = molar_mass("Ca(OH)2")
        self.assertAlmostEqual(m, 74.092, places=2)

    def test_hydrate_mass(self):
        m, _ = molar_mass("CuSO4·5H2O")
        self.assertAlmostEqual(m, 249.677, places=2)

    def test_breakdown_present(self):
        _, info = molar_mass("CO2")
        self.assertIn("C", info["breakdown"])
        self.assertEqual(info["breakdown"]["O"]["count"], 2)

    def test_invalid_returns_none(self):
        m, info = molar_mass("Zz")
        self.assertIsNone(m)
        self.assertIn("error", info)

    def test_radioactive_flagged(self):
        # Pu has no stable isotope -> most-stable-isotope mass is used + flagged.
        _, info = molar_mass("PuO2")
        self.assertTrue(info["uses_isotope_mass"])

    def test_uranium_not_flagged(self):
        # U has a conventional standard atomic weight, so it is NOT flagged.
        _, info = molar_mass("UO2")
        self.assertFalse(info["uses_isotope_mass"])


class TestFormulaGate(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(check_formula("H2SO4").status, VALID_FORMULA)

    def test_invalid(self):
        self.assertEqual(check_formula("Qz9").status, INVALID_FORMULA)

    def test_to_dict_shape(self):
        d = check_formula("NaCl").to_dict()
        self.assertEqual(d["tool"], "elementgate")
        self.assertIn("public_wording", d)


class TestReaction(unittest.TestCase):
    def test_water_synthesis_balanced(self):
        self.assertEqual(check_reaction("2 H2 + O2 -> 2 H2O").status, BALANCED)

    def test_water_synthesis_unbalanced(self):
        r = check_reaction("H2 + O2 -> H2O")
        self.assertEqual(r.status, UNBALANCED)
        self.assertEqual(r.atom_diff.get("O"), 1)

    def test_combustion_propane(self):
        self.assertEqual(
            check_reaction("C3H8 + 5 O2 -> 3 CO2 + 4 H2O").status, BALANCED)

    def test_combustion_propane_wrong(self):
        self.assertEqual(
            check_reaction("C3H8 + O2 -> 3 CO2 + 4 H2O").status, UNBALANCED)

    def test_equals_arrow(self):
        self.assertEqual(check_reaction("N2 + 3 H2 = 2 NH3").status, BALANCED)

    def test_ionic_charge_balanced(self):
        r = check_reaction("Fe^3+ + 3 OH- -> Fe(OH)3")
        self.assertEqual(r.status, BALANCED)
        self.assertEqual(r.lhs_charge, 0)

    def test_ionic_charge_unbalanced(self):
        r = check_reaction("Fe^3+ + 2 OH- -> Fe(OH)3")
        self.assertEqual(r.status, UNBALANCED)
        self.assertIn("charge", r.reason)

    def test_precipitation_balanced(self):
        self.assertEqual(
            check_reaction("AgNO3 + NaCl -> AgCl + NaNO3").status, BALANCED)

    def test_neutralisation(self):
        self.assertEqual(
            check_reaction("HCl + NaOH -> NaCl + H2O").status, BALANCED)

    def test_no_arrow_malformed(self):
        self.assertEqual(check_reaction("H2 + O2 H2O").status, MALFORMED)

    def test_bad_species_malformed(self):
        self.assertEqual(check_reaction("H2 + Zz -> H2O").status, MALFORMED)

    def test_empty_side_malformed(self):
        self.assertEqual(check_reaction("-> H2O").status, MALFORMED)

    def test_charge_plus_not_split(self):
        # "H+ + OH- -> H2O" : '+' charge must not be read as a species separator
        r = check_reaction("H+ + OH- -> H2O")
        self.assertEqual(r.status, BALANCED)


class TestDeterminism(unittest.TestCase):
    def test_same_formula_same_mass(self):
        self.assertEqual(molar_mass("C6H12O6")[0], molar_mass("C6H12O6")[0])

    def test_reaction_repeatable(self):
        a = check_reaction("2 H2 + O2 -> 2 H2O").to_dict()
        b = check_reaction("2 H2 + O2 -> 2 H2O").to_dict()
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
