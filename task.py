import logging
import re
import sqlite3
import sys
from datetime import datetime
from typing import Any, Callable, TypeAlias
from urllib.error import HTTPError
from urllib.request import urlopen

from db import DBRepository

TaskHandler: TypeAlias = Callable[[str, str | None], None]

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)


class Task:
    """Data transfer object representing unit task. Implements Command design pattern."""

    def __init__(self, task_handler: TaskHandler, url: str, pattern: str | None = None) -> None:
        self.task_handler = task_handler
        self.url = url
        self.pattern = pattern

    def execute(self) -> Any:
        """Unfreezes task handler and runs it with the arguments."""
        self.task_handler(self.url, self.pattern)


def handle_task(url: str, regex_pattern: str | None = None) -> None:
    """Requests URL and stores response information in DB."""
    try:
        db_repo = DBRepository("monitoring.db")

        request_timestamp = datetime.now().timestamp()
        pattern_match = None

        start_time = datetime.now()
        try:
            with urlopen(url) as response:
                response_data = response.read().decode("utf-8")
                if regex_pattern:
                    match = re.search(regex_pattern, response_data)
                    if match:
                        pattern_match = match.group(0)
            db_repo.insert_result(
                url, request_timestamp, (datetime.now() - start_time).total_seconds(), response.getcode(), pattern_match
            )
            logger.info("URL %s successfully saved to DB." % url)
        except HTTPError as e:
            db_repo.insert_result(
                url, request_timestamp, (datetime.now() - start_time).total_seconds(), e.code, pattern_match
            )
            logger.error("URL %s failed: %s." % (url, e))
        except Exception as e:
            db_repo.insert_exception(url, request_timestamp, str(e))
            logger.error("URL %s failed: %s." % (url, e))
    except sqlite3.Error as e:
        logger.critical("DB operation failed: %s." % e)
