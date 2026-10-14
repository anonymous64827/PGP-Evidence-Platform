import sqlite3

db = sqlite3.connect("database/evidence.db")

db.execute("ALTER TABLE audit_logs ADD COLUMN previous_hash TEXT")
db.execute("ALTER TABLE audit_logs ADD COLUMN event_hash TEXT")

db.commit()

print("Audit table updated successfully.")

db.close()