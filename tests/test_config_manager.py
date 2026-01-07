import os
import sys

# להוסיף את תיקיית הפרויקט ל-sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from client.config_manager import ConfigManager


def test_config_manager_creates_default_config_if_missing(tmp_path):
    # יוצרים נתיב לקובץ קונפיג זמני (לא נוגעים ב-~/.config האמיתי)
    config_dir = tmp_path / "config_dir"
    config_dir.mkdir()
    config_file = config_dir / "config.json"

    # חשוב: להעביר config_path מותאם, אחרת הוא ישתמש ב-~/.config/asset_client
    manager = ConfigManager(config_path=str(config_file))

    # הקובץ אמור להיווצר
    assert config_file.exists()

    # המילון הפנימי אמור להכיל את המפתחות הדרושים
    assert "server_url" in manager.config
    assert "watch_directory" in manager.config

    # וה-getters צריכים להחזיר מחרוזות
    assert isinstance(manager.get_server_url(), str)
    assert isinstance(manager.get_watch_directory(), str)


def test_config_manager_updates_watch_directory(tmp_path):
    config_dir = tmp_path / "config_dir"
    config_dir.mkdir()
    config_file = config_dir / "config.json"

    manager = ConfigManager(config_path=str(config_file))

    new_dir = "/tmp/some/other/path"
    manager.set_watch_directory(new_dir)

    # לוודא שזה נשמר באובייקט
    assert manager.get_watch_directory() == new_dir

    # לוודא שזה נשמר גם בקובץ
    # נטען מחדש מאותו config_path
    manager2 = ConfigManager(config_path=str(config_file))
    assert manager2.get_watch_directory() == new_dir
