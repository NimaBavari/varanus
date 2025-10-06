from __future__ import annotations

import sqlite3
import threading


class DBRepository:
    """SQLite repository with thread-safe operations.

    Utilises thread-local connections to ensure thread safety while implementing the singleton pattern for table
    initialisation.
    """

    _instance = None
    _lock = threading.Lock()
    _local = threading.local()

    def __new__(cls, db_filepath: str) -> DBRepository:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DBRepository, cls).__new__(cls)
                    cls._instance.db_filepath = db_filepath
                    cls._instance._init_tables()
        return cls._instance

    def _init_tables(self) -> None:
        """Initialises database tables using a temporary connection."""
        conn = sqlite3.connect(self.db_filepath, check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            request_timestamp REAL NOT NULL,
            response_time REAL NOT NULL,
            response_code INTEGER NOT NULL,
            pattern_match TEXT);"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS exceptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            request_timestamp REAL NOT NULL,
            exc_txt TEXT NOT NULL);"""
        )
        conn.commit()
        conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """Gets thread-local database connection."""
        if not hasattr(self._local, "conn"):
            # Enable WAL mode for better concurrent access
            self._local.conn = sqlite3.connect(self.db_filepath, check_same_thread=False, timeout=30.0)
            # Enable WAL mode for better concurrent performance
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA synchronous=NORMAL")
            self._local.conn.execute("PRAGMA cache_size=10000")
            self._local.conn.execute("PRAGMA temp_store=memory")
        return self._local.conn

    def insert_result(
        self, url: str, request_timestamp: float, response_time: float, response_code: int, pattern_match: str | None
    ) -> None:
        """Inserts a result record into the `results` table."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO results (url, request_timestamp, response_time, response_code, pattern_match)
            VALUES (?, ?, ?, ?, ?);""",
            (url, request_timestamp, response_time, response_code, pattern_match),
        )
        conn.commit()

    def insert_exception(self, url: str, request_timestamp: float, exc_txt: str) -> None:
        """Inserts an exception record into the `exceptions` table."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO exceptions (url, request_timestamp, exc_txt) VALUES (?, ?, ?);""",
            (url, request_timestamp, exc_txt),
        )
        conn.commit()
