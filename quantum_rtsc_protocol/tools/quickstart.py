from __future__ import annotations
import os, json, subprocess
import typer
from tools.rtsc_calculator import allen_dynes_tc
from analysis.supercon_analysis import run as analysis_run

app = typer.Typer(help="Run the full demo pipeline end-to-end.")

@app.command()
def demo(omega_log_mev: float = 135.0,
         lambda_h: float = 1.9,
         lambda_plasmon: float = 0.6,
         lambda_flat: float = 0.25,
         mu_star: float = 0.10):
    os.makedirs("reports/demo", exist_ok=True)
    tc = allen_dynes_tc(omega_log_mev, lambda_h, lambda_plasmon, lambda_flat, mu_star)
    # Mask
    subprocess.check_call(["python", "tools/mask_generator.py"])
    # Analysis
    analysis_run("examples/sample_data", "reports/demo",
                 omega_log_mev, lambda_h, lambda_plasmon, lambda_flat, mu_star)
    summary = {"Tc_K": tc, "note": "Demo run complete"}
    with open("reports/demo/summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Demo Tc={tc:.1f} K; artifacts in reports/demo/ and masks/")

app = typer.Typer()
app.command()(demo)

if __name__ == "__main__":
    app()
