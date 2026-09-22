import sqlite3
from pathlib import Path
class MemoryStore:
    def __init__(self):
        path = Path(__file__).resolve().parents[3] / "memory" / "ai_engineer.db"
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, project TEXT, kind TEXT, content TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
        self.db.commit()
    def add(self, project, kind, content):
        self.db.execute("INSERT INTO memories(project,kind,content) VALUES (?,?,?)", (project,kind,content)); self.db.commit()
    def recent(self, project, limit=20):
        rows = self.db.execute("SELECT kind,content,created_at FROM memories WHERE project=? ORDER BY id DESC LIMIT ?", (project,limit)).fetchall()
        return [{"kind":r[0],"content":r[1],"created_at":r[2]} for r in rows]
