"""Parse a chemical formula into element counts (+ optional ionic charge).

Supports:
  * simple formulas            H2O, CO2, NaCl, C6H12O6
  * nested groups              Ca(OH)2, Fe2(SO4)3, K4[Fe(CN)6]
  * hydrates (· or .)          CuSO4·5H2O, Na2CO3.10H2O
  * ionic charge               SO4^2-, Fe^3+, NH4+, OH-

Returns a ParsedFormula with the per-element counts, total charge, and an error
message if the string could not be parsed. Parsing is deterministic and uses
only the standard library.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, Optional

from .elements import is_element

_SYMBOL = re.compile(r"[A-Z][a-z]?")
_INT = re.compile(r"\d+")
# trailing charge. With a caret the magnitude may be >1 (Fe^3+, SO4^2-);
# without a caret only the sign is the charge (NH4+ is +1, not +4) so a bare
# digit stays part of the formula. Use the caret form for multi-charge ions.
_CHARGE_CARET = re.compile(r"\^(\d*)\s*([+-])$")
_CHARGE_BARE = re.compile(r"([+-])$")
_OPEN = "(["
_CLOSE = ")]"


@dataclass
class ParsedFormula:
    formula: str
    counts: Dict[str, int] = field(default_factory=dict)
    charge: int = 0
    ok: bool = True
    error: str = ""

    def to_dict(self) -> dict:
        return {"formula": self.formula, "counts": dict(self.counts),
                "charge": self.charge, "ok": self.ok, "error": self.error}


def _strip_charge(token: str):
    """Return (formula_without_charge, charge_int)."""
    m = _CHARGE_CARET.search(token)
    if m:
        mag = int(m.group(1)) if m.group(1) else 1
        sign = 1 if m.group(2) == "+" else -1
        return token[: m.start()], sign * mag
    m = _CHARGE_BARE.search(token)
    if m:
        sign = 1 if m.group(1) == "+" else -1
        return token[: m.start()], sign
    return token, 0


def _parse_group(s: str, i: int):
    """Parse from index i until a closing bracket or end. Returns (counts, i, err)."""
    counts: Counter = Counter()
    while i < len(s):
        ch = s[i]
        if ch in _CLOSE:
            return counts, i, ""
        if ch in _OPEN:
            sub, j, err = _parse_group(s, i + 1)
            if err:
                return counts, j, err
            if j >= len(s) or s[j] not in _CLOSE:
                return counts, j, "unbalanced bracket"
            j += 1                                   # consume the close bracket
            m = _INT.match(s, j)
            mult = int(m.group()) if m else 1
            if m:
                j = m.end()
            for el, c in sub.items():
                counts[el] += c * mult
            i = j
            continue
        m = _SYMBOL.match(s, i)
        if not m:
            return counts, i, f"unexpected character {ch!r} at position {i}"
        sym = m.group()
        if not is_element(sym):
            return counts, i, f"unknown element {sym!r}"
        i = m.end()
        n = _INT.match(s, i)
        num = int(n.group()) if n else 1
        if n:
            i = n.end()
        counts[sym] += num
    return counts, i, ""


def parse_formula(formula: str) -> ParsedFormula:
    raw = (formula or "").strip()
    if not raw:
        return ParsedFormula(formula, ok=False, error="empty formula")

    body, charge = _strip_charge(raw)
    body = body.replace("×", "·").strip()
    if not body:
        return ParsedFormula(formula, ok=False, error="formula is only a charge")

    total: Counter = Counter()
    # hydrate parts split on · or a '.' that precedes a new formula chunk
    for part in re.split(r"[·.]", body):
        part = part.strip()
        if not part:
            return ParsedFormula(formula, ok=False, error="empty hydrate component")
        m = _INT.match(part)             # leading hydrate multiplier (e.g. 5H2O)
        mult = int(m.group()) if m else 1
        rest = part[m.end():] if m else part
        counts, idx, err = _parse_group(rest, 0)
        if err:
            return ParsedFormula(formula, ok=False, error=err)
        if idx != len(rest):
            return ParsedFormula(formula, ok=False,
                                 error=f"could not parse near {rest[idx:]!r}")
        for el, c in counts.items():
            total[el] += c * mult

    if not total:
        return ParsedFormula(formula, ok=False, error="no elements found")
    return ParsedFormula(formula, counts=dict(total), charge=charge, ok=True)
