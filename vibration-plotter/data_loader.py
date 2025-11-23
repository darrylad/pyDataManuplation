"""
Module for loading and concatenating CSV files from the data directory.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List
import logging

# Setup logging to track what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_csv_files(directory: Path) -> List[Path]:
    """
    Find all CSV files in a directory.
    
    Args:
        directory: Path to search for CSV files
        
    Returns:
        List of Path objects pointing to CSV files, sorted by name
    """
    csv_files = sorted(directory.glob("*.csv"))
    logger.info(f"Found {len(csv_files)} CSV files in {directory.name}")
    return csv_files


def load_and_concatenate_csvs(csv_files: List[Path]) -> pd.DataFrame:
    """
    Load multiple CSV files and concatenate them into a single DataFrame.
    The time column is adjusted to be continuous across files.
    
    Args:
        csv_files: List of CSV file paths to load
        
    Returns:
        Concatenated DataFrame with continuous time
    """
    if not csv_files:
        logger.warning("No CSV files provided")
        return pd.DataFrame()
    
    dataframes = []
    cumulative_time = 0.0
    
    for i, csv_file in enumerate(csv_files):
        logger.info(f"  Loading: {csv_file.name}")
        
        # Read CSV file
        df = pd.read_csv(csv_file)
        
        # Adjust time to be continuous
        if i > 0:
            # Add the maximum time from previous files
            df['Channel name'] = df['Channel name'] + cumulative_time
        
        # Update cumulative time for next file
        cumulative_time = df['Channel name'].max()
        
        dataframes.append(df)
    
    # Concatenate all dataframes
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    logger.info(f"  Total data points: {len(combined_df)}")
    logger.info(f"  Time range: {combined_df['Channel name'].min():.4f} to {combined_df['Channel name'].max():.4f}")
    
    return combined_df


def load_all_conditions(data_root: Path, conditions: List[str]) -> Dict[str, pd.DataFrame]:
    """
    Load data for all experimental conditions.
    
    Args:
        data_root: Root directory containing condition folders
        conditions: List of condition names (folder names)
        
    Returns:
        Dictionary mapping condition names to DataFrames
    """
    all_data = {}
    
    for condition in conditions:
        condition_path = data_root / condition
        
        if not condition_path.exists():
            logger.warning(f"Condition directory not found: {condition}")
            continue
        
        logger.info(f"Loading condition: {condition}")
        
        # Find and load all CSV files for this condition
        csv_files = find_csv_files(condition_path)
        df = load_and_concatenate_csvs(csv_files)
        
        if not df.empty:
            all_data[condition] = df
    
    return all_data


# Quick test function to verify loading works
def test_loading(data_root: Path, condition: str):
    """
    Test function to load and display info about a single condition.
    """
    print(f"\n🧪 Testing data loading for: {condition}")
    print("=" * 60)
    
    condition_path = data_root / condition
    csv_files = find_csv_files(condition_path)
    df = load_and_concatenate_csvs(csv_files)
    
    print(f"\nDataFrame shape: {df.shape}")
    print(f"\nFirst few rows:")
    print(df.head())
    print(f"\nLast few rows:")
    print(df.tail())
    print(f"\nColumn statistics:")
    print(df.describe())