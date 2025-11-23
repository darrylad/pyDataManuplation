"""
Configuration file for the vibration data plotter.
This keeps all settings in one place for easy modification.
"""

from pathlib import Path

# Data paths
DATA_ROOT = Path("/Users/darrylad/Darryl/Research/Darryl/Data")

# Conditions to analyze (in display order)
CONDITIONS = ["Healthy", "10 um", "45 um", "75 um", "100 um"]

# Plot configuration
PLOT_CONFIG = {
    "height_per_row": 300,  # Height of each subplot row
    "width": 1800,          # Total width of the plot
    "title_font_size": 16,
    "axis_font_size": 12,
}

# Color scheme for each axis
AXIS_COLORS = {
    "X": "#FF6B6B",  # Red
    "Y": "#4ECDC4",  # Teal
    "Z": "#95E1D3",  # Light teal
}

# Data column names (from your CSV)
TIME_COLUMN = "Channel name"
AXIS_COLUMNS = ["X", "Y", "Z"]

# FFT Configuration
FFT_CONFIG = {
    "nperseg": 1024,        # Window size for Welch's method (power of 2)
    "max_frequency": None,  # Max frequency to display (None = auto, up to Nyquist)
    "freq_units": "Hz",
    "mag_units": "Acceleration (g)",
    "overlap": 512,         # Overlap between segments (usually nperseg/2)
}

# PDF Export Configuration
PDF_CONFIG = {
    # Figure size (width, height) in inches
    # For widescreen: 16:9 aspect ratio
    # 20 inches wide = ~1920px at 96 DPI (typical monitor)
    "figsize": (20, 12),    # Wide format for monitors
    
    # DPI (dots per inch) - resolution quality
    # 150 DPI = good screen quality, reasonable file size
    # 300 DPI = print quality (use if needed, but larger files)
    "dpi": 150,
    
    # Downsampling for faster rendering
    # Keep every Nth point (10 = keep 10%, discard 90%)
    # Visual quality remains identical on screen
    "downsample_factor": 10,
    
    # Line width for plots
    "line_width": 0.8,
    
    # Font sizes
    "title_size": 14,
    "label_size": 10,
    "tick_size": 8,
    "suptitle_size": 16,
    
    # Spacing between subplots
    "hspace": 0.3,  # Vertical space
    "wspace": 0.15,  # Horizontal space
    
    # Rasterization (converts plots to pixels for smaller file size)
    "rasterized": True,
}