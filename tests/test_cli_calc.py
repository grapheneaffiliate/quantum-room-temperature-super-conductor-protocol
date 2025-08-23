import json
import subprocess
import sys
from pathlib import Path
import pytest

def test_cli_calc_synthetic():
    """Test CLI with synthetic parameters that should give Tc ≈ 298.15 K."""
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log",
        "120",
        "--omega-units",
        "meV",
        "--lambda-val",
        "2.5",
        "--mu-star",
        "0.12",
        "--f-omega",
        "1.35",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, f"CLI failed: stderr={proc.stderr}"
    
    # Parse JSON output
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        pytest.fail(f"CLI output is not valid JSON: {e}\nOutput: {proc.stdout}")
    
    # Validate structure
    assert "results" in out, "Missing 'results' key in output"
    assert "Tc_K" in out["results"], "Missing 'Tc_K' in results"
    assert "status" in out, "Missing 'status' key in output"
    assert out["status"] == "ok", f"Expected status 'ok', got '{out['status']}'"
    
    # Validate calculation: expected base calc: ~220.85 * 1.35 = ~298.15
    tc = out["results"]["Tc_K"]
    expected_tc = 298.15
    tolerance = 0.2
    assert abs(tc - expected_tc) < tolerance, f"Tc = {tc:.2f} K, expected ~{expected_tc} K (tolerance ±{tolerance})"

def test_cli_calc_error_handling():
    """Test CLI error handling with invalid inputs."""
    # Test negative lambda
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log",
        "120",
        "--lambda-val",
        "-1.0",
        "--mu-star",
        "0.12",
        "--f-omega",
        "1.35",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 2, "Expected non-zero exit code for invalid lambda"
    
    # Parse error JSON from stderr
    try:
        err = json.loads(proc.stderr)
        assert err["status"] == "error"
        assert "lambda=-1.0 must be > 0" in err["error"]
    except json.JSONDecodeError:
        pytest.fail(f"Error output is not valid JSON: {proc.stderr}")

def test_cli_calc_units_conversion():
    """Test CLI with omega_log in Kelvin units."""
    # 120 meV ≈ 1392.54 K
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log",
        "1392.54",
        "--omega-units",
        "K",
        "--lambda-val",
        "2.5",
        "--mu-star",
        "0.12",
        "--f-omega",
        "1.35",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, f"CLI failed: stderr={proc.stderr}"
    
    out = json.loads(proc.stdout)
    tc = out["results"]["Tc_K"]
    # Should give same result as meV test
    expected_tc = 298.15
    tolerance = 0.2
    assert abs(tc - expected_tc) < tolerance, f"Tc = {tc:.2f} K, expected ~{expected_tc} K with K units"

def test_cli_calc_provenance():
    """Test that CLI includes provenance information."""
    cmd = [
        sys.executable,
        "-m",
        "quantum_rtsc_protocol.cli",
        "calc",
        "--omega-log",
        "120",
        "--lambda-val",
        "2.5",
        "--mu-star",
        "0.12",
        "--f-omega",
        "1.35",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    
    out = json.loads(proc.stdout)
    assert "provenance" in out
    assert "timestamp_utc" in out["provenance"]
    assert "git_sha" in out["provenance"]
    # git_sha can be None if not in a git repo
    assert isinstance(out["provenance"]["git_sha"], (str, type(None)))
