from quantum_rtsc_protocol.tools import rtsc_calculator

def test_tc_monotonic_lambda():
    # Test with the correct signature: lambda_eff, mu_star, omega_log_mev
    lambda_eff_a = rtsc_calculator.multi_channel_lambda(1.0, 0.5, 0.2)
    lambda_eff_b = rtsc_calculator.multi_channel_lambda(1.2, 0.6, 0.3)
    a = rtsc_calculator.allen_dynes_tc(lambda_eff_a, 0.12, 120)
    b = rtsc_calculator.allen_dynes_tc(lambda_eff_b, 0.12, 120)
    assert b > a
