import pytest
from quantum_rtsc_protocol.tools.rtsc_calculator import allen_dynes_tc, lambda_for_tc

# Golden regression tests
def test_tc_golden_values():
    tc1 = allen_dynes_tc(145, 2.6, 0.10, 1.2)
    assert abs(tc1 - 339.44) < 0.1
    tc2 = allen_dynes_tc(150, 2.54, 0.12, 1.0)
    assert abs(tc2 - 278.53) < 0.1

def test_lambda_inverse():
    lam = lambda_for_tc(300, 140, 0.10, 1.0)
    assert abs(lam - 3.1879) < 0.002
    tc_back = allen_dynes_tc(140, lam, 0.10, 1.0)
    assert abs(tc_back - 300.0) < 0.1

def test_monotonicity():
    base = allen_dynes_tc(140, 2.5, 0.10, 1.0)
    assert allen_dynes_tc(140, 2.6, 0.10, 1.0) > base
    assert allen_dynes_tc(145, 2.5, 0.10, 1.0) > base
    assert allen_dynes_tc(140, 2.5, 0.12, 1.0) < base
    assert allen_dynes_tc(140, 2.5, 0.10, 1.1) > base

def test_denominator_guard():
    with pytest.raises(ValueError):
        allen_dynes_tc(140, 0.1, 0.5, 1.0)
