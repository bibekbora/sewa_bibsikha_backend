import logging
import sys
from datetime import datetime
from pathlib import Path


class LoggerConfig:
    """
    Class-based logger configuration to manage different loggers (API, Cron, etc.)
    with support for file and console output.
    """

    def __init__(self, log_dir: str = "logs", log_format: str | None = None):
        self.log_dir = Path(log_dir)
        self.log_format = log_format or "%(asctime)s - %(module)s.%(funcName)s:%(lineno)d - %(name)s - %(levelname)s - %(message)s"
        self.formatter = logging.Formatter(self.log_format)

    def get_logger(
        self,
        name: str,
        log_file: str | None = None,
        level: int = logging.INFO,
        use_console: bool = True,
        use_file: bool = True,
    ) -> logging.Logger:
        """
        Setup and return a logger instance.

        Args:
            name: The name of the logger.
            log_file: The name of the log file (e.g., 'api.log').
            level: Logging level (default: logging.INFO).
            use_console: Whether to output logs to the console.
            use_file: Whether to output logs to a file.
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Clear existing handlers to avoid duplicates if initialized multiple times
        if logger.hasHandlers():
            logger.handlers.clear()

        # Console Handler
        if use_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(self.formatter)
            logger.addHandler(console_handler)

        # File Handler
        if use_file and log_file:
            # Create a date-wise subdirectory (e.g., logs/02-12-2025/)
            current_date = datetime.now().strftime("%d-%m-%Y")
            file_path = self.log_dir / current_date / log_file

            # Ensure directory exists for nested paths if any
            file_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(file_path)
            file_handler.setFormatter(self.formatter)
            logger.addHandler(file_handler)
        elif use_file and not log_file:
            # If file logging is requested but no file is provided, warn or fallback
            # For now, we just don't add the file handler to avoid errors
            pass

        # Prevent propagation to root logger if handlers are set here
        # This avoids double logging if the root logger is also configured
        logger.propagate = False

        return logger


logger_config = LoggerConfig()


# API Logger: Logs to console and api.log
api_logger = logger_config.get_logger(
    name="api_logger",
    log_file="api.log",
    level=logging.INFO,
    use_console=True,
    use_file=False,
)
