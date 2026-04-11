import logging
import os
import sys
from datetime import datetime
from typing import Optional

class NexusLogger:
    """
    Standardized logger for Nexus Hub components.
    Supports console and file output with configurable levels.
    """
    _instances = {}

    def __new__(cls, name: str = "nexus-core", log_dir: Optional[str] = None):
        if name not in cls._instances:
            instance = super(NexusLogger, cls).__new__(cls)
            instance._setup(name, log_dir)
            cls._instances[name] = instance
        return cls._instances[name]

    def _setup(self, name: str, log_dir: Optional[str]):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Avoid duplicate handlers
        if self.logger.handlers:
            return

        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File Handler
        if not log_dir:
            # Default to a 'logs' directory in the project root or nexus-hub root
            # Assuming we are in nexus-hub/core/
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_dir = os.path.join(base_dir, "logs")

        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception as e:
                self.logger.error(f"Failed to create log directory {log_dir}: {e}")
                return

        log_file = os.path.join(log_dir, f"{name}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

def get_nexus_logger(name: str = "nexus-core") -> logging.Logger:
    return NexusLogger(name).get_logger()

if __name__ == "__main__":
    # Self-test
    log = get_nexus_logger("logger-test")
    log.info("Nexus Logger initialized successfully.")
    log.debug("Debug mode is active.")
    log.error("This is an example error log.")
