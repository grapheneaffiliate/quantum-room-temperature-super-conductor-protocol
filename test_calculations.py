import pytest
import numpy as np
from analysis.supercon_analysis import weighted_log_average, allen_dynes_tc, gap_to_tc_ratio
from tools.rtsc_calculator import multi_channel_lambda, spectral_weight_factor, validate_acceptance

def test_weighted_log_average():
    freqs = [100, 150, 200]
    weights = [0.2, 0.5, 0.3]
    result = weighted_log_average(freqs, weights)
    assert result > 0
    assert 100 < result < 200

def test_allen_dynes_tc():
    tc = allen_dynes_tc(lambda_eff=2.6, mu_star=0.12, omega_log_mev=130)
    assert tc > 250  # should be in RTSC range

def test_gap_to_tc_ratio():
    ratio = gap_to_tc_ratio(delta_mev=65, tc_k=300)
    assert ratio > 4.5

def test_multi_channel_lambda():
    lam_eff = multi_channel_lambda(2.0, 0.4, 0.2)
    assert np.isclose(lam_eff, 2.6)

def test_spectral_weight_factor():
    f_omega = spectral_weight_factor(0.8, 0.2)
    assert np.isclose(f_omega, 4.0)

def test_validate_acceptance():
    results = validate_acceptance(omega_log=130, delta_mev=65, tc_k=300)
    assert results["omega_log_pass"]
    assert results["gap_pass"]
    assert results["ratio_pass"]
