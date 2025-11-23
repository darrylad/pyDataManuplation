# Bifurcator

Split datasets into multiple subsets (split-1, split-2, ...) while preserving folder structure.

## Features

- Split files by percentage across multiple subsets
- Filter by file extension
- Randomize file selection with optional seed
- Process leaf folders only or all folders
- Multiple rounding methods for small folders
- Maintains folder hierarchy in output
- Detailed logging

## Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

## Usage

```bash
python main.py <input_path> [output_path]
```

### Arguments

- `input_path` (required): Path to dataset folder
- `output_path` (optional): Custom output location (default: `./outputs`)

### Examples

```bash
# Use default output location
python main.py /path/to/dataset

# Specify custom output location
python main.py /path/to/dataset /custom/output
```

### Interactive Configuration

The tool will prompt you to configure:

1. **Number of splits**: How many subsets (e.g., 2 for train/test, 3 for train/val/test)
2. **Split percentages**: Percentage for each split (last split auto-calculated)
3. **File extensions**: Filter specific file types (e.g., `.png,.jpg`) or process all files
4. **Folder mode**: Process only leaf folders or all folders
5. **Randomization**: Shuffle files with optional seed for reproducibility
6. **Rounding method**: How to handle small folders (standard/floor/ceil/proportional)

## Output

```
outputs/
├── split-1/
│   └── [maintains input structure]
├── split-2/
│   └── [maintains input structure]
├── split-3/
│   └── [maintains input structure]
└── log.txt
```

## Example Session

```
Enter the number of splits: 3
Enter percentage for split-1: 70
Enter percentage for split-2: 15
Split-3 percentage (auto-calculated): 15%
Enter file endings to look for: .png
Process only folders with no subfolders? yes
Randomize file selection? yes
Enter random seed: 42
```

## Deactivate venv

```bash
deactivate
```