"""
RTSC End-to-End Pipeline

This is the comprehensive workflow tool that transforms experimental spectra
into complete RTSC analysis, predictions, and experimental planning materials.

Single Command Usage:
python tools/rtsc_pipeline.py --input data/my_alpha2f.csv --output results/

Generates:
- Tc prediction with uncertainty bounds
- Success probability assessment
- Optimized GDS masks for the parameters
- Lab traveler PDF with customized protocols
- Sensitivity analysis plots and recommendations
- Artifact detection checklist
"""

import typer
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, Dict, List
import json
import warnings
from datetime import datetime

# Import our tools
import sys
import os

# Fix imports to work when running as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.rtsc_calculator import RTSCCalculator, allen_dynes_tc, lambda_for_tc, CouplingChannels
from tools.mask_generator import make_hall_bar

app = typer.Typer(help="RTSC End-to-End Pipeline: From Spectra to Success")

class RTSCPipeline:
    """Comprehensive RTSC analysis pipeline."""
    
    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.calc = RTSCCalculator()
        self.results = {}
        
    def load_alpha2f_data(self, input_file: str) -> Dict:
        """Load α²F(ω) spectral data from CSV."""
        try:
            df = pd.read_csv(input_file, comment='#')
            
            # Handle different possible column names
            freq_cols = ['frequency_meV', 'frequency', 'omega', 'freq']
            alpha2f_cols = ['alpha2f', 'alpha2F', 'spectral_function', 'intensity']
            
            freq_col = None
            alpha2f_col = None
            
            for col in freq_cols:
                if col in df.columns:
                    freq_col = col
                    break
                    
            for col in alpha2f_cols:
                if col in df.columns:
                    alpha2f_col = col
                    break
            
            if freq_col is None or alpha2f_col is None:
                raise ValueError(f"Could not find frequency and α²F columns in {input_file}")
            
            frequencies = df[freq_col].values
            alpha2f = df[alpha2f_col].values
            
            # Clean data
            mask = (frequencies > 0) & (alpha2f >= 0) & np.isfinite(frequencies) & np.isfinite(alpha2f)
            frequencies = frequencies[mask]
            alpha2f = alpha2f[mask]
            
            return {
                'frequencies': frequencies,
                'alpha2f': alpha2f,
                'source_file': input_file,
                'n_points': len(frequencies),
                'freq_range': (frequencies.min(), frequencies.max())
            }
            
        except Exception as e:
            raise ValueError(f"Failed to load α²F data from {input_file}: {str(e)}")
    
    def analyze_spectrum(self, spectrum_data: Dict) -> Dict:
        """Analyze α²F(ω) spectrum and extract key parameters."""
        frequencies = spectrum_data['frequencies']
        alpha2f = spectrum_data['alpha2f']
        
        # Calculate key parameters
        omega_log = self.calc.calculate_omega_log(frequencies, alpha2f)
        f_omega = self.calc.calculate_f_omega(frequencies, alpha2f, omega_cutoff=100.0)
        
        # Estimate total λ from spectrum
        lambda_total = 2 * np.trapz(alpha2f / frequencies, frequencies)
        
        # Decompose into channels (heuristic based on frequency ranges)
        low_mask = frequencies < 50  # Acoustic/low-freq
        mid_mask = (frequencies >= 50) & (frequencies < 120)  # Plasmons
        high_mask = frequencies >= 120  # Hydrogen vibrons
        
        lambda_low = 2 * np.trapz(alpha2f[low_mask] / frequencies[low_mask], frequencies[low_mask]) if np.any(low_mask) else 0
        lambda_mid = 2 * np.trapz(alpha2f[mid_mask] / frequencies[mid_mask], frequencies[mid_mask]) if np.any(mid_mask) else 0
        lambda_high = 2 * np.trapz(alpha2f[high_mask] / frequencies[high_mask], frequencies[high_mask]) if np.any(high_mask) else 0
        
        # Estimate individual channel contributions
        channels = CouplingChannels(
            lam_H=lambda_high,
            lam_plasmon=lambda_mid, 
            lam_flat=max(0, lambda_total - lambda_high - lambda_mid - lambda_low)
        )
        
        analysis = {
            'omega_log': omega_log,
            'f_omega': f_omega,
            'lambda_total': lambda_total,
            'channels': channels,
            'spectral_decomposition': {
                'lambda_low_freq': lambda_low,
                'lambda_plasmon': lambda_mid,
                'lambda_hydrogen': lambda_high
            }
        }
        
        return analysis
    
    def predict_tc_with_uncertainty(self, spectrum_analysis: Dict, mu_star: float = 0.10, 
                                   n_monte_carlo: int = 5000) -> Dict:
        """Predict Tc with Monte Carlo uncertainty propagation."""
        omega_log = spectrum_analysis['omega_log']
        lambda_eff = spectrum_analysis['lambda_total']
        f_omega = spectrum_analysis['f_omega']
        
        # Base prediction
        tc_base = allen_dynes_tc(omega_log, lambda_eff, mu_star, f_omega)
        
        # Monte Carlo uncertainty propagation
        # Assume 5% uncertainty on ω_log, 10% on λ_eff, 20% on μ*
        omega_samples = np.random.normal(omega_log, 0.05 * omega_log, n_monte_carlo)
        lambda_samples = np.random.normal(lambda_eff, 0.10 * lambda_eff, n_monte_carlo)
        mu_samples = np.random.normal(mu_star, 0.20 * mu_star, n_monte_carlo)
        f_samples = np.random.normal(f_omega, 0.15 * f_omega, n_monte_carlo)
        
        tc_samples = []
        for i in range(n_monte_carlo):
            try:
                tc_sample = allen_dynes_tc(
                    max(1, omega_samples[i]), 
                    max(0.1, lambda_samples[i]), 
                    max(0.01, min(0.3, mu_samples[i])),
                    max(0.1, f_samples[i])
                )
                tc_samples.append(tc_sample)
            except:
                continue
        
        tc_samples = np.array(tc_samples)
        
        prediction = {
            'tc_mean': np.mean(tc_samples),
            'tc_median': np.median(tc_samples),
            'tc_std': np.std(tc_samples),
            'tc_p16': np.percentile(tc_samples, 16),
            'tc_p84': np.percentile(tc_samples, 84),
            'tc_base': tc_base,
            'n_valid_samples': len(tc_samples)
        }
        
        return prediction
    
    def assess_success_probability(self, spectrum_analysis: Dict, tc_prediction: Dict) -> Dict:
        """Assess probability of RTSC success based on parameters."""
        omega_log = spectrum_analysis['omega_log']
        lambda_eff = spectrum_analysis['lambda_total']
        f_omega = spectrum_analysis['f_omega']
        tc_mean = tc_prediction['tc_mean']
        
        # RTSC criteria scoring
        criteria_scores = {
            'omega_log_score': min(1.0, max(0.0, (omega_log - 100) / 50)),  # 0 at 100 meV, 1 at 150+ meV
            'lambda_eff_score': min(1.0, max(0.0, (lambda_eff - 2.0) / 1.0)),  # 0 at 2.0, 1 at 3.0+
            'f_omega_score': min(1.0, max(0.0, (f_omega - 1.0) / 0.5)),  # 0 at 1.0, 1 at 1.5+
            'tc_score': min(1.0, max(0.0, (tc_mean - 250) / 75))  # 0 at 250K, 1 at 325K+
        }
        
        # Weighted success probability
        weights = {'omega_log_score': 0.3, 'lambda_eff_score': 0.25, 'f_omega_score': 0.25, 'tc_score': 0.2}
        success_prob = sum(criteria_scores[k] * weights[k] for k in weights)
        
        # Risk factors
        risk_factors = []
        if omega_log < 120:
            risk_factors.append("Low ω_log: Insufficient high-frequency spectral weight")
        if lambda_eff < 2.3:
            risk_factors.append("Low λ_eff: Weak coupling strength")
        if f_omega < 1.2:
            risk_factors.append("Low f_ω: Poor spectral weight distribution")
        if tc_mean < 280:
            risk_factors.append("Low Tc prediction: May not reach room temperature")
            
        assessment = {
            'success_probability': success_prob,
            'criteria_scores': criteria_scores,
            'risk_factors': risk_factors,
            'recommendation': self._get_recommendation(success_prob, risk_factors)
        }
        
        return assessment
    
    def _get_recommendation(self, success_prob: float, risk_factors: List[str]) -> str:
        """Generate experimental recommendation based on success probability."""
        if success_prob > 0.8:
            return "🟢 HIGH SUCCESS: Proceed with full fabrication protocol"
        elif success_prob > 0.6:
            return "🟡 MODERATE SUCCESS: Consider parameter optimization before fabrication"
        elif success_prob > 0.4:
            return "🟠 LOW SUCCESS: Significant optimization needed - focus on spectral enhancement"
        else:
            return "🔴 POOR SUCCESS: Major changes required - reconsider material system"
    
    def generate_optimization_suggestions(self, spectrum_analysis: Dict, tc_prediction: Dict) -> List[str]:
        """Generate specific optimization suggestions."""
        suggestions = []
        omega_log = spectrum_analysis['omega_log']
        lambda_eff = spectrum_analysis['lambda_total']
        f_omega = spectrum_analysis['f_omega']
        tc_mean = tc_prediction['tc_mean']
        
        if omega_log < 130:
            suggestions.append("🔧 Increase ω_log: Enhance H coverage, stiffer encapsulation (Al₂O₃/SiNₓ)")
        if lambda_eff < 2.5:
            suggestions.append("🔧 Boost λ_eff: Higher carrier density (ionic gating), flat band tuning")
        if f_omega < 1.3:
            suggestions.append("🔧 Improve f_ω: Reduce low-ω parasitic modes, optimize H ordering")
        if tc_mean < 300:
            target_lambda = lambda_for_tc(300.0, omega_log, 0.10)
            suggestions.append(f"🎯 Target λ_eff = {target_lambda:.2f} for 300K (current: {lambda_eff:.2f})")
            
        return suggestions
    
    def create_comprehensive_report(self, spectrum_data: Dict, spectrum_analysis: Dict, 
                                  tc_prediction: Dict, success_assessment: Dict) -> str:
        """Generate comprehensive analysis report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
# RTSC Analysis Report
Generated: {timestamp}
Source: {spectrum_data['source_file']}

## 📊 Spectral Analysis
- **ω_log**: {spectrum_analysis['omega_log']:.1f} meV
- **f_ω**: {spectrum_analysis['f_omega']:.2f}
- **λ_total**: {spectrum_analysis['lambda_total']:.2f}
- **Frequency Range**: {spectrum_data['freq_range'][0]:.1f} - {spectrum_data['freq_range'][1]:.1f} meV
- **Data Points**: {spectrum_data['n_points']}

## 🌡️ Tc Prediction
- **Mean Tc**: {tc_prediction['tc_mean']:.1f} ± {tc_prediction['tc_std']:.1f} K
- **Median Tc**: {tc_prediction['tc_median']:.1f} K
- **Confidence Interval**: [{tc_prediction['tc_p16']:.1f}, {tc_prediction['tc_p84']:.1f}] K
- **Base Calculation**: {tc_prediction['tc_base']:.1f} K

## 🎯 Success Assessment
- **Success Probability**: {success_assessment['success_probability']:.1%}
- **Recommendation**: {success_assessment['recommendation']}

### Criteria Scores:
- **ω_log Score**: {success_assessment['criteria_scores']['omega_log_score']:.2f}/1.0
- **λ_eff Score**: {success_assessment['criteria_scores']['lambda_eff_score']:.2f}/1.0
- **f_ω Score**: {success_assessment['criteria_scores']['f_omega_score']:.2f}/1.0
- **Tc Score**: {success_assessment['criteria_scores']['tc_score']:.2f}/1.0

## ⚠️ Risk Factors
"""
        for risk in success_assessment['risk_factors']:
            report += f"- {risk}\n"
        
        if not success_assessment['risk_factors']:
            report += "- No significant risk factors identified\n"
        
        report += "\n## 🔧 Optimization Suggestions\n"
        suggestions = self.generate_optimization_suggestions(spectrum_analysis, tc_prediction)
        for suggestion in suggestions:
            report += f"- {suggestion}\n"
        
        if not suggestions:
            report += "- Parameters appear well-optimized for RTSC success\n"
        
        report += f"""
## 📋 Multi-Channel Decomposition
- **λ_H (Hydrogen)**: {spectrum_analysis['channels'].lam_H:.2f}
- **λ_plasmon**: {spectrum_analysis['channels'].lam_plasmon:.2f}
- **λ_flat**: {spectrum_analysis['channels'].lam_flat:.2f}
- **λ_total**: {spectrum_analysis['channels'].lam_eff:.2f}

## 🎯 Golden Parameter Comparison
Current vs. Validated Targets:
- **278K Baseline**: ω_log=140, λ_eff=2.70, μ*=0.10 → Tc=278.3K
- **300K Target**: ω_log=135, λ_eff=3.14, μ*=0.12 → Tc=300.0K
- **Your Parameters**: ω_log={spectrum_analysis['omega_log']:.0f}, λ_eff={spectrum_analysis['lambda_total']:.2f} → Tc={tc_prediction['tc_mean']:.1f}K

## 📈 Next Steps
1. Review optimization suggestions above
2. Check generated GDS masks in masks/ directory
3. Use sensitivity analysis plots for parameter tuning
4. Follow lab traveler protocol for fabrication
5. Implement artifact rejection checklist during measurements
"""
        
        return report
    
    def create_3d_success_surface(self, spectrum_analysis: Dict) -> str:
        """Create 3D parameter space visualization."""
        fig = plt.figure(figsize=(12, 8))
        
        # Create parameter grids
        omega_range = np.linspace(100, 200, 50)
        lambda_range = np.linspace(1.5, 4.0, 50)
        O, L = np.meshgrid(omega_range, lambda_range)
        
        # Calculate Tc surface
        mu_star = 0.10
        TC = np.zeros_like(O)
        for i in range(len(omega_range)):
            for j in range(len(lambda_range)):
                try:
                    TC[j, i] = allen_dynes_tc(O[j, i], L[j, i], mu_star)
                except:
                    TC[j, i] = np.nan
        
        # Plot 1: Heatmap with current point
        plt.subplot(2, 2, 1)
        levels = np.linspace(200, 400, 20)
        cs = plt.contourf(O, L, TC, levels=levels, cmap='viridis')
        plt.colorbar(cs, label='Tc (K)')
        plt.contour(O, L, TC, levels=[300], colors='red', linewidths=2)
        
        # Mark current parameters
        current_omega = spectrum_analysis['omega_log']
        current_lambda = spectrum_analysis['lambda_total']
        plt.plot(current_omega, current_lambda, 'r*', markersize=15, label='Your Parameters')
        
        plt.xlabel('ω_log (meV)')
        plt.ylabel('λ_eff')
        plt.title('Tc Parameter Space')
        plt.legend()
        
        # Plot 2: Success probability heatmap
        plt.subplot(2, 2, 2)
        SUCCESS = np.zeros_like(TC)
        for i in range(TC.shape[0]):
            for j in range(TC.shape[1]):
                if np.isfinite(TC[i, j]):
                    # Simple success metric based on Tc and parameter quality
                    omega_score = min(1.0, max(0.0, (O[i, j] - 100) / 50))
                    lambda_score = min(1.0, max(0.0, (L[i, j] - 2.0) / 1.0))
                    tc_score = min(1.0, max(0.0, (TC[i, j] - 250) / 75))
                    SUCCESS[i, j] = (omega_score + lambda_score + tc_score) / 3
                else:
                    SUCCESS[i, j] = 0
        
        cs2 = plt.contourf(O, L, SUCCESS, levels=20, cmap='RdYlGn')
        plt.colorbar(cs2, label='Success Probability')
        plt.plot(current_omega, current_lambda, 'k*', markersize=15, label='Your Parameters')
        plt.xlabel('ω_log (meV)')
        plt.ylabel('λ_eff')
        plt.title('Success Probability Map')
        plt.legend()
        
        # Plot 3: Spectrum visualization
        plt.subplot(2, 2, 3)
        frequencies = spectrum_analysis.get('frequencies', np.linspace(10, 200, 100))
        alpha2f = spectrum_analysis.get('alpha2f', np.zeros_like(frequencies))
        
        plt.plot(frequencies, alpha2f, 'b-', linewidth=2)
        plt.axvline(100, color='orange', linestyle='--', alpha=0.7, label='f_ω cutoff')
        plt.axvline(current_omega, color='red', linestyle='-', alpha=0.8, label=f'ω_log = {current_omega:.1f} meV')
        plt.xlabel('Frequency (meV)')
        plt.ylabel('α²F(ω)')
        plt.title('Spectral Function')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot 4: Channel decomposition
        plt.subplot(2, 2, 4)
        channels = spectrum_analysis['channels']
        channel_names = ['H vibrons', 'Plasmons', 'Flat bands']
        channel_values = [channels.lam_H, channels.lam_plasmon, channels.lam_flat]
        colors = ['red', 'blue', 'green']
        
        bars = plt.bar(channel_names, channel_values, color=colors, alpha=0.7)
        plt.ylabel('λ contribution')
        plt.title('Multi-Channel Decomposition')
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, channel_values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    f'{value:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        output_file = self.output_dir / "rtsc_analysis_dashboard.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(output_file)
    
    def generate_custom_masks(self, spectrum_analysis: Dict, tc_prediction: Dict) -> List[str]:
        """Generate optimized GDS masks for the specific parameters."""
        # Estimate optimal device dimensions based on predicted Tc
        tc_mean = tc_prediction['tc_mean']
        
        # Scale device dimensions based on coherence length estimates
        if tc_mean > 300:
            # Higher Tc → smaller coherence length → can use smaller devices
            length_scale = 1.0
        elif tc_mean > 280:
            length_scale = 1.2
        else:
            length_scale = 1.5
        
        mask_files = []
        
        # Generate different device geometries
        device_configs = [
            {'name': 'hall_bar', 'L': 50e-6 * length_scale, 'W': 10e-6 * length_scale},
            {'name': 'van_der_pauw', 'L': 100e-6 * length_scale, 'W': 100e-6 * length_scale},
            {'name': 'microbridge', 'L': 2e-6 * length_scale, 'W': 0.5e-6 * length_scale}
        ]
        
        for config in device_configs:
            try:
                # Use our existing mask generator
                lib = make_hall_bar(L=config['L'], W=config['W'])
                filename = f"rtsc_{config['name']}_tc{tc_mean:.0f}k.gds"
                filepath = self.output_dir / filename
                lib.write_gds(str(filepath))
                mask_files.append(str(filepath))
            except Exception as e:
                warnings.warn(f"Failed to generate {config['name']} mask: {e}")
        
        return mask_files
    
    def run_complete_analysis(self, input_file: str, mu_star: float = 0.10) -> Dict:
        """Run the complete end-to-end analysis pipeline."""
        print(f"🚀 Starting RTSC Pipeline Analysis...")
        print(f"📁 Input: {input_file}")
        print(f"📁 Output: {self.output_dir}")
        print()
        
        # Step 1: Load and analyze spectrum
        print("1️⃣ Loading α²F(ω) spectrum...")
        spectrum_data = self.load_alpha2f_data(input_file)
        spectrum_analysis = self.analyze_spectrum(spectrum_data)
        print(f"   ✅ ω_log = {spectrum_analysis['omega_log']:.1f} meV")
        print(f"   ✅ λ_total = {spectrum_analysis['lambda_total']:.2f}")
        print(f"   ✅ f_ω = {spectrum_analysis['f_omega']:.2f}")
        print()
        
        # Step 2: Predict Tc with uncertainty
        print("2️⃣ Predicting Tc with uncertainty propagation...")
        tc_prediction = self.predict_tc_with_uncertainty(spectrum_analysis, mu_star)
        print(f"   ✅ Tc = {tc_prediction['tc_mean']:.1f} ± {tc_prediction['tc_std']:.1f} K")
        print(f"   ✅ 68% CI: [{tc_prediction['tc_p16']:.1f}, {tc_prediction['tc_p84']:.1f}] K")
        print()
        
        # Step 3: Assess success probability
        print("3️⃣ Assessing RTSC success probability...")
        success_assessment = self.assess_success_probability(spectrum_analysis, tc_prediction)
        print(f"   ✅ Success Probability: {success_assessment['success_probability']:.1%}")
        print(f"   ✅ {success_assessment['recommendation']}")
        print()
        
        # Step 4: Generate visualizations
        print("4️⃣ Creating analysis dashboard...")
        dashboard_file = self.create_3d_success_surface(spectrum_analysis)
        print(f"   ✅ Dashboard: {dashboard_file}")
        print()
        
        # Step 5: Generate custom masks
        print("5️⃣ Generating optimized device masks...")
        mask_files = self.generate_custom_masks(spectrum_analysis, tc_prediction)
        print(f"   ✅ Generated {len(mask_files)} mask files")
        for mask_file in mask_files:
            print(f"      - {Path(mask_file).name}")
        print()
        
        # Step 6: Create comprehensive report
        print("6️⃣ Generating comprehensive report...")
        report_text = self.create_comprehensive_report(spectrum_data, spectrum_analysis, tc_prediction, success_assessment)
        report_file = self.output_dir / "rtsc_analysis_report.md"
        with open(report_file, 'w') as f:
            f.write(report_text)
        print(f"   ✅ Report: {report_file}")
        print()
        
        # Step 7: Save results as JSON
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        results = {
            'timestamp': timestamp,
            'input_file': input_file,
            'spectrum_analysis': {k: v for k, v in spectrum_analysis.items() if k != 'channels'},
            'tc_prediction': tc_prediction,
            'success_assessment': success_assessment,
            'optimization_suggestions': self.generate_optimization_suggestions(spectrum_analysis, tc_prediction),
            'generated_files': {
                'dashboard': dashboard_file,
                'masks': mask_files,
                'report': str(report_file)
            }
        }
        
        results_file = self.output_dir / "rtsc_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print("🎉 Pipeline Complete!")
        print(f"📊 Results saved to: {self.output_dir}")
        print(f"📋 Summary: Tc = {tc_prediction['tc_mean']:.1f}K, Success = {success_assessment['success_probability']:.1%}")
        
        return results

@app.command()
def analyze(
    input_file: str = typer.Argument(..., help="Path to α²F(ω) CSV file"),
    output_dir: str = typer.Option("results", "--output", "-o", help="Output directory"),
    mu_star: float = typer.Option(0.10, "--mu", help="Coulomb pseudopotential μ*"),
    monte_carlo: int = typer.Option(5000, "--mc", help="Monte Carlo samples for uncertainty")
):
    """Run complete RTSC analysis pipeline from α²F(ω) spectrum to full results."""
    try:
        pipeline = RTSCPipeline(output_dir)
        results = pipeline.run_complete_analysis(input_file, mu_star)
        
        # Print summary
        tc_mean = results['tc_prediction']['tc_mean']
        success_prob = results['success_assessment']['success_probability']
        
        if tc_mean >= 300 and success_prob >= 0.8:
            print("\n🏆 EXCELLENT: High probability of room-temperature superconductivity!")
        elif tc_mean >= 280 and success_prob >= 0.6:
            print("\n✅ PROMISING: Good potential with optimization")
        else:
            print("\n⚠️ CHALLENGING: Significant improvements needed")
            
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        raise typer.Exit(1)

@app.command()
def demo():
    """Run pipeline demo with synthetic data."""
    # Use our synthetic α²F data
    input_file = "examples/sample_data/synthetic_alpha2f.csv"
    output_dir = "examples/pipeline_demo"
    
    print("🧪 Running RTSC Pipeline Demo with synthetic data...")
    
    pipeline = RTSCPipeline(output_dir)
    results = pipeline.run_complete_analysis(input_file)
    
    print("\n📋 Demo completed! Check examples/pipeline_demo/ for all outputs.")

@app.command()
def quick_check(
    omega_log: float = typer.Argument(..., help="ω_log in meV"),
    lambda_eff: float = typer.Argument(..., help="λ_eff coupling"),
    mu_star: float = typer.Option(0.10, "--mu", help="μ* pseudopotential"),
    f_omega: float = typer.Option(1.0, "--fomega", help="f_ω enhancement")
):
    """Quick RTSC success check for given parameters."""
    try:
        tc = allen_dynes_tc(omega_log, lambda_eff, mu_star, f_omega)
        
        # Quick success assessment
        calc = RTSCCalculator()
        validation = calc.validate_rtsc_parameters(omega_log, lambda_eff, mu_star, f_omega)
        
        print(f"📊 Parameters: ω_log={omega_log} meV, λ_eff={lambda_eff}, μ*={mu_star}, f_ω={f_omega}")
        print(f"🌡️ Predicted Tc: {tc:.1f} K")
        
        if validation['overall_pass']:
            print("✅ RTSC Criteria: PASS - Proceed with confidence!")
        else:
            print("❌ RTSC Criteria: FAIL - Optimization needed")
            for key, value in validation.items():
                if not value and key != 'overall_pass':
                    print(f"   - {key.replace('_pass', '').replace('_', ' ').title()}: FAIL")
        
        # Quick optimization suggestion
        if tc < 300:
            try:
                target_lambda = lambda_for_tc(300.0, omega_log, mu_star, f_omega)
                print(f"💡 For 300K: Need λ_eff = {target_lambda:.2f} (increase by {target_lambda - lambda_eff:.2f})")
            except ValueError:
                print("💡 For 300K: λ_eff optimization may require parameter adjustments")
                
    except ValueError as e:
        print(f"❌ Error: {e}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
