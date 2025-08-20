import importlib.util, pathlib

# Dynamically import rtsc_calculator from tools
spec = importlib.util.spec_from_file_location(
    "rtsc_calculator",
    str(pathlib.Path(__file__).resolve().parents[1] / "tools" / "rtsc_calculator.py")
)
rtsc_calculator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rtsc_calculator)

def test_tc_monotonic_lambda():
    # Test with the correct signature: lambda_eff, mu_star, omega_log_mev
    lambda_eff_a = rtsc_calculator.multi_channel_lambda(1.0, 0.5, 0.2)
    lambda_eff_b = rtsc_calculator.multi_channel_lambda(1.2, 0.6, 0.3)
    a = rtsc_calculator.allen_dynes_tc(lambda_eff_a, 0.12, 120)
    b = rtsc_calculator.allen_dynes_tc(lambda_eff_b, 0.12, 120)
    assert b > a
