import sqlite3

from watchcat.snapshot import Snapshot
from watchcat.storage.storage import Storage


class SqlStorage(Storage):
    def __init__(self, db_path: str):
        super().__init__(db_path)
        conn = sqlite3.connect(db_path)
        self.cur = conn.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS Snapshot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id TEXT,
            timestamp REAL,
            content TEXT
        )
        """
        self.cur.execute(query)

    def get(self, resource_id: str):
        query = f"""
        SELECT content FROM Snapshot WHERE resource_id = '{resource_id}' ORDER BY id DESC
        """
        self.cur.execute(query)
        content = self.cur.fetchone()
        return content

    def set(self, snapshot: Snapshot):
        query = """
        INSERT INTO Snapshot (resource_id, timestamp, content) VALUES (?, ?, ?)
        """
        self.cur.execute(query, (snapshot.resource_id, snapshot.timestamp, snapshot.content))
