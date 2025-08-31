from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import sys
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), "reports.db")


def init_db() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                category TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.post("/report")
def create_report():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    title = data.get("title")
    description = data.get("description")
    location = data.get("location")
    category = data.get("category") or "Other"

    if not all(isinstance(x, str) for x in [title, description, location, category]):
        return jsonify({"error": "Fields 'title', 'description', 'location', 'category' must be strings"}), 400

    created_at = datetime.utcnow().isoformat() + "Z"

    with get_db_connection() as conn:
        cur = conn.execute(
            "INSERT INTO reports (title, description, location, category, created_at) VALUES (?, ?, ?, ?, ?)",
            (title, description, location, category, created_at),
        )
        report_id = cur.lastrowid

    print(
        f"New report received: id={report_id}, title={title!r}, description={description!r}, location={location!r}, category={category!r}",
        file=sys.stdout,
        flush=True,
    )

    return jsonify({"status": "received", "id": report_id})


@app.get("/reports")
def list_reports():
    category = request.args.get("category")
    query = request.args.get("q")

    sql = "SELECT id, title, description, location, category, created_at FROM reports"
    params = []
    clauses = []
    if category and category.lower() != "all":
        clauses.append("category = ?")
        params.append(category)
    if query:
        clauses.append("(title LIKE ? OR description LIKE ? OR location LIKE ?)")
        like = f"%{query}%"
        params.extend([like, like, like])
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY datetime(created_at) DESC, id DESC"

    with get_db_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
        reports = [dict(row) for row in rows]

    return jsonify({"items": reports, "count": len(reports)})


init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

