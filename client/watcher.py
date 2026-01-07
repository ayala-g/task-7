import os
from typing import Iterable, Optional

from .state_manager import StateManager
from .hash_utils import calculate_file_hash
from .uploader import Uploader    


class DirectoryWatcher:
    """
    Watches a directory for files and reports new/changed files.

    - It walks over all files in the watch directory.
    - For each file, it calculates a hash.
    - It checks with StateManager if this (path, hash) was already uploaded.
    - If not, it calls the handler method for new/changed files.
    """

    def __init__(
    self,
    watch_directory: str,
    state_manager: StateManager,
    recursive: bool = False,
    uploader: Optional[Uploader] = None,) -> None:
        """
        :param watch_directory: directory to scan for files
        :param state_manager: StateManager instance to track uploaded files
        :param recursive: if True, walk sub-directories as well
        :param uploader: Uploader instance used to send files to the server
        """
        self.watch_directory = watch_directory
        self.state_manager = state_manager
        self.recursive = recursive
        self.uploader = uploader     


    def _iter_files(self) -> Iterable[str]:
        """
        Iterate over all files in the watch directory.

        If recursive is False:
            - Only direct files inside the directory are returned.
        If recursive is True:
            - All files in sub-directories are also returned.
        """
        if not os.path.isdir(self.watch_directory):
            # If the watch directory does not exist or is not a directory,
            # just return an empty iterator
            return []

        if not self.recursive:
            # Non-recursive: only files directly in the directory
            for name in os.listdir(self.watch_directory):
                full_path = os.path.join(self.watch_directory, name)
                if os.path.isfile(full_path):
                    yield full_path
        else:
            # Recursive: walk through all sub-directories
            for root, _, files in os.walk(self.watch_directory):
                for name in files:
                    # Yield each file path one-by-one instead of building a full list in memory
                    yield os.path.join(root, name)

    def scan_once(self) -> None:

        #Scan the directory and handle new/changed files.
        print(f"Scanning directory: {self.watch_directory}")

        for path in self._iter_files():
            try:
                file_hash = calculate_file_hash(path)
            except OSError as e:
                # If the file cannot be read (permissions, removed, etc.), skip it
                print(f"Skipping file (cannot read): {path} ({e})")
                continue

            if self.state_manager.is_uploaded(path, file_hash):
                # File already uploaded with the same content
                print(f"[SKIP] Already uploaded: {path}")
            else:
                # New or changed file
                self._handle_new_or_changed_file(path, file_hash)



    def _handle_new_or_changed_file(self, file_path: str, file_hash: str) -> None:
        """
        Handle a new or changed file.

        For now:
        - Upload the file to the server (if uploader is configured).
        - If upload succeeds, mark it as uploaded in the state.
        """
        print(f"[NEW/CHANGED] {file_path}")

        # If no uploader is provided, just mark as uploaded locally
        if self.uploader is None:                        
            self.state_manager.mark_uploaded(file_path, file_hash)
            return

        # Try to upload the file
        success = self.uploader.upload_file(file_path, file_hash)  
        if success:
            # Only mark as uploaded if the server accepted the file
            self.state_manager.mark_uploaded(file_path, file_hash) 
        else:
            print(f"[WARN] Not marking as uploaded because upload failed: {file_path}")  # CHANGED
