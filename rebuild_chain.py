from backend.app.core.database import SessionLocal
from backend.app.models.audit import AuditLog
from backend.app.services.timeline.chain import calculate_event_hash


db = SessionLocal()

logs = (
    db.query(AuditLog)
    .order_by(AuditLog.evidence_id, AuditLog.id.asc())
    .all()
)

last_hash = {}

for log in logs:
    previous_hash = last_hash.get(log.evidence_id, "GENESIS")

    event_hash = calculate_event_hash(
        evidence_id=log.evidence_id,
        action=log.action,
        result=log.result,
        original_hash=log.original_hash,
        current_hash=log.current_hash,
        timestamp=log.timestamp,
        previous_hash=previous_hash
    )

    log.previous_hash = previous_hash
    log.event_hash = event_hash

    last_hash[log.evidence_id] = event_hash

db.commit()

print("Audit chain rebuilt successfully.")

for log in logs:
    print(
        log.id,
        log.evidence_id,
        log.previous_hash,
        "->",
        log.event_hash
    )

db.close()