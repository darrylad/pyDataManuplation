# CSV Splitter

A simple command-line tool to recursively split large CSV files into smaller chunks.

## Run

Go to the project directory in Terminal and run:

### Setting up a virtual environment (optional but recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

### Get dependencies

```bash
pip install -r requirements.txt
```

### Run

```bash
python main.py <PATH_TO_FOLDER_OR_CSV_FILE> 
```
Replace `<PATH_TO_FOLDER_OR_CSV_FILE>` with the path to the folder containing CSV files or a single CSV file you want to split.

Source files will never be modified. Results will be saved to `outputs/` in the project directory.

### Deactivate virtual environment

```bash
deactivate
```