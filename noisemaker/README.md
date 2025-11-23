# Noisemaker

Add realistic noise to vibration CSV data for testing ML model robustness.

## Features

- **Gaussian White Noise**: Simulates sensor noise at configurable SNR levels
- **Operational Variation**: Simulates speed/load changes via time-warping
- Processes folders recursively
- Maintains original folder structure in outputs
- Never modifies source files

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

```bash
python main.py <PATH_TO_CSV_FOLDER>
```

### Interactive Prompts

The tool will guide you through:

1. **Noise Type Selection**: Gaussian, Operational, or both
2. **SNR Levels** (if Gaussian): Default `[40, 30, 20, 15, 10]` dB
3. **Operational Variation** (if Operational): Default `±5%`
4. **Column Selection**: Which columns to add noise to

### Example

```bash
# Process all CSVs in a folder
python main.py /path/to/data

# Process CSVs in current directory
python main.py .
```

## Output

Results are saved to `outputs/` with subfolders for each noise type:

```
outputs/
├── gaussian_snr40/
│   └── [maintains input structure]
├── gaussian_snr30/
├── operational_var5/
└── processing_log_YYYYMMDD_HHMMSS.txt
```

## CSV Requirements

- First column: Time/index
- Remaining columns: Numeric data (e.g., X, Y, Z accelerometer axes)

## Deactivate venv

```bash
deactivate
```