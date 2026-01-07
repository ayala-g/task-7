Asset Catalog – Distributed Asset Storage System

This project simulates a distributed asset catalog system.

Remote clients watch a directory and automatically upload files to a
central server, which stores the assets and their metadata.

Assets may be any type: images, audio, videos, documents, text or binary files.

📦 Project Structure
.
├── client/          – CLI client that watches a directory
├── server/          – HTTP server that stores assets
├── tests/           – automated tests (pytest)
└── README.md

✨ Features
Client

✔ Runs as CLI
✔ Watches a directory for changes
✔ Uploads files to server
✔ Never uploads the same file twice
✔ Recovers state between runs
✔ Stores config / cache according to Linux conventions

Server

✔ Simple HTTP upload endpoint
✔ Deduplicates by file hash
✔ Stores assets in MinIO (S3 compatible storage)
✔ Persists metadata to assets_index.json

▶️ Running the Server

Requirements:

Python (venv)

MinIO container running

Start MinIO (if not already running):

docker ps


Visit MinIO:

http://localhost:9001


Default login:

user: minioadmin
pass: minioadmin


Create bucket named:

assets


Then run the server:

cd project-root
python -m server.main


Server runs at:

http://localhost:8000

▶️ Running the Client

Configure watch folder + server URL automatically via config manager.

Run:

python -m client.main


The client will:

scan the watch directory

compute file hashes

upload only new/changed files

mark uploaded files in state file

🧪 Running Tests
pytest


Covers:

hashing logic

state manager

config manager

directory watcher behavior

🗄 MinIO Storage

Uploaded files are stored in:

bucket: assets


Files are saved as:

<sha256_hash>.<ext>


Metadata persisted in:

server/assets_index.json

📝 Notes & Assumptions

Small files only (uploads buffered in memory)

MinIO used as local S3 simulator

Client does NOT modify files

Designed to be extended in next assignments

🚀 Future Improvements (optional ideas)

authentication

background worker queue

retry failed uploads

full REST API for listing / downloading assets

✔️ Summary

This project demonstrates:

file watching

HTTP communication

persistent state

MinIO / S3 usage

clean architecture & testing