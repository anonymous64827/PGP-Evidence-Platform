import sqlite3

db = sqlite3.connect("database/evidence.db")

rows = db.execute(
    "SELECT evidence_id, file_name FROM evidence WHERE file_path IS NULL"
).fetchall()

for evidence_id, file_name in rows:
    file_path = f"evidence_vault/{evidence_id}_{file_name}"

    db.execute(
        "UPDATE evidence SET file_path = ? WHERE evidence_id = ?",
        (file_path, evidence_id)
    )

db.commit()

print(
    db.execute(
        "SELECT evidence_id, file_path FROM evidence"
    ).fetchall()
)

db.close()