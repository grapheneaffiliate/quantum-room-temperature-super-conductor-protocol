"""
Enhanced RTSC Calculator
Extends Allen-Dynes with multi-channel coupling and artifact checks.
"""

import numpy as np

def multi_channel_lambda(lambda_h, lambda_plasmon=0.0, lambda_flat=0.0):
    """
    Compute effective lambda from multiple channels.
    """
    return lambda_h + lambda_plasmon + lambda_flat

def spectral_weight_factor(high_omega_weight, low_omega_weight):
    """
    Compute f_ω enhancement factor.
    """
    if low_omega_weight <= 0:
        return np.inf
    return high_omega_weight / low_omega_weight

def allen_dynes_tc(lambda_eff, mu_star, omega_log_mev):
    """
    Allen-Dynes Tc estimation.
    """
    omega_log_k = omega_log_mev * 11.6045
    denom = 1.04 * (1 + lambda_eff) - lambda_eff * mu_star * (1 + 0.62 * lambda_eff)
    if denom <= 0:
        return 0.0
    return (omega_log_k / 1.2) * np.exp(-1.04 * (1 + lambda_eff) / denom)

def validate_acceptance(omega_log, delta_mev, tc_k):
    """
    Validate acceptance criteria for RTSC.
    """
    kB_meV_per_K = 0.08617
    ratio = (2 * delta_mev) / (kB_meV_per_K * tc_k)
    return {
        "omega_log_pass": omega_log >= 120,
        "gap_pass": delta_mev >= 58,
        "ratio_pass": ratio >= 4.5,
        "tc_k": tc_k,
        "ratio": ratio
    }

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="RTSC Calculator")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add calc subcommand
    calc_parser = subparsers.add_parser('calc', help='Calculate Tc')
    calc_parser.add_argument('--omega-log-mev', type=float, default=130, help='Log-averaged phonon frequency in meV')
    calc_parser.add_argument('--lambda-h', type=float, default=2.0, help='Hydrogen coupling')
    calc_parser.add_argument('--lambda-plasmon', type=float, default=0.4, help='Plasmon coupling')
    calc_parser.add_argument('--lambda-flat', type=float, default=0.2, help='Flat band coupling')
    calc_parser.add_argument('--mu-star', type=float, default=0.12, help='Coulomb pseudopotential')
    
    if len(sys.argv) == 1:
        # Default example usage
        lam_eff = multi_channel_lambda(lambda_h=2.0, lambda_plasmon=0.4, lambda_flat=0.2)
        f_omega = spectral_weight_factor(high_omega_weight=0.8, low_omega_weight=0.2)
        print("λ_eff =", lam_eff, "f_ω =", f_omega)

        tc = allen_dynes_tc(lam_eff, mu_star=0.12, omega_log_mev=130)
        print("Estimated Tc =", tc, "K")

        results = validate_acceptance(omega_log=130, delta_mev=65, tc_k=tc)
        print("Acceptance:", results)
    else:
        args = parser.parse_args()
        
        if args.command == 'calc':
            lam_eff = multi_channel_lambda(args.lambda_h, args.lambda_plasmon, args.lambda_flat)
            tc = allen_dynes_tc(lam_eff, args.mu_star, args.omega_log_mev)
            print(f"Tc = {tc:.2f} K")
        else:
            parser.print_help()
