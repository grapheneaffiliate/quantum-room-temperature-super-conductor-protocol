import json
import subprocess
import sys
import pytest
from pathlib import Path

def test_cli_physics_validation_ranges():
    """Test CLI physics validation with various invalid parameter ranges."""
    
    # Test omega_log out of range (too small)
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log", "5",  # Too small
        "--lambda-val", "2.5",
        "--mu-star", "0.12",
        "--f-omega", "1.35",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 2
    err = json.loads(proc.stderr)
    assert "out of physical range [10, 1000]" in err["error"]
    
    # Test omega_log out of range (too large)
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log", "2000",  # Too large
        "--lambda-val", "2.5",
        "--mu-star", "0.12",
        "--f-omega", "1.35",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 2
    err = json.loads(proc.stderr)
    assert "out of physical range [10, 1000]" in err["error"]
    
    # Test lambda too large
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log", "120",
        "--lambda-val", "15",  # Too large
        "--mu-star", "0.12",
        "--f-omega", "1.35",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 2
    err = json.loads(proc.stderr)
    assert "unrealistically large" in err["error"]
    
    # Test mu* too small
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log", "120",
        "--lambda-val", "2.5",
        "--mu-star", "0.005",  # Too small
        "--f-omega", "1.35",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 2
    err = json.loads(proc.stderr)
    assert "must be in (0.01, 0.3)" in err["error"]
    
    # Test mu* too large
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log", "120",
        "--lambda-val", "2.5",
        "--mu-star", "0.35",   # Too large
        "--f-omega", "1.35",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 2
    err = json.loads(proc.stderr)
    assert "must be in (0.01, 0.3)" in err["error"]
    
    # Test f_omega out of range
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log", "120",
        "--lambda-val", "2.5",
        "--mu-star", "0.12",
        "--f-omega", "0.8",   # Too small
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 2
    err = json.loads(proc.stderr)
    assert "out of allowed range [1.0, 1.5]" in err["error"]

def test_cli_denominator_validation():
    """Test Allen-Dynes denominator validation with critical parameter combinations."""
    
    # Test parameters that make denominator negative
    # For λ=2.0, critical μ* = 2.0/(1+0.62*2.0) = 2.0/2.24 ≈ 0.893
    # So μ*=0.9 should make denominator negative
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log", "120",
        "--lambda-val", "2.0",
        "--mu-star", "0.9",  # This should make denominator negative
        "--f-omega", "1.35",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 2
    err = json.loads(proc.stderr)
    assert "Allen-Dynes denominator" in err["error"]
    assert "≤ 0" in err["error"]
    assert "need μ* <" in err["error"]
    
    # Test parameters that make denominator very small (should warn but succeed)
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log", "120",
        "--lambda-val", "5.0",
        "--mu-star", "0.29",  # Makes small but positive denominator
        "--f-omega", "1.35",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    # Should succeed but with warning (warnings go to stderr in Python)
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert out["status"] == "ok"
    assert "derived" in out
    assert out["derived"]["denominator"] < 0.1  # Verify small denominator

def test_cli_exponential_underflow_protection():
    """Test protection against exponential underflow in Allen-Dynes formula."""
    
    # Test parameters that would cause exponential underflow
    # Need to use mu* > 0.01 to pass the range check first
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log", "120",
        "--lambda-val", "10.0",  # Very large lambda
        "--mu-star", "0.02",     # Small but valid mu* 
        "--f-omega", "1.35",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 2
    err = json.loads(proc.stderr)
    assert "Exponential term too small" in err["error"]
    assert "negligible Tc" in err["error"]

def test_cli_enhanced_error_messages():
    """Test that enhanced error messages provide helpful context."""
    
    # Test lambda validation with context
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log", "120",
        "--lambda-val", "-1.0",  # Negative
        "--mu-star", "0.12",
        "--f-omega", "1.35",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 2
    err = json.loads(proc.stderr)
    assert "lambda=-1.0" in err["error"]
    assert "electron-phonon coupling strength" in err["error"]
    
    # Test mu* validation with context
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log", "120",
        "--lambda-val", "2.5",
        "--mu-star", "0.4",    # Invalid mu*
        "--f-omega", "1.35",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 2
    err = json.loads(proc.stderr)
    assert "mu*=0.4" in err["error"]
    assert "Coulomb pseudopotential range" in err["error"]
    
    # Test f_omega validation with context
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log", "120",
        "--lambda-val", "2.5",
        "--mu-star", "0.12",
        "--f-omega", "2.0",   # Invalid f_omega
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 2
    err = json.loads(proc.stderr)
    assert "f_omega=2.0" in err["error"]
    assert "spectral shape factor" in err["error"]

def test_cli_valid_parameters_still_work():
    """Ensure that valid parameters still work after enhanced validation."""
    
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log", "120",
        "--lambda-val", "2.5",
        "--mu-star", "0.12",
        "--f-omega", "1.35",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    
    out = json.loads(proc.stdout)
    assert out["status"] == "ok"
    assert "results" in out
    assert "Tc_K" in out["results"]
    assert "derived" in out
    assert "denominator" in out["derived"]
    assert out["derived"]["denominator"] > 0
    
    # Verify the calculation is reasonable
    tc = out["results"]["Tc_K"]
    assert 250 < tc < 350  # Reasonable range for these parameters

def test_cli_boundary_conditions():
    """Test CLI behavior at parameter boundaries."""
    
    # Test minimum valid omega_log
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log", "10",     # Minimum
        "--lambda-val", "2.5",
        "--mu-star", "0.12",
        "--f-omega", "1.35",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    
    # Test maximum valid omega_log
    cmd[4] = "1000"  # Maximum
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    
    # Test minimum valid mu*
    cmd[4] = "120"   # Reset omega_log
    cmd[8] = "0.011" # Just above minimum
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    
    # Test maximum valid f_omega
    cmd[8] = "0.12"  # Reset mu*
    cmd[10] = "1.5"  # Maximum
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
