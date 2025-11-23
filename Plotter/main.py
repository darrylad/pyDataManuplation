import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.gridspec as gridspec

def plot_signal_file(ax, csv_path):
    """Plot a single signal CSV file on given axes"""
    df = pd.read_csv(csv_path)
    
    # Rasterize the plot lines to reduce file size
    ax.plot(df['time'], df['ch1'], label='CH1', color='blue', linewidth=0.8, rasterized=True)
    ax.plot(df['time'], df['ch2'], label='CH2', color='red', linewidth=0.8, rasterized=True)
    
    ax.set_xlabel('Time (s)', fontsize=8)
    ax.set_ylabel('Signal Value', fontsize=8)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=7)

def plot_all_signals_pdf(data_root='PHMDC2019_Data', output_pdf='signal_plots.pdf'):
    """
    Plot all signal files organized by folder pairs (signal_1 and signal_2) in a PDF
    
    Parameters:
    - data_root: Root directory of the dataset
    - output_pdf: Output PDF filename
    """
    data_path = Path(data_root)
    
    # Find all directories containing signal files
    signal_dirs = set()
    for signal_file in data_path.glob('**/signal_*.csv'):
        signal_dirs.add(signal_file.parent)
    
    signal_dirs = sorted(signal_dirs)
    print(f"Found {len(signal_dirs)} directories with signal files")
    
    # Create PDF
    with PdfPages(output_pdf) as pdf:
        rows_per_page = 4  # Number of folder pairs per page
        
        for page_start in range(0, len(signal_dirs), rows_per_page):
            page_dirs = signal_dirs[page_start:page_start + rows_per_page]
            
            # Create figure for this page
            fig = plt.figure(figsize=(11, 14))  # Letter size
            
            for idx, signal_dir in enumerate(page_dirs):
                # Get the parent folder names for title
                parent_names = f"{signal_dir.parent.name}/{signal_dir.name}"
                
                # Find signal_1 and signal_2 files
                signal_1 : Path = signal_dir / 'signal_1.csv'
                signal_2 : Path = signal_dir / 'signal_2.csv'

                # Create subplot for this row (2 columns)
                # Left column: signal_1
                ax1: plt.Axes = plt.subplot(rows_per_page, 2, idx * 2 + 1)
                if signal_1.exists():
                    try:
                        plot_signal_file(ax1, signal_1)
                        ax1.set_title(f"{parent_names} - Signal 1", fontsize=9, fontweight='bold')
                    except Exception as e:
                        ax1.text(0.5, 0.5, f'Error: {e}', ha='center', va='center', transform=ax1.transAxes)
                        ax1.set_title(f"{parent_names} - Signal 1 (Error)", fontsize=9, color='red')
                else:
                    ax1.text(0.5, 0.5, 'File not found', ha='center', va='center', transform=ax1.transAxes)
                    ax1.set_title(f"{parent_names} - Signal 1 (Missing)", fontsize=9, color='gray')
                
                # Right column: signal_2
                ax2 = plt.subplot(rows_per_page, 2, idx * 2 + 2)
                if signal_2.exists():
                    try:
                        plot_signal_file(ax2, signal_2)
                        ax2.set_title(f"{parent_names} - Signal 2", fontsize=9, fontweight='bold')
                    except Exception as e:
                        ax2.text(0.5, 0.5, f'Error: {e}', ha='center', va='center', transform=ax2.transAxes)
                        ax2.set_title(f"{parent_names} - Signal 2 (Error)", fontsize=9, color='red')
                else:
                    ax2.text(0.5, 0.5, 'File not found', ha='center', va='center', transform=ax2.transAxes)
                    ax2.set_title(f"{parent_names} - Signal 2 (Missing)", fontsize=9, color='gray')
            
            plt.tight_layout()
            # Increase DPI for rasterized content to maintain quality
            pdf.savefig(fig, dpi=200)
            plt.close(fig)
            
            print(f"Processed page {page_start // rows_per_page + 1} ({len(page_dirs)} folders)")
    
    print(f"\nAll plots saved to: {output_pdf}")


if __name__ == "__main__":
    # Create single PDF with all plots
    plot_all_signals_pdf(
        data_root="/Users/darrylad/Darryl/Research/18. Fatigue Crack Growth in Aluminum Lap Joint",
        output_pdf="signal_plots.pdf"
    )