import os
import sys
from pathlib import Path
from csv_splitter import CSVSplitter
from file_handler import FileHandler
from utils import get_user_choice, display_csv_info, get_normalization_choices
from logger import Logger, logged_input

def main():
    """Main entry point for CSV splitter application."""
    
    # Create output directory first (before logging starts)
    output_dir = Path.cwd() / 'outputs'
    output_dir.mkdir(exist_ok=True)
    
    # Initialize logger
    logger = Logger(output_dir)
    
    try:
        # Get input path from command-line argument or user input
        if len(sys.argv) > 1:
            input_path = sys.argv[1]
            print(f"[INPUT] Path provided as argument: {input_path}")
        else:
            input_path = logged_input("Enter the path to CSV file or folder: ").strip()
        
        if not os.path.exists(input_path):
            print(f"Error: Path '{input_path}' does not exist.")
            return
        
        print(f"\nLooking for CSV files in {input_path}...")
        
        # Initialize file handler
        file_handler = FileHandler(input_path)
        csv_files = file_handler.find_csv_files()
        
        if not csv_files:
            print("No CSV files found in the specified path.")
            return
        
        # Display information about all CSV files
        display_csv_info(csv_files)
        
        # Get user choice for split method
        split_method = get_user_choice(
            "Choose split method:\n1. By number of files\n2. By points per file\nEnter choice (1 or 2): ",
            ['1', '2']
        )
        
        # Get the split value based on method
        if split_method == '1':
            split_value = int(logged_input("Enter number of files to split into: "))
            split_by = 'files'
        else:
            split_value = int(logged_input("Enter number of data points per file: "))
            split_by = 'points'
        
        print(f"\n[CONFIG] Split method: {'Number of files' if split_by == 'files' else 'Points per file'}")
        print(f"[CONFIG] Split value: {split_value}\n")
        
        # Process each CSV file
        splitter = CSVSplitter(split_by, split_value)
        
        for csv_path, info in csv_files.items():
            print(f"\n{'='*60}")
            print(f"Processing: {csv_path.name}")
            print(f"{'='*60}")
            
            # Get normalization choices for this specific CSV file
            columns = info['columns']
            normalize_cols = get_normalization_choices(columns)
            
            if normalize_cols:
                print(f"[CONFIG] Will normalize columns in each split file: {', '.join(normalize_cols)}\n")
            
            file_handler.split_and_save(csv_path, info, splitter, output_dir, normalize_cols)
        
        print(f"\n✓ All files processed successfully!")
        print(f"Output location: {output_dir.absolute()}")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n\nError occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Close logger and restore stdout
        logger.close()

if __name__ == "__main__":
    main()