import pandas as pd
from typing import List, Tuple, Optional

class CSVSplitter:
    """Handles the logic for splitting CSV data."""
    
    def __init__(self, split_by: str, split_value: int, normalize_columns: Optional[List[str]] = None):
        """
        Initialize splitter.
        
        Args:
            split_by: 'files' or 'points'
            split_value: Number of files or points per file
            normalize_columns: List of column names to normalize (subtract minimum)
        """
        self.split_by = split_by
        self.split_value = split_value
        self.normalize_columns = normalize_columns or []
    
    def normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize specified columns by subtracting their minimum values.
        
        Args:
            df: DataFrame to normalize
            
        Returns:
            Normalized DataFrame
        """
        if not self.normalize_columns:
            return df
        
        df_normalized = df.copy()
        
        for col in self.normalize_columns:
            if col in df_normalized.columns:
                min_val = df_normalized[col].min()
                df_normalized[col] = df_normalized[col] - min_val
                print(f"    [NORMALIZE] Column '{col}': subtracted minimum value {min_val}")
            else:
                print(f"    [WARNING] Column '{col}' not found, skipping normalization")
        
        return df_normalized
    
    def calculate_splits(self, total_rows: int) -> Tuple[int, int]:
        """
        Calculate number of splits and points per file.
        
        Args:
            total_rows: Total number of data rows
            
        Returns:
            Tuple of (points_per_file, remainder)
        """
        if self.split_by == 'files':
            points_per_file = total_rows // self.split_value
            remainder = total_rows % self.split_value
        else:  # split_by == 'points'
            points_per_file = self.split_value
            remainder = total_rows % self.split_value
        
        return points_per_file, remainder
    
    def split_dataframe(self, df: pd.DataFrame) -> List[Tuple[int, pd.DataFrame]]:
        """
        Split dataframe into chunks.
        
        Args:
            df: DataFrame to split
            
        Returns:
            List of tuples (file_number, dataframe_chunk)
        """
        total_rows = len(df)
        points_per_file, remainder = self.calculate_splits(total_rows)
        
        chunks = []
        start_idx = 0
        file_num = 1
        
        # Split into equal chunks
        num_full_files = total_rows // points_per_file if points_per_file > 0 else 0
        
        for i in range(num_full_files):
            end_idx = start_idx + points_per_file
            if end_idx > total_rows:
                break
            chunks.append((file_num, df.iloc[start_idx:end_idx]))
            start_idx = end_idx
            file_num += 1
        
        # Handle remainder
        if remainder > 0 and start_idx < total_rows:
            chunks.append(('remainder', df.iloc[start_idx:]))
        
        return chunks