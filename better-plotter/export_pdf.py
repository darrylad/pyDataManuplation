"""
Standalone PDF export script using Matplotlib.
Run this separately from the main HTML generation.
"""

import logging
import sys
from pathlib import Path

# Import modules
from config import (
    DATA_ROOT, CONDITIONS, AXIS_COLORS,
    TIME_COLUMN, AXIS_COLUMNS, FFT_CONFIG, PDF_CONFIG
)
from data_loader import load_all_conditions
from signal_processor import compute_all_frequency_spectra, get_frequency_display_range
from plotter_static import create_time_domain_pdf, create_frequency_domain_pdf
from logger_utils import setup_logging

# Setup logging will be done in main()
logger = logging.getLogger(__name__)


def main(data_path: Path = None):
    """
    Main function for PDF export.
    
    Args:
        data_path: Optional path to data directory. If None, uses DATA_ROOT from config.
    """
    # Use provided path or default from config
    if data_path is None:
        data_path = DATA_ROOT
    
    # Setup logging to file and console
    output_dir = Path("output")
    log_path = setup_logging(output_dir, "pdf_export_log.txt")
    
    print("📄 PDF EXPORT TOOL (Matplotlib Backend)")
    print(f"\nUsing data path: {data_path}")
    print(f"Logging to: {log_path}")
    print(f"\nConfiguration:")
    print(f"  Figure size: {PDF_CONFIG['figsize'][0]}\" × {PDF_CONFIG['figsize'][1]}\"")
    print(f"  DPI: {PDF_CONFIG['dpi']}")
    print(f"  Downsampling: Every {PDF_CONFIG['downsample_factor']} points")
    print(f"  Rasterized: {PDF_CONFIG['rasterized']}")
    
    print("STEP 1: LOADING DATA")
    
    all_data = load_all_conditions(data_path, CONDITIONS)
    
    if not all_data:
        logger.error("❌ No data loaded! Check your data path.")
        return
    
    print(f"\n✅ Loaded {len(all_data)} conditions")
    
    print("STEP 2: COMPUTING FREQUENCY SPECTRA")
    
    all_spectra = compute_all_frequency_spectra(
        all_data=all_data,
        time_column=TIME_COLUMN,
        axis_columns=AXIS_COLUMNS,
        fft_config=FFT_CONFIG
    )
    
    max_freq = get_frequency_display_range(all_spectra, FFT_CONFIG)
    
    print(f"\n✅ Computed spectra for {len(all_spectra)} conditions")
    
    # Output directory already exists from logging setup
    output_dir.mkdir(exist_ok=True)
    
    print("STEP 3: GENERATING TIME-DOMAIN PDF")
    
    time_pdf_path = output_dir / "time_domain.pdf"
    create_time_domain_pdf(
        all_data=all_data,
        conditions=CONDITIONS,
        time_column=TIME_COLUMN,
        axis_columns=AXIS_COLUMNS,
        axis_colors=AXIS_COLORS,
        pdf_config=PDF_CONFIG,
        output_path=time_pdf_path
    )
    
    print("STEP 4: GENERATING FREQUENCY-DOMAIN PDF")
    
    freq_pdf_path = output_dir / "frequency_domain.pdf"
    create_frequency_domain_pdf(
        all_spectra=all_spectra,
        conditions=CONDITIONS,
        axis_columns=AXIS_COLUMNS,
        axis_colors=AXIS_COLORS,
        pdf_config=PDF_CONFIG,
        max_frequency=max_freq,
        output_path=freq_pdf_path
    )
    
    print("PDF EXPORT COMPLETE")
    print("\nGenerated files:")
    print(f"  📈 Time Domain:      {time_pdf_path}")
    print(f"  📊 Frequency Domain: {freq_pdf_path}")
    print(f"  📝 Log File:         {log_path}")
    print("\nFile specifications:")
    print(f"  Format: PDF (rasterized)")
    print(f"  Resolution: {PDF_CONFIG['dpi']} DPI")
    print(f"  Size: {PDF_CONFIG['figsize'][0]}\" × {PDF_CONFIG['figsize'][1]}\"")
    print(f"  Optimized for: Widescreen displays")


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