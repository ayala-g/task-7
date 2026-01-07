import os
import sys

# מוסיפים את תיקיית הפרויקט (התיקייה שמעל tests) ל־sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from client.hash_utils import calculate_file_hash


def test_calculate_file_hash_same_content_same_hash(tmp_path):
    file1 = tmp_path / "a.txt"
    file2 = tmp_path / "b.txt"

    file1.write_text("hello", encoding="utf-8")
    file2.write_text("hello", encoding="utf-8")

    h1 = calculate_file_hash(str(file1))
    h2 = calculate_file_hash(str(file2))

    assert h1 == h2


def test_calculate_file_hash_different_content_different_hash(tmp_path):
    file1 = tmp_path / "a.txt"
    file2 = tmp_path / "b.txt"

    file1.write_text("aaa", encoding="utf-8")
    file2.write_text("bbb", encoding="utf-8")

    h1 = calculate_file_hash(str(file1))
    h2 = calculate_file_hash(str(file2))

    assert h1 != h2
