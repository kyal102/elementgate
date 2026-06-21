# Examples

All commands use only the Python standard library. Every result is deterministic.

## 30-second showcase

```bash
python -m elementgate --demo
```

## Validate a formula

```bash
python -m elementgate formula "Fe2(SO4)3"
python -m elementgate formula "K4[Fe(CN)6]"
python -m elementgate formula "CuSO4·5H2O"
```

```
  formula : Fe2(SO4)3
  status  : VALID_FORMULA
  atoms   : {'Fe': 2, 'S': 3, 'O': 12}
  charge  : 0
  mass    : 399.858 g/mol
```

## Molar mass with breakdown

```bash
python -m elementgate mass "C6H12O6"
```

```
  C6H12O6: 180.156 g/mol  (VALID_FORMULA)
    C: 6 × 12.011 = 72.066
    H: 12 × 1.008 = 12.096
    O: 6 × 15.999 = 95.994
```

## Check a reaction

```bash
python -m elementgate reaction "2 H2 + O2 -> 2 H2O"
python -m elementgate reaction "C3H8 + 5 O2 -> 3 CO2 + 4 H2O"
python -m elementgate reaction "Fe^3+ + 3 OH- -> Fe(OH)3"
```

An unbalanced reaction reports exactly what's off:

```bash
python -m elementgate reaction "H2 + O2 -> H2O"
```

```
  status   : UNBALANCED
  reason   : atoms not conserved: O +1 (lhs-rhs)
```

Add `--json` to any command for machine-readable output:

```bash
python -m elementgate reaction "N2 + 3 H2 = 2 NH3" --json
```

## In Python

```python
from elementgate import check_formula, check_reaction, molar_mass

check_formula("Ca(OH)2").molar_mass          # 74.092
molar_mass("CuSO4·5H2O")[0]                  # 249.677
check_reaction("HCl + NaOH -> NaCl + H2O").status   # "BALANCED"
```

## Verdicts

| Status | Meaning |
|--------|---------|
| `VALID_FORMULA` | parses into known elements |
| `INVALID_FORMULA` | unknown element or malformed string |
| `BALANCED` | atoms **and** charge are conserved across the arrow |
| `UNBALANCED` | atom and/or charge mismatch (with the exact diff) |
| `MALFORMED_INPUT` | no arrow, empty side, or an unparseable species |

`BALANCED` means the equation conserves atoms and charge — not that the reaction
actually occurs. See [LIMITATIONS.md](LIMITATIONS.md).
