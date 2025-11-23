"""
Simple logging utility to write to both console and file.
"""

import logging
import sys
from pathlib import Path


class DualOutput:
    """
    Custom stream that writes to both terminal and file.
    This captures both print() statements and logging output.
    """
    def __init__(self, terminal, log_file):
        self.terminal = terminal
        self.log_file = log_file
        
    def write(self, message):
        """Write to both terminal and file."""
        # Always write to terminal
        self.terminal.write(message)
        self.terminal.flush()
        
        # Write to log file if message is not completely empty
        # This includes newlines (\n), spaces, and actual text
        if message:  # Changed from message.strip()
            self.log_file.write(message)
            self.log_file.flush()
    
    def flush(self):
        """Flush both outputs."""
        self.terminal.flush()
        self.log_file.flush()


def setup_logging(output_dir: Path = None, log_filename: str = "log.txt"):
    """
    Setup logging to write to both console and file.
    
    This captures:
    - All print() statements
    - All logging messages (logger.info(), logger.error(), etc.)
    
    Args:
        output_dir: Directory to write log file (default: "output")
        log_filename: Name of log file (default: "log.txt")
    
    Returns:
        Path to log file
    """
    # Use default output directory if not specified
    if output_dir is None:
        output_dir = Path("output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Full path to log file
    log_path = output_dir / log_filename
    
    # Open log file
    log_file = open(log_path, 'w', encoding='utf-8')
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers = []
    
    # Set logging level
    root_logger.setLevel(logging.INFO)
    
    # Create a custom stream handler that writes to both console and file
    dual_stream = DualOutput(sys.stdout, log_file)
    
    # Create handler with the dual stream
    console_handler = logging.StreamHandler(dual_stream)
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Also redirect print statements to the same dual stream
    sys.stdout = dual_stream
    
    return log_path