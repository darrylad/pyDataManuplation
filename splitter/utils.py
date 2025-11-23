from pathlib import Path
from typing import Dict, List
from logger import logged_input

def display_csv_info(csv_files: Dict[Path, Dict]):
    """
    Display information about all CSV files found.
    
    Args:
        csv_files: Dictionary mapping file paths to their info
    """
    print("\n" + "="*60)
    print("CSV FILES FOUND")
    print("="*60)
    
    for csv_path, info in csv_files.items():
        print(f"\nFile: {csv_path.name}")
        print(f"  Total data points: {info['total_rows']}")
        if info['first_point']:
            print(f"  First data point: {info['first_point']}")
    
    print("\n" + "="*60 + "\n")

def display_columns(columns: List[str]):
    """
    Display available columns with their index numbers.
    
    Args:
        columns: List of column names
    """
    print("\n" + "="*60)
    print("AVAILABLE COLUMNS")
    print("="*60)
    print("0. No normalization")
    for idx, col in enumerate(columns, 1):
        print(f"{idx}. {col}")
    print("="*60 + "\n")

def get_normalization_choices(columns: List[str]) -> List[str]:
    """
    Get user's choice for columns to normalize.
    
    Args:
        columns: List of available column names
        
    Returns:
        List of column names to normalize
    """
    display_columns(columns)
    
    choice_str = logged_input(
        "Enter column numbers to normalize (comma-separated, 0 for none): "
    ).strip()
    
    if choice_str == '0' or not choice_str:
        print("[CONFIG] No normalization selected")
        return []
    
    # Parse comma-separated choices
    try:
        choices = [int(x.strip()) for x in choice_str.split(',')]
        normalize_cols = []
        
        for choice in choices:
            if choice == 0:
                continue
            elif 1 <= choice <= len(columns):
                col_name = columns[choice - 1]
                normalize_cols.append(col_name)
                print(f"[CONFIG] Will normalize column: {col_name}")
            else:
                print(f"[WARNING] Invalid choice {choice}, skipping")
        
        return normalize_cols
    
    except ValueError:
        print("[ERROR] Invalid input format. No normalization will be applied.")
        return []

def get_user_choice(prompt: str, valid_choices: List[str]) -> str:
    """
    Get user input with validation.
    
    Args:
        prompt: Prompt message
        valid_choices: List of valid input choices
        
    Returns:
        User's choice
    """
    while True:
        choice = logged_input(prompt).strip()
        if choice in valid_choices:
            return choice
        print(f"Invalid choice. Please enter one of: {', '.join(valid_choices)}")