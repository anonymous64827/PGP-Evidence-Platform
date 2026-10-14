import hashlib
import os
import uuid
from pathlib import Path


EVIDENCE_VAULT = Path("evidence_vault")
EVIDENCE_VAULT.mkdir(exist_ok=True)


def calculate_sha256(file_path: str) -> str:
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()


def save_evidence(file_bytes: bytes, original_filename: str) -> dict:
    evidence_id = f"EVID-{uuid.uuid4().hex[:8].upper()}"

    safe_filename = Path(original_filename).name
    file_path = EVIDENCE_VAULT / f"{evidence_id}_{safe_filename}"

    with open(file_path, "wb") as file:
        file.write(file_bytes)

    sha256_hash = calculate_sha256(str(file_path))

    return {
        "evidence_id": evidence_id,
        "file_name": safe_filename,
        "file_path": str(file_path),
        "file_size": len(file_bytes),
        "sha256_hash": sha256_hash,
    }
