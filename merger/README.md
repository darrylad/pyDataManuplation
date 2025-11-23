# CSV Merger

Merges CSV files containing exercise data by class with continuous time values.

## Description

This tool processes a directory structure where:
- First-level subdirectories represent classes
- CSV files within each class folder contain exercise data
- Files are merged vertically with continuous time columns (no overlapping timestamps)

## Usage

```bash
python main.py <root_directory_path> [output_directory]
```

### Arguments

- `root_directory_path` (required): Path to the directory containing class folders
- `output_directory` (optional): Custom output directory (defaults to `./outputs`)

### Examples

```bash
# Use default output directory (./outputs)
python main.py /Users/darrylad/Darryl/Research/Darryl/Data

# Specify custom output directory
python main.py /path/to/data /path/to/custom/output
```

## Input Structure

```
root_directory/
├── Class1/
│   ├── DO200B Ex1.csv
│   ├── DO200B Ex2 5min.csv
│   └── DO200B Ex3.csv
└── Class2/
    ├── Ex1.csv
    └── Ex2.csv
```

## Output Structure

```
outputs/
├── Class1/
│   └── Class1_merged.csv
├── Class2/
│   └── Class2_merged.csv
└── merger_log_YYYYMMDD_HHMMSS.txt
```

## Features

- Natural sorting of files (Ex1, Ex2, Ex10, Ex11...)
- Continuous time column across merged exercises
- Preserves all data with maximum precision
- Generates detailed log file
- Creates organized output folders by class

## Requirements

See `requirements.txt`:
- pandas>=2.0.0
- natsort>=8.0.0