
# Data Manipulation Tools

Utilities for manipulating data in batches using Python. Source files are never modified. Outputs are saved to `outputs/` in each project.

## Run

Go to the root directory of your desired project in Terminal and run:

### Setup Python venv

```bash
# Create a virtual environment:
python3 -m venv .venv

# Activate the virtual environment:
source .venv/bin/activate   # On Windows use `.venv\Scripts\activate`
```
### Get Requirements

```bash
pip install -r requirements.txt
```
This will install the required packages into your virtual environment.

### General Usage

```bash
python <PROJECT_MAIN_FILE> <ARGUMENTS>
```

For more details, see the `README.md` file in each project folder.

### Deactivate venv

```bash
# When done, deactivate the virtual environment:
deactivate
``` 