import os
import sys

# מוסיפים את תיקיית הפרויקט (התיקייה שמעל tests) ל־sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from client.state_manager import StateManager


def test_mark_uploaded_and_is_uploaded(tmp_path):
    state_file = tmp_path / "state.json"
    manager = StateManager(state_path=str(state_file))

    path = "/tmp/file1.txt"
    h = "abc123"

    assert not manager.is_uploaded(path, h)

    manager.mark_uploaded(path, h)

    assert manager.is_uploaded(path, h)


def test_state_persists_between_runs(tmp_path):
    state_file = tmp_path / "state.json"

    m1 = StateManager(state_path=str(state_file))
    m1.mark_uploaded("/tmp/x.txt", "zzz")

    m2 = StateManager(state_path=str(state_file))

    assert m2.is_uploaded("/tmp/x.txt", "zzz")


