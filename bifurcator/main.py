import os
import shutil
import random
from pathlib import Path
from typing import List, Tuple
import sys
from logger import Logger


class DatasetSplitter:
    def __init__(self, input_path: str, output_base: str = "outputs"):
        self.input_path = Path(input_path)
        self.output_base = Path(output_base)
        self.splits = []
        self.file_extensions = []
        self.only_leaf_folders = True
        self.randomize = False
        self.seed = None
        self.rounding_method = "standard"
        
        if not self.input_path.exists():
            raise ValueError(f"Input path '{input_path}' does not exist")
    
    def setup_splits(self):
        """Configure the number of splits and their percentages."""
        while True:
            try:
                num_splits = int(input("Enter the number of splits: "))
                if num_splits < 1:
                    print("Number of splits must be at least 1.")
                    continue
                break
            except ValueError:
                print("Please enter a valid integer.")
        
        total_percentage = 0
        for i in range(1, num_splits + 1):
            if i == num_splits:
                # Auto-calculate last split
                remaining = 100 - total_percentage
                print(f"Split-{i} percentage (auto-calculated): {remaining}%")
                self.splits.append((f"split-{i}", remaining))
                total_percentage += remaining
            else:
                while True:
                    try:
                        percentage = float(input(f"Enter percentage for split-{i}: "))
                        if percentage < 0 or percentage > 100:
                            print("Percentage must be between 0 and 100.")
                            continue
                        if total_percentage + percentage > 100:
                            print(f"Total percentage would exceed 100%. Remaining: {100 - total_percentage}%")
                            continue
                        total_percentage += percentage
                        self.splits.append((f"split-{i}", percentage))
                        break
                    except ValueError:
                        print("Please enter a valid number.")
        
        if total_percentage != 100:
            print(f"\nWarning: Total percentage is {total_percentage}%, not 100%")
    
    def setup_file_extensions(self):
        """Configure which file extensions to process."""
        extensions_input = input("Enter file endings to look for (comma-separated, e.g., .png,.jpg) or press Enter for all files: ").strip()
        
        if extensions_input:
            self.file_extensions = [ext.strip() for ext in extensions_input.split(',')]
            # Ensure extensions start with a dot
            self.file_extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in self.file_extensions]
        else:
            self.file_extensions = []  # Empty list means all files
    
    def setup_folder_mode(self):
        """Configure whether to process only leaf folders or all folders."""
        while True:
            choice = input("Process only folders with no subfolders (leaf folders only)? (yes/no): ").strip().lower()
            if choice in ['yes', 'y']:
                self.only_leaf_folders = True
                break
            elif choice in ['no', 'n']:
                self.only_leaf_folders = False
                break
            else:
                print("Please enter 'yes' or 'no'.")
    
    def setup_randomization(self):
        """Configure randomization settings."""
        while True:
            choice = input("Randomize file selection? (yes/no): ").strip().lower()
            if choice in ['yes', 'y']:
                self.randomize = True
                while True:
                    try:
                        seed_input = input("Enter random seed (or press Enter for random seed): ").strip()
                        if seed_input:
                            self.seed = int(seed_input)
                        else:
                            self.seed = None
                        break
                    except ValueError:
                        print("Please enter a valid integer for seed.")
                break
            elif choice in ['no', 'n']:
                self.randomize = False
                break
            else:
                print("Please enter 'yes' or 'no'.")
    
    def setup_rounding_method(self):
        """Configure how to handle rounding when splitting small folders."""
        print("\nRounding methods for folders with few files:")
        print("1. standard - Standard rounding (default)")
        print("2. floor - Always round down")
        print("3. ceil - Always round up")
        print("4. proportional - Distribute remainder proportionally")
        
        while True:
            choice = input("Select rounding method (1-4) or press Enter for default: ").strip()
            if choice == '' or choice == '1':
                self.rounding_method = "standard"
                break
            elif choice == '2':
                self.rounding_method = "floor"
                break
            elif choice == '3':
                self.rounding_method = "ceil"
                break
            elif choice == '4':
                self.rounding_method = "proportional"
                break
            else:
                print("Please enter a number between 1 and 4.")
    
    def is_leaf_folder(self, folder: Path) -> bool:
        """Check if a folder contains no subfolders."""
        return not any(item.is_dir() for item in folder.iterdir())
    
    def should_process_file(self, file: Path) -> bool:
        """Check if a file should be processed based on extension filters."""
        if not self.file_extensions:
            return True
        return file.suffix.lower() in [ext.lower() for ext in self.file_extensions]
    
    def get_target_folders(self) -> List[Path]:
        """Get all folders that should be processed."""
        target_folders = []
        
        for root, dirs, files in os.walk(self.input_path):
            root_path = Path(root)
            
            if self.only_leaf_folders:
                # Only process if it's a leaf folder
                if not dirs:  # No subdirectories
                    # Check if there are files matching our criteria
                    matching_files = [f for f in files if self.should_process_file(Path(f))]
                    if matching_files:
                        target_folders.append(root_path)
            else:
                # Process all folders that have matching files
                matching_files = [f for f in files if self.should_process_file(Path(f))]
                if matching_files:
                    target_folders.append(root_path)
        
        return target_folders
    
    def calculate_split_counts(self, total_files: int) -> List[int]:
        """Calculate how many files go into each split."""
        if self.rounding_method == "proportional":
            counts = []
            remaining = total_files
            
            for i, (_, percentage) in enumerate(self.splits):
                if i == len(self.splits) - 1:
                    # Last split gets all remaining files
                    counts.append(remaining)
                else:
                    count = round(total_files * percentage / 100)
                    counts.append(count)
                    remaining -= count
            
            return counts
        else:
            counts = []
            used = 0
            
            for i, (_, percentage) in enumerate(self.splits):
                if i == len(self.splits) - 1:
                    # Last split gets all remaining files
                    counts.append(total_files - used)
                else:
                    if self.rounding_method == "standard":
                        count = round(total_files * percentage / 100)
                    elif self.rounding_method == "floor":
                        count = int(total_files * percentage / 100)
                    elif self.rounding_method == "ceil":
                        count = int(total_files * percentage / 100) + (1 if (total_files * percentage / 100) % 1 > 0 else 0)
                    
                    counts.append(count)
                    used += count
            
            return counts
    
    def split_folder(self, folder: Path):
        """Split files in a folder according to configured splits."""
        # Get all files matching criteria
        files = [f for f in folder.iterdir() if f.is_file() and self.should_process_file(f)]
        
        if not files:
            return
        
        # Randomize if needed
        if self.randomize:
            if self.seed is not None:
                random.seed(self.seed)
            random.shuffle(files)
        
        # Calculate split counts
        split_counts = self.calculate_split_counts(len(files))
        
        # Create relative path structure
        rel_path = folder.relative_to(self.input_path)
        
        # Distribute files
        file_index = 0
        for (split_name, _), count in zip(self.splits, split_counts):
            # Create output directory
            output_dir = self.output_base / split_name / rel_path
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy files
            for _ in range(count):
                if file_index < len(files):
                    src_file = files[file_index]
                    dst_file = output_dir / src_file.name
                    shutil.copy2(src_file, dst_file)
                    file_index += 1
        
        print(f"Processed: {rel_path} ({len(files)} files)")
    
    def clear_output_folder(self):
        """Clear the existing output folder."""
        if self.output_base.exists():
            print(f"Clearing existing '{self.output_base}' folder...")
            shutil.rmtree(self.output_base)
    
    def run(self):
        """Execute the splitting process."""
        print("=" * 60)
        print("Dataset Bifurcator")
        print("=" * 60)
        print(f"Input path: {self.input_path}")
        print()
        
        # Setup configuration
        self.setup_splits()
        self.setup_file_extensions()
        self.setup_folder_mode()
        self.setup_randomization()
        self.setup_rounding_method()
        
        # Display configuration
        print("\n" + "=" * 60)
        print("Configuration Summary:")
        print("=" * 60)
        print(f"Input path: {self.input_path}")
        print(f"Output path: {self.output_base}")
        print(f"Splits: {[(name, f'{pct}%') for name, pct in self.splits]}")
        print(f"File extensions: {self.file_extensions if self.file_extensions else 'All files'}")
        print(f"Leaf folders only: {self.only_leaf_folders}")
        print(f"Randomize: {self.randomize}" + (f" (seed: {self.seed})" if self.seed is not None else ""))
        print(f"Rounding method: {self.rounding_method}")
        print("=" * 60)
        
        # Confirm before proceeding
        while True:
            confirm = input("\nProceed with splitting? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                break
            elif confirm in ['no', 'n']:
                print("Operation cancelled.")
                return
            else:
                print("Please enter 'yes' or 'no'.")
        
        # Clear output folder
        self.clear_output_folder()
        
        # Get folders to process
        print("\nScanning folders...")
        target_folders = self.get_target_folders()
        
        if not target_folders:
            print("No folders found matching the criteria.")
            return
        
        print(f"Found {len(target_folders)} folder(s) to process.\n")
        
        # Process each folder
        for folder in target_folders:
            self.split_folder(folder)
        
        print("\n" + "=" * 60)
        print("Splitting complete!")
        print(f"Output saved to: {self.output_base.absolute()}")
        print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_path> [output_path]")
        print("\nExamples:")
        print("  python main.py /path/to/dataset")
        print("  python main.py /path/to/dataset /path/to/output")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    # Check if output path is provided
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
        output_base = Path(output_path) / "outputs"
    else:
        output_base = "outputs"
    
    try:
        # Determine log file location
        log_path = Path(output_base) / "log.txt"
        
        with Logger(str(log_path)):
            splitter = DatasetSplitter(input_path, str(output_base))
            splitter.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()