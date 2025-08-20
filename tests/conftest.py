import sys
import os

# Add the project root to the Python path
# This allows tests to import the quantum_rtsc_protocol package
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
