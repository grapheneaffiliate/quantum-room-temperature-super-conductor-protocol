#!/usr/bin/env python
"""Quick test script to verify CI fixes are working."""

import subprocess
import sys

def run_tests():
    """Run the test suite and report results."""
    print("Running quantum-rtsc-protocol test suite...")
    print("=" * 60)
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd="."
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    print("=" * 60)
    if result.returncode == 0:
        print("✅ All tests passed successfully!")
    else:
        print(f"❌ Tests failed with return code: {result.returncode}")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_tests())
