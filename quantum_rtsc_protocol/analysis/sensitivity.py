import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os

# Add the parent directory to the path so we can import from tools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.rtsc_calculator import RTSCCalculator

# Create a global calculator instance
calc = RTSCCalculator()

# Create wrapper functions for compatibility
def allen_dynes_tc(omega_log, lambda_eff, mu_star, f_omega=1.0):
    """Wrapper function for RTSCCalculator.calculate_tc"""
    return calc.calculate_tc(omega_log, lambda_eff, mu_star)

def lambda_for_tc(target_tc, omega_log, mu_star, f_omega=1.0):
    """Calculate lambda_eff needed for a target Tc"""
    # Use optimization to find lambda_eff that gives target_tc
    from scipy.optimize import minimize_scalar
    
    def objective(lambda_eff):
        tc = calc.calculate_tc(omega_log, lambda_eff, mu_star)
        return abs(tc - target_tc)
    
    result = minimize_scalar(objective, bounds=(0.5, 5.0), method='bounded')
    return result.x

def run_sensitivity():
    # --- 1) Heatmap across ω_log–λ_eff ---
    omega_vals = np.linspace(90, 180, 361)  # meV
    lam_vals = np.linspace(1.8, 3.6, 361)
    O, L = np.meshgrid(omega_vals, lam_vals)
    TC = np.vectorize(allen_dynes_tc)(O, L, 0.12, 1.0)

    plt.figure(figsize=(8, 6))
    levels = np.linspace(np.nanmin(TC[np.isfinite(TC)]), 
                         min(600, np.nanmax(TC[np.isfinite(TC)])), 16)
    cf = plt.contourf(O, L, TC, levels=levels)
    cbar = plt.colorbar(cf)
    cbar.set_label("Tc (K) — μ* = 0.12, fω = 1.0")
    cs = plt.contour(O, L, TC, levels=[300], linewidths=2, colors="red")
    # Add a simple legend entry for the 300K contour
    plt.plot([], [], color="red", linewidth=2, label="Tc = 300 K")
    plt.xlabel("ω_log (meV)")
    plt.ylabel("λ_eff")
    plt.title("Tc sensitivity — Allen–Dynes Map")
    plt.legend(loc="lower right", fontsize=8, frameon=True)
    plt.tight_layout()
    plt.savefig("examples/validation_runs/tc_sensitivity_heatmap.png", dpi=200)
    plt.close()

    # --- 2) Threshold λ_eff vs ω_log curves ---
    omegas = np.linspace(100, 180, 81)
    mu_s_list = [0.12, 0.10, 0.08]
    fws = [1.0, 1.3]
    plt.figure(figsize=(8, 6))
    for mu_s in mu_s_list:
        for fw in fws:
            lambdas = [lambda_for_tc(300.0, om, mu_s, fw) for om in omegas]
            plt.plot(omegas, lambdas, label=f"μ*={mu_s}, fω={fw}")
    plt.gca().invert_yaxis()
    plt.xlabel("ω_log (meV)")
    plt.ylabel("λ_eff for Tc=300 K")
    plt.title("Tc=300K threshold curves")
    plt.legend()
    plt.tight_layout()
    plt.savefig("examples/validation_runs/threshold_curves_lambda_vs_omega.png", dpi=200)
    plt.close()

    # --- 3) Local finite-difference sensitivity ---
    points = [
        ("A", 120.0, 2.50, 0.12, 1.38),
        ("B", 135.0, 2.70, 0.10, 1.195),
    ]
    rows = []
    for label, om, lam, mu_s, fw in points:
        tc0 = allen_dynes_tc(om, lam, mu_s, fw)
        dom, dlam, dmu, dfw = 1.0, 0.05, 0.01, 0.05
        d_tc_d_omega = (allen_dynes_tc(om+dom, lam, mu_s, fw) - tc0) / dom
        d_tc_d_lambda = (allen_dynes_tc(om, lam+dlam, mu_s, fw) - tc0) / dlam
        d_tc_d_mu = (allen_dynes_tc(om, lam, mu_s+dmu, fw) - tc0) / dmu
        d_tc_d_fw = (allen_dynes_tc(om, lam, mu_s, fw+dfw) - tc0) / dfw
        rows.append({
            "Point": label,
            "Tc_base (K)": round(tc0, 2),
            "dTc/dω (K/meV)": round(d_tc_d_omega, 2),
            "dTc/dλ (K/unit)": round(d_tc_d_lambda, 2),
            "dTc/dμ* (K/0.01)": round(d_tc_d_mu, 2),
            "dTc/dfω (K/unit)": round(d_tc_d_fw, 2),
        })
        # bar chart
        plt.figure(figsize=(6,4))
        labels = ["ω_log", "λ_eff", "μ*", "fω"]
        values = [d_tc_d_omega, d_tc_d_lambda, d_tc_d_mu, d_tc_d_fw]
        plt.bar(labels, values)
        plt.title(f"Sensitivity @ {label} (Tc≈{tc0:.0f} K)")
        plt.ylabel("ΔTc (K/unit)")
        plt.tight_layout()
        plt.savefig(f"examples/validation_runs/sensitivity_bar_{label}.png", dpi=200)
        plt.close()
    df = pd.DataFrame(rows)
    df.to_csv("examples/validation_runs/tc_local_sensitivity.csv", index=False)
    print("Sensitivity simulation complete. Results saved under examples/validation_runs/")

if __name__ == "__main__":
    run_sensitivity()
