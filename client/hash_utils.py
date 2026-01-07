import hashlib

# Calculates sha256 hash for a given file path
def calculate_file_hash(file_path: str) -> str:
    sha = hashlib.sha256()

    with open(file_path, "rb") as f:
        # Read file in chunks (better for big files)
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)

    # Convert the binary hash value to a readable hexadecimal string
    return sha.hexdigest()
