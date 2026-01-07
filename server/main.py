import os
import json
from io import BytesIO

from flask import Flask, request, jsonify
from minio import Minio
from minio.error import S3Error

# Base directory of the server/ folder
BASE_DIR = os.path.dirname(__file__)

# File that stores which hashes already exist on the server
ASSETS_INDEX_FILE = os.path.join(BASE_DIR, "assets_index.json")

# In-memory index: { file_hash: { "bucket": ..., "object_name": ... } }
if os.path.exists(ASSETS_INDEX_FILE):
    with open(ASSETS_INDEX_FILE, "r", encoding="utf-8") as f:
        ASSETS_INDEX = json.load(f)
else:
    ASSETS_INDEX = {}


def save_assets_index() -> None:
    """Save the current ASSETS_INDEX dictionary to disk."""
    with open(ASSETS_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(ASSETS_INDEX, f, indent=2, ensure_ascii=False)


# ===== MinIO configuration =====

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = False  # http (לא https)
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "assets")

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE,
)

# לוודא שה-bucket קיים
if not minio_client.bucket_exists(MINIO_BUCKET):
    minio_client.make_bucket(MINIO_BUCKET)


app = Flask(__name__)


@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Receive a file + its hash from the client and store it on MinIO.
    """
    uploaded_file = request.files.get("file")
    file_hash = request.form.get("hash")

    if uploaded_file is None or file_hash is None:
        return jsonify({"error": "missing file or hash"}), 400

    # Check if this hash already exists on the server
    existing_entry = ASSETS_INDEX.get(file_hash)
    if existing_entry is not None:
        print(f"[DUPLICATE] Received file with existing hash={file_hash}")
        print(f"           Already stored as: {existing_entry}")
        return jsonify({
            "status": "already_exists",
            "stored_as": existing_entry,
        }), 200

    # New content: upload to MinIO using hash as the base name
    orig_filename = uploaded_file.filename or "uploaded_file"
    _, ext = os.path.splitext(orig_filename)
    object_name = f"{file_hash}{ext}"  # e.g. <hash>.png

    # Read the file into memory (טוב למשימה, קבצים קטנים)
    file_bytes = uploaded_file.read()
    file_size = len(file_bytes)

    try:
        minio_client.put_object(
            MINIO_BUCKET,
            object_name,
            data=BytesIO(file_bytes),
            length=file_size,
            content_type=uploaded_file.mimetype,
        )
    except S3Error as e:
        print(f"[ERROR] Failed to upload to MinIO: {e}")
        return jsonify({"error": "failed_to_upload_to_minio"}), 500

    # Update index: remember where this hash is stored
    entry = {
        "bucket": MINIO_BUCKET,
        "object_name": object_name,
    }
    ASSETS_INDEX[file_hash] = entry
    save_assets_index()

    print(f"[NEW] Received file: {orig_filename}, hash={file_hash}")
    print(f"     Stored in MinIO bucket='{MINIO_BUCKET}', object='{object_name}'")

    return jsonify({"status": "ok", "stored_as": entry}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
