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

    def __str__(self) -> str:
        return f"<SqlStorage(db_path={self.db_path})>"

    def set(self, snapshot: Snapshot):
        query = """
        INSERT INTO Snapshot (resource_id, timestamp, content) VALUES (?, ?, ?)
        """
        self.cur.execute(query, (snapshot.resource_id, snapshot.timestamp, snapshot.content))

    def get(self, resource_id: str) -> Snapshot:
        query = f"""
        SELECT * FROM Snapshot WHERE resource_id = '{resource_id}' ORDER BY id DESC
        """
        self.cur.execute(query)
        _, resource_id, timestamp, content = self.cur.fetchone()
        snapshot = Snapshot(resource_id, timestamp, content)
        return snapshot
