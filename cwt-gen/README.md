
# Continuous Wavelet Transform 

Generate RGB scalogram images from CSV files using Continuous Wavelet Transform (CWT). The program maps X, Y, Z columns to R, G, B channels respectively.

## Setup

### Create Python venv

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

### Install Requirements

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Process a single CSV file
python main.py data.csv

# Process all CSV files in a directory (recursive)
python main.py /path/to/folder
```

### Advanced Options

```bash
# Custom image resolution
python main.py data.csv --width 256 --height 256

# Custom frequency resolution (more scales = higher frequency detail)
python main.py data.csv --scales 128

# All custom parameters
python main.py /path/to/folder --scales 128 --width 256 --height 256
```

### Arguments

- `path` (required): Path to CSV file or directory
- `--scales N`: Number of wavelet scales (default: 128)
- `--width PIXELS`: Output image width (default: 1024)
- `--height PIXELS`: Output image height (default: 512)
- `--version`: Show version information

## Requirements

CSV files must contain columns named: **X**, **Y**, **Z**

## Output

- RGB PNG images saved to `outputs/[path]/*_cwt.png`
- Processing log saved to `outputs/log.txt`
- Original folder structure is maintained

Source files are never modified.

## Deactivate Python venv

```bash
deactivate
```