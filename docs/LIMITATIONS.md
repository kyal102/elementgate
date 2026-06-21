# Limitations

ElementGate is a **deterministic checker of chemical bookkeeping** — formula
well-formedness, molar mass, and conservation of atoms and charge. Read these
limits before drawing conclusions from it.

## What it does

- **Formula parsing** — nested groups (`Ca(OH)2`, `K4[Fe(CN)6]`), hydrates
  (`CuSO4·5H2O`), and ionic charge (`SO4^2-`, `NH4+`).
- **Molar mass** — from IUPAC conventional standard atomic weights.
- **Reaction balance** — checks that every element's atom count and the total
  charge are equal on both sides of `LHS -> RHS`.

## What it does NOT do

- It does **not** predict whether a reaction occurs, what the products are, or
  in what proportions. `BALANCED` means the equation you wrote conserves atoms
  and charge — **not** that the reaction is real, spontaneous, or favorable.
- It does **not** model thermodynamics, kinetics, equilibrium, phases, or
  oxidation states.
- It does **not** balance reactions for you (it checks a balance you provide).
- It does **not** replace experiment, a chemistry reference, or expert review.

## Known parsing caveats

- **Multi-charge ions need a caret.** `Fe^3+` and `SO4^2-` parse correctly.
  Without the caret, only the sign is read as charge, so `Fe3+` is interpreted
  as *three Fe atoms with charge +1*, not one Fe³⁺. This is deliberate: a bare
  trailing digit is ambiguous with an atom count.
- **Bracket types are not strictly matched** — `(` may be closed by `]`. Real
  formulas rarely mismatch; this keeps the parser simple.
- **Atomic weights are reference data**, not measurements. For elements with no
  stable isotope, the most-stable-isotope mass number is used and the result is
  flagged `uses_isotope_mass`.
- Isotopic labelling (e.g. `^14C`), charges written mid-formula, and abbreviated
  organic notation (e.g. `Et`, `Ph`) are out of scope.

## Determinism

Given the same input, ElementGate always returns the same result. There is no
model, randomness, or network access.
