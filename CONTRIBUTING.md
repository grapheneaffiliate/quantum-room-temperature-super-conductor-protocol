# Contributing to Quantum RTSC Protocol

Thank you for your interest in contributing to the Quantum Room Temperature Superconductivity (RTSC) Protocol! This project aims to provide a reproducible, scientifically rigorous pathway to room temperature superconductivity.

## 🔬 Types of Contributions

### **Experimental Data**
- Upload experimental results using our [Experimental Results](/.github/ISSUE_TEMPLATE/experimental_results.md) template
- Include raw data files (CSV format preferred)
- Provide detailed experimental conditions and parameters
- Share both positive and negative results for scientific completeness

### **Code Improvements**
- Bug fixes and performance optimizations
- Enhanced analysis algorithms
- New calculation methods or validation tools
- Documentation improvements

### **Scientific Enhancements**
- Theoretical model refinements
- New artifact detection methods
- Enhanced parameter validation
- Literature review updates

## 📋 Contribution Guidelines

### **Before You Start**
1. Check existing [Issues](../../issues) to avoid duplicate work
2. Review our [RTSC Claim Card](docs/RTSC_Claim_Card.md) for success criteria
3. Read the [Theory Background](docs/Theory_Background.md) for context

### **Code Standards**
- Follow PEP 8 style guidelines
- Add comprehensive docstrings to all functions
- Include unit tests for new functionality
- Ensure all tests pass: `pytest -q`
- Use type hints where appropriate

### **Scientific Standards**
- Cite relevant literature in docstrings
- Include uncertainty estimates for experimental data
- Provide clear methodology descriptions
- Follow our [Safety Protocols](docs/Safety_Protocols.md)

## 🚀 Getting Started

### **Development Setup**
```bash
# Clone the repository
git clone https://github.com/grapheneaffiliate/quantum-rtsc-protocol.git
cd quantum-rtsc-protocol

# Install dependencies
pip install -r requirements.txt

# Run tests to verify setup
pytest -q

# Test core functionality
python tools/rtsc_calculator.py
python tools/mask_generator.py
python analysis/sensitivity.py
```

### **CLI Usage Examples**
```bash
# Calculate Tc for specific parameters
python -m tools.rtsc_calculator calculate --omega 145 --lambda 2.6 --mu 0.10 --fomega 1.2

# Find λ_eff needed for target Tc
python -m tools.rtsc_calculator inverse --tc 300 --omega 140 --mu 0.10

# Run demonstration
python -m tools.rtsc_calculator demo
```

## 📊 Data Contribution Guidelines

### **Experimental Data Format**
Please use our standardized CSV formats:

**α²F(ω) Spectral Data:**
```csv
frequency_meV,alpha2f,mode_assignment
10.0,0.0234,acoustic
80.0,0.0298,plasmon_peak
150.0,0.0823,h_vibron_peak
```

**Transport Data:**
```csv
temperature_K,resistance_ohm,current_A,voltage_V
250,100.5,1e-6,1e-4
300,0.001,1e-6,1e-9
```

**STS/Gap Data:**
```csv
position_um,gap_meV,temperature_K
0.0,65.2,300
1.0,64.8,300
```

### **Required Metadata**
- Sample preparation details
- Measurement conditions (temperature, pressure, field)
- Equipment specifications
- Uncertainty estimates
- Control measurements

## 🔍 Review Process

### **Pull Request Requirements**
1. **Clear Description**: Explain what changes you made and why
2. **Tests**: Include tests for new functionality
3. **Documentation**: Update relevant docs and docstrings
4. **Scientific Validation**: For theoretical changes, provide literature support

### **Review Criteria**
- **Scientific Accuracy**: Calculations must be physically sound
- **Reproducibility**: Methods must be clearly documented
- **Code Quality**: Clean, well-documented, tested code
- **Safety**: Adherence to safety protocols for experimental work

## 🏆 Recognition

### **Contributor Types**
- **Code Contributors**: Listed in repository contributors
- **Data Contributors**: Acknowledged in data files and publications
- **Scientific Contributors**: Co-authorship consideration for significant contributions

### **Citation Guidelines**
If you use this protocol in your research, please cite:
```bibtex
@software{quantum_rtsc_protocol,
  title = {Quantum RTSC Protocol: Room Temperature Superconductivity},
  author = {RTSC Protocol Team},
  year = {2025},
  url = {https://github.com/grapheneaffiliate/quantum-rtsc-protocol},
  version = {v1.0}
}
```

## 🛡️ Safety and Ethics

### **Experimental Safety**
- Follow all [Safety Protocols](docs/Safety_Protocols.md)
- Report safety incidents immediately
- Use proper PPE and ventilation
- Maintain detailed safety logs

### **Scientific Ethics**
- Report all results honestly (positive and negative)
- Acknowledge all contributors appropriately
- Share data and methods openly
- Avoid premature claims without proper validation

## 📞 Getting Help

### **Questions and Support**
- **General Questions**: Open a [Discussion](../../discussions)
- **Bug Reports**: Use our [Bug Report](/.github/ISSUE_TEMPLATE/bug_report.md) template
- **Feature Requests**: Use our [Enhancement Request](/.github/ISSUE_TEMPLATE/enhancement_request.md) template
- **Experimental Help**: Contact the maintainers directly

### **Community Guidelines**
- Be respectful and constructive in all interactions
- Focus on scientific merit and reproducibility
- Help newcomers learn the protocol
- Share knowledge and expertise freely

## 📈 Roadmap Priorities

Current focus areas (see [ROADMAP.md](ROADMAP.md) for details):
1. **Parameter Optimization**: Enhanced f_ω and ω_log tuning
2. **Artifact Detection**: Improved null hypothesis testing
3. **Automation**: Streamlined measurement workflows
4. **Validation**: Independent laboratory replication

---

**Thank you for contributing to the advancement of room temperature superconductivity research!** 🚀

For questions about contributing, please open an issue or contact the maintainers.
