<p align="center"><img src="assets/logo.png" alt="ElementGate" width="140"></p>

# ElementGate

[![CI](https://github.com/kyal102/elementgate/actions/workflows/ci.yml/badge.svg)](https://github.com/kyal102/elementgate/actions/workflows/ci.yml) ![license](https://img.shields.io/badge/license-MIT-green)

**A deterministic chemistry validator.** Paste a chemical formula or a reaction
— ElementGate parses it, computes the molar mass, and tells you whether the
reaction conserves atoms *and* charge. No model, no network, no dependencies.

```bash
python -m elementgate --demo
```

## What it checks

| Input | ElementGate answers |
|-------|---------------------|
| `Ca(OH)2` | well-formed? atoms `{Ca:1, O:2, H:2}`, **74.092 g/mol** |
| `CuSO4·5H2O` | hydrate parsed, **249.677 g/mol** |
| `Fe^3+ + 3 OH- -> Fe(OH)3` | **BALANCED** (atoms + charge conserved) |
| `H2 + O2 -> H2O` | **UNBALANCED** — `O +1 (lhs-rhs)` |
| `Xy2` | **INVALID_FORMULA** — unknown element `Xy` |

## One command (pure Python stdlib)

```bash
python -m elementgate formula  "K4[Fe(CN)6]"
python -m elementgate mass     "C6H12O6"
python -m elementgate reaction "C3H8 + 5 O2 -> 3 CO2 + 4 H2O"
python -m elementgate reaction "N2 + 3 H2 = 2 NH3" --json
```

### Real output

```
$ python -m elementgate reaction "2 H2 + O2 -> 2 H2O"
  reaction : 2 H2 + O2 -> 2 H2O
  status   : BALANCED
  lhs atoms: {'H': 4, 'O': 2}
  rhs atoms: {'H': 4, 'O': 2}
  reason   : atoms and charge are conserved
```

## Features

- **Formula parsing** — nested groups `Ca(OH)2` / `Fe2(SO4)3` / `K4[Fe(CN)6]`,
  hydrates `CuSO4·5H2O`, ions `SO4^2-` / `NH4+`.
- **Molar mass** — all 118 elements, IUPAC conventional standard atomic weights,
  with a per-element breakdown.
- **Reaction balancing check** — verifies conservation of every element **and**
  net charge, and reports the exact imbalance when a reaction doesn't balance.
- **Deterministic** — same input, same answer, every time.

## In Python

```python
from elementgate import check_formula, check_reaction, molar_mass

molar_mass("CuSO4·5H2O")[0]                        # 249.677
check_reaction("HCl + NaOH -> NaCl + H2O").status  # "BALANCED"
check_formula("Qz9").status                        # "INVALID_FORMULA"
```

## What this is — and isn't

ElementGate checks **chemical bookkeeping**: well-formedness, molar mass, and
conservation of atoms and charge. **`BALANCED` means the equation you wrote
conserves atoms and charge — not that the reaction is real, spontaneous, or
favorable.** It does not predict products, thermodynamics, or kinetics, and it
does not replace experiment or a chemistry reference. See
[docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## Tests

```bash
python -m unittest discover -s tests -q     # 41 tests
```

## Part of the ClaimGate ecosystem

A small family of standalone, MIT-licensed verification tools (pure stdlib):

- **[ElementGate](https://github.com/kyal102/elementgate)** — chemistry formulas & reactions *(this repo)*
- **[UnitGate](https://github.com/kyal102/unitgate)** — physics-equation dimensional consistency
- **[EvidencePack](https://github.com/kyal102/evidencepack)** — tamper-evident result receipts
- **[ReplayGate](https://github.com/kyal102/replaygate)** — replay receipts, detect drift
- **[ClaimLint](https://github.com/kyal102/claimlint)** — lint README/docs for over-claims
- **[ClaimGate](https://github.com/kyal102/claimgate)** — extract & route claims to gates

## License

MIT — see [LICENSE](LICENSE).
