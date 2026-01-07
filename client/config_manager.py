import os
import json
from typing import Any, Dict

# Path to the configuration directory and file
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "asset_client")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

class ConfigManager:
    """
    Manages the configuration file for the client.
    Responsibilities:
    -Ensure a configuration file exists
    -creats a deafult configuration file if missing
    -provide simple access to configuration values
    """

    def __init__(self,config_path:str = CONFIG_FILE)->None:
        self.config_path = config_path 
        self.config: Dict[str, Any] = {}
        self._load_or_create_default()


    def _load_or_create_default(self) -> None:
        #Loads the configuration file if it exists,
        #and if it doesnt , creats a directory and a default config file.

        #Making sure that the config directory exists:
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        if not os.path.exists(self.config_path):
            #Default configuration
            self.config ={
                "server_url" :  "http://localhost:8000",
                # Default watch directory
                "watch_directory" : r"C:\Users\dnkhn\OneDrive\שולחן העבודה\משימות\משימה 7\תקיית מעקב"
            }
            self._save()        
        else:
            # Load existing config
            with open(self.config_path,"r", encoding ="utf-8")as f:
                 self.config = json.load(f)

    # A function that writes the current configuration to config.json.
    def _save(self) ->None:
        with open(self.config_path,"w",encoding ="utf-8")as f:
            json.dump(self.config,f,indent=2, ensure_ascii=False)

    # A function that returns the server URL:
    def get_server_url(self) -> str:
        return self.config.get("server_url","")


    # A function that returns the directory path that the client should watch
    def get_watch_directory(self) -> str:
        return self.config.get("watch_directory","")
    
    # A function that updates the watch directory and saves the configuration.
    def set_watch_directory(self, path:str) -> None:
        self.config["watch_directory"] = path
        self._save()
