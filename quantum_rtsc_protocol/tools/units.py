# tools/units.py
def to_mev(x: float, units: str) -> float:
    u = units.lower()
    if u == "mev": return x
    if u in ("cm-1", "cm^-1", "raman"): return x * 0.1239841984
    if u == "thz": return x * 4.135667696
    raise ValueError(f"Unknown units: {units}")
