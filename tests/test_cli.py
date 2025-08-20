import subprocess, sys

def test_cli_runs():
    # Test running the calculator directly as a script
    import pathlib
    script_path = pathlib.Path(__file__).resolve().parents[1] / "tools" / "rtsc_calculator.py"
    subprocess.check_call([sys.executable, str(script_path), "calc", "--omega-log-mev", "135"])
