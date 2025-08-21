"""
Enhanced RTSC Calculator

This module implements the Allen-Dynes multi-channel coupling calculations
for the Quantum RTSC Protocol. It provides comprehensive tools for predicting
superconducting transition temperatures and analyzing experimental data.

Key Features:
- Allen-Dynes Tc calculations with multi-channel coupling
- Spectral weight analysis (f_omega calculations)
- Parameter sensitivity analysis
- Experimental data validation
- Artifact detection algorithms

Dependencies:
- numpy
- scipy
- matplotlib
- pandas

Usage:
from tools.rtsc_calculator import RTSCCalculator

calc = RTSCCalculator()
tc = calc.calculate_tc(omega_log=140, lambda_eff=2.7, mu_star=0.10)
"""

import numpy as np
import scipy.constants as const
from scipy.optimize import minimize_scalar
from typing import Dict, List, Tuple, Optional
import warnings
from dataclasses import dataclass
import typer

@dataclass
class CouplingChannels:
    """Data class for multi-channel coupling parameters."""
    lam_H: float
    lam_plasmon: float
    lam_flat: float
    
    @property
    def lam_eff(self) -> float:
        """Total effective coupling."""
        return self.lam_H + self.lam_plasmon + self.lam_flat
    
    def validate_channels(self) -> bool:
        """Validate that channels don't overlap spectrally."""
        # Basic validation - all channels should be positive
        if any(lam < 0 for lam in [self.lam_H, self.lam_plasmon, self.lam_flat]):
            raise ValueError("All coupling channels must be positive")
        
        # Check for reasonable ranges to prevent double counting
        if self.lam_H > 3.0:
            warnings.warn("λ_H > 3.0: Check for spectral overlap with other channels")
        if self.lam_plasmon > 1.0:
            warnings.warn("λ_plasmon > 1.0: Check for overlap with phonon spectrum")
        if self.lam_flat > 1.0:
            warnings.warn("λ_flat > 1.0: Check for realistic flat band DOS")
            
        return True

def multi_channel_lambda(lambda_h: float, lambda_plasmon: float, lambda_flat: float) -> float:
    """
    Backward-compatible wrapper for multi-channel lambda calculation.
    Delegates to RTSCCalculator.calculate_multi_channel_lambda.
    """
    return RTSCCalculator().calculate_multi_channel_lambda(lambda_h, lambda_plasmon, lambda_flat)


def allen_dynes_tc_legacy(lambda_eff: float, mu_star: float, omega_mev: float, f_omega: float = 1.0) -> float:
    """
    Legacy wrapper for backward compatibility with tests expecting argument order:
    (lambda_eff, mu_star, omega_mev).
    Internally calls allen_dynes_tc_new with reordered arguments.
    """
    return allen_dynes_tc_new(omega_mev, lambda_eff, mu_star, f_omega)


# Provide both legacy and new interfaces without recursion
def allen_dynes_tc(*args, **kwargs):
    """
    Backward-compatible Allen-Dynes Tc function.
    - If called with (lambda_eff, mu_star, omega_mev[, f_omega]) → legacy order
    - If called with (omega_mev, lambda_eff[, mu_star, f_omega]) → new order
    """
    if len(args) >= 3:
        # Detect legacy vs new by argument positions
        if isinstance(args[0], (int, float)) and isinstance(args[2], (int, float)):
            # If first arg is small (<10) and third arg is large (>20), assume legacy order
            if args[0] < 10 and args[2] > 20:
                return allen_dynes_tc_new(args[2], args[0], args[1], args[3] if len(args) > 3 else 1.0)
        # Otherwise assume new order
        return allen_dynes_tc_new(*args, **kwargs)
    return allen_dynes_tc_new(*args, **kwargs)


def allen_dynes_tc_new(omega_mev: float, lam_eff: float, mu_star: float = 0.12, f_omega: float = 1.0) -> float:
    """
    Standalone Allen-Dynes Tc calculation with enhanced guard rails.
    
    Args:
        omega_mev: Logarithmic average phonon frequency (meV)
        lam_eff: Effective electron-phonon coupling
        mu_star: Coulomb pseudopotential (default 0.12)
        f_omega: Spectral weight enhancement factor (default 1.0)
        
    Returns:
        Tc: Superconducting transition temperature (K)
        
    Raises:
        ValueError: For unphysical input parameters
    """
    # Enhanced guard rails
    if lam_eff <= 0:
        raise ValueError("λ_eff must be > 0")
    if mu_star < 0 or mu_star > 0.3:
        raise ValueError("μ* out of range [0, 0.3]")
    if omega_mev <= 0:
        raise ValueError("ω_log must be > 0")
    if f_omega <= 0:
        raise ValueError("f_ω must be > 0")
    
    # Check denominator for physical validity
    den = lam_eff - mu_star * (1 + 0.62 * lam_eff)
    if den <= 0:
        raise ValueError("Unphysical input: denominator ≤ 0 (λ_eff too small or μ* too large)")
    
    # Convert meV to K
    omega_k = 11.6045 * omega_mev
    
    # Allen-Dynes formula with f_ω enhancement
    prefactor = (omega_k / 1.2) * f_omega
    exponent = -1.04 * (1 + lam_eff) / den
    
    tc = prefactor * np.exp(exponent)
    return tc

def lambda_for_tc(tc_target: float, omega_mev: float, mu_star: float = 0.12, f_omega: float = 1.0) -> float:
    """
    Calculate λ_eff needed for a target Tc using bisection method.
    
    Args:
        tc_target: Target transition temperature (K)
        omega_mev: Logarithmic average frequency (meV)
        mu_star: Coulomb pseudopotential (default 0.12)
        f_omega: Spectral weight enhancement factor (default 1.0)
        
    Returns:
        lambda_eff: Required effective coupling
        
    Raises:
        ValueError: If no solution exists in reasonable range
    """
    from scipy.optimize import brentq
    
    def tc_residual(lam_eff):
        try:
            tc_calc = allen_dynes_tc(omega_mev, lam_eff, mu_star, f_omega)
            return tc_calc - tc_target
        except ValueError:
            return -tc_target  # Return large negative if unphysical
    
    # Check if solution exists in reasonable range
    lam_min, lam_max = 0.5, 5.0
    
    try:
        # Check bounds
        res_min = tc_residual(lam_min)
        res_max = tc_residual(lam_max)
        
        if res_min * res_max > 0:
            # No sign change - check which bound is closer
            if abs(res_max) < abs(res_min):
                warnings.warn(f"Solution may need λ_eff > {lam_max}")
                return lam_max
            else:
                raise ValueError(f"No solution found: target Tc={tc_target}K too low for given parameters")
        
        # Use bisection to find solution
        lambda_solution = brentq(tc_residual, lam_min, lam_max, xtol=1e-6, maxiter=80)
        return lambda_solution
        
    except ValueError as e:
        raise ValueError(f"Failed to find λ_eff for Tc={tc_target}K: {str(e)}")

class RTSCCalculator:
    """Enhanced calculator for RTSC protocol parameters."""
    
    def __init__(self):
        """Initialize the calculator with physical constants."""
        self.kb = const.k * 6.242e21  # Boltzmann constant in meV/K
        self.hbar = const.hbar * 6.582e-13  # Reduced Planck constant in meV·s
        
    def calculate_tc(self, omega_log: float, lambda_eff: float, mu_star: float) -> float:
        """
        Calculate superconducting Tc using Allen-Dynes formula.
        
        Args:
            omega_log: Logarithmic average phonon frequency (meV)
            lambda_eff: Effective electron-phonon coupling
            mu_star: Coulomb pseudopotential
            
        Returns:
            Tc: Superconducting transition temperature (K)
        """
        if lambda_eff <= mu_star:
            warnings.warn("λ_eff <= μ*: No superconductivity predicted")
            return 0.0
            
        # Allen-Dynes formula
        prefactor = omega_log / (1.2 * self.kb)
        exponent = -1.04 * (1 + lambda_eff) / (lambda_eff - mu_star * (1 + 0.62 * lambda_eff))
        
        tc = prefactor * np.exp(exponent)
        return tc
    
    def calculate_multi_channel_lambda(self, lambda_h: float, lambda_plasmon: float, 
                                     lambda_flat: float) -> float:
        """
        Calculate effective coupling from multiple channels.
        
        Args:
            lambda_h: Hydrogen vibron coupling
            lambda_plasmon: Plasmonic coupling
            lambda_flat: Flat band coupling
            
        Returns:
            lambda_eff: Total effective coupling
        """
        return lambda_h + lambda_plasmon + lambda_flat
    
    def calculate_gap(self, tc: float, lambda_eff: float) -> float:
        """
        Calculate superconducting gap at T=0.
        
        Args:
            tc: Transition temperature (K)
            lambda_eff: Effective coupling strength
            
        Returns:
            gap: Superconducting gap at T=0 (meV)
        """
        # Strong coupling correction to BCS ratio
        if lambda_eff < 1.0:
            ratio = 1.764  # Weak coupling BCS
        else:
            # Empirical strong coupling formula
            ratio = 1.764 * (1 + 0.4 * lambda_eff)
            
        gap = ratio * self.kb * tc
        return gap
    
    def calculate_gap_at_temperature(self, gap_0: float, temperature: float, tc: float) -> float:
        """
        Calculate temperature-dependent gap using BCS theory.
        
        Args:
            gap_0: Gap at T=0 (meV)
            temperature: Temperature (K)
            tc: Transition temperature (K)
            
        Returns:
            gap_T: Gap at temperature T (meV)
        """
        if temperature >= tc:
            return 0.0
            
        t = temperature / tc
        # BCS gap equation (approximate)
        gap_t = gap_0 * np.tanh(1.74 * np.sqrt((tc / temperature) - 1))
        return gap_t
    
    def calculate_omega_log(self, frequencies: np.ndarray, alpha2f: np.ndarray) -> float:
        """
        Calculate logarithmic average frequency from α²F(ω).
        
        Args:
            frequencies: Frequency array (meV)
            alpha2f: α²F(ω) spectral function
            
        Returns:
            omega_log: Logarithmic average frequency (meV)
        """
        # Ensure positive frequencies and α²F
        mask = (frequencies > 0) & (alpha2f > 0)
        freq_clean = frequencies[mask]
        alpha2f_clean = alpha2f[mask]
        
        if len(freq_clean) == 0:
            return 0.0
            
        # Calculate λ for normalization
        lambda_total = 2 * np.trapz(alpha2f_clean / freq_clean, freq_clean)
        
        if lambda_total <= 0:
            return 0.0
            
        # Logarithmic average
        integrand = (alpha2f_clean / freq_clean) * np.log(freq_clean)
        omega_log = np.exp(2 * np.trapz(integrand, freq_clean) / lambda_total)
        
        return omega_log
    
    def calculate_f_omega(self, frequencies: np.ndarray, alpha2f: np.ndarray, 
                         omega_cutoff: float = 100.0) -> float:
        """
        Calculate spectral weight enhancement factor f_ω.
        
        Args:
            frequencies: Frequency array (meV)
            alpha2f: α²F(ω) spectral function
            omega_cutoff: Cutoff frequency for high-ω definition (meV)
            
        Returns:
            f_omega: Spectral weight enhancement factor
        """
        # Split into low and high frequency regions
        low_mask = frequencies < omega_cutoff
        high_mask = frequencies >= omega_cutoff
        
        # Calculate spectral weights
        lambda_low = 2 * np.trapz(alpha2f[low_mask] / frequencies[low_mask], frequencies[low_mask])
        lambda_high = 2 * np.trapz(alpha2f[high_mask] / frequencies[high_mask], frequencies[high_mask])
        
        if lambda_low <= 0:
            return np.inf if lambda_high > 0 else 1.0
            
        f_omega = lambda_high / lambda_low
        return f_omega
    
    def validate_rtsc_parameters(self, omega_log: float, lambda_eff: float, 
                                mu_star: float, f_omega: float) -> Dict[str, bool]:
        """
        Validate parameters against RTSC success criteria.
        
        Args:
            omega_log: Logarithmic average frequency (meV)
            lambda_eff: Effective coupling
            mu_star: Coulomb pseudopotential
            f_omega: Spectral weight enhancement
            
        Returns:
            validation: Dictionary of pass/fail results
        """
        validation = {
            'omega_log_pass': omega_log >= 120.0,
            'lambda_eff_pass': 2.5 <= lambda_eff <= 2.7,
            'mu_star_pass': mu_star <= 0.12,
            'f_omega_pass': f_omega >= 1.35,
            'overall_pass': False
        }
        
        validation['overall_pass'] = all([
            validation['omega_log_pass'],
            validation['lambda_eff_pass'],
            validation['mu_star_pass'],
            validation['f_omega_pass']
        ])
        
        return validation
    
    def analyze_experimental_data(self, raman_data: Dict, ftir_data: Dict, 
                                 sts_data: Dict, transport_data: Dict) -> Dict:
        """
        Comprehensive analysis of experimental data.
        
        Args:
            raman_data: {'frequencies': array, 'intensities': array}
            ftir_data: {'frequencies': array, 'alpha2f': array}
            sts_data: {'gap_300k': float, 'uniformity': float}
            transport_data: {'tc': float, 'resistance_drop': float}
            
        Returns:
            analysis: Complete analysis results
        """
        analysis = {}
        
        # Extract ω_log from FTIR
        if 'frequencies' in ftir_data and 'alpha2f' in ftir_data:
            analysis['omega_log'] = self.calculate_omega_log(
                ftir_data['frequencies'], ftir_data['alpha2f']
            )
            analysis['f_omega'] = self.calculate_f_omega(
                ftir_data['frequencies'], ftir_data['alpha2f']
            )
        
        # Analyze STS data
        if 'gap_300k' in sts_data:
            analysis['gap_300k'] = sts_data['gap_300k']
            if 'tc' in transport_data:
                tc = transport_data['tc']
                analysis['2delta_kbtc_ratio'] = (2 * sts_data['gap_300k']) / (self.kb * tc)
        
        # Transport analysis
        if 'tc' in transport_data:
            analysis['tc_transport'] = transport_data['tc']
            analysis['resistance_drop'] = transport_data.get('resistance_drop', 0)
        
        # Validation
        if all(key in analysis for key in ['omega_log', 'f_omega']):
            # Estimate λ_eff from gap and Tc
            if 'gap_300k' in analysis and 'tc_transport' in analysis:
                estimated_lambda = self.estimate_lambda_from_gap(
                    analysis['gap_300k'], analysis['tc_transport']
                )
                analysis['lambda_eff_estimated'] = estimated_lambda
                
                validation = self.validate_rtsc_parameters(
                    analysis['omega_log'], estimated_lambda, 0.10, analysis['f_omega']
                )
                analysis['validation'] = validation
        
        return analysis
    
    def estimate_lambda_from_gap(self, gap: float, tc: float) -> float:
        """
        Estimate λ_eff from measured gap and Tc.
        
        Args:
            gap: Superconducting gap (meV)
            tc: Transition temperature (K)
            
        Returns:
            lambda_eff: Estimated effective coupling
        """
        # Use strong coupling relation: Δ ≈ 1.764 * (1 + 0.4λ) * kB * Tc
        ratio = gap / (self.kb * tc)
        if ratio <= 1.764:
            return 0.0  # Weak coupling
        else:
            lambda_eff = (ratio / 1.764 - 1) / 0.4
            return max(0.0, lambda_eff)
    
    def optimize_parameters(self, target_tc: float = 300.0) -> Dict:
        """
        Optimize parameters for target Tc.
        
        Args:
            target_tc: Target transition temperature (K)
            
        Returns:
            optimal_params: Optimized parameter set
        """
        def objective(lambda_eff):
            tc = self.calculate_tc(omega_log=140, lambda_eff=lambda_eff, mu_star=0.10)
            return abs(tc - target_tc)
        
        result = minimize_scalar(objective, bounds=(1.0, 4.0), method='bounded')
        
        optimal_params = {
            'omega_log': 140.0,
            'lambda_eff': result.x,
            'mu_star': 0.10,
            'predicted_tc': self.calculate_tc(140.0, result.x, 0.10),
            'gap_0': self.calculate_gap(target_tc, result.x)
        }
        
        return optimal_params
    
    def sensitivity_analysis(self, base_params: Dict, variation: float = 0.1) -> Dict:
        """
        Perform sensitivity analysis around base parameters.
        
        Args:
            base_params: {'omega_log': float, 'lambda_eff': float, 'mu_star': float}
            variation: Fractional variation for sensitivity (default 10%)
            
        Returns:
            sensitivity: Sensitivity coefficients
        """
        base_tc = self.calculate_tc(**base_params)
        sensitivity = {}
        
        for param, value in base_params.items():
            # Positive variation
            params_plus = base_params.copy()
            params_plus[param] = value * (1 + variation)
            tc_plus = self.calculate_tc(**params_plus)
            
            # Negative variation
            params_minus = base_params.copy()
            params_minus[param] = value * (1 - variation)
            tc_minus = self.calculate_tc(**params_minus)
            
            # Sensitivity coefficient
            dtc_dparam = (tc_plus - tc_minus) / (2 * variation * value)
            sensitivity[f'd_tc_d_{param}'] = dtc_dparam
            sensitivity[f'{param}_sensitivity'] = abs(dtc_dparam * value / base_tc)
        
        return sensitivity
    
    def detect_artifacts(self, iv_data: Dict, temperature_data: Dict) -> Dict:
        """
        Detect common experimental artifacts.
        
        Args:
            iv_data: {'voltage': array, 'current': array, 'pulsed': bool}
            temperature_data: {'temperature': array, 'resistance': array}
            
        Returns:
            artifacts: Dictionary of artifact detection results
        """
        artifacts = {}
        
        # Heating artifact detection
        if 'voltage' in iv_data and 'current' in iv_data:
            power = iv_data['voltage'] * iv_data['current']
            resistance = iv_data['voltage'] / iv_data['current']
            
            # Check for power-dependent resistance
            if len(power) > 10:
                correlation = np.corrcoef(power, resistance)[0, 1]
                artifacts['heating_artifact'] = abs(correlation) > 0.5
            else:
                artifacts['heating_artifact'] = False
        
        # Ionic conduction detection
        if 'temperature' in temperature_data and 'resistance' in temperature_data:
            temp = temperature_data['temperature']
            res = temperature_data['resistance']
            
            # Check for temperature-independent conductivity
            if len(temp) > 5:
                # Calculate temperature coefficient
                temp_coeff = np.polyfit(temp, np.log(res), 1)[0]
                artifacts['ionic_conduction'] = abs(temp_coeff) < 0.001  # Very weak T dependence
            else:
                artifacts['ionic_conduction'] = False
        
        return artifacts
    
    def generate_synthetic_data(self, params: Dict, noise_level: float = 0.05) -> Dict:
        """
        Generate synthetic experimental data for testing.
        
        Args:
            params: {'omega_log': float, 'lambda_eff': float, 'mu_star': float, 'tc': float}
            noise_level: Fractional noise level
            
        Returns:
            synthetic_data: Generated data sets
        """
        tc = params['tc']
        gap_0 = self.calculate_gap(tc, params['lambda_eff'])
        
        # Temperature array
        temperatures = np.linspace(250, 350, 100)
        
        # Resistance vs temperature
        resistance = np.zeros_like(temperatures)
        for i, T in enumerate(temperatures):
            if T > tc:
                # Normal state resistance (linear in T)
                resistance[i] = 100 + 0.1 * (T - 300)
            else:
                # Superconducting state
                resistance[i] = 1e-6  # Essentially zero
        
        # Add noise
        resistance += noise_level * np.random.normal(0, np.mean(resistance), len(resistance))
        
        # Gap vs temperature
        gaps = np.array([self.calculate_gap_at_temperature(gap_0, T, tc) for T in temperatures])
        
        # Synthetic α²F(ω)
        frequencies = np.linspace(10, 300, 1000)
        alpha2f = np.zeros_like(frequencies)
        
        # Hydrogen peak around 150 meV
        h_peak = 150
        h_width = 20
        alpha2f += 0.8 * np.exp(-((frequencies - h_peak) / h_width)**2)
        
        # Plasmon peak around 80 meV
        p_peak = 80
        p_width = 15
        alpha2f += 0.3 * np.exp(-((frequencies - p_peak) / p_width)**2)
        
        # Low frequency acoustic modes
        alpha2f += 0.1 * np.exp(-frequencies / 30)
        
        synthetic_data = {
            'temperature': temperatures,
            'resistance': resistance,
            'gaps': gaps,
            'frequencies': frequencies,
            'alpha2f': alpha2f,
            'omega_log_calculated': self.calculate_omega_log(frequencies, alpha2f),
            'f_omega_calculated': self.calculate_f_omega(frequencies, alpha2f)
        }
        
        return synthetic_data
    
    def create_parameter_space_map(self, omega_range: Tuple[float, float] = (100, 200),
                                  lambda_range: Tuple[float, float] = (1.5, 3.5),
                                  resolution: int = 50) -> Dict:
        """
        Create a parameter space map of Tc values.
        
        Args:
            omega_range: Range of ω_log values (meV)
            lambda_range: Range of λ_eff values
            resolution: Grid resolution
            
        Returns:
            param_map: Parameter space mapping
        """
        omega_vals = np.linspace(omega_range[0], omega_range[1], resolution)
        lambda_vals = np.linspace(lambda_range[0], lambda_range[1], resolution)
        
        omega_grid, lambda_grid = np.meshgrid(omega_vals, lambda_vals)
        tc_grid = np.zeros_like(omega_grid)
        
        mu_star = 0.10  # Fixed for this analysis
        
        for i in range(resolution):
            for j in range(resolution):
                tc_grid[i, j] = self.calculate_tc(
                    omega_grid[i, j], lambda_grid[i, j], mu_star
                )
        
        param_map = {
            'omega_log': omega_grid,
            'lambda_eff': lambda_grid,
            'tc': tc_grid,
            'rtsc_region': tc_grid >= 300.0
        }
        
        return param_map

def demo_calculations():
    """Demonstration of calculator capabilities."""
    calc = RTSCCalculator()
    
    print("=== RTSC Calculator Demo ===\n")
    
    # Basic Tc calculation
    omega_log = 140  # meV
    lambda_eff = 2.7
    mu_star = 0.10
    
    tc = calc.calculate_tc(omega_log, lambda_eff, mu_star)
    gap = calc.calculate_gap(tc, lambda_eff)
    
    print(f"Input Parameters:")
    print(f"  ω_log = {omega_log} meV")
    print(f"  λ_eff = {lambda_eff}")
    print(f"  μ* = {mu_star}")
    print(f"\nPredicted Results:")
    print(f"  Tc = {tc:.1f} K")
    print(f"  Δ(0) = {gap:.1f} meV")
    print(f"  2Δ/kBTc = {2*gap/(calc.kb*tc):.2f}")
    
    # Multi-channel analysis
    lambda_h = 1.8
    lambda_plasmon = 0.5
    lambda_flat = 0.4
    lambda_total = calc.calculate_multi_channel_lambda(lambda_h, lambda_plasmon, lambda_flat)
    
    print(f"\nMulti-Channel Analysis:")
    print(f"  λ_H = {lambda_h}")
    print(f"  λ_plasmon = {lambda_plasmon}")
    print(f"  λ_flat = {lambda_flat}")
    print(f"  λ_total = {lambda_total}")
    
    # Validation
    validation = calc.validate_rtsc_parameters(omega_log, lambda_eff, mu_star, 1.6)
    print(f"\nValidation Results:")
    for key, value in validation.items():
        status = "PASS" if value else "FAIL"
        print(f"  {key}: {status}")
    
    # Sensitivity analysis
    base_params = {'omega_log': omega_log, 'lambda_eff': lambda_eff, 'mu_star': mu_star}
    sensitivity = calc.sensitivity_analysis(base_params)
    
    print(f"\nSensitivity Analysis:")
    for key, value in sensitivity.items():
        if 'sensitivity' in key:
            print(f"  {key}: {value:.3f}")

# CLI Interface using Typer
app = typer.Typer(help="RTSC Calculator CLI")

@app.command()
def calculate(
    omega: float = typer.Option(140.0, "--omega", help="omega_log in meV"),
    lambda_eff: float = typer.Option(2.7, "--lambda", help="lambda_eff coupling strength"),
    mu_star: float = typer.Option(0.10, "--mu", help="mu* Coulomb pseudopotential"),
    f_omega: float = typer.Option(1.35, "--fomega", help="f_omega spectral enhancement factor")
):
    """Calculate Tc using Allen-Dynes formula."""
    try:
        tc = allen_dynes_tc(omega, lambda_eff, mu_star, f_omega)
        gap = RTSCCalculator().calculate_gap(tc, lambda_eff)
        
        print(f"Input: omega_log={omega} meV, lambda_eff={lambda_eff}, mu*={mu_star}, f_omega={f_omega}")
        print(f"Result: Tc = {tc:.1f} K, Delta(0) = {gap:.1f} meV")
        print(f"2Delta/kBTc = {2*gap/(0.0862*tc):.2f}")
        
        # Validation
        calc = RTSCCalculator()
        validation = calc.validate_rtsc_parameters(omega, lambda_eff, mu_star, f_omega)
        if validation['overall_pass']:
            print("RTSC criteria: PASS")
        else:
            print("RTSC criteria: FAIL")
            for key, value in validation.items():
                if not value and key != 'overall_pass':
                    print(f"  - {key}: FAIL")
                    
    except ValueError as e:
        print(f"Error: {e}")
        raise typer.Exit(1)

@app.command()
def inverse(
    target_tc: float = typer.Option(300.0, "--tc", help="Target Tc in K"),
    omega: float = typer.Option(140.0, "--omega", help="omega_log in meV"),
    mu_star: float = typer.Option(0.10, "--mu", help="mu* Coulomb pseudopotential"),
    f_omega: float = typer.Option(1.0, "--fomega", help="f_omega spectral enhancement factor")
):
    """Calculate lambda_eff needed for target Tc."""
    try:
        lambda_needed = lambda_for_tc(target_tc, omega, mu_star, f_omega)
        tc_check = allen_dynes_tc(omega, lambda_needed, mu_star, f_omega)
        
        print(f"Target: Tc = {target_tc} K")
        print(f"Required: lambda_eff = {lambda_needed:.3f}")
        print(f"Verification: Tc = {tc_check:.1f} K")
        
    except ValueError as e:
        print(f"Error: {e}")
        raise typer.Exit(1)

@app.command()
def demo():
    """Run demonstration calculations."""
    demo_calculations()

if __name__ == "__main__":
    app()
