"""
F Block Allotment Register — backend server.

A tiny Flask app that stores the entire register (flats, rooms, occupants,
activity log) as one JSON document inside a SQLite database file
(fblock.db). The frontend (static/index.html) is the same interface built
earlier as a Claude artifact — only the persistence layer changed, from
Claude's window.storage to real HTTP + SQLite.

Run locally:
    pip install -r requirements.txt
    python app.py
    -> open http://localhost:5000

Deploy (Render / Railway / any host that runs a Python web service):
    Start command:  gunicorn app:app
    The SQLite file (fblock.db) is created next to this script on first run
    and seeded from seed_data.json.

    IMPORTANT: most free hosting tiers use an ephemeral filesystem, meaning
    fblock.db can be wiped on redeploy/restart. For anything beyond a demo,
    either (a) pay for a host with a persistent disk (Render's paid tier
    supports "Persistent Disks"), or (b) swap SQLite for a hosted Postgres
    instance (Render/Railway both offer a free Postgres add-on) - the app.py
    changes needed for that are minimal, ask if you want that version.
"""

import json
import os
import sqlite3
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "fblock.db")
SEED_PATH = os.path.join(BASE_DIR, "seed_data.json")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            data TEXT NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.commit()
    return conn


def load_state():
    conn = get_db()
    row = conn.execute("SELECT data FROM state WHERE id = 1").fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None


def save_state(data):
    conn = get_db()
    conn.execute(
        """INSERT INTO state (id, data, updated_at) VALUES (1, ?, CURRENT_TIMESTAMP)
           ON CONFLICT(id) DO UPDATE SET data = excluded.data, updated_at = CURRENT_TIMESTAMP""",
        (json.dumps(data),),
    )
    conn.commit()
    conn.close()


def ensure_seeded():
    if load_state() is None:
        with open(SEED_PATH, "r") as f:
            seed = json.load(f)
        save_state(seed)


@app.route("/api/state", methods=["GET"])
def api_get_state():
    data = load_state()
    if data is None:
        return jsonify({"error": "not seeded"}), 500
    return jsonify(data)


@app.route("/api/state", methods=["POST"])
def api_save_state():
    data = request.get_json(silent=True)
    if not data or "5" not in data or "6" not in data:
        return jsonify({"error": "invalid payload — expected the full register object"}), 400
    save_state(data)
    return jsonify({"ok": True})


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Wipes the live database back to the original seed data. Use with care."""
    with open(SEED_PATH, "r") as f:
        seed = json.load(f)
    save_state(seed)
    return jsonify({"ok": True, "message": "Reset to seed data"})


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


ensure_seeded()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
