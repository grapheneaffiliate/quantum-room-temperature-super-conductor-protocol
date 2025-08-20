from __future__ import annotations
import json, os
import pandas as pd
import importlib.util, pathlib

# dynamic import of rtsc_calculator
spec_calc = importlib.util.spec_from_file_location(
    "rtsc_calculator",
    str(pathlib.Path(__file__).resolve().parents[0].parent / "tools" / "rtsc_calculator.py")
)
rtsc_calculator = importlib.util.module_from_spec(spec_calc)
spec_calc.loader.exec_module(rtsc_calculator)

def allen_dynes_tc(omega_log_mev: float, lambda_h: float, lambda_plasmon: float, lambda_flat: float, mu_star: float) -> float:
    """Wrapper for allen_dynes_tc with multi-channel support."""
    lambda_eff = rtsc_calculator.multi_channel_lambda(lambda_h, lambda_plasmon, lambda_flat)
    return rtsc_calculator.allen_dynes_tc(lambda_eff, mu_star, omega_log_mev)
# define MEV_TO_K locally (avoid missing attribute)
MEV_TO_K = 11.6045

# dynamic import of validators
spec_val = importlib.util.spec_from_file_location(
    "validators",
    str(pathlib.Path(__file__).resolve().parents[0] / "validators.py")
)
validators = importlib.util.module_from_spec(spec_val)
spec_val.loader.exec_module(validators)
evaluate_transport = validators.evaluate_transport
evaluate_susceptibility = validators.evaluate_susceptibility
evaluate_raman_gap = validators.evaluate_raman_gap

def kB_eV_per_K() -> float:
    return 8.617333262e-5  # eV/K

def two_delta0_meV(tc_k: float, ratio_2delta_over_kbT: float = 3.53) -> float:
    # 2Δ0 = (2Δ0/kB Tc) * kB * Tc, default BCS weak-coupling 3.53; strong coupling can be ~4–5+
    return ratio_2delta_over_kbT * kB_eV_per_K() * tc_k * 1000.0

def weighted_log_average(freqs, weights):
    """Calculate weighted logarithmic average of frequencies."""
    import numpy as np
    freqs = np.array(freqs)
    weights = np.array(weights)
    weights = weights / weights.sum()  # normalize
    return np.exp(np.sum(weights * np.log(freqs)))

def gap_to_tc_ratio(delta_mev: float, tc_k: float) -> float:
    """Calculate 2Δ/kB*Tc ratio."""
    kb_mev_per_k = kB_eV_per_K() * 1000  # convert to meV/K
    return delta_mev / (kb_mev_per_k * tc_k)

def run(in_dir: str, out_dir: str,
        omega_log_mev: float, lambda_h: float, lambda_plasmon: float, lambda_flat: float,
        mu_star: float, two_delta_ratio: float = 3.53):
    os.makedirs(out_dir, exist_ok=True)

    # Load data
    df_iv = pd.read_csv(os.path.join(in_dir, "iv_4probe.csv"))
    df_chi = pd.read_csv(os.path.join(in_dir, "ac_susceptibility.csv"))
    df_raman = pd.read_csv(os.path.join(in_dir, "raman.csv"))

    # Theory Tc
    tc_pred = allen_dynes_tc(omega_log_mev, lambda_h, lambda_plasmon, lambda_flat, mu_star)
    two_delta_mev = two_delta0_meV(tc_pred, two_delta_ratio)

    # Measurements → validators
    tr = evaluate_transport(df_iv)
    sr = evaluate_susceptibility(df_chi)
    rr = evaluate_raman_gap(df_raman, expected_2delta_mev=two_delta_mev)

    # Aggregate verdict
    passes = [tr.passed, sr.passed, rr.passed]
    verdict = "PASS" if all(passes) else "FAIL"

    # Write JSON report
    report = {
        "inputs": {
            "omega_log_mev": omega_log_mev,
            "lambda_h": lambda_h,
            "lambda_plasmon": lambda_plasmon,
            "lambda_flat": lambda_flat,
            "mu_star": mu_star,
            "two_delta_ratio": two_delta_ratio
        },
        "theory": {"Tc_pred_K": tc_pred, "twoDelta0_meV": two_delta_mev},
        "transport": tr.__dict__,
        "susceptibility": sr.__dict__,
        "raman": rr.__dict__,
        "verdict": verdict
    }
    with open(os.path.join(out_dir, "report.json"), "w") as f:
        json.dump(report, f, indent=2)
    print(f"Wrote {os.path.join(out_dir, 'report.json')}")
    print(f"VERDICT: {verdict}")

if __name__ == "__main__":
    # Default demo parameters (adjust to taste)
    run(
        in_dir="examples/sample_data",
        out_dir="reports/demo",
        omega_log_mev=135.0,
        lambda_h=1.9, lambda_plasmon=0.6, lambda_flat=0.25,
        mu_star=0.10, two_delta_ratio=3.53
    )
