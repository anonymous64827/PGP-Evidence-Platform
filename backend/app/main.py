from datetime import datetime
import json

from fastapi import FastAPI, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware


from sqlalchemy.orm import Session

from backend.app.core.database import Base, engine, SessionLocal
from backend.app.models.evidence import Evidence
from backend.app.models.audit import AuditLog
from backend.app.models.ai_analysis import AIAnalysis

from backend.app.services.evidence.ingestion import save_evidence
from backend.app.services.evidence.verifier import verify_file

from backend.app.services.timeline.chain import (
    calculate_event_hash,
    verify_chain
)

from backend.app.services.ai.analyzer import analyze_text


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="PGP Evidence Platform",
    description="Secure and intelligent digital evidence management system",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {
        "message": "PGP Evidence Platform API is running",
        "status": "online",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/evidence/upload")
async def upload_evidence(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_bytes = await file.read()

    result = save_evidence(
        file_bytes,
        file.filename
    )

    evidence = Evidence(
        evidence_id=result["evidence_id"],
        file_name=result["file_name"],
        file_path=result["file_path"],
        file_type=file.content_type,
        file_size=result["file_size"],
        sha256_hash=result["sha256_hash"],
        status="SUBMITTED",
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return {
        "message": "Evidence uploaded successfully",
        "evidence_id": result["evidence_id"],
        "file_name": result["file_name"],
        "file_size": result["file_size"],
        "sha256_hash": result["sha256_hash"],
        "status": "SUBMITTED",
    }


@app.get("/evidence/{evidence_id}/verify")
def verify_evidence(
    evidence_id: str,
    db: Session = Depends(get_db)
):
    evidence = (
        db.query(Evidence)
        .filter(Evidence.evidence_id == evidence_id)
        .first()
    )

    if not evidence:
        return {
            "status": "NOT_FOUND",
            "message": "Evidence ID does not exist."
        }

    result = verify_file(
        evidence.file_path,
        evidence.sha256_hash
    )

    previous_audit = (
        db.query(AuditLog)
        .filter(AuditLog.evidence_id == evidence_id)
        .order_by(AuditLog.id.desc())
        .first()
    )

    previous_hash = (
        previous_audit.event_hash
        if previous_audit and previous_audit.event_hash
        else "GENESIS"
    )

    timestamp = datetime.utcnow()

    event_hash = calculate_event_hash(
        evidence_id=evidence_id,
        action="VERIFY_EVIDENCE",
        result=result["status"],
        original_hash=result["original_hash"],
        current_hash=result["current_hash"],
        timestamp=timestamp,
        previous_hash=previous_hash
    )

    audit = AuditLog(
        evidence_id=evidence_id,
        action="VERIFY_EVIDENCE",
        result=result["status"],
        original_hash=result["original_hash"],
        current_hash=result["current_hash"],
        timestamp=timestamp,
        previous_hash=previous_hash,
        event_hash=event_hash
    )

    db.add(audit)
    db.commit()

    return {
        "evidence_id": evidence_id,
        "file_name": evidence.file_name,
        **result
    }


@app.get("/evidence/{evidence_id}/history")
def evidence_history(
    evidence_id: str,
    db: Session = Depends(get_db)
):
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.evidence_id == evidence_id)
        .order_by(AuditLog.timestamp.asc())
        .all()
    )

    if not logs:
        return {
            "evidence_id": evidence_id,
            "message": "No audit history found.",
            "history": []
        }

    return {
        "evidence_id": evidence_id,
        "history": [
            {
                "action": log.action,
                "result": log.result,
                "original_hash": log.original_hash,
                "current_hash": log.current_hash,
                "timestamp": log.timestamp,
                "previous_hash": log.previous_hash,
                "event_hash": log.event_hash
            }
            for log in logs
        ]
    }


@app.get("/evidence/{evidence_id}/chain/verify")
def verify_evidence_chain(
    evidence_id: str,
    db: Session = Depends(get_db)
):
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.evidence_id == evidence_id)
        .order_by(AuditLog.id.asc())
        .all()
    )

    result = verify_chain(logs)

    return {
        "evidence_id": evidence_id,
        **result
    }


@app.post("/evidence/{evidence_id}/analyze")
def analyze_evidence(
    evidence_id: str,
    db: Session = Depends(get_db)
):
    evidence = (
        db.query(Evidence)
        .filter(Evidence.evidence_id == evidence_id)
        .first()
    )

    if not evidence:
        return {
            "status": "NOT_FOUND",
            "message": "Evidence ID does not exist."
        }

    try:
        with open(
            evidence.file_path,
            "r",
            encoding="utf-8"
        ) as file:
            evidence_text = file.read()

    except UnicodeDecodeError:
        return {
            "status": "UNSUPPORTED",
            "message": "This first AI version supports text evidence only."
        }

    analysis = analyze_text(evidence_text)

    ai_record = AIAnalysis(
        evidence_id=evidence_id,
        evidence_hash=evidence.sha256_hash,
        evidence_type=analysis.evidence_type,
        summary=analysis.summary,
        key_entities=json.dumps(analysis.key_entities),
        important_dates=json.dumps(analysis.important_dates),
        locations=json.dumps(analysis.locations),
        important_observations=json.dumps(
            analysis.important_observations
        ),
        potentially_relevant_information=json.dumps(
            analysis.potentially_relevant_information
        ),
        confidence_level=analysis.confidence_level
    )

    db.add(ai_record)
    db.flush()

    # Add AI analysis to the cryptographic audit chain
    previous_audit = (
        db.query(AuditLog)
        .filter(AuditLog.evidence_id == evidence_id)
        .order_by(AuditLog.id.desc())
        .first()
    )

    previous_hash = (
        previous_audit.event_hash
        if previous_audit and previous_audit.event_hash
        else "GENESIS"
    )

    timestamp = datetime.utcnow()

    event_hash = calculate_event_hash(
        evidence_id=evidence_id,
        action="AI_ANALYSIS",
        result="SUCCESS",
        original_hash=evidence.sha256_hash,
        current_hash=evidence.sha256_hash,
        timestamp=timestamp,
        previous_hash=previous_hash
    )

    audit = AuditLog(
        evidence_id=evidence_id,
        action="AI_ANALYSIS",
        result="SUCCESS",
        original_hash=evidence.sha256_hash,
        current_hash=evidence.sha256_hash,
        timestamp=timestamp,
        previous_hash=previous_hash,
        event_hash=event_hash
    )

    db.add(audit)
    db.commit()
    db.refresh(ai_record)

    return {
        "status": "SUCCESS",
        "analysis_id": ai_record.id,
        "evidence_id": evidence_id,
        "evidence_hash": evidence.sha256_hash,
        "audit_event_hash": event_hash,
        "analysis": {
            "evidence_type": analysis.evidence_type,
            "summary": analysis.summary,
            "key_entities": analysis.key_entities,
            "important_dates": analysis.important_dates,
            "locations": analysis.locations,
            "important_observations": analysis.important_observations,
            "potentially_relevant_information":
                analysis.potentially_relevant_information,
            "confidence_level": analysis.confidence_level
        }
    }


@app.get("/evidence/{evidence_id}/analysis")
def get_evidence_analysis(
    evidence_id: str,
    db: Session = Depends(get_db)
):
    analysis = (
        db.query(AIAnalysis)
        .filter(AIAnalysis.evidence_id == evidence_id)
        .order_by(AIAnalysis.id.desc())
        .first()
    )

    if not analysis:
        return {
            "status": "NOT_FOUND",
            "message": "No AI analysis found for this evidence."
        }

    return {
        "status": "SUCCESS",
        "analysis_id": analysis.id,
        "evidence_id": analysis.evidence_id,
        "evidence_hash": analysis.evidence_hash,
        "analysis": {
            "evidence_type": analysis.evidence_type,
            "summary": analysis.summary,
            "key_entities": json.loads(analysis.key_entities),
            "important_dates": json.loads(analysis.important_dates),
            "locations": json.loads(analysis.locations),
            "important_observations": json.loads(
                analysis.important_observations
            ),
            "potentially_relevant_information": json.loads(
                analysis.potentially_relevant_information
            ),
            "confidence_level": analysis.confidence_level,
            "created_at": analysis.created_at
        }
    }


@app.get("/evidence/{evidence_id}/analysis/verify")
def verify_ai_analysis(
    evidence_id: str,
    db: Session = Depends(get_db)
):
    analysis = (
        db.query(AIAnalysis)
        .filter(AIAnalysis.evidence_id == evidence_id)
        .order_by(AIAnalysis.id.desc())
        .first()
    )

    if not analysis:
        return {
            "status": "NOT_FOUND",
            "message": "No AI analysis found for this evidence."
        }

    evidence = (
        db.query(Evidence)
        .filter(Evidence.evidence_id == evidence_id)
        .first()
    )

    if not evidence:
        return {
            "status": "NOT_FOUND",
            "message": "Evidence ID does not exist."
        }

    result = verify_file(
        evidence.file_path,
        evidence.sha256_hash
    )

    current_hash = result["current_hash"]
    analyzed_hash = analysis.evidence_hash

    valid = current_hash == analyzed_hash

    return {
        "evidence_id": evidence_id,
        "analysis_id": analysis.id,
        "valid": valid,
        "message": (
            "AI analysis matches the current evidence."
            if valid
            else "Evidence was modified after the AI analysis."
        ),
        "analyzed_evidence_hash": analyzed_hash,
        "current_evidence_hash": current_hash,
        "evidence_status": result["status"]
    }
@app.get("/evidence")
def get_all_evidence(
    db: Session = Depends(get_db)
):
    evidence_records = (
        db.query(Evidence)
        .order_by(Evidence.id.desc())
        .all()
    )

    return {
        "count": len(evidence_records),
        "evidence": [
            {
                "evidence_id": item.evidence_id,
                "file_name": item.file_name,
                "file_type": item.file_type,
                "file_size": item.file_size,
                "sha256_hash": item.sha256_hash,
                "status": item.status,
            }
            for item in evidence_records
        ]
    }