import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class DualOutput:
    """Captures output to both terminal and log file."""
    
    def __init__(self, log_file_path: Path):
        """
        Initialize dual output.
        
        Args:
            log_file_path: Path to the log file
        """
        self.terminal = sys.stdout
        self.log_file = open(log_file_path, 'w', encoding='utf-8')
    
    def write(self, message):
        """Write to both terminal and log file."""
        self.terminal.write(message)
        self.log_file.write(message)
        self.log_file.flush()  # Ensure immediate write
    
    def flush(self):
        """Flush both outputs."""
        self.terminal.flush()
        self.log_file.flush()
    
    def close(self):
        """Close the log file."""
        self.log_file.close()

class Logger:
    """Manages logging for the CSV splitter application."""
    
    def __init__(self, output_dir: Path):
        """
        Initialize logger.
        
        Args:
            output_dir: Directory where log file will be saved
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"csv_splitter_log_{timestamp}.txt"
        self.log_path = output_dir / log_filename
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create dual output
        self.dual_output = DualOutput(self.log_path)
        
        # Redirect stdout
        sys.stdout = self.dual_output
        
        # Log session start
        print("="*60)
        print(f"CSV SPLITTER - LOG SESSION")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
    
    def log_input(self, prompt: str, value: str):
        """
        Log user input.
        
        Args:
            prompt: The prompt message
            value: User's input value
        """
        print(f"[INPUT] {prompt.strip()}: {value}")
    
    def close(self):
        """Close logger and restore stdout."""
        print("\n" + "="*60)
        print(f"Session ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Log saved to: {self.log_path}")
        print("="*60)
        
        # Restore original stdout
        sys.stdout = self.dual_output.terminal
        self.dual_output.close()
        
        # Print to terminal only (after restoring stdout)
        print(f"\nLog file saved: {self.log_path}")

def logged_input(prompt: str) -> str:
    """
    Get user input and log it.
    
    Args:
        prompt: Input prompt message
        
    Returns:
        User's input
    """
    # Print prompt (will go to log automatically via dual output)
    sys.stdout.terminal.write(prompt)
    sys.stdout.terminal.flush()
    
    # Get input from terminal
    value = sys.stdin.readline().rstrip('\n')
    
    # Write the input value to log file only
    sys.stdout.log_file.write(value + '\n')
    sys.stdout.log_file.flush()
    
    return value