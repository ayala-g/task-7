import os
import requests


class Uploader:
    #Responsible for sending files to the remote server over HTTP.

    def __init__(self, server_url: str) -> None:
        # Make sure there is no trailing slash at the end of the URL
        self.server_url = server_url.rstrip("/")

    def upload_file(self, file_path: str, file_hash: str) -> bool:
        """
        Upload a single file to the server.

        :param file_path: full path to the file on the client machine
        :param file_hash: hash of the file content (sha256 string)
        :return: True if upload succeeded, False otherwise
        """
        url = f"{self.server_url}/upload"

        try:
            with open(file_path, "rb") as f:
                files = {
                    # field name "file" must match what the server expects
                    "file": (os.path.basename(file_path), f)
                }
                data = {
                    # field name "hash" must match what the server expects
                    "hash": file_hash
                }
                response = requests.post(url, files=files, data=data, timeout=10)
        except OSError as e:
            print(f"[ERROR] Could not open file for upload: {file_path} ({e})")
            return False
        except requests.RequestException as e:
            print(f"[ERROR] HTTP request failed for {file_path}: {e}")
            return False

        if response.status_code == 200:
            print(f"[UPLOADED] {file_path}")
            return True
        else:
            print(f"[ERROR] Upload failed for {file_path}: {response.status_code} {response.text}")
            return False
