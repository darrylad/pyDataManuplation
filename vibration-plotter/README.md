# Vibration Data Plotter

Visualize vibration data across multiple experimental conditions. Generates interactive HTML plots and high-quality PDF exports with both time-domain and frequency-domain (FFT) analysis.

## Features

- **Time Domain Analysis**: Visualize raw acceleration data across X, Y, Z axes
- **Frequency Domain Analysis**: FFT-based frequency spectrum using Welch's method
- **Interactive HTML Plots**: Zoom, pan, and explore data with Plotly
- **PDF Export**: High-quality static plots optimized for presentations and reports
- **Multi-Condition Comparison**: Analyze multiple experimental conditions side-by-side

## Setup

```bash
# Navigate to project directory
cd vibration-plotter

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Edit `config.py` to set:
- `DATA_ROOT`: Path to your data directory
- `CONDITIONS`: List of condition folder names (e.g., ["Healthy", "10 um", "45 um"])
- Plot appearance and FFT parameters

## Usage

### Generate Interactive HTML Plots

```bash
# Use default data path from config.py
python main.py

# Or specify custom data path
python main.py /path/to/your/data
```

**Outputs** (in `output/` folder):
- `time_domain.html` - Interactive time-series plots
- `frequency_domain.html` - Interactive FFT spectrum plots
- `log.txt` - Processing log

### Export High-Quality PDFs

```bash
# Use default data path from config.py
python export_pdf.py

# Or specify custom data path
python export_pdf.py /path/to/your/data
```

**Outputs** (in `output/` folder):
- `time_domain.pdf` - Static time-series plots
- `frequency_domain.pdf` - Static FFT spectrum plots
- `pdf_export_log.txt` - Export log

## Data Format

Expected CSV structure:
- One folder per condition (e.g., `Healthy/`, `10 um/`)
- CSV files with columns: `Channel name` (time), `X`, `Y`, `Z` (acceleration)
- Multiple CSV files per condition are automatically concatenated

## Interactive Plot Features

- **Zoom**: Click and drag
- **Pan**: Hold Shift and drag
- **Reset**: Double-click
- **Hover**: See exact values at any point
- **Compare**: Unified hover shows all values at same time point
