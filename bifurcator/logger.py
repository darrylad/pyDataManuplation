import sys
import builtins
import shutil
from datetime import datetime
from pathlib import Path


class DualOutput:
    """Handles simultaneous output to console and log file."""
    
    def __init__(self, log_path: str):
        self.log_path = Path(log_path)
        self.terminal = sys.stdout
        self.log_file = None
        
        # Ensure the directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open log file
        self.log_file = open(self.log_path, 'w', encoding='utf-8')
        
        # Write header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"Dataset Bifurcator Log - {timestamp}\n{'=' * 60}\n\n"
        self.log_file.write(header)
        self.log_file.flush()
    
    def write(self, message):
        """Write message to both terminal and log file."""
        self.terminal.write(message)
        if self.log_file:
            self.log_file.write(message)
            self.log_file.flush()
    
    def flush(self):
        """Flush both outputs."""
        self.terminal.flush()
        if self.log_file:
            self.log_file.flush()
    
    def close(self):
        """Close the log file."""
        if self.log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            footer = f"\n{'=' * 60}\nLog ended - {timestamp}\n"
            self.log_file.write(footer)
            self.log_file.close()
            self.log_file = None


class DualInput:
    """Handles input while logging to file."""
    
    def __init__(self, log_file_handle, original_input):
        self.log_file = log_file_handle
        self.original_input = original_input
    
    def __call__(self, prompt=""):
        """Capture input and log it."""
        # Display prompt
        sys.stdout.write(prompt)
        sys.stdout.flush()
        
        # Get input using the original input function
        user_input = self.original_input()
        
        # Log the input
        if self.log_file:
            self.log_file.write(f"{user_input}\n")
            self.log_file.flush()
        
        return user_input


class Logger:
    """Context manager for dual output logging."""
    
    def __init__(self, final_log_path: str = "outputs/log.txt"):
        self.final_log_path = Path(final_log_path)
        # Create temporary log in current directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.temp_log_path = Path(f".temp_log_{timestamp}.txt")
        self.dual_output = None
        self.original_stdout = None
        self.original_input = None
    
    def __enter__(self):
        """Setup dual output and input."""
        self.dual_output = DualOutput(str(self.temp_log_path))
        self.original_stdout = sys.stdout
        self.original_input = builtins.input
        
        # Redirect stdout
        sys.stdout = self.dual_output
        
        # Redirect input
        builtins.input = DualInput(self.dual_output.log_file, self.original_input)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original stdout and input, close log file, and move to final location."""
        # Restore stdout
        sys.stdout = self.original_stdout
        
        # Restore input
        builtins.input = self.original_input
        
        # Close log file
        if self.dual_output:
            self.dual_output.close()
        
        # Only move log file if there was no exception (successful completion)
        if exc_type is None:
            try:
                # Ensure the output directory exists
                self.final_log_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move the temp log to final location
                shutil.move(str(self.temp_log_path), str(self.final_log_path))
                print(f"Log file saved to: {self.final_log_path.absolute()}")
            except Exception as e:
                print(f"Warning: Could not move log file to final location: {e}")
                print(f"Log file remains at: {self.temp_log_path.absolute()}")
        else:
            # If there was an error, clean up the temp log file
            try:
                if self.temp_log_path.exists():
                    self.temp_log_path.unlink()
            except Exception as e:
                print(f"Warning: Could not remove temporary log file: {e}")
        
        # Don't suppress exceptions
        return False