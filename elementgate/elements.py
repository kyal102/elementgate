"""Periodic table: element symbol -> (atomic number, standard atomic weight).

Atomic weights are IUPAC conventional values (g/mol). For elements with no
stable isotope, the mass number of the most stable / common isotope is used and
flagged in ``RADIOACTIVE``. These are reference data, not measurements made by
this tool.
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

# symbol: (Z, standard atomic weight)
ELEMENTS: Dict[str, Tuple[int, float]] = {
    "H": (1, 1.008), "He": (2, 4.0026),
    "Li": (3, 6.94), "Be": (4, 9.0122), "B": (5, 10.81), "C": (6, 12.011),
    "N": (7, 14.007), "O": (8, 15.999), "F": (9, 18.998), "Ne": (10, 20.180),
    "Na": (11, 22.990), "Mg": (12, 24.305), "Al": (13, 26.982), "Si": (14, 28.085),
    "P": (15, 30.974), "S": (16, 32.06), "Cl": (17, 35.45), "Ar": (18, 39.95),
    "K": (19, 39.098), "Ca": (20, 40.078), "Sc": (21, 44.956), "Ti": (22, 47.867),
    "V": (23, 50.942), "Cr": (24, 51.996), "Mn": (25, 54.938), "Fe": (26, 55.845),
    "Co": (27, 58.933), "Ni": (28, 58.693), "Cu": (29, 63.546), "Zn": (30, 65.38),
    "Ga": (31, 69.723), "Ge": (32, 72.630), "As": (33, 74.922), "Se": (34, 78.971),
    "Br": (35, 79.904), "Kr": (36, 83.798),
    "Rb": (37, 85.468), "Sr": (38, 87.62), "Y": (39, 88.906), "Zr": (40, 91.224),
    "Nb": (41, 92.906), "Mo": (42, 95.95), "Tc": (43, 98.0), "Ru": (44, 101.07),
    "Rh": (45, 102.91), "Pd": (46, 106.42), "Ag": (47, 107.87), "Cd": (48, 112.41),
    "In": (49, 114.82), "Sn": (50, 118.71), "Sb": (51, 121.76), "Te": (52, 127.60),
    "I": (53, 126.90), "Xe": (54, 131.29),
    "Cs": (55, 132.91), "Ba": (56, 137.33), "La": (57, 138.91), "Ce": (58, 140.12),
    "Pr": (59, 140.91), "Nd": (60, 144.24), "Pm": (61, 145.0), "Sm": (62, 150.36),
    "Eu": (63, 151.96), "Gd": (64, 157.25), "Tb": (65, 158.93), "Dy": (66, 162.50),
    "Ho": (67, 164.93), "Er": (68, 167.26), "Tm": (69, 168.93), "Yb": (70, 173.05),
    "Lu": (71, 174.97), "Hf": (72, 178.49), "Ta": (73, 180.95), "W": (74, 183.84),
    "Re": (75, 186.21), "Os": (76, 190.23), "Ir": (77, 192.22), "Pt": (78, 195.08),
    "Au": (79, 196.97), "Hg": (80, 200.59), "Tl": (81, 204.38), "Pb": (82, 207.2),
    "Bi": (83, 208.98), "Po": (84, 209.0), "At": (85, 210.0), "Rn": (86, 222.0),
    "Fr": (87, 223.0), "Ra": (88, 226.0), "Ac": (89, 227.0), "Th": (90, 232.04),
    "Pa": (91, 231.04), "U": (92, 238.03), "Np": (93, 237.0), "Pu": (94, 244.0),
    "Am": (95, 243.0), "Cm": (96, 247.0), "Bk": (97, 247.0), "Cf": (98, 251.0),
    "Es": (99, 252.0), "Fm": (100, 257.0), "Md": (101, 258.0), "No": (102, 259.0),
    "Lr": (103, 262.0), "Rf": (104, 267.0), "Db": (105, 268.0), "Sg": (106, 269.0),
    "Bh": (107, 270.0), "Hs": (108, 269.0), "Mt": (109, 278.0), "Ds": (110, 281.0),
    "Rg": (111, 282.0), "Cn": (112, 285.0), "Nh": (113, 286.0), "Fl": (114, 289.0),
    "Mc": (115, 290.0), "Lv": (116, 293.0), "Ts": (117, 294.0), "Og": (118, 294.0),
}

# Elements whose listed weight is a most-stable-isotope mass number, not a
# standard atomic weight (no stable isotope exists).
RADIOACTIVE = {
    "Tc", "Pm", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Np", "Pu", "Am", "Cm",
    "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs",
    "Mt", "Ds", "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og",
}


def is_element(symbol: str) -> bool:
    return symbol in ELEMENTS


def atomic_number(symbol: str) -> Optional[int]:
    e = ELEMENTS.get(symbol)
    return e[0] if e else None


def atomic_weight(symbol: str) -> Optional[float]:
    e = ELEMENTS.get(symbol)
    return e[1] if e else None
