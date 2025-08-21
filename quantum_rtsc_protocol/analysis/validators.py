from __future__ import annotations
import numpy as np
import pandas as pd

class TransportResult:
    def __init__(self, tc_est_k: float | None, drop_ratio: float, passed: bool, reason: str):
        self.tc_est_k = tc_est_k
        self.drop_ratio = drop_ratio
        self.passed = passed
        self.reason = reason

class SusceptibilityResult:
    def __init__(self, onset_k: float | None, slope: float | None, passed: bool, reason: str):
        self.onset_k = onset_k
        self.slope = slope
        self.passed = passed
        self.reason = reason

class RamanResult:
    def __init__(self, feature_meV: float | None, passed: bool, reason: str):
        self.feature_meV = feature_meV
        self.passed = passed
        self.reason = reason

def evaluate_transport(df_iv: pd.DataFrame, drop_threshold: float = 0.02) -> TransportResult:
    """
    drop_threshold: fraction of high-T resistance below which we call 'superconducting-like'.
    """
    df_iv = df_iv.copy()
    df_iv["R_ohm"] = df_iv["V_V"] / df_iv["I_A"]
    # Take median of top-3 highest T points as 'normal' resistance
    df_sorted = df_iv.sort_values("T_K", ascending=False)
    r_norm = df_sorted.head(3)["R_ohm"].median()
    # Find first T where R drops below threshold*R_norm
    below = df_iv[df_iv["R_ohm"] <= drop_threshold * r_norm].sort_values("T_K")
    tc_est = float(below["T_K"].iloc[0]) if len(below) else None
    drop_ratio = df_iv["R_ohm"].min() / r_norm
    passed = tc_est is not None and drop_ratio <= drop_threshold
    reason = "OK" if passed else "No clear resistive transition"
    return TransportResult(tc_est, float(drop_ratio), passed, reason)

def evaluate_susceptibility(df_chi: pd.DataFrame, step_threshold: float = -1e-5) -> SusceptibilityResult:
    """
    Simple check: does chi_real become more negative with decreasing T and cross a step?
    """
    df_chi = df_chi.sort_values("T_K")
    dchi = np.gradient(df_chi["chi_real"].values, df_chi["T_K"].values)
    onset_idx = np.argmin(dchi)  # most negative slope
    onset_k = float(df_chi["T_K"].iloc[onset_idx])
    slope = float(dchi[onset_idx])
    passed = slope < step_threshold
    reason = "OK" if passed else "No strong diamagnetic onset"
    return SusceptibilityResult(onset_k, slope, passed, reason)

def evaluate_raman_gap(df_raman: pd.DataFrame, expected_2delta_mev: float, window_mev: float = 12.0) -> RamanResult:
    """
    Toy feature check: a dip near expected 2Δ0.
    """
    diffs = np.abs(df_raman["energy_meV"].values - expected_2delta_mev)
    nearest_idx = int(np.argmin(diffs))
    feature_mev = float(df_raman["energy_meV"].iloc[nearest_idx])
    # Flag as pass if intensity at nearest is at least 5% lower than median baseline
    baseline = float(df_raman["intensity"].median())
    val = float(df_raman["intensity"].iloc[nearest_idx])
    passed = (baseline - val) / baseline >= 0.05 and abs(feature_mev - expected_2delta_mev) <= window_mev
    reason = "OK" if passed else "No spectral feature near 2Δ0"
    return RamanResult(feature_mev, passed, reason)
