"""
Superconductivity Analysis Tools for RTSC Protocol
"""

import numpy as np

def weighted_log_average(frequencies, weights):
    """
    Compute logarithmic average frequency (ω_log).
    frequencies: array of phonon frequencies (meV)
    weights: spectral weights (normalized)
    """
    frequencies = np.array(frequencies)
    weights = np.array(weights)
    weights /= np.sum(weights)
    log_avg = np.exp(np.sum(weights * np.log(frequencies)))
    return log_avg

def allen_dynes_tc(lambda_eff, mu_star, omega_log_mev):
    """
    Allen-Dynes Tc estimation.
    lambda_eff: effective coupling constant
    mu_star: Coulomb pseudopotential
    omega_log_mev: logarithmic average phonon frequency (meV)
    Returns Tc in Kelvin
    """
    omega_log_k = omega_log_mev * 11.6045  # convert meV to K
    denom = 1.04 * (1 + lambda_eff) - lambda_eff * mu_star * (1 + 0.62 * lambda_eff)
    if denom <= 0:
        return 0.0
    tc = (omega_log_k / 1.2) * np.exp(-1.04 * (1 + lambda_eff) / denom)
    return tc

def gap_to_tc_ratio(delta_mev, tc_k):
    """
    Compute 2Δ/kB Tc ratio.
    delta_mev: superconducting gap (meV)
    tc_k: critical temperature (K)
    """
    kB_meV_per_K = 0.08617
    return (2 * delta_mev) / (kB_meV_per_K * tc_k)

if __name__ == "__main__":
    # Example usage
    freqs = [100, 150, 200]  # meV
    weights = [0.2, 0.5, 0.3]
    omega_log = weighted_log_average(freqs, weights)
    print("ω_log =", omega_log, "meV")

    tc = allen_dynes_tc(lambda_eff=2.6, mu_star=0.12, omega_log_mev=omega_log)
    print("Estimated Tc =", tc, "K")

    ratio = gap_to_tc_ratio(delta_mev=65, tc_k=tc)
    print("2Δ/kB Tc =", ratio)
