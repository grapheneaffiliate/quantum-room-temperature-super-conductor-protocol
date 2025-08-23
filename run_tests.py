#!/usr/bin/env python
"""Run tests and capture output for debugging CI issues."""

import subprocess
import sys
import os

def run_command(cmd, cwd="."):
    """Run a command and return output."""
    print(f"Running: {cmd}")
    print("=" * 60)
    
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=cwd
    )
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    print(f"Return code: {result.returncode}")
    print("=" * 60)
    return result.returncode

def main():
    """Run all CI tests."""
    os.environ['MPLBACKEND'] = 'Agg'
    
    print("Testing quantum-rtsc-protocol CI pipeline")
    print("=" * 60)
    
    # First, run unit tests
    print("\n1. Running unit tests...")
    ret = run_command("python -m pytest tests/ -v --tb=short")
    if ret != 0:
        print(f"❌ Unit tests failed with code {ret}")
        return ret
    
    # Then run the demo pipeline
    print("\n2. Running demo pipeline...")
    ret = run_command("make demo")
    if ret != 0:
        print(f"❌ Demo pipeline failed with code {ret}")
        return ret
    
    # Check if output files exist
    print("\n3. Checking output files...")
    files_to_check = [
        "out/demo/rtsc_results.json",
        "out/demo/rtsc_analysis_report.md",
        "out/demo/rtsc_analysis_dashboard.png"
    ]
    
    for file in files_to_check:
        if os.path.exists(file) and os.path.getsize(file) > 0:
            print(f"✅ {file} exists and is not empty")
        else:
            print(f"❌ {file} is missing or empty")
            return 1
    
    # Validate JSON output
    print("\n4. Validating JSON output...")
    try:
        import json
        with open('out/demo/rtsc_results.json') as f:
            data = json.load(f)
        
        required_fields = ['timestamp', 'tc_estimate_K', 'success_probability']
        for field in required_fields:
            if field in data:
                print(f"✅ Field '{field}' found in JSON")
            else:
                print(f"❌ Field '{field}' missing from JSON")
                return 1
    except Exception as e:
        print(f"❌ Error validating JSON: {e}")
        return 1
    
    print("\n✅ All CI tests passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
