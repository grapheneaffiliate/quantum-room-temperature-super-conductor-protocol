import pandas as pd
from quantum_rtsc_protocol.analysis import validators

def test_transport_demo():
    df = pd.read_csv("examples/sample_data/iv_4probe.csv")
    res = validators.evaluate_transport(df)
    assert res.passed

def test_suscept_demo():
    df = pd.read_csv("examples/sample_data/ac_susceptibility.csv")
    res = validators.evaluate_susceptibility(df)
    assert res.passed

def test_raman_demo():
    # 2Δ0 ~ 55 meV; sample has a dip near ~52 meV
    df = pd.read_csv("examples/sample_data/raman.csv")
    res = validators.evaluate_raman_gap(df, expected_2delta_mev=55.0, window_mev=12.0)
    assert res.passed
