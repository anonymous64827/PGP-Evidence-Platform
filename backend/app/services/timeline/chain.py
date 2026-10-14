import hashlib
import json


def calculate_event_hash(
    evidence_id,
    action,
    result,
    original_hash,
    current_hash,
    timestamp,
    previous_hash
):
    event_data = {
        "evidence_id": evidence_id,
        "action": action,
        "result": result,
        "original_hash": original_hash,
        "current_hash": current_hash,
        "timestamp": str(timestamp),
        "previous_hash": previous_hash,
    }

    canonical_data = json.dumps(
        event_data,
        sort_keys=True
    )

    return hashlib.sha256(
        canonical_data.encode("utf-8")
    ).hexdigest()

def verify_chain(logs):
    if not logs:
        return {
            "valid": True,
            "message": "No audit events found.",
            "checked_events": 0
        }

    expected_previous_hash = "GENESIS"

    for log in logs:

        if log.previous_hash != expected_previous_hash:
            return {
                "valid": False,
                "message": "Chain broken: previous hash mismatch.",
                "broken_event_id": log.id,
                "checked_events": logs.index(log)
            }

        calculated_hash = calculate_event_hash(
            evidence_id=log.evidence_id,
            action=log.action,
            result=log.result,
            original_hash=log.original_hash,
            current_hash=log.current_hash,
            timestamp=log.timestamp,
            previous_hash=log.previous_hash
        )

        if calculated_hash != log.event_hash:
            return {
                "valid": False,
                "message": "Chain broken: event hash mismatch.",
                "broken_event_id": log.id,
                "checked_events": logs.index(log) + 1
            }

        expected_previous_hash = log.event_hash

    return {
        "valid": True,
        "message": "Audit chain is cryptographically valid.",
        "checked_events": len(logs)
    }

def verify_chain(logs):
    if not logs:
        return {
            "valid": True,
            "message": "No audit events found.",
            "checked_events": 0
        }

    expected_previous_hash = "GENESIS"

    for log in logs:

        if log.previous_hash != expected_previous_hash:
            return {
                "valid": False,
                "message": "Chain broken: previous hash mismatch.",
                "broken_event_id": log.id,
                "checked_events": logs.index(log)
            }

        calculated_hash = calculate_event_hash(
            evidence_id=log.evidence_id,
            action=log.action,
            result=log.result,
            original_hash=log.original_hash,
            current_hash=log.current_hash,
            timestamp=log.timestamp,
            previous_hash=log.previous_hash
        )

        if calculated_hash != log.event_hash:
            return {
                "valid": False,
                "message": "Chain broken: event hash mismatch.",
                "broken_event_id": log.id,
                "checked_events": logs.index(log) + 1
            }

        expected_previous_hash = log.event_hash

    return {
        "valid": True,
        "message": "Audit chain is cryptographically valid.",
        "checked_events": len(logs)
    }