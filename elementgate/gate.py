"""ElementGate: deterministic chemistry checks.

  * check_formula(f)   -> is ``f`` a well-formed formula of known elements?
  * molar_mass(f)      -> molar mass (g/mol) + per-element breakdown
  * check_reaction(r)  -> is ``LHS -> RHS`` balanced in mass AND charge?

ElementGate checks formula well-formedness, molar mass, and conservation of
atoms and charge in a reaction. It does not predict whether a reaction occurs,
its products, thermodynamics, or kinetics, and it does not replace experiment.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .elements import atomic_weight, RADIOACTIVE
from .formula import parse_formula

PUBLIC_WORDING = (
    "ElementGate checks formula well-formedness, molar mass, and conservation "
    "of atoms and charge. It does not predict reaction products, thermodynamics "
    "or kinetics, and does not replace experiment."
)

VALID_FORMULA = "VALID_FORMULA"
INVALID_FORMULA = "INVALID_FORMULA"
BALANCED = "BALANCED"
UNBALANCED = "UNBALANCED"
MALFORMED = "MALFORMED_INPUT"

_ARROWS = ("<->", "<=>", "-->", "->", "=>", "→", "⟶", "⇌", "=")
_SPLIT_PLUS = re.compile(r"\s+\+\s+")          # species separator (not a charge +)
_COEFF = re.compile(r"^(\d+)\s*(.+)$")


@dataclass
class FormulaResult:
    status: str
    formula: str
    counts: Dict[str, int] = field(default_factory=dict)
    charge: int = 0
    molar_mass: Optional[float] = None
    reason: str = ""

    def to_dict(self) -> dict:
        return {"tool": "elementgate", "status": self.status, "formula": self.formula,
                "counts": self.counts, "charge": self.charge,
                "molar_mass_g_per_mol": self.molar_mass, "reason": self.reason,
                "public_wording": PUBLIC_WORDING}


@dataclass
class ReactionResult:
    status: str
    reaction: str
    lhs_atoms: Dict[str, int] = field(default_factory=dict)
    rhs_atoms: Dict[str, int] = field(default_factory=dict)
    atom_diff: Dict[str, int] = field(default_factory=dict)
    lhs_charge: int = 0
    rhs_charge: int = 0
    reason: str = ""

    def to_dict(self) -> dict:
        return {"tool": "elementgate", "status": self.status, "reaction": self.reaction,
                "lhs_atoms": self.lhs_atoms, "rhs_atoms": self.rhs_atoms,
                "atom_diff": self.atom_diff, "lhs_charge": self.lhs_charge,
                "rhs_charge": self.rhs_charge, "reason": self.reason,
                "public_wording": PUBLIC_WORDING}


def molar_mass(formula: str) -> Tuple[Optional[float], dict]:
    """Return (mass_g_per_mol, breakdown). mass is None if the formula is invalid."""
    p = parse_formula(formula)
    if not p.ok:
        return None, {"error": p.error}
    total = 0.0
    breakdown = {}
    approx = False
    for el, n in sorted(p.counts.items()):
        w = atomic_weight(el)
        if w is None:                                   # pragma: no cover
            return None, {"error": f"no atomic weight for {el}"}
        contribution = w * n
        total += contribution
        breakdown[el] = {"count": n, "atomic_weight": w,
                         "subtotal": round(contribution, 4)}
        if el in RADIOACTIVE:
            approx = True
    return round(total, 4), {"breakdown": breakdown, "uses_isotope_mass": approx}


def check_formula(formula: str) -> FormulaResult:
    p = parse_formula(formula)
    if not p.ok:
        return FormulaResult(INVALID_FORMULA, formula, reason=p.error)
    mass, _ = molar_mass(formula)
    return FormulaResult(VALID_FORMULA, formula, counts=p.counts, charge=p.charge,
                         molar_mass=mass,
                         reason="well-formed formula of known elements")


def _parse_side(side: str):
    """Parse one side of a reaction. Returns (atoms, charge, error)."""
    atoms: Dict[str, int] = {}
    charge = 0
    species = [s for s in _SPLIT_PLUS.split(side.strip()) if s.strip()]
    if not species:
        return atoms, charge, "empty side"
    for sp in species:
        sp = sp.strip()
        m = _COEFF.match(sp)
        coeff = int(m.group(1)) if m else 1
        body = m.group(2).strip() if m else sp
        p = parse_formula(body)
        if not p.ok:
            return atoms, charge, f"{body!r}: {p.error}"
        for el, n in p.counts.items():
            atoms[el] = atoms.get(el, 0) + n * coeff
        charge += p.charge * coeff
    return atoms, charge, ""


def check_reaction(reaction: str) -> ReactionResult:
    r = (reaction or "").strip()
    arrow = next((a for a in _ARROWS if a in r), None)
    if not arrow:
        return ReactionResult(MALFORMED, r,
                              reason="no reaction arrow found (use -> or =)")
    lhs_s, _, rhs_s = r.partition(arrow)
    if not lhs_s.strip() or not rhs_s.strip():
        return ReactionResult(MALFORMED, r, reason="both sides must be non-empty")

    lhs, lq, el = _parse_side(lhs_s)
    if el:
        return ReactionResult(MALFORMED, r, reason=f"left side: {el}")
    rhs, rq, er = _parse_side(rhs_s)
    if er:
        return ReactionResult(MALFORMED, r, reason=f"right side: {er}")

    diff = {}
    for elem in set(lhs) | set(rhs):
        d = lhs.get(elem, 0) - rhs.get(elem, 0)
        if d != 0:
            diff[elem] = d

    mass_ok = not diff
    charge_ok = (lq == rq)
    if mass_ok and charge_ok:
        reason = "atoms and charge are conserved"
        status = BALANCED
    else:
        problems = []
        if not mass_ok:
            problems.append("atoms not conserved: " + ", ".join(
                f"{e} {'+' if d > 0 else ''}{d} (lhs-rhs)" for e, d in sorted(diff.items())))
        if not charge_ok:
            problems.append(f"charge not conserved: lhs {lq:+d} vs rhs {rq:+d}")
        reason = "; ".join(problems)
        status = UNBALANCED
    return ReactionResult(status, r, lhs_atoms=lhs, rhs_atoms=rhs, atom_diff=diff,
                          lhs_charge=lq, rhs_charge=rq, reason=reason)
