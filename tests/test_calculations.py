import importlib.util, pathlib, numpy as np

# Dynamically import supercon_analysis and rtsc_calculator
spec_sa = importlib.util.spec_from_file_location(
    "supercon_analysis",
    str(pathlib.Path(__file__).resolve().parents[1] / "analysis" / "supercon_analysis.py")
)
supercon_analysis = importlib.util.module_from_spec(spec_sa)
spec_sa.loader.exec_module(supercon_analysis)

spec_calc = importlib.util.spec_from_file_location(
    "rtsc_calculator",
    str(pathlib.Path(__file__).resolve().parents[1] / "tools" / "rtsc_calculator.py")
)
rtsc_calculator = importlib.util.module_from_spec(spec_calc)
spec_calc.loader.exec_module(rtsc_calculator)

def test_weighted_log_average():
    freqs = [100, 150, 200]
    weights = [0.2, 0.5, 0.3]
    result = supercon_analysis.weighted_log_average(freqs, weights)
    assert result > 0
    assert 100 < result < 200

def test_allen_dynes_tc():
    tc = supercon_analysis.allen_dynes_tc(omega_log_mev=130, lambda_h=2.0, lambda_plasmon=0.4, lambda_flat=0.2, mu_star=0.12)
    assert tc > 250  # should be in RTSC range

def test_gap_to_tc_ratio():
    ratio = supercon_analysis.gap_to_tc_ratio(delta_mev=130, tc_k=300)  # Use higher delta for stronger coupling
    assert ratio > 4.5

def test_multi_channel_lambda():
    lam_eff = rtsc_calculator.multi_channel_lambda(2.0, 0.4, 0.2)
    assert np.isclose(lam_eff, 2.6)

def test_spectral_weight_factor():
    f_omega = rtsc_calculator.spectral_weight_factor(0.8, 0.2)
    assert np.isclose(f_omega, 4.0)

def test_validate_acceptance():
    results = rtsc_calculator.validate_acceptance(omega_log=130, delta_mev=65, tc_k=300)
    assert results["omega_log_pass"]
    assert results["gap_pass"]
    assert results["ratio_pass"]
