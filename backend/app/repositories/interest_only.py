import sqlite3
from datetime import datetime, timezone

def _row(r):
    d = dict(r)
    d["enabled"] = bool(d["enabled"])
    return d

def list_all(conn):
    return [_row(r) for r in conn.execute("SELECT * FROM interest_only_rules ORDER BY id").fetchall()]

def get(conn, rid):
    row = conn.execute("SELECT * FROM interest_only_rules WHERE id=?", (rid,)).fetchone()
    return _row(row) if row else None

def create(conn, name, interest_only_months, enabled=True):
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO interest_only_rules(name,interest_only_months,enabled,created_at) VALUES (?,?,?,?)",
        (name, int(interest_only_months), 1 if enabled else 0, now))
    conn.commit()
    return get(conn, int(cur.lastrowid))

def update(conn, rid, name, interest_only_months, enabled):
    conn.execute(
        "UPDATE interest_only_rules SET name=?, interest_only_months=?, enabled=? WHERE id=?",
        (name, int(interest_only_months), 1 if enabled else 0, rid))
    conn.commit()
    return get(conn, rid)

def set_enabled(conn, rid, enabled):
    conn.execute("UPDATE interest_only_rules SET enabled=? WHERE id=?", (1 if enabled else 0, rid))
    conn.commit()
    return get(conn, rid)
