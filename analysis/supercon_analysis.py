"""
Superconductivity Analysis Tools for RTSC Protocol

This module provides higher-level analysis workflows built on top of the
RTSCCalculator. It includes data visualization, parameter sweeps, and
integration with experimental datasets.

Dependencies:
- numpy
- matplotlib
- pandas
- seaborn

Usage:
from analysis.supercon_analysis import SuperconAnalysis

analysis = SuperconAnalysis()
analysis.plot_parameter_space()
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from tools.rtsc_calculator import RTSCCalculator

class SuperconAnalysis:
    """High-level analysis and visualization tools for RTSC protocol."""
    
    def __init__(self):
        self.calc = RTSCCalculator()
        sns.set_theme(style="whitegrid")
    
    def plot_parameter_space(self, omega_range=(100, 200), lambda_range=(1.5, 3.5), resolution=50):
        """Plot Tc as a function of ω_log and λ_eff."""
        param_map = self.calc.create_parameter_space_map(omega_range, lambda_range, resolution)
        
        plt.figure(figsize=(10, 8))
        contour = plt.contourf(param_map['omega_log'], param_map['lambda_eff'], param_map['tc'], 
                              levels=50, cmap='viridis')
        plt.colorbar(contour, label="Tc (K)")
        plt.contour(param_map['omega_log'], param_map['lambda_eff'], param_map['rtsc_region'], 
                   levels=[0.5], colors='red', linewidths=2)
        plt.xlabel("ω_log (meV)")
        plt.ylabel("λ_eff")
        plt.title("RTSC Parameter Space Map")
        plt.show()
    
    def plot_gap_vs_temperature(self, tc=300, lambda_eff=2.7):
        """Plot superconducting gap as a function of temperature."""
        gap_0 = self.calc.calculate_gap(tc, lambda_eff)
        temperatures = np.linspace(0, tc, 200)
        gaps = [self.calc.calculate_gap_at_temperature(gap_0, T, tc) for T in temperatures]
        
        plt.figure(figsize=(8, 6))
        plt.plot(temperatures, gaps, label=f"λ_eff={lambda_eff}")
        plt.axhline(gap_0, color='gray', linestyle='--', label="Δ(0)")
        plt.xlabel("Temperature (K)")
        plt.ylabel("Gap Δ (meV)")
        plt.title("Superconducting Gap vs Temperature")
        plt.legend()
        plt.show()
    
    def plot_synthetic_data(self, params=None):
        """Generate and plot synthetic experimental data."""
        if params is None:
            params = {'omega_log': 140, 'lambda_eff': 2.7, 'mu_star': 0.10, 'tc': 320}
        
        data = self.calc.generate_synthetic_data(params)
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Resistance vs Temperature
        axes[0, 0].plot(data['temperature'], data['resistance'])
        axes[0, 0].set_xlabel("Temperature (K)")
        axes[0, 0].set_ylabel("Resistance (Ω)")
        axes[0, 0].set_title("Resistance vs Temperature")
        
        # Gap vs Temperature
        axes[0, 1].plot(data['temperature'], data['gaps'])
        axes[0, 1].set_xlabel("Temperature (K)")
        axes[0, 1].set_ylabel("Gap Δ (meV)")
        axes[0, 1].set_title("Gap vs Temperature")
        
        # α²F(ω)
        axes[1, 0].plot(data['frequencies'], data['alpha2f'])
        axes[1, 0].set_xlabel("Frequency (meV)")
        axes[1, 0].set_ylabel("α²F(ω)")
        axes[1, 0].set_title("Eliashberg Function α²F(ω)")
        
        # Summary text
        summary = f"ω_log = {data['omega_log_calculated']:.1f} meV\nf_ω = {data['f_omega_calculated']:.2f}"
        axes[1, 1].axis('off')
        axes[1, 1].text(0.1, 0.5, summary, fontsize=12)
        
        plt.tight_layout()
        plt.show()
    
    def analyze_experimental_csv(self, filepath: str):
        """Load and analyze experimental CSV data (temperature vs resistance)."""
        df = pd.read_csv(filepath)
        if 'Temperature' not in df.columns or 'Resistance' not in df.columns:
            raise ValueError("CSV must contain 'Temperature' and 'Resistance' columns")
        
        temperatures = df['Temperature'].values
        resistance = df['Resistance'].values
        
        # Estimate Tc as midpoint of resistance drop
        r_norm = (resistance - resistance.min()) / (resistance.max() - resistance.min())
        tc_index = np.argmin(np.abs(r_norm - 0.5))
        tc_estimated = temperatures[tc_index]
        
        plt.figure(figsize=(8, 6))
        plt.plot(temperatures, resistance, label="Experimental Data")
        plt.axvline(tc_estimated, color='red', linestyle='--', label=f"Estimated Tc = {tc_estimated:.1f} K")
        plt.xlabel("Temperature (K)")
        plt.ylabel("Resistance (Ω)")
        plt.title("Experimental Resistance vs Temperature")
        plt.legend()
        plt.show()
        
        return {"tc_estimated": tc_estimated, "data_points": len(df)}

def demo():
    analysis = SuperconAnalysis()
    analysis.plot_parameter_space()
    analysis.plot_gap_vs_temperature()
    analysis.plot_synthetic_data()

if __name__ == "__main__":
    demo()
