import os
import sys

# הוספת תיקיית הפרויקט ל-sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from client.watcher import DirectoryWatcher
from client.state_manager import StateManager
from client.hash_utils import calculate_file_hash


class FakeUploader:
    """
    A fake uploader used for tests.
    It doesn't send HTTP, just records what was asked to upload.
    """
    def __init__(self):
        self.uploaded_calls = []

    def upload_file(self, file_path: str, file_hash: str) -> bool:
        # just remember that we were called
        self.uploaded_calls.append((file_path, file_hash))
        return True


def test_watcher_uploads_new_file_and_marks_state(tmp_path):
    # create a temporary watch directory
    watch_dir = tmp_path / "watch"
    watch_dir.mkdir()

    # create a file inside
    file_path = watch_dir / "a.txt"
    file_path.write_text("hello world", encoding="utf-8")

    # state file in temp dir (not in ~/.local/share)
    state_file = tmp_path / "state.json"
    state = StateManager(state_path=str(state_file))

    uploader = FakeUploader()

    watcher = DirectoryWatcher(
        watch_directory=str(watch_dir),
        state_manager=state,
        recursive=False,
        uploader=uploader,
    )

    watcher.scan_once()

    # 1) the uploader should be called exactly once
    assert len(uploader.uploaded_calls) == 1
    uploaded_path, uploaded_hash = uploader.uploaded_calls[0]
    assert uploaded_path == str(file_path)

    # 2) state manager should mark this file as uploaded
    expected_hash = calculate_file_hash(str(file_path))
    assert uploaded_hash == expected_hash
    assert state.is_uploaded(str(file_path), expected_hash)


def test_watcher_does_not_reupload_already_uploaded_file(tmp_path):
    watch_dir = tmp_path / "watch"
    watch_dir.mkdir()

    file_path = watch_dir / "a.txt"
    file_path.write_text("hello world", encoding="utf-8")

    state_file = tmp_path / "state.json"
    state = StateManager(state_path=str(state_file))

    uploader = FakeUploader()

    watcher = DirectoryWatcher(
        watch_directory=str(watch_dir),
        state_manager=state,
        recursive=False,
        uploader=uploader,
    )

    # first scan - should upload once
    watcher.scan_once()
    assert len(uploader.uploaded_calls) == 1

    # clear calls and scan again
    uploader.uploaded_calls.clear()
    watcher.scan_once()

    # second scan - should not upload again (because of state)
    assert uploader.uploaded_calls == []
