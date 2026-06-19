import hashlib


def generate_hashes(file_path: str) -> dict:
    """
    Generates cryptographic hashes (MD5, SHA-1, SHA-256, SHA-512) for a file.
    Used for file integrity verification and chain-of-custody purposes.
    """
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    return {
        "md5": hashlib.md5(file_bytes).hexdigest(),
        "sha1": hashlib.sha1(file_bytes).hexdigest(),
        "sha256": hashlib.sha256(file_bytes).hexdigest(),
        "sha512": hashlib.sha512(file_bytes).hexdigest()
    }