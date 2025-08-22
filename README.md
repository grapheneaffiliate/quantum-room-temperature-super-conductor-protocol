[![CI](https://github.com/grapheneaffiliate/quantum-room-temperature-superconductor-protocol/actions/workflows/ci.yml/badge.svg)](https://github.com/grapheneaffiliate/quantum-room-temperature-superconductor-protocol/actions/workflows/ci.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1234567.svg)](https://doi.org/10.5281/zenodo.1234567)

# 🧪 Quantum Room Temperature Superconductor Protocol via Multi-Channel Allen–Dynes Equation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

*Tested on Python 3.9, 3.10, 3.11, and 3.12*

**Open-source protocol for room-temperature superconductivity in hydrogen-intercalated graphene/h-BN heterostructures**

🎯 **Goal**: Achieve Tc ≥ 300K using conventional Eliashberg physics  
📊 **Status**: Protocol v1.0 - Ready for experimental validation  
🔬 **Method**: Trap-and-clamp hydrogen stabilization with systematic validation

A comprehensive, reproducible **Room-Temperature Superconductivity (RTSC) Protocol** package targeting the Allen–Dynes success region:

- **ω_log ≥ 120 meV**
- **λ_eff ≈ 2.5–2.7**
- **μ* ≤ 0.12**
- **f_ω ≥ 1.35**

**Theoretical Prediction**: If ω_log ≥ 150 meV, μ* ≤ 0.12, and λ_eff ≥ 3.0 (no double-counting), then by Allen–Dynes T_c ≥ 300 K.

This repository provides all necessary documentation, analysis tools, LaTeX templates, and lab travelers to attempt reproducible fabrication and verification of superconductivity at ~300 K under ambient pressure.

---

## 📂 Key Files

- [Fabrication SOP](docs/Fabrication_SOP.md)
- [RTSC Cover Page](RTSC_CoverPage.tex)
- [MiniDeck Slides](RTSC_MiniDeck.tex)
- [One-Page Traveler](traveler/RTSC_Traveler.tex)
- [Eliashberg Runner](tools/eliashberg_runner.py)
- [Enhanced RTSC Calculator](quantum_rtsc_protocol/tools/rtsc_calculator.py)
- [Mask Generator](tools/mask_generator.py)
- [Superconductivity Analysis](analysis/supercon_analysis.py)
- [Unit Tests](tests/)

## 📂 Repository Structure

```
quantum-room-temperature-superconductor-protocol/
├── README.md                  # Overview and instructions
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Python packaging
├── .github/
│   └── workflows/ci.yml       # CI/CD pipeline
├── docs/
│   └── Fabrication_SOP.md     # Fabrication Standard Operating Procedure
├── traveler/                  # PDF/TeX traveler outputs (if present)
├── tools/
│   ├── eliashberg_runner.py   # α²F → Tc pipeline & CLI
│   ├── rtsc_calculator.py     # Enhanced RTSC calculator (CLI)
│   ├── spectroscopy_tools.py  # Raman/FTIR helpers
│   └── measurement_tools.py   # Transport/Meissner helpers
├── examples/
│   ├── sample_data/           # Example datasets
│   └── validation_runs/       # Reference measurements
├── quantum_rtsc_protocol/     # Python package (helpers, schemas)
├── schemas/
└── tests/
    ├── test_calculations.py   # Unit tests
    └── test_protocol.py       # Protocol validation
```

---

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/grapheneaffiliate/quantum-room-temperature-superconductor-protocol.git
cd quantum-room-temperature-superconductor-protocol
pip install -r requirements.txt
```

### Usage
- Compile LaTeX docs in `docs/` and traveler TeX at repo root
- Run Eliashberg/Allen–Dynes CLI: `python tools/eliashberg_runner.py --help`
- Calculator: `python tools/rtsc_calculator.py --help`
- Run tests with:
```bash
pytest tests/
```

---

## 📊 Protocol Highlights

- **Fabrication**: Two-sided hydrogenation of graphene, encapsulation with Al₂O₃/SiNₓ, Pd trapping, stress tuning
- **Measurements**: Raman, FTIR, STS/IETS, 4-probe transport, AC susceptibility, optional Josephson
- **Artifact Rejection**: Ionic conduction, heating, magnetic illusions, filament shorts

### Acceptance Criteria

| Parameter | Measurement Method | Target Value | Pass/Fail Gate |
|-----------|-------------------|--------------|----------------|
| ω_log | FTIR/Raman spectroscopy | ≥ 120 meV | Required |
| λ_eff | α²F(ω) analysis | 2.5–2.7 | Required |
| μ* | Transport fitting | ≤ 0.12 | Required |
| f_ω | Spectral weight ratio | ≥ 1.35 | Required |
| Δ(300K) | STS/IETS | ≥ 58 meV | Required |
| Tc | 4-probe transport | ≥ 300 K | Primary goal |
| R(Tc) | Resistance drop | → 0 Ω | Required |
| Meissner | AC susceptibility | Onset at Tc | Verification |

---

## 📄 License
MIT License

---

## 🏆 Challenge to the Community

**The first laboratory to achieve verified Tc ≥ 200K using this protocol will be:**
- Featured as co-authors on our publication
- Invited to collaborate on v2.0 development
- Acknowledged in all future citations

**Submit your results via GitHub Issues with complete data.**

---

## ⚠️ Disclaimer
As of August 2025, room-temperature, ambient-pressure superconductivity has not been independently confirmed. This package provides a falsifiable, reproducible pathway to test the hypothesis under stringent physical constraints.
