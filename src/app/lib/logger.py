import logging
import contextvars
from pathlib import Path

site_key_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "site_key", default="-"
)

class SiteKeyFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.site_key = site_key_var.get()
        return True

def setup_logging(level=logging.DEBUG, log_file="logs/app.log"):
    logger = logging.getLogger("crawler")
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | [%(site_key)s] | %(message)s"
    )
    site_filter = SiteKeyFilter()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(site_filter)

    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(site_filter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger