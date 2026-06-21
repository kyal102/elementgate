"""ElementGate — deterministic chemistry formula & reaction validator.

    from elementgate import check_formula, check_reaction, molar_mass

ElementGate parses chemical formulas, computes molar mass, and checks whether a
reaction conserves atoms and charge. Pure standard library; no private code.
"""
from .gate import (
    check_formula, check_reaction, molar_mass, PUBLIC_WORDING,
    VALID_FORMULA, INVALID_FORMULA, BALANCED, UNBALANCED, MALFORMED,
)
from .formula import parse_formula

__version__ = "0.1.0"

__all__ = [
    "check_formula", "check_reaction", "molar_mass", "parse_formula",
    "PUBLIC_WORDING", "VALID_FORMULA", "INVALID_FORMULA",
    "BALANCED", "UNBALANCED", "MALFORMED", "__version__",
]
