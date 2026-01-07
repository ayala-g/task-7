import os
import json
from typing import Any, Dict

# Path to the state directory and file.
# According to Linux conventions, state (user data) should be under:  ~/.local/share/<app_name>
STATE_DIR = os.path.join(os.path.expanduser("~"), ".local", "share", "asset_client")
STATE_FILE = os.path.join(STATE_DIR, "state.json")


class StateManager:
    """
    Manages the client state between runs.
    Responsibilities:
    - Ensure a state file exists
    - Load state from disk on startup
    - Save state back to disk after changes
    - Track which files have already been uploaded
    """

    def __init__(self, state_path: str = STATE_FILE) -> None:
        self.state_path = state_path
        # This dictionary will hold all state data in memory
        self.state: Dict[str, Any] = {}
        self._load_or_create_default()

    def _load_or_create_default(self) -> None:
        #Loads the state file if it exists.
        #If it does not exist — creates the directory and a default state file.

        # Make sure the state directory exists
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)

        if not os.path.exists(self.state_path):
            # Default empty state
            self.state = {
                # Mapping: file_path (str) -> file_hash (str)
                "uploaded_files": {}
            }
            self._save()
        else:
            # Load existing state
            with open(self.state_path, "r", encoding="utf-8") as f:
                self.state = json.load(f)

    def _save(self) -> None:
        #Writes the current state to state.json.
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def mark_uploaded(self, file_path: str, file_hash: str) -> None:
        """
        Marks a file as uploaded by storing its hash in the state.

        :param file_path: full path to the file
        :param file_hash: hash of the file content (e.g. sha256 string)
        """
        self.state.setdefault("uploaded_files", {})
        self.state["uploaded_files"][file_path] = file_hash
        self._save()

    def is_uploaded(self, file_path: str, file_hash: str) -> bool:
        """
        Checks if a file with this path AND hash has already been uploaded.

        We check both:
        - same path
        - same hash (content)
        """
        uploaded_files = self.state.get("uploaded_files", {})
        saved_hash = uploaded_files.get(file_path)
        return saved_hash == file_hash

    def get_uploaded_files(self) -> Dict[str, str]:
        #Returns the dictionary of uploaded files: { file_path: file_hash }

        return self.state.get("uploaded_files", {}).copy()
