---
name: Bug Report
about: Report a bug in the RTSC protocol implementation
title: '[BUG] '
labels: bug
assignees: ''
---

## 🐛 Bug Description
A clear and concise description of what the bug is.

## 🔬 Experimental Context
**Protocol Step:** Which part of the protocol were you executing?
- [ ] Fabrication (Day 1-7)
- [ ] Measurement (Day 1-7)
- [ ] Analysis
- [ ] Other: ___________

**Specific Tool/Script:** Which tool encountered the issue?
- [ ] `tools/rtsc_calculator.py`
- [ ] `analysis/supercon_analysis.py`
- [ ] `masks/mask_generator.py`
- [ ] Other: ___________

## 📋 Steps to Reproduce
1. Go to '...'
2. Run command '....'
3. Input parameters '....'
4. See error

## 💻 Expected vs Actual Behavior
**Expected:** What you expected to happen
**Actual:** What actually happened

## 📊 Data and Logs
**Error Message:**
```
Paste error message here
```

**Input Parameters:**
```python
# Paste your input parameters
omega_log = 
lambda_eff = 
mu_star = 
```

**Sample Data:** (if applicable)
- Attach CSV files or data snippets that caused the issue

## 🖥️ Environment
**Operating System:** [e.g., Windows 11, Ubuntu 22.04, macOS 13]
**Python Version:** [e.g., 3.9.7]
**Package Versions:**
```bash
pip list | grep -E "(numpy|scipy|pandas|matplotlib)"
```

## 📸 Screenshots
If applicable, add screenshots to help explain your problem.

## 🔍 Additional Context
Add any other context about the problem here. Include:
- Lab equipment specifications
- Material parameters
- Environmental conditions
- Previous successful runs

## ✅ Checklist
- [ ] I have searched existing issues for duplicates
- [ ] I have included all relevant error messages
- [ ] I have provided sample data if applicable
- [ ] I have specified my environment details
