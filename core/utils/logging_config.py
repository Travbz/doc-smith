import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
from rich.logging import RichHandler
from rich.console import Console
from rich.traceback import install as install_rich_traceback
from ...config.settings import LOG_LEVEL, LOG_FILE, LOGS_DIR

# Install rich traceback handler
install_rich_traceback(show_locals=True)

# Create rich console
console = Console()

class CustomFormatter(logging.Formatter):
    """Custom formatter with color support."""
    
    COLORS = {
        'DEBUG': '\033[0;36m',  # Cyan
        'INFO': '\033[0;32m',   # Green
        'WARNING': '\033[0;33m', # Yellow
        'ERROR': '\033[0;31m',   # Red
        'CRITICAL': '\033[0;35m' # Purple
    }
    RESET = '\033[0m'

    def format(self, record):
        # Save the original format
        original_fmt = self._fmt

        # Add color if terminal supports it
        if sys.stderr.isatty():
            record.levelname = f"{self.COLORS.get(record.levelname, '')}{record.levelname}{self.RESET}"

        # Restore the original format
        self._fmt = original_fmt

        return super().format(record)

def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """Set up a logger with the specified configuration."""
    logger = logging.getLogger(name)
    
    # Set log level
    logger.setLevel(level or LOG_LEVEL)

    # Clear any existing handlers
    logger.handlers.clear()

    # Create handlers
    handlers = []

    # Console handler with rich formatting
    console_handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=True,
        show_path=True
    )
    handlers.append(console_handler)

    # File handler if specified
    if log_file or LOG_FILE:
        file_path = log_file or LOG_FILE
        LOGS_DIR.mkdir(exist_ok=True)
        
        # Create a new log file for each run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(
            LOGS_DIR / f"{file_path.stem}_{timestamp}.log"
        )
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    # Add handlers to logger
    for handler in handlers:
        logger.addHandler(handler)

    return logger

def log_exception(logger: logging.Logger, exc: Exception, context: str = ""):
    """Log an exception with rich formatting and context."""
    console.print(f"[red]Exception in {context}:[/red]", style="bold red")
    console.print_exception()
    logger.error(f"Exception in {context}: {str(exc)}", exc_info=True)

# Create the base logger
logger = setup_logger("docsmith")