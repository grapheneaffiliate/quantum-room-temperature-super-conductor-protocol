def test_legacy_hyphenated_path_invocation(tmp_path):
    import sys, subprocess, numpy as np
    p = tmp_path / "a2F.csv"
    # Provide sufficient data points for sanitization
    om = np.array([80, 100, 120, 140, 160, 180, 200], float)
    a2f = np.array([0.5, 0.7, 1.0, 0.9, 0.8, 0.6, 0.4], float)
    np.savetxt(p, np.column_stack([om, a2f]), delimiter=",")
    r = subprocess.run([sys.executable, "tools/eliashberg_runner.py",
                        "--alpha2F_csv", str(p), "--mu_star", "0.12"])
    assert r.returncode in (0, 10)
