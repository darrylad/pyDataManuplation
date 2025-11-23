"""
Module for signal processing operations including FFT analysis.
"""

import numpy as np
import pandas as pd
from scipy import signal
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_sampling_rate(time_data: np.ndarray) -> float:
    """
    Calculate the sampling rate from time data.
    
    The sampling rate is how many samples per second we have.
    For example: if samples are 0.001s apart, sampling rate = 1000 Hz
    
    Args:
        time_data: Array of time values
        
    Returns:
        Sampling rate in Hz
    """
    # Calculate time differences between consecutive samples
    time_diffs = np.diff(time_data)
    
    # Average time step (should be consistent for uniform sampling)
    avg_dt = np.mean(time_diffs)
    
    # Sampling rate is 1 / time_step
    fs = 1.0 / avg_dt
    
    logger.info(f"  Calculated sampling rate: {fs:.2f} Hz")
    logger.info(f"  Average time step: {avg_dt*1000:.4f} ms")
    
    return fs


def compute_frequency_spectrum(df: pd.DataFrame, 
                               time_column: str,
                               axis_columns: List[str],
                               fft_config: Dict) -> Dict:
    """
    Compute frequency spectrum for all axes using Welch's method.
    
    Welch's method:
    1. Splits the signal into overlapping segments
    2. Computes FFT for each segment
    3. Averages the results
    
    This reduces noise and gives a cleaner frequency spectrum.
    
    Args:
        df: DataFrame with time series data
        time_column: Name of time column
        axis_columns: List of axis names to process
        fft_config: Configuration dictionary for FFT parameters
        
    Returns:
        Dictionary containing:
        - 'sampling_rate': Sampling frequency
        - 'nyquist_freq': Maximum meaningful frequency
        - For each axis: {'frequencies': array, 'magnitude': array}
    """
    # Step 1: Calculate sampling rate from time data
    time_data = df[time_column].values
    fs = calculate_sampling_rate(time_data)
    
    # Nyquist frequency = half the sampling rate (max frequency we can detect)
    nyquist_freq = fs / 2.0
    logger.info(f"  Nyquist frequency: {nyquist_freq:.2f} Hz")
    
    # Initialize results dictionary
    result = {
        'sampling_rate': fs,
        'nyquist_freq': nyquist_freq
    }
    
    # Step 2: Compute spectrum for each axis
    for axis in axis_columns:
        signal_data = df[axis].values
        
        # Determine window size (can't be larger than signal length)
        nperseg = min(fft_config['nperseg'], len(signal_data))
        overlap = min(fft_config['overlap'], nperseg - 1)
        
        logger.info(f"  Computing FFT for {axis} axis...")
        logger.info(f"    Signal length: {len(signal_data)} samples")
        logger.info(f"    Window size: {nperseg} samples")
        logger.info(f"    Overlap: {overlap} samples")
        
        # Compute Power Spectral Density using Welch's method
        frequencies, psd = signal.welch(
            signal_data,
            fs=fs,
            nperseg=nperseg,
            noverlap=overlap,
            scaling='density',  # Power spectral density
            window='hann'       # Hann window reduces spectral leakage
        )
        
        # Convert PSD to magnitude (amplitude)
        # PSD units are (acceleration^2)/Hz
        # Magnitude units are acceleration
        magnitude = np.sqrt(psd * fs / 2)  # Scale to get amplitude
        
        # Store results
        result[axis] = {
            'frequencies': frequencies,
            'magnitude': magnitude
        }
        
        # Log some stats
        peak_freq = frequencies[np.argmax(magnitude)]
        peak_mag = np.max(magnitude)
        logger.info(f"    Peak frequency: {peak_freq:.2f} Hz")
        logger.info(f"    Peak magnitude: {peak_mag:.4f}")
    
    return result


def compute_all_frequency_spectra(all_data: Dict[str, pd.DataFrame],
                                  time_column: str,
                                  axis_columns: List[str],
                                  fft_config: Dict) -> Dict[str, Dict]:
    """
    Compute frequency spectra for all conditions.
    
    Args:
        all_data: Dictionary mapping condition names to DataFrames
        time_column: Name of time column
        axis_columns: List of axis names
        fft_config: FFT configuration
        
    Returns:
        Dictionary mapping condition names to frequency spectrum results
    """
    all_spectra = {}
    
    print("\n" + "="*80)
    print("COMPUTING FREQUENCY SPECTRA")
    print("="*80)
    
    for condition, df in all_data.items():
        print(f"\nProcessing: {condition}")
        print("-" * 60)
        
        spectrum = compute_frequency_spectrum(
            df, time_column, axis_columns, fft_config
        )
        
        all_spectra[condition] = spectrum
    
    return all_spectra


def get_frequency_display_range(all_spectra: Dict[str, Dict],
                                fft_config: Dict) -> float:
    """
    Determine the maximum frequency to display in plots.
    
    Uses either the configured max or the Nyquist frequency.
    
    Args:
        all_spectra: Dictionary of frequency spectra for all conditions
        fft_config: FFT configuration
        
    Returns:
        Maximum frequency to display (Hz)
    """
    # Get the minimum Nyquist frequency across all conditions
    min_nyquist = min(spec['nyquist_freq'] for spec in all_spectra.values())
    
    # Use configured max or Nyquist
    if fft_config['max_frequency'] is not None:
        max_freq = min(fft_config['max_frequency'], min_nyquist)
    else:
        max_freq = min_nyquist
    
    logger.info(f"Frequency display range: 0 - {max_freq:.2f} Hz")
    
    return max_freq