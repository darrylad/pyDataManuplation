"""
Noise Addition Tool for Vibration Data CSV Files
Adds various types of noise to accelerometer data for model robustness testing
"""

import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.interpolate import interp1d
from typing import List, Dict, Tuple
import argparse
from datetime import datetime


# ============================================================================
# NOISE GENERATION FUNCTIONS
# ============================================================================

def add_gaussian_noise(signal: np.ndarray, snr_db: float) -> np.ndarray:
    """
    Add white Gaussian noise to signal at specified SNR.
    
    Args:
        signal: 1D array of signal values
        snr_db: Signal-to-noise ratio in dB (higher = less noise)
    
    Returns:
        Noisy signal
    """
    signal_power = np.mean(signal ** 2)
    noise_power = signal_power / (10 ** (snr_db / 10))
    noise = np.random.normal(0, np.sqrt(noise_power), len(signal))
    return signal + noise


def add_operational_noise(signal: np.ndarray, variation_percent: float = 5) -> np.ndarray:
    """
    Simulate operational variation (speed/load changes) via time-warping.
    
    Args:
        signal: 1D array of signal values
        variation_percent: Percentage of variation (default 5%)
    
    Returns:
        Time-warped signal with same length as input
    """
    original_length = len(signal)
    
    # Random time-stretch factor
    stretch = 1 + np.random.uniform(-variation_percent/100, variation_percent/100)
    
    # Resample signal
    orig_time = np.arange(original_length)
    new_time = np.linspace(0, original_length-1, int(original_length * stretch))
    
    interpolator = interp1d(orig_time, signal, kind='cubic', 
                           fill_value='extrapolate', bounds_error=False)
    warped = interpolator(new_time)
    
    # Ensure output has exactly the same length as input
    if len(warped) > original_length:
        # Truncate if too long
        return warped[:original_length]
    elif len(warped) < original_length:
        # Pad with last value if too short
        padding = np.full(original_length - len(warped), warped[-1])
        return np.concatenate([warped, padding])
    else:
        return warped


# ============================================================================
# USER INTERACTION FUNCTIONS
# ============================================================================

def validate_input_folder(folder_path: str) -> Path:
    """Validate input folder path."""
    folder_path = Path(folder_path).expanduser().resolve()
    
    if not folder_path.exists():
        print(f"❌ Error: '{folder_path}' does not exist.")
        sys.exit(1)
    
    if not folder_path.is_dir():
        print(f"❌ Error: '{folder_path}' is not a directory.")
        sys.exit(1)
    
    return folder_path


def select_noise_types() -> List[str]:
    """Prompt user to select noise types."""
    print("\n" + "="*60)
    print("SELECT NOISE TYPES")
    print("="*60)
    print("1. Gaussian White Noise (sensor noise)")
    print("2. Operational Variation (speed/load changes)")
    print("\nEnter comma-separated numbers (e.g., '1' or '1,2'): ", end="")
    
    selection = input().strip()
    
    noise_map = {
        '1': 'gaussian',
        '2': 'operational'
    }
    
    selected = []
    for num in selection.split(','):
        num = num.strip()
        if num in noise_map:
            selected.append(noise_map[num])
        else:
            print(f"⚠️  Warning: Ignoring invalid selection '{num}'")
    
    if not selected:
        print("❌ No valid noise types selected. Using Gaussian noise as default.")
        selected = ['gaussian']
    
    return selected


def get_snr_levels() -> List[float]:
    """Get SNR levels for Gaussian noise."""
    print("\n" + "="*60)
    print("SNR LEVELS FOR GAUSSIAN NOISE")
    print("="*60)
    print("Default SNR levels: [40, 30, 20, 15, 10] dB")
    print("(40 dB = clean, 30 dB = good, 20 dB = noisy, 10 dB = very noisy)")
    print("\nPress ENTER for default, or enter custom values (comma-separated): ", end="")
    
    user_input = input().strip()
    
    if not user_input:
        return [40, 30, 20, 15, 10]
    
    try:
        snr_levels = [float(x.strip()) for x in user_input.split(',')]
        if all(s > 0 for s in snr_levels):
            return sorted(snr_levels, reverse=True)
        else:
            print("⚠️  Invalid SNR values. Using defaults.")
            return [40, 30, 20, 15, 10]
    except ValueError:
        print("⚠️  Invalid input. Using default SNR levels.")
        return [40, 30, 20, 15, 10]


def get_operational_variation() -> float:
    """Get operational variation percentage."""
    print("\n" + "="*60)
    print("OPERATIONAL VARIATION PERCENTAGE")
    print("="*60)
    print("Default: 5% (simulates ±5% speed/load variation)")
    print("\nPress ENTER for default, or enter custom percentage (1-20): ", end="")
    
    user_input = input().strip()
    
    if not user_input:
        return 5.0
    
    try:
        variation = float(user_input)
        if 1 <= variation <= 20:
            return variation
        else:
            print("⚠️  Value out of range. Using default 5%.")
            return 5.0
    except ValueError:
        print("⚠️  Invalid input. Using default 5%.")
        return 5.0


def select_columns(df: pd.DataFrame) -> List[str]:
    """Let user select which columns to add noise to."""
    print("\n" + "="*60)
    print("SELECT COLUMNS FOR NOISE ADDITION")
    print("="*60)
    
    columns = df.columns.tolist()
    for i, col in enumerate(columns, 1):
        print(f"{i}. {col}")
    
    print("\nEnter comma-separated numbers (e.g., '2,3,4' for X,Y,Z): ", end="")
    selection = input().strip()
    
    if not selection:
        # Default: select all numeric columns except first (time)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if columns[0] in numeric_cols:
            numeric_cols.remove(columns[0])
        return numeric_cols
    
    try:
        indices = [int(x.strip()) - 1 for x in selection.split(',')]
        selected_cols = [columns[i] for i in indices if 0 <= i < len(columns)]
        
        if selected_cols:
            return selected_cols
        else:
            print("⚠️  No valid columns. Using X, Y, Z by default.")
            return ['X', 'Y', 'Z']
    except (ValueError, IndexError):
        print("⚠️  Invalid selection. Using X, Y, Z by default.")
        return ['X', 'Y', 'Z']


def confirm_processing() -> bool:
    """Ask user to confirm before starting processing."""
    print("\n" + "="*60)
    print("READY TO START PROCESSING")
    print("="*60)
    while True:
        response = input("\nStart processing? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            print("\n⚠️  Processing cancelled by user.")
            return False
        else:
            print("⚠️  Please enter 'y' or 'n'")


# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================

class ProcessingLogger:
    """Logger for tracking processing configuration and results."""
    
    def __init__(self, output_base: Path):
        self.output_base = output_base
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = output_base / f"processing_log_{self.timestamp}.txt"
        self.processed_files = []
        self.failed_files = []
        
    def write_header(self, config: Dict):
        """Write configuration header to log file."""
        with open(self.log_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("VIBRATION DATA NOISE ADDITION - PROCESSING LOG\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Log File: {self.log_file.name}\n\n")
            
            f.write("-"*80 + "\n")
            f.write("CONFIGURATION\n")
            f.write("-"*80 + "\n")
            f.write(f"Input Folder: {config['input_folder']}\n")
            f.write(f"Output Folder: {config['output_folder']}\n")
            f.write(f"Total CSV Files Found: {config['total_files']}\n\n")
            
            f.write(f"Noise Types: {', '.join(config['noise_types'])}\n")
            
            if 'gaussian' in config['noise_types']:
                f.write(f"SNR Levels (dB): {config['snr_levels']}\n")
            
            if 'operational' in config['noise_types']:
                f.write(f"Operational Variation: ±{config['op_variation']}%\n")
            
            f.write(f"Columns with Noise Applied: {', '.join(config['columns'])}\n\n")
            
            f.write("-"*80 + "\n")
            f.write("OUTPUT STRUCTURE\n")
            f.write("-"*80 + "\n")
            
            if 'gaussian' in config['noise_types']:
                for snr in config['snr_levels']:
                    f.write(f"  gaussian_snr{int(snr)}/\n")
                    f.write(f"    └── [maintains input folder structure]\n")
            
            if 'operational' in config['noise_types']:
                f.write(f"  operational_var{int(config['op_variation'])}/\n")
                f.write(f"    └── [maintains input folder structure]\n")
            
            f.write("\n")
    
    def log_processed(self, csv_path: Path, success: bool = True):
        """Log a processed file."""
        if success:
            self.processed_files.append(str(csv_path))
        else:
            self.failed_files.append(str(csv_path))
    
    def write_summary(self, total_counts: Dict[str, int]):
        """Write processing summary to log file."""
        with open(self.log_file, 'a') as f:
            f.write("-"*80 + "\n")
            f.write("PROCESSING SUMMARY\n")
            f.write("-"*80 + "\n")
            f.write(f"Successfully Processed: {len(self.processed_files)} files\n")
            f.write(f"Failed: {len(self.failed_files)} files\n\n")
            
            f.write("Output Files Generated:\n")
            for noise_type, count in sorted(total_counts.items()):
                f.write(f"  • {noise_type}: {count} files\n")
            
            f.write(f"\nTotal Output Files: {sum(total_counts.values())}\n\n")
            
            if self.failed_files:
                f.write("-"*80 + "\n")
                f.write("FAILED FILES\n")
                f.write("-"*80 + "\n")
                for failed in self.failed_files:
                    f.write(f"  ✗ {failed}\n")
                f.write("\n")
            
            f.write("-"*80 + "\n")
            f.write("SUCCESSFULLY PROCESSED FILES\n")
            f.write("-"*80 + "\n")
            for processed in self.processed_files:
                f.write(f"  ✓ {processed}\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write(f"Log completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n")


# ============================================================================
# CSV PROCESSING FUNCTIONS
# ============================================================================

def find_csv_files(root_folder: Path) -> List[Path]:
    """Recursively find all CSV files in folder and subfolders."""
    csv_files = list(root_folder.rglob("*.csv"))
    return csv_files


def process_csv_file(
    csv_path: Path,
    noise_types: List[str],
    snr_levels: List[float],
    op_variation: float,
    columns_to_noise: List[str],
    output_base: Path,
    input_base: Path,
    logger: ProcessingLogger
) -> Dict[str, int]:
    """
    Process a single CSV file with selected noise types.
    
    Returns:
        Dictionary with counts of files generated per noise type
    """
    # Read CSV
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        logger.log_processed(csv_path, success=False)
        return {}
    
    # Verify columns exist
    valid_cols = [col for col in columns_to_noise if col in df.columns]
    if not valid_cols:
        logger.log_processed(csv_path, success=False)
        return {}
    
    # Calculate relative path to maintain structure
    rel_path = csv_path.relative_to(input_base)
    
    file_counts = {}
    
    # Process Gaussian noise
    if 'gaussian' in noise_types:
        for snr in snr_levels:
            noisy_df = df.copy()
            
            for col in valid_cols:
                noisy_df[col] = add_gaussian_noise(df[col].values, snr)
            
            # Create output path
            output_dir = output_base / f"gaussian_snr{int(snr)}" / rel_path.parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_filename = f"{csv_path.stem}_snr{int(snr)}.csv"
            output_path = output_dir / output_filename
            
            noisy_df.to_csv(output_path, index=False)
            
            file_counts[f"gaussian_snr{int(snr)}"] = file_counts.get(f"gaussian_snr{int(snr)}", 0) + 1
    
    # Process Operational noise
    if 'operational' in noise_types:
        noisy_df = df.copy()
        
        for col in valid_cols:
            noisy_signal = add_operational_noise(df[col].values, op_variation)
            # Ensure the length matches
            if len(noisy_signal) != len(df):
                logger.log_processed(csv_path, success=False)
                return file_counts
            noisy_df[col] = noisy_signal
        
        # Create output path
        output_dir = output_base / f"operational_var{int(op_variation)}" / rel_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_filename = f"{csv_path.stem}_opvar{int(op_variation)}.csv"
        output_path = output_dir / output_filename
        
        noisy_df.to_csv(output_path, index=False)
        
        file_counts[f"operational_var{int(op_variation)}"] = file_counts.get(f"operational_var{int(op_variation)}", 0) + 1
    
    # Log success
    logger.log_processed(csv_path, success=True)
    return file_counts


def print_progress(iteration, total, current_file):
    """Print simple progress: percentage, count, and filename."""
    percent = 100 * (iteration / float(total))
    
    # Truncate filename if too long
    max_filename_len = 60
    if len(current_file) > max_filename_len:
        display_name = '...' + current_file[-(max_filename_len-3):]
    else:
        display_name = current_file
    
    print(f'\r{percent:.1f}% | {iteration}/{total} | {display_name}', end='', flush=True)
    
    if iteration == total:
        print()  # New line on completion


# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Add realistic noise to vibration CSV data for ML model robustness testing.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py /path/to/csv/folder
  python main.py ~/data/vibration_csvs
  python main.py .
        """
    )
    parser.add_argument(
        'input_folder',
        type=str,
        help='Path to the folder containing CSV files (searched recursively)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("VIBRATION DATA NOISE ADDITION TOOL")
    print("="*60)
    print("This tool adds realistic noise to CSV vibration data")
    print("for testing ML model robustness.")
    
    # Step 1: Validate input folder
    input_folder = validate_input_folder(args.input_folder)
    print(f"\n✓ Input folder: {input_folder}")
    
    # Step 2: Find CSV files
    csv_files = find_csv_files(input_folder)
    
    if not csv_files:
        print(f"\n❌ No CSV files found in '{input_folder}'")
        sys.exit(1)
    
    print(f"✓ Found {len(csv_files)} CSV file(s)")
    
    # Step 3: Select noise types
    noise_types = select_noise_types()
    print(f"\n✓ Selected noise types: {', '.join(noise_types)}")
    
    # Step 4: Get parameters
    snr_levels = []
    op_variation = 5.0
    
    if 'gaussian' in noise_types:
        snr_levels = get_snr_levels()
        print(f"✓ SNR levels: {snr_levels} dB")
    
    if 'operational' in noise_types:
        op_variation = get_operational_variation()
        print(f"✓ Operational variation: ±{op_variation}%")
    
    # Step 5: Select columns (using first CSV as reference)
    sample_df = pd.read_csv(csv_files[0])
    columns_to_noise = select_columns(sample_df)
    print(f"\n✓ Columns to add noise: {', '.join(columns_to_noise)}")
    
    # Step 6: Set up output folder
    output_base = Path.cwd() / "outputs"
    output_base.mkdir(exist_ok=True)
    
    print(f"\n✓ Output folder: {output_base}")
    
    # Step 7: Confirmation prompt
    if not confirm_processing():
        sys.exit(0)
    
    # Step 8: Initialize logger
    config = {
        'input_folder': str(input_folder),
        'output_folder': str(output_base),
        'total_files': len(csv_files),
        'noise_types': noise_types,
        'snr_levels': snr_levels if 'gaussian' in noise_types else [],
        'op_variation': op_variation if 'operational' in noise_types else 0,
        'columns': columns_to_noise
    }
    
    logger = ProcessingLogger(output_base)
    logger.write_header(config)
    
    print(f"\n✓ Log file: {logger.log_file.name}")
    
    # Step 9: Process all CSV files with simple progress display
    print("\n" + "="*60)
    print("PROCESSING FILES")
    print("="*60)
    print()
    
    total_counts = {}
    total_files = len(csv_files)
    
    for i, csv_path in enumerate(csv_files, 1):
        # Update progress
        print_progress(i, total_files, csv_path.name)
        
        counts = process_csv_file(
            csv_path,
            noise_types,
            snr_levels,
            op_variation,
            columns_to_noise,
            output_base,
            input_folder,
            logger
        )
        
        # Aggregate counts
        for key, count in counts.items():
            total_counts[key] = total_counts.get(key, 0) + count
    
    # Step 10: Write summary to log
    logger.write_summary(total_counts)
    
    # Step 11: Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✓ Processed {len(csv_files)} CSV files")
    print(f"  • Successful: {len(logger.processed_files)}")
    print(f"  • Failed: {len(logger.failed_files)}")
    print(f"\n✓ Total output files generated:")
    for noise_type, count in sorted(total_counts.items()):
        print(f"  • {noise_type}: {count} files")
    print(f"\n✓ All outputs saved to: {output_base}")
    print(f"✓ Log file saved to: {logger.log_file}")
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)