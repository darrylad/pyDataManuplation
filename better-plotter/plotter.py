"""
Module for creating interactive plots using Plotly.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Tuple
import numpy as np


def calculate_global_ranges(all_data: Dict[str, pd.DataFrame], 
                           axes: List[str]) -> Dict[str, Tuple[float, float]]:
    """
    Calculate global min/max ranges across all conditions for consistent scaling.
    
    Args:
        all_data: Dictionary of condition name to DataFrame
        axes: List of axis names to calculate ranges for (e.g., ['X', 'Y', 'Z'])
        
    Returns:
        Dictionary mapping axis names to (min, max) tuples
    """
    ranges = {}
    
    for axis in axes:
        all_values = []
        
        # Collect all values for this axis across all conditions
        for df in all_data.values():
            all_values.extend(df[axis].values)
        
        # Calculate global min/max with some padding
        min_val = np.min(all_values)
        max_val = np.max(all_values)
        padding = (max_val - min_val) * 0.05  # 5% padding
        
        ranges[axis] = (min_val - padding, max_val + padding)
        
        print(f"{axis}-axis range: [{ranges[axis][0]:.2f}, {ranges[axis][1]:.2f}]")
    
    return ranges


def calculate_global_frequency_ranges(all_spectra: Dict[str, Dict],
                                     axes: List[str],
                                     max_frequency: float) -> Dict[str, Tuple[float, float]]:
    """
    Calculate global magnitude ranges for frequency plots.
    
    This ensures all frequency plots have the same Y-axis scale
    for easy visual comparison.
    
    Args:
        all_spectra: Dictionary of frequency spectra for all conditions
        axes: List of axis names
        max_frequency: Maximum frequency to include
        
    Returns:
        Dictionary mapping axis names to (min, max) magnitude tuples
    """
    ranges = {}
    
    print("\n📏 Calculating global frequency ranges:")
    
    for axis in axes:
        all_magnitudes = []
        
        # Collect all magnitude values for this axis across all conditions
        for spectrum in all_spectra.values():
            frequencies = spectrum[axis]['frequencies']
            magnitudes = spectrum[axis]['magnitude']
            
            # Only include frequencies up to max_frequency
            mask = frequencies <= max_frequency
            all_magnitudes.extend(magnitudes[mask])
        
        # Calculate global min/max with padding
        min_mag = 0  # Magnitude can't be negative
        max_mag = np.max(all_magnitudes)
        padding = max_mag * 0.05  # 5% padding on top
        
        ranges[axis] = (min_mag, max_mag + padding)
        
        print(f"{axis}-axis magnitude range: [0, {ranges[axis][1]:.4f}]")
    
    return ranges


def create_vibration_plot(all_data: Dict[str, pd.DataFrame],
                         conditions: List[str],
                         time_column: str,
                         axis_columns: List[str],
                         axis_colors: Dict[str, str],
                         plot_config: Dict) -> go.Figure:
    """
    Create a comprehensive multi-panel plot of vibration data (TIME DOMAIN).
    
    Layout: 
    - Rows: One per condition (Healthy, 10 um, etc.)
    - Columns: One per axis (X, Y, Z)
    
    Args:
        all_data: Dictionary mapping condition names to DataFrames
        conditions: List of conditions in desired display order
        time_column: Name of the time column
        axis_columns: List of axis column names ['X', 'Y', 'Z']
        axis_colors: Dictionary mapping axis names to colors
        plot_config: Dictionary with plot configuration parameters
        
    Returns:
        Plotly Figure object
    """
    # Calculate how many rows we need (one per condition)
    n_conditions = len(conditions)
    n_axes = len(axis_columns)
    
    print(f"\n📊 Creating TIME DOMAIN plot: {n_conditions} rows × {n_axes} columns")
    
    # Calculate global ranges for consistent scaling
    print("\n📏 Calculating global ranges for consistent scaling:")
    global_ranges = calculate_global_ranges(all_data, axis_columns)
    
    # Also calculate time range
    all_times = []
    for df in all_data.values():
        all_times.extend(df[time_column].values)
    time_range = (min(all_times), max(all_times))
    print(f"Time range: [{time_range[0]:.4f}, {time_range[1]:.4f}] seconds")
    
    # Create subplot titles
    subplot_titles = []
    for condition in conditions:
        for axis in axis_columns:
            subplot_titles.append(f"{condition} - {axis} axis")
    
    # Create subplots
    fig = make_subplots(
        rows=n_conditions,
        cols=n_axes,
        subplot_titles=subplot_titles,
        vertical_spacing=0.05,
        horizontal_spacing=0.03,
        shared_xaxes='rows',  # Share x-axis (time) across columns
    )
    
    # Add traces for each condition and axis
    for row_idx, condition in enumerate(conditions, start=1):
        if condition not in all_data:
            print(f"⚠️  Warning: No data for condition '{condition}'")
            continue
        
        df = all_data[condition]
        time_data = df[time_column]
        
        for col_idx, axis in enumerate(axis_columns, start=1):
            # Add the trace
            fig.add_trace(
                go.Scatter(
                    x=time_data,
                    y=df[axis],
                    mode='lines',
                    name=f"{condition} - {axis}",
                    line=dict(color=axis_colors[axis], width=1),
                    showlegend=False,  # Too many traces for legend
                ),
                row=row_idx,
                col=col_idx
            )
            
            # Update axes for this subplot
            fig.update_xaxes(
                title_text="Time (s)" if row_idx == n_conditions else "",
                range=time_range,
                row=row_idx,
                col=col_idx
            )
            
            fig.update_yaxes(
                title_text="Acceleration" if col_idx == 1 else "",
                range=global_ranges[axis],
                row=row_idx,
                col=col_idx
            )
    
    # Update overall layout
    total_height = plot_config['height_per_row'] * n_conditions
    
    fig.update_layout(
        height=total_height,
        width=plot_config['width'],
        title_text="Vibration Data Analysis - Time Domain",
        title_font_size=plot_config['title_font_size'],
        font_size=plot_config['axis_font_size'],
        hovermode='x unified',  # Show all y-values at same x
        template='plotly_white',
    )
    
    return fig


def create_frequency_plot(all_spectra: Dict[str, Dict],
                         conditions: List[str],
                         axis_columns: List[str],
                         axis_colors: Dict[str, str],
                         plot_config: Dict,
                         max_frequency: float) -> go.Figure:
    """
    Create a comprehensive multi-panel plot of frequency spectra (FREQUENCY DOMAIN).
    
    Layout: 
    - Rows: One per condition (Healthy, 10 um, etc.)
    - Columns: One per axis (X, Y, Z)
    
    Args:
        all_spectra: Dictionary mapping condition names to frequency spectra
        conditions: List of conditions in desired display order
        axis_columns: List of axis column names ['X', 'Y', 'Z']
        axis_colors: Dictionary mapping axis names to colors
        plot_config: Dictionary with plot configuration parameters
        max_frequency: Maximum frequency to display
        
    Returns:
        Plotly Figure object
    """
    n_conditions = len(conditions)
    n_axes = len(axis_columns)
    
    print(f"\n📊 Creating FREQUENCY DOMAIN plot: {n_conditions} rows × {n_axes} columns")
    
    # Calculate global magnitude ranges for consistent scaling
    global_ranges = calculate_global_frequency_ranges(
        all_spectra, axis_columns, max_frequency
    )
    
    # Create subplot titles
    subplot_titles = []
    for condition in conditions:
        for axis in axis_columns:
            subplot_titles.append(f"{condition} - {axis} axis")
    
    # Create subplots
    fig = make_subplots(
        rows=n_conditions,
        cols=n_axes,
        subplot_titles=subplot_titles,
        vertical_spacing=0.05,
        horizontal_spacing=0.03,
        shared_xaxes='rows',  # Share x-axis (frequency) across rows
    )
    
    # Add traces for each condition and axis
    for row_idx, condition in enumerate(conditions, start=1):
        if condition not in all_spectra:
            print(f"⚠️  Warning: No spectrum data for condition '{condition}'")
            continue
        
        spectrum = all_spectra[condition]
        
        for col_idx, axis in enumerate(axis_columns, start=1):
            frequencies = spectrum[axis]['frequencies']
            magnitudes = spectrum[axis]['magnitude']
            
            # Filter to max frequency
            mask = frequencies <= max_frequency
            freq_plot = frequencies[mask]
            mag_plot = magnitudes[mask]
            
            # Add the trace
            fig.add_trace(
                go.Scatter(
                    x=freq_plot,
                    y=mag_plot,
                    mode='lines',
                    name=f"{condition} - {axis}",
                    line=dict(color=axis_colors[axis], width=1.5),
                    fill='tozeroy',  # Fill area under curve
                    fillcolor=axis_colors[axis],
                    opacity=0.3,
                    showlegend=False,
                ),
                row=row_idx,
                col=col_idx
            )
            
            # Update axes for this subplot
            fig.update_xaxes(
                title_text="Frequency (Hz)" if row_idx == n_conditions else "",
                range=[0, max_frequency],
                row=row_idx,
                col=col_idx
            )
            
            fig.update_yaxes(
                title_text="Magnitude" if col_idx == 1 else "",
                range=global_ranges[axis],
                row=row_idx,
                col=col_idx
            )
    
    # Update overall layout
    total_height = plot_config['height_per_row'] * n_conditions
    
    fig.update_layout(
        height=total_height,
        width=plot_config['width'],
        title_text="Vibration Data Analysis - Frequency Domain (FFT)",
        title_font_size=plot_config['title_font_size'],
        font_size=plot_config['axis_font_size'],
        hovermode='x unified',
        template='plotly_white',
    )
    
    return fig