# shim to maintain backward/CI compatibility with hyphenated path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quantum_rtsc_protocol.tools.eliashberg_runner import main

if __name__ == "__main__":
    sys.exit(main())
