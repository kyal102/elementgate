"""ElementGate CLI.

    python -m elementgate --demo
    python -m elementgate formula "Ca(OH)2"
    python -m elementgate mass "CuSO4·5H2O"
    python -m elementgate reaction "2 H2 + O2 -> 2 H2O"
    python -m elementgate reaction "C3H8 + 5 O2 -> 3 CO2 + 4 H2O" --json
"""
from __future__ import annotations

import argparse
import json
import sys

from .gate import check_formula, check_reaction, molar_mass, PUBLIC_WORDING, BALANCED, VALID_FORMULA


def _utf8():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def _print_formula(res, breakdown):
    print(f"  formula : {res.formula}")
    print(f"  status  : {res.status}")
    if res.counts:
        print(f"  atoms   : {res.counts}")
        print(f"  charge  : {res.charge:+d}" if res.charge else "  charge  : 0")
        print(f"  mass    : {res.molar_mass} g/mol")
        if breakdown and breakdown.get("uses_isotope_mass"):
            print("  note    : includes an element with no stable isotope "
                  "(most-stable-isotope mass used)")
    else:
        print(f"  reason  : {res.reason}")


def _print_reaction(res):
    print(f"  reaction : {res.reaction}")
    print(f"  status   : {res.status}")
    print(f"  lhs atoms: {res.lhs_atoms}")
    print(f"  rhs atoms: {res.rhs_atoms}")
    if res.lhs_charge or res.rhs_charge:
        print(f"  charge   : lhs {res.lhs_charge:+d}  rhs {res.rhs_charge:+d}")
    print(f"  reason   : {res.reason}")


def _demo() -> int:
    _utf8()
    print("# ElementGate demo")
    print(f"  {PUBLIC_WORDING}\n")

    print("## Formulas")
    for f in ["H2O", "Ca(OH)2", "Fe2(SO4)3", "CuSO4·5H2O", "NaCl", "Xy2"]:
        r = check_formula(f)
        mark = "OK " if r.status == VALID_FORMULA else "BAD"
        mass = f"{r.molar_mass} g/mol" if r.molar_mass is not None else r.reason
        print(f"  [{mark}] {f:<14} {r.status:<16} {mass}")

    print("\n## Reactions")
    for rx in [
        "2 H2 + O2 -> 2 H2O",
        "H2 + O2 -> H2O",                       # unbalanced
        "C3H8 + 5 O2 -> 3 CO2 + 4 H2O",
        "Fe^3+ + 3 OH- -> Fe(OH)3",             # charge-balanced ionic
    ]:
        r = check_reaction(rx)
        mark = "BAL  " if r.status == BALANCED else "UNBAL"
        print(f"  [{mark}] {rx}")
        if r.status != BALANCED:
            print(f"          -> {r.reason}")

    print("\n  Verdicts are computed deterministically from element counts and")
    print("  charges. BALANCED means atoms + charge are conserved — not that the")
    print("  reaction actually proceeds. This does not replace experiment.")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="elementgate",
                                description="Deterministic chemistry formula & reaction validator.")
    p.add_argument("--demo", action="store_true", help="run a short self-contained showcase")
    sub = p.add_subparsers(dest="cmd")

    pf = sub.add_parser("formula", help="validate a chemical formula")
    pf.add_argument("text"); pf.add_argument("--json", action="store_true")
    pm = sub.add_parser("mass", help="compute molar mass")
    pm.add_argument("text"); pm.add_argument("--json", action="store_true")
    pr = sub.add_parser("reaction", help="check if a reaction is balanced")
    pr.add_argument("text"); pr.add_argument("--json", action="store_true")

    args = p.parse_args(argv)

    if args.demo and not args.cmd:
        return _demo()

    if args.cmd in ("formula", "mass"):
        _utf8()
        res = check_formula(args.text)
        _, info = molar_mass(args.text)
        if args.cmd == "mass":
            out = {"tool": "elementgate", "formula": args.text,
                   "molar_mass_g_per_mol": res.molar_mass,
                   "status": res.status, "breakdown": info.get("breakdown"),
                   "public_wording": PUBLIC_WORDING}
            if args.json:
                print(json.dumps(out, indent=2))
            else:
                print(f"  {args.text}: {res.molar_mass} g/mol  ({res.status})")
                for el, b in (info.get("breakdown") or {}).items():
                    print(f"    {el}: {b['count']} × {b['atomic_weight']} = {b['subtotal']}")
            return 0 if res.status == VALID_FORMULA else 1
        if args.json:
            print(json.dumps(res.to_dict(), indent=2))
        else:
            _print_formula(res, info)
        return 0 if res.status == VALID_FORMULA else 1

    if args.cmd == "reaction":
        _utf8()
        res = check_reaction(args.text)
        if args.json:
            print(json.dumps(res.to_dict(), indent=2))
        else:
            _print_reaction(res)
        return 0 if res.status == BALANCED else 1

    p.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
