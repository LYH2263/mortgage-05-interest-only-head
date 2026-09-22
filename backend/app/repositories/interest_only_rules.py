from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).isoformat()


def list_all(conn, enabled_only: bool = False):
    sql = "SELECT * FROM interest_only_rules"
    if enabled_only:
        sql += " WHERE enabled = 1"
    return [dict(r) for r in conn.execute(sql + " ORDER BY id").fetchall()]


def get(conn, rid: int):
    row = conn.execute("SELECT * FROM interest_only_rules WHERE id=?", (rid,)).fetchone()
    return dict(row) if row else None


def insert(conn, name: str, interest_only_months: int):
    now = _now()
    cur = conn.execute(
        "INSERT INTO interest_only_rules(name,interest_only_months,enabled,created_at,updated_at) VALUES (?,?,1,?,?)",
        (name, interest_only_months, now, now),
    )
    conn.commit()
    return get(conn, int(cur.lastrowid))


def update(conn, rid: int, name: str | None, interest_only_months: int | None, enabled: bool | None):
    fields, params = [], []
    if name is not None:
        fields.append("name=?"); params.append(name)
    if interest_only_months is not None:
        fields.append("interest_only_months=?"); params.append(interest_only_months)
    if enabled is not None:
        fields.append("enabled=?"); params.append(1 if enabled else 0)
    if not fields:
        return get(conn, rid)
    fields.append("updated_at=?"); params.append(_now())
    params.append(rid)
    conn.execute(f"UPDATE interest_only_rules SET {','.join(fields)} WHERE id=?", params)
    conn.commit()
    return get(conn, rid)
