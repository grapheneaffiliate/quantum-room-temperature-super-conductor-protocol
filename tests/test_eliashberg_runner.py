def test_units_conversion_cm1_to_mev(tmp_path):
    import numpy as np, json, subprocess, sys
    p = tmp_path / "a2F.csv"
    # More data points at 1000 and 1200 cm^-1 (≈124 & 149 meV)
    om = np.array([800, 900, 1000, 1100, 1200, 1300, 1400], float)
    a2f = np.array([0.5, 0.7, 1.0, 0.9, 0.8, 0.6, 0.4], float)
    arr = np.column_stack([om, a2f])
    np.savetxt(p, arr, delimiter=",")
    cmd = [sys.executable, "tools/eliashberg_runner.py", "--alpha2F_csv", str(p),
           "--units", "cm-1", "--mu_star", "0.12", "--json-out", str(tmp_path/"o.json")]
    assert subprocess.run(cmd).returncode in (0,10)
    d = json.load(open(tmp_path/"o.json"))
    assert d["schema_version"] == "ad-screen-1"

def test_multimodality_triggers_exit_code(tmp_path):
    import numpy as np, subprocess, sys
    p = tmp_path / "bimodal.csv"
    om = np.linspace(40,220,1801)
    a = np.exp(-0.5*((om-80)/6)**2) + 0.8*np.exp(-0.5*((om-160)/7)**2)
    np.savetxt(p, np.c_[om, a], delimiter=",")
    r = subprocess.run([sys.executable, "tools/eliashberg_runner.py",
                        "--alpha2F_csv", str(p), "--mu_star", "0.12"], capture_output=True)
    assert r.returncode == 10  # escalate on multimodality
