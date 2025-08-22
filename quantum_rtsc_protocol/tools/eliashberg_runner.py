# tools/eliashberg_runner.py
from __future__ import annotations
import argparse, json, math, sys
from dataclasses import dataclass
from typing import Tuple, Optional

import numpy as np
from numpy.typing import NDArray
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

K_PER_MEV = 11.604518121  # Kelvin per meV
RUNNER_VERSION = "1.0.1"
SCHEMA_VERSION = "ad-screen-1"

# Units import with fallback
try:
    from .units import to_mev  # package context
except Exception:  # script context
    from units import to_mev

@dataclass
class ADInputs:
    lambda_eff: float
    mu_star: float
    omega_log_meV: float
    omega2_meV: Optional[float] = None  # sqrt(<omega^2>), optional

@dataclass
class ADResult:
    Tc_K: float
    f1: float
    f2: float
    exponent: float
    omega_log_meV: float
    omega2_over_omegalog: Optional[float]
    lambda_eff: float
    mu_star: float

def trapz(x: NDArray[np.float64], y: NDArray[np.float64]) -> float:
    return float(np.trapezoid(y, x))

def moments_from_a2F(omega_meV: NDArray[np.float64],
                     a2F: NDArray[np.float64]) -> Tuple[float, float, float]:
    """
    Compute λ, ω_log, ω2 (sqrt(<ω^2>)) from α^2F(ω).
    Assumes ω in meV, α^2F in usual Eliashberg units (consistent).
    λ = 2 ∫ dω α^2F(ω)/ω
    ω_log = exp[(2/λ) ∫ dω (α^2F(ω)/ω) ln ω]
    <ω^2> = (2/λ) ∫ dω α^2F(ω) * ω
    """
    # Avoid ω=0 by clipping
    eps = 1e-6
    om = np.clip(omega_meV.astype(float), eps, None)
    a = a2F.astype(float)

    integrand_lam = a / om
    lam = 2.0 * trapz(om, integrand_lam)
    if lam <= 0:
        raise ValueError("Computed lambda <= 0; check α²F(ω) units/data.")

    log_integrand = (a / om) * np.log(om)
    omega_log = math.exp((2.0 / lam) * trapz(om, log_integrand))

    omega2_avg = (2.0 / lam) * trapz(om, a * om)  # <ω^2> (since integrand has ω)
    omega2 = math.sqrt(max(omega2_avg, eps))

    return lam, float(omega_log), float(omega2)

def allen_dynes(ad: ADInputs) -> ADResult:
    """
    Allen–Dynes Tc with strong-coupling (f1) and shape (f2) factors.
    Form (Allen & Dynes, PRB 12, 905 (1975)):
      Tc = f1 * f2 * (ω_log / 1.2) * exp[-1.04(1+λ)/(λ - μ*(1+0.62λ))]
    with
      f1 = [1 + (λ/Λ1)^{3/2}]^{1/3},   Λ1 = 2.46(1 + 3.8 μ*)
      f2 = 1 + [ ( (ω2/ω_log - 1) λ^2 ) / ( λ^2 + Λ2^2 ) ],
      Λ2 = 1.82(1 + 6.3 μ*) (ω2/ω_log)
    """
    lam, mu = ad.lambda_eff, ad.mu_star
    if lam <= 0 or ad.omega_log_meV <= 0:
        raise ValueError("lambda_eff and omega_log_meV must be > 0")

    # Defaults if ω2 unknown: set f2→1 (conservative)
    omegalog = ad.omega_log_meV
    if ad.omega2_meV and ad.omega2_meV > 0:
        ratio = ad.omega2_meV / omegalog
    else:
        ratio = None

    # f1
    Lambda1 = 2.46 * (1.0 + 3.8 * mu)
    f1 = (1.0 + (lam / Lambda1) ** 1.5) ** (1.0 / 3.0)

    # f2
    if ratio is not None:
        Lambda2 = 1.82 * (1.0 + 6.3 * mu) * ratio
        f2 = 1.0 + ((ratio - 1.0) * lam * lam) / (lam * lam + Lambda2 * Lambda2)
    else:
        f2 = 1.0

    # Exponential
    denom = lam - mu * (1.0 + 0.62 * lam)
    if denom <= 0:
        # In pathological cases AD exponent blows up; return tiny Tc with flags
        exponent = -1e6
        TcK = 0.0
    else:
        exponent = -1.04 * (1.0 + lam) / denom
        TcK = f1 * f2 * (omegalog * K_PER_MEV / 1.2) * math.exp(exponent)

    return ADResult(
        Tc_K=TcK, f1=f1, f2=f2, exponent=exponent,
        omega_log_meV=omegalog,
        omega2_over_omegalog=(ratio if ratio is not None else None),
        lambda_eff=lam, mu_star=mu
    )

def shannon_entropy(a2F: NDArray[np.float64]) -> float:
    w = np.clip(a2F, 1e-16, None)
    p = w / w.sum()
    return float(-(p * np.log(p)).sum())

def spectral_shape_metrics(omega_meV: NDArray[np.float64],
                           a2F: NDArray[np.float64],
                           smooth_sigma: float = 1.0,
                           prom_frac: float = 0.05,
                           min_distance: int = 5) -> dict:
    """Basic multimodality metrics for gating."""
    a_s = gaussian_filter1d(a2F, sigma=smooth_sigma) if smooth_sigma > 0 else a2F
    peaks, _ = find_peaks(a_s, prominence=a_s.max() * prom_frac, distance=min_distance)
    peak_count = int(len(peaks))

    # Entropy (dimensionless)
    entropy = shannon_entropy(a_s)

    # ω2/ω_log
    lam, omegalog, omega2 = moments_from_a2F(omega_meV, a2F)  # Use raw for moments
    ratio = omega2 / omegalog if omegalog > 0 else float("nan")

    return {
        "peak_count": peak_count,
        "entropy": entropy,
        "omega2_over_omegalog": ratio,
        "lambda_from_alpha2F": lam,
        "omega_log_meV": omegalog,
        "omega2_meV": omega2,
    }

def load_csv(path: str) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    arr = np.loadtxt(path, delimiter=",", dtype=float)
    if arr.ndim != 2 or arr.shape[1] < 2:
        raise ValueError("CSV must have at least two columns: omega, alpha2F")
    om, a = sanitize_csv(arr[:, 0], arr[:, 1])
    if om.size < 3:
        raise ValueError("Not enough valid points after sanitization.")
    return om, a

def sanitize_csv(omega, a2F):
    om = np.asarray(omega, float)
    a = np.asarray(a2F, float)
    m = np.isfinite(om) & np.isfinite(a) & (om > 0) & (a >= 0)
    om, a = om[m], a[m]
    order = np.argsort(om)
    return om[order], a[order]

def validate_inputs(lambda_eff: float, mu_star: float, omegalog: float, denom: float) -> list[str]:
    warnings = []
    if not (0.05 <= mu_star <= 0.20):
        warnings.append("mu_star_out_of_typical_range")
    if lambda_eff > 5:
        warnings.append("lambda_unusually_large")
    if denom <= 0:
        warnings.append("ad_denominator_nonpositive")
    if omegalog < 40:
        warnings.append("omegalog_low_for_RT_targets")
    return warnings

def run_from_alpha2F_arrays(omega_meV: NDArray[np.float64],
                            a2F: NDArray[np.float64],
                            mu_star: float,
                            smooth_sigma: float = 1.0,
                            prom_frac: float = 0.05,
                            min_distance: int = 5) -> dict:
    lam, omegalog, omega2 = moments_from_a2F(omega_meV, a2F)
    denom = lam - mu_star * (1.0 + 0.62 * lam)
    warnings = validate_inputs(lam, mu_star, omegalog, denom)
    adres = allen_dynes(ADInputs(lambda_eff=lam, mu_star=mu_star,
                                 omega_log_meV=omegalog, omega2_meV=omega2))
    shape = spectral_shape_metrics(omega_meV, a2F, smooth_sigma, prom_frac, min_distance)
    return {
        "mode": "alpha2F",
        "inputs": {"mu_star": mu_star},
        "derived": {
            "lambda_eff": lam,
            "omega_log_meV": omegalog,
            "omega2_meV": omega2,
            "omega2_over_omegalog": shape["omega2_over_omegalog"],
        },
        "AD": adrs_to_dict(adres),
        "shape_metrics": shape,
        "warnings": warnings,
    }

def run_from_alpha2F(csv_path: str, mu_star: float, smooth_sigma: float = 1.0, prom_frac: float = 0.05, min_distance: int = 5) -> dict:
    om, a = load_csv(csv_path)
    return run_from_alpha2F_arrays(om, a, mu_star, smooth_sigma, prom_frac, min_distance)

def run_from_params(lambda_eff: float, mu_star: float,
                    omega_log_meV: float, omega2_meV: Optional[float]) -> dict:
    omegalog = omega_log_meV
    denom = lambda_eff - mu_star * (1.0 + 0.62 * lambda_eff)
    warnings = validate_inputs(lambda_eff, mu_star, omegalog, denom)
    adres = allen_dynes(ADInputs(lambda_eff=lambda_eff, mu_star=mu_star,
                                 omega_log_meV=omega_log_meV, omega2_meV=omega2_meV))
    out = {"mode": "params", "inputs": {
        "lambda_eff": lambda_eff,
        "mu_star": mu_star,
        "omega_log_meV": omega_log_meV,
        "omega2_meV": omega2_meV,
    }, "AD": adrs_to_dict(adres),
      "warnings": warnings}
    if omega2_meV:
        out["derived"] = {"omega2_over_omegalog": omega2_meV / omega_log_meV}
    return out

def adrs_to_dict(r: ADResult) -> dict:
    return {
        "Tc_K": r.Tc_K,
        "f1": r.f1,
        "f2": r.f2,
        "exponent": r.exponent,
        "lambda_eff": r.lambda_eff,
        "mu_star": r.mu_star,
        "omega_log_meV": r.omega_log_meV,
        "omega2_over_omegalog": r.omega2_over_omegalog,
    }

def envelope(payload: dict) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "runner_version": RUNNER_VERSION,
        "payload": payload
    }

def main():
    ap = argparse.ArgumentParser(description="Allen–Dynes screening with shape metrics.")
    ap.epilog = """Examples:
  # Params mode
  rtsc-ad-screen --lambda_eff 3.0 --mu_star 0.12 --omega_log_meV 150 --verbose > screen.json

  # α²F mode (Raman in cm^-1)
  rtsc-ad-screen --alpha2F_csv data/a2F_raman.csv --units cm-1 --mu_star 0.12 --verbose > screen.json
"""
    ap.add_argument("--alpha2F_csv", type=str, help="CSV with columns: omega, alpha2F")
    ap.add_argument("--lambda_eff", type=float)
    ap.add_argument("--mu_star", type=float, required=True)
    ap.add_argument("--omega_log_meV", type=float)
    ap.add_argument("--omega2_meV", type=float)
    ap.add_argument("--units", default="meV", help="meV|cm-1|THz for alpha2F CSV frequencies")
    ap.add_argument("--smooth-sigma", type=float, default=1.0, help="Gaussian sigma for peak detection smoothing")
    ap.add_argument("--prom-frac", type=float, default=0.05, help="Prominence fraction for peak detection")
    ap.add_argument("--min-distance", type=int, default=5, help="Min distance between peaks")
    ap.add_argument("--json-out", type=str, help="Write JSON to file")
    ap.add_argument("--verbose", action="store_true", help="Print f1,f2,shape to STDERR")
    args = ap.parse_args()  # <-- FIX

    if args.alpha2F_csv:
        om_raw, a = load_csv(args.alpha2F_csv)
        om_mev = np.array([to_mev(v, args.units) for v in om_raw], dtype=float)  # <-- keep conversion
        res = run_from_alpha2F_arrays(
            om_mev, a, args.mu_star, args.smooth_sigma, args.prom_frac, args.min_distance
        )
    else:
        if args.lambda_eff is None or args.omega_log_meV is None:
            raise SystemExit("Provide --alpha2F_csv OR (--lambda_eff --omega_log_meV)")
        res = run_from_params(args.lambda_eff, args.mu_star, args.omega_log_meV, args.omega2_meV)

    if args.verbose:
        print(f"f1={res['AD']['f1']:.3f}, f2={res['AD']['f2']:.3f}", file=sys.stderr)
        if "shape_metrics" in res:
            sm = res["shape_metrics"]
            print(f"peak_count={sm['peak_count']}, entropy={sm['entropy']:.3f}, "
                  f"omega2/omegalog={sm['omega2_over_omegalog']:.3f}", file=sys.stderr)

    enveloped = envelope(res)
    json_str = json.dumps(enveloped, indent=2)
    print(json_str)

    if args.json_out:
        with open(args.json_out, "w") as f:
            f.write(json_str)

    # Exit code for MCP: escalate also on multimodality
    payload = enveloped["payload"]
    ad = payload["AD"]
    warnings = set(payload.get("warnings", []))
    shape_ratio = payload.get("derived", {}).get("omega2_over_omegalog") \
                  or ad.get("omega2_over_omegalog")
    peak_count = payload.get("shape_metrics", {}).get("peak_count")
    multimodal = (shape_ratio is not None and shape_ratio > 1.20) or (peak_count is not None and peak_count >= 2)

    if ("ad_denominator_nonpositive" in warnings) or (ad["Tc_K"] >= 200) or (ad["lambda_eff"] > 2) or multimodal:
        sys.exit(10)

if __name__ == "__main__":
    main()
