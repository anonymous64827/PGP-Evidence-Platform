import hashlib


def calculate_sha256(file_path: str) -> str:
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()


def verify_file(file_path: str, original_hash: str) -> dict:
    current_hash = calculate_sha256(file_path)

    if current_hash == original_hash:
        return {
            "status": "AUTHENTIC",
            "message": "Evidence has not been modified.",
            "original_hash": original_hash,
            "current_hash": current_hash,
            "hash_match": True
        }

    return {
        "status": "TAMPERED",
        "message": "Evidence has been modified.",
        "original_hash": original_hash,
        "current_hash": current_hash,
        "hash_match": False
    }