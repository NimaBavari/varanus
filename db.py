from __future__ import annotations

import sqlite3


class DBRepository:
    """SQLite repository.

    Implements Singleton design pattern to minimise the overhead from initialising DB and creating tables each
    instantiation.
    """

    _instance = None

    def __new__(cls, db_filepath: str) -> DBRepository:
        if cls._instance is None:
            cls._instance = super(DBRepository, cls).__new__(cls)
            cls._instance.conn = sqlite3.connect(db_filepath)
            cls._instance.cursor = cls._instance.conn.cursor()

            cls._instance.cursor.execute(
                """CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                request_timestamp REAL NOT NULL,
                response_time REAL NOT NULL,
                response_code INTEGER NOT NULL,
                pattern_match TEXT);"""
            )

            cls._instance.cursor.execute(
                """CREATE TABLE IF NOT EXISTS exceptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                request_timestamp REAL NOT NULL,
                exc_txt TEXT NOT NULL);"""
            )
            cls._instance.conn.commit()
        return cls._instance

    def insert_result(
        self, url: str, request_timestamp: float, response_time: float, response_code: int, pattern_match: str | None
    ) -> None:
        """Inserts a result record into the 'results' table."""
        self.cursor.execute(
            """INSERT INTO results (url, request_timestamp, response_time, response_code, pattern_match)
            VALUES (?, ?, ?, ?, ?);""",
            (url, request_timestamp, response_time, response_code, pattern_match),
        )
        self.conn.commit()

    def insert_exception(self, url: str, request_timestamp: float, exc_txt: str) -> None:
        """Inserts an exception record into the 'exceptions' table."""
        self.cursor.execute(
            """INSERT INTO exceptions (url, request_timestamp, exc_txt) VALUES (?, ?, ?);""",
            (url, request_timestamp, exc_txt),
        )
        self.conn.commit()
