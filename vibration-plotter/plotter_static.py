"""
Static plotting module using Matplotlib for PDF export.
Optimized for performance and file size with rasterization.
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def downsample_data(df: pd.DataFrame, factor: int) -> pd.DataFrame:
    """
    Downsample DataFrame by keeping every Nth row.
    
    This dramatically reduces rendering time while maintaining
    visual fidelity (screens can't display millions of points anyway).
    
    Args:
        df: DataFrame to downsample
        factor: Keep every Nth point (e.g., 10 = keep 10%)
        
    Returns:
        Downsampled DataFrame
    """
    if factor <= 1:
        return df
    
    original_len = len(df)
    downsampled = df.iloc[::factor].reset_index(drop=True)
    new_len = len(downsampled)
    
    logger.info(f"  Downsampled: {original_len:,} → {new_len:,} points ({new_len/original_len*100:.1f}%)")
    
    return downsampled


def calculate_global_ranges_static(all_data: Dict[str, pd.DataFrame],
                                  axes: List[str]) -> Dict[str, Tuple[float, float]]:
    """
    Calculate global min/max ranges for consistent Y-axis scaling.
    
    Similar to Plotly version but for Matplotlib.
    
    Args:
        all_data: Dictionary mapping condition names to DataFrames
        axes: List of axis names
        
    Returns:
        Dictionary mapping axis names to (min, max) tuples
    """
    ranges = {}
    
    for axis in axes:
        all_values = []
        for df in all_data.values():
            all_values.extend(df[axis].values)
        
        min_val = np.min(all_values)
        max_val = np.max(all_values)
        padding = (max_val - min_val) * 0.05
        
        ranges[axis] = (min_val - padding, max_val + padding)
    
    return ranges


def calculate_global_frequency_ranges_static(all_spectra: Dict[str, Dict],
                                           axes: List[str],
                                           max_frequency: float) -> Dict[str, Tuple[float, float]]:
    """
    Calculate global magnitude ranges for frequency plots.
    
    Args:
        all_spectra: Dictionary of frequency spectra
        axes: List of axis names
        max_frequency: Maximum frequency to include
        
    Returns:
        Dictionary mapping axis names to (min, max) magnitude tuples
    """
    ranges = {}
    
    for axis in axes:
        all_magnitudes = []
        for spectrum in all_spectra.values():
            frequencies = spectrum[axis]['frequencies']
            magnitudes = spectrum[axis]['magnitude']
            mask = frequencies <= max_frequency
            all_magnitudes.extend(magnitudes[mask])
        
        min_mag = 0
        max_mag = np.max(all_magnitudes)
        padding = max_mag * 0.05
        
        ranges[axis] = (min_mag, max_mag + padding)
    
    return ranges


def create_time_domain_pdf(all_data: Dict[str, pd.DataFrame],
                          conditions: List[str],
                          time_column: str,
                          axis_columns: List[str],
                          axis_colors: Dict[str, str],
                          pdf_config: Dict,
                          output_path: Path):
    """
    Create time-domain plot and save as PDF using Matplotlib.
    
    This function creates a 5×3 grid of subplots:
    - 5 rows: One per condition (Healthy, 10 um, etc.)
    - 3 columns: One per axis (X, Y, Z)
    
    Args:
        all_data: Dictionary mapping condition names to DataFrames
        conditions: List of conditions in display order
        time_column: Name of time column
        axis_columns: List of axis names
        axis_colors: Dictionary mapping axis names to colors
        pdf_config: PDF configuration dictionary
        output_path: Where to save the PDF
    """
    print(f"\n📊 Creating time-domain PDF with Matplotlib...")
    
    # Step 1: Downsample data for faster rendering
    print(f"  Downsampling data (factor: {pdf_config['downsample_factor']})...")
    downsampled_data = {}
    for condition, df in all_data.items():
        downsampled_data[condition] = downsample_data(df, pdf_config['downsample_factor'])
    
    # Step 2: Calculate global ranges for consistent scaling
    print("  Calculating global ranges...")
    global_ranges = calculate_global_ranges_static(downsampled_data, axis_columns)
    
    # Calculate time range
    all_times = []
    for df in downsampled_data.values():
        all_times.extend(df[time_column].values)
    time_range = (min(all_times), max(all_times))
    
    # Step 3: Create figure with subplots
    n_conditions = len(conditions)
    n_axes = len(axis_columns)
    
    print(f"  Creating figure: {n_conditions} rows × {n_axes} columns")
    
    # Create figure with specified size
    fig = plt.figure(figsize=pdf_config['figsize'], dpi=pdf_config['dpi'])
    
    # Create grid specification for subplots
    gs = gridspec.GridSpec(
        n_conditions, n_axes,
        figure=fig,
        hspace=pdf_config['hspace'],  # Vertical spacing
        wspace=pdf_config['wspace']   # Horizontal spacing
    )
    
    # Add overall title
    fig.suptitle(
        'Vibration Data Analysis - Time Domain',
        fontsize=pdf_config['suptitle_size'],
        fontweight='bold'
    )
    
    # Step 4: Plot data in each subplot
    print("  Plotting data...")
    for row_idx, condition in enumerate(conditions):
        if condition not in downsampled_data:
            logger.warning(f"No data for condition: {condition}")
            continue
        
        df = downsampled_data[condition]
        time_data = df[time_column].values
        
        for col_idx, axis in enumerate(axis_columns):
            # Create subplot
            ax = fig.add_subplot(gs[row_idx, col_idx])
            
            # Plot the data with rasterization
            ax.plot(
                time_data,
                df[axis].values,
                color=axis_colors[axis],
                linewidth=pdf_config['line_width'],
                rasterized=pdf_config['rasterized']  # Rasterize for smaller file
            )
            
            # Set consistent Y-axis range
            ax.set_ylim(global_ranges[axis])
            
            # Set consistent X-axis range
            ax.set_xlim(time_range)
            
            # Add title (condition - axis)
            ax.set_title(
                f"{condition} - {axis} axis",
                fontsize=pdf_config['title_size']
            )
            
            # Add X-axis label only on bottom row
            if row_idx == n_conditions - 1:
                ax.set_xlabel('Time (s)', fontsize=pdf_config['label_size'])
            
            # Add Y-axis label only on left column
            if col_idx == 0:
                ax.set_ylabel('Acceleration', fontsize=pdf_config['label_size'])
            
            # Set tick label sizes
            ax.tick_params(labelsize=pdf_config['tick_size'])
            
            # Add grid for readability
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Step 5: Save as PDF
    print(f"  Saving to: {output_path}")
    plt.savefig(
        output_path,
        dpi=pdf_config['dpi'],
        bbox_inches='tight',  # Remove extra whitespace
        format='pdf'
    )
    
    # Close figure to free memory
    plt.close(fig)
    
    print(f"✅ Time-domain PDF saved successfully!")


def create_frequency_domain_pdf(all_spectra: Dict[str, Dict],
                               conditions: List[str],
                               axis_columns: List[str],
                               axis_colors: Dict[str, str],
                               pdf_config: Dict,
                               max_frequency: float,
                               output_path: Path):
    """
    Create frequency-domain plot and save as PDF using Matplotlib.
    
    Args:
        all_spectra: Dictionary mapping condition names to frequency spectra
        conditions: List of conditions in display order
        axis_columns: List of axis names
        axis_colors: Dictionary mapping axis names to colors
        pdf_config: PDF configuration dictionary
        max_frequency: Maximum frequency to display
        output_path: Where to save the PDF
    """
    print(f"\n📊 Creating frequency-domain PDF with Matplotlib...")
    
    # Step 1: Calculate global magnitude ranges
    print("  Calculating global frequency ranges...")
    global_ranges = calculate_global_frequency_ranges_static(
        all_spectra, axis_columns, max_frequency
    )
    
    # Step 2: Create figure
    n_conditions = len(conditions)
    n_axes = len(axis_columns)
    
    print(f"  Creating figure: {n_conditions} rows × {n_axes} columns")
    
    fig = plt.figure(figsize=pdf_config['figsize'], dpi=pdf_config['dpi'])
    
    gs = gridspec.GridSpec(
        n_conditions, n_axes,
        figure=fig,
        hspace=pdf_config['hspace'],
        wspace=pdf_config['wspace']
    )
    
    fig.suptitle(
        'Vibration Data Analysis - Frequency Domain (FFT)',
        fontsize=pdf_config['suptitle_size'],
        fontweight='bold'
    )
    
    # Step 3: Plot frequency spectra
    print("  Plotting frequency spectra...")
    for row_idx, condition in enumerate(conditions):
        if condition not in all_spectra:
            logger.warning(f"No spectrum for condition: {condition}")
            continue
        
        spectrum = all_spectra[condition]
        
        for col_idx, axis in enumerate(axis_columns):
            frequencies = spectrum[axis]['frequencies']
            magnitudes = spectrum[axis]['magnitude']
            
            # Filter to max frequency
            mask = frequencies <= max_frequency
            freq_plot = frequencies[mask]
            mag_plot = magnitudes[mask]
            
            # Create subplot
            ax = fig.add_subplot(gs[row_idx, col_idx])
            
            # Plot with filled area (like Plotly version)
            ax.plot(
                freq_plot,
                mag_plot,
                color=axis_colors[axis],
                linewidth=pdf_config['line_width'],
                rasterized=pdf_config['rasterized']
            )
            
            # Fill area under curve
            ax.fill_between(
                freq_plot,
                mag_plot,
                alpha=0.3,
                color=axis_colors[axis],
                rasterized=pdf_config['rasterized']
            )
            
            # Set consistent ranges
            ax.set_ylim(global_ranges[axis])
            ax.set_xlim(0, max_frequency)
            
            # Add title
            ax.set_title(
                f"{condition} - {axis} axis",
                fontsize=pdf_config['title_size']
            )
            
            # Add labels
            if row_idx == n_conditions - 1:
                ax.set_xlabel('Frequency (Hz)', fontsize=pdf_config['label_size'])
            
            if col_idx == 0:
                ax.set_ylabel('Magnitude', fontsize=pdf_config['label_size'])
            
            # Set tick sizes
            ax.tick_params(labelsize=pdf_config['tick_size'])
            
            # Add grid
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    
    # Step 4: Save as PDF
    print(f"  Saving to: {output_path}")
    plt.savefig(
        output_path,
        dpi=pdf_config['dpi'],
        bbox_inches='tight',
        format='pdf'
    )
    
    plt.close(fig)
    
    print(f"✅ Frequency-domain PDF saved successfully!")