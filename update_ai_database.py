import sqlite3

db = sqlite3.connect("database/evidence.db")

db.execute("""
CREATE TABLE IF NOT EXISTS ai_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evidence_id TEXT NOT NULL,
    evidence_type TEXT,
    summary TEXT,
    key_entities TEXT,
    important_dates TEXT,
    locations TEXT,
    important_observations TEXT,
    potentially_relevant_information TEXT,
    confidence_level TEXT,
    created_at DATETIME
)
""")

db.commit()

print("AI analysis table created successfully.")

db.close()