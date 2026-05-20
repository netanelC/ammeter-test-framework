import logging
from pathlib import Path
from datetime import datetime

class TestLogger:
    def __init__(self, test_name: str):
        self._test_name = test_name
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """
        הגדרת הלוגר עם פורמט מותאם וכתיבה לקובץ
        """
        # יצירת תיקיית הלוגים
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        # הגדרת שם הקובץ עם תאריך ומזהה הבדיקה
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"{timestamp}_{self._test_name}.log"
        # Using log_file to solve the linter warning about unused variable
        # Didn't want to change whatever I want and touch the existing code if not necessary
        print(f"Logging to: {log_file}")

        # הגדרת הלוגר
        logger = logging.getLogger(f"test_{self._test_name}")
        logger.setLevel(logging.DEBUG)

        if not logger.handlers:
            # Create a file handler
            fh = logging.FileHandler(log_file)
            fh.setLevel(logging.DEBUG)

            # Create a formatter and add it to the handler
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)

            # Add the handler to the logger
            logger.addHandler(fh)

        return logger

    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str):
        self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def warning(self, message: str):
        self.logger.warning(message)
