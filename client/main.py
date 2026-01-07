from .config_manager import ConfigManager
from .state_manager import StateManager
from .watcher import DirectoryWatcher
from .uploader import Uploader
import time


def main():
    # Load configuration (server URL, watch directory, etc.)
    config = ConfigManager()

    print("=== Client configuration ===")
    print("Server URL:     ", config.get_server_url())
    print("Watch directory:", config.get_watch_directory())

    # Load client state (which files were already uploaded)
    state = StateManager()

    # Create uploader that knows how to talk to the server
    uploader = Uploader(server_url=config.get_server_url())

    # Create a watcher for the configured directory
    watcher = DirectoryWatcher(
        watch_directory=config.get_watch_directory(),
        state_manager=state,
        recursive=False,   # or True if you want sub-directories
        uploader=uploader, # now watcher is connected to the server through uploader
    )

    print("\n=== Scanning for files (press Ctrl+C to stop) ===")
    try:
        while True:
            watcher.scan_once()
            time.sleep(5)  # Afew seconds to wait befor scanning again.
    except KeyboardInterrupt:
        print("\nStopping watcher, bye!")


if __name__ == "__main__":
    main()
