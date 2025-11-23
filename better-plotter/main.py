"""
Main script to run the vibration data analysis and plotting.
"""

import logging
import sys
from pathlib import Path

# Import our modules
from config import (
    DATA_ROOT, CONDITIONS, PLOT_CONFIG, AXIS_COLORS, 
    TIME_COLUMN, AXIS_COLUMNS, FFT_CONFIG
)
from data_loader import load_all_conditions
from plotter import create_vibration_plot, create_frequency_plot
from signal_processor import compute_all_frequency_spectra, get_frequency_display_range
from logger_utils import setup_logging

# Setup logging will be done in main()
logger = logging.getLogger(__name__)


def main(data_path: Path = None):
    """
    Main function to execute the complete analysis pipeline.
    
    Args:
        data_path: Optional path to data directory. If None, uses DATA_ROOT from config.
    """
    # Use provided path or default from config
    if data_path is None:
        data_path = DATA_ROOT
    
    # Setup logging to file and console 
    output_dir = Path("output")
    log_path = setup_logging(output_dir, "log.txt")
    
    print(f"Using data path: {data_path}")
    print(f"Logging to: {log_path}\n")
    
    print("STEP 1: LOADING DATA")
    
    all_data = load_all_conditions(data_path, CONDITIONS)
    
    if not all_data:
        logger.error("❌ No data loaded! Check your data path and condition names.")
        return
    
    print(f"\n✅ Successfully loaded {len(all_data)} conditions")
    
    print("STEP 2: COMPUTING FREQUENCY SPECTRA (FFT)")
    
    all_spectra = compute_all_frequency_spectra(
        all_data=all_data,
        time_column=TIME_COLUMN,
        axis_columns=AXIS_COLUMNS,
        fft_config=FFT_CONFIG
    )
    
    # Determine frequency display range
    max_freq = get_frequency_display_range(all_spectra, FFT_CONFIG)
    
    print(f"\n✅ Successfully computed spectra for {len(all_spectra)} conditions")
    
    print("STEP 3: CREATING TIME DOMAIN PLOT")
    
    time_fig = create_vibration_plot(
        all_data=all_data,
        conditions=CONDITIONS,
        time_column=TIME_COLUMN,
        axis_columns=AXIS_COLUMNS,
        axis_colors=AXIS_COLORS,
        plot_config=PLOT_CONFIG
    )
    
    print("STEP 4: CREATING FREQUENCY DOMAIN PLOT")
    
    freq_fig = create_frequency_plot(
        all_spectra=all_spectra,
        conditions=CONDITIONS,
        axis_columns=AXIS_COLUMNS,
        axis_colors=AXIS_COLORS,
        plot_config=PLOT_CONFIG,
        max_frequency=max_freq
    )
    
    print("STEP 5: SAVING")

    # Create output directory (already exists from logging setup)
    output_dir.mkdir(exist_ok=True)
    
    # Save time domain plot
    time_output = output_dir / "time_domain.html"
    time_fig.write_html(str(time_output))
    print(f"\n✅ Time domain plot saved to: {time_output}")
    
    # Save frequency domain plot
    freq_output = output_dir / "frequency_domain.html"
    freq_fig.write_html(str(freq_output))
    print(f"✅ Frequency domain plot saved to: {freq_output}")
    
    print("COMPLETE")
    print("\nGenerated files:")
    print(f"  📈 Time Domain:      {time_output}")
    print(f"  📊 Frequency Domain: {freq_output}")
    print(f"  📝 Log File:         {log_path}")
    print("\nInteractive features:")
    print("  • Zoom: Click and drag")
    print("  • Pan: Hold shift and drag")
    print("  • Reset: Double click")
    print("  • Hover: See exact values")
    print("  • Compare: Hover shows all values at same point")


if __name__ == "__main__":
    # Check for command-line argument
    if len(sys.argv) > 1:
        # Use provided path
        custom_path = Path(sys.argv[1])
        if not custom_path.exists():
            print(f"❌ Path does not exist: {custom_path}")
            sys.exit(1)
        main(data_path=custom_path)
    else:
        # Use default path from config
        main()