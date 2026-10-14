import sqlite3

db = sqlite3.connect("database/evidence.db")

db.execute("""
ALTER TABLE ai_analyses
ADD COLUMN evidence_hash TEXT
""")

db.commit()

print("AI analysis evidence_hash column added successfully.")

db.close()