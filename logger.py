"""Logger library."""
import asyncio
import logging
import logging.handlers
import re
from datetime import datetime, timedelta
from pathlib import Path

debug_formatter = logging.Formatter(
    "%(asctime)s - [%(levelname)s] - [%(name)s:%(lineno)d] - %(message)s", "%m-%d %H:%M:%S"
)

standard_formatter = logging.Formatter("%(asctime)s - [%(levelname)s] -  %(message)s", "%m-%d %H:%M:%S")

audit_formatter = logging.Formatter("%(asctime)s - [%(levelname)s] -  %(message)s", "%m-%d %H:%M:%S")

date_re = re.compile(r"\d{2}-\d{2} \d{2}:\d{2}:\d{2}")


def init(level, path):
    """Initialize logging for starforge.

    Args:
        level (string): What level to use for logging.
        path (string): Where to write the file to
    """
    log_levels = {
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    root_logger = logging.getLogger()
    # KILL THE VERBOSITY OF REQUESTS LOGGING
    logging.getLogger("requests").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("boto").setLevel(logging.ERROR)

    # GET GLOBAL LOGGER
    root_logger.setLevel(logging.DEBUG)
    s_handler = logging.StreamHandler()
    s_handler.setLevel(log_levels[level])

    if level.upper() == "DEBUG":
        s_handler.setFormatter(debug_formatter)
    else:
        s_handler.setFormatter(standard_formatter)
    root_logger.addHandler(s_handler)
    log_to_file(path, root_logger)
    return root_logger


def audit_init(name, log_file, level=logging.INFO):
    """Initialize the audit log.

    Args:
        name: the name of the logger
        log_file: the output filename or path object
        level: the desired log level (default: INFO)

    Returns: an audit logger
    """
    handler = logging.FileHandler(log_file)
    handler.setFormatter(audit_formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def migration_init(name, log_file, level=logging.INFO):
    """Initialize the migration log.

    Args:
        name: the name of the logger
        log_file: the output filename or path object
        level: the desired log level (default: INFO)

    Returns: a migration logger
    """
    handler = logging.FileHandler(log_file)
    handler.setFormatter(standard_formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def log_to_file(full_path, root_logger):
    """Enable debug logs to disk.

    Args:
        full_path (string): The full path to the file
        root_logger (Logger): object to use the logger
    """
    full_path = Path(full_path).resolve()
    full_path.parent.mkdir(parents=True, exist_ok=True)
    log_file_handler = logging.FileHandler(full_path)
    log_file_handler.setLevel(logging.DEBUG)
    log_file_handler.setFormatter(debug_formatter)
    root_logger.addHandler(log_file_handler)


def now():
    """Return the current local date and time.

    (Wrapping datetime.now() makes it easy to mock the current time for unit test.)
    """
    return datetime.now()


async def atail(filename, max_entries=10, max_hours=None):
    """Read the tail end of a log file, one log entry at a time.

    Args:
        filename: the name of the log file to read
        max_entries: start reading, at most, this many log entries from the end
        max_hours: start reading, at most, this many hours in the past

    Returns: a generator that iterates over lines in at the tail of the file
    """
    date_fmt = "%m-%d %H:%M:%S"
    target_date = (  # this isn't really a specific date; it's a date without a meaningful year
        datetime.strptime(now().strftime(date_fmt), date_fmt) - timedelta(hours=max_hours) if max_hours else None
    )
    cmd = f"tail -n {max_entries} {filename} | tac"
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    lines = []
    multi_lines = []
    for line in stdout.decode().splitlines():
        multi_lines.append(line)
        if date := date_re.match(line):
            if target_date is not None and datetime.strptime(date.group(), date_fmt) < target_date:
                break
            lines.append("\n".join(reversed(multi_lines)))
            multi_lines = []

    for line in reversed(lines):
        yield line
