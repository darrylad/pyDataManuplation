import os
import pandas as pd
from pathlib import Path
from typing import Dict, List
from csv_splitter import CSVSplitter

class FileHandler:
    """Handles file operations including reading, writing, and directory traversal."""
    
    def __init__(self, input_path: str):
        """
        Initialize file handler.
        
        Args:
            input_path: Path to file or directory
        """
        self.input_path = Path(input_path)
    
    def find_csv_files(self) -> Dict[Path, Dict]:
        """
        Find all CSV files in input path.
        
        Returns:
            Dictionary mapping file paths to their info (row count, first data point)
        """
        csv_files = {}
        
        if self.input_path.is_file() and self.input_path.suffix.lower() == '.csv':
            info = self._get_csv_info(self.input_path)
            csv_files[self.input_path] = info
        
        elif self.input_path.is_dir():
            for csv_path in self.input_path.rglob('*.csv'):
                info = self._get_csv_info(csv_path)
                csv_files[csv_path] = info
        
        return csv_files
    
    def _get_csv_info(self, csv_path: Path) -> Dict:
        """
        Get information about a CSV file.
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            Dictionary with row count, first data point, and column names
        """
        df = pd.read_csv(csv_path)
        return {
            'total_rows': len(df),
            'first_point': df.iloc[0].to_dict() if len(df) > 0 else None,
            'columns': df.columns.tolist()
        }
    
    def split_and_save(self, csv_path: Path, info: Dict, splitter: CSVSplitter, output_dir: Path, normalize_columns: List[str]):
        """
        Split CSV file and save results.
        
        Args:
            csv_path: Path to input CSV file
            info: File information dictionary
            splitter: CSVSplitter instance
            output_dir: Base output directory
            normalize_columns: List of column names to normalize in each split file
        """
        # Read the CSV
        df = pd.read_csv(csv_path)
        
        # Calculate relative path for maintaining folder structure
        if self.input_path.is_dir():
            relative_path = csv_path.relative_to(self.input_path)
        else:
            relative_path = csv_path.name
        
        # Create output folder structure
        # Replace .csv with folder name
        base_name = csv_path.stem  # filename without extension
        output_folder = output_dir / relative_path.parent / base_name
        output_folder.mkdir(parents=True, exist_ok=True)
        
        # Split the dataframe
        chunks = splitter.split_dataframe(df)
        
        # Save each chunk
        for file_num, chunk_df in chunks:
            # Normalize this chunk if columns are specified
            if normalize_columns:
                print(f"  Normalizing chunk {file_num}...")
                chunk_df = self._normalize_chunk(chunk_df, normalize_columns)
            
            if file_num == 'remainder':
                output_filename = f"{base_name}_remainder.csv"
            else:
                output_filename = f"{base_name}_{file_num}.csv"
            
            output_path = output_folder / output_filename
            chunk_df.to_csv(output_path, index=False)
            print(f"  ✓ Created: {output_filename} ({len(chunk_df)} rows)")
    
    def _normalize_chunk(self, df: pd.DataFrame, normalize_columns: List[str]) -> pd.DataFrame:
        """
        Normalize specified columns in a dataframe chunk.
        
        Args:
            df: DataFrame chunk to normalize
            normalize_columns: List of column names to normalize
            
        Returns:
            Normalized DataFrame
        """
        df_normalized = df.copy()
        
        for col in normalize_columns:
            if col in df_normalized.columns:
                min_val = df_normalized[col].min()
                df_normalized[col] = df_normalized[col] - min_val
                print(f"    [NORMALIZE] Column '{col}': subtracted minimum value {min_val}")
            else:
                print(f"    [WARNING] Column '{col}' not found, skipping normalization")
        
        return df_normalized