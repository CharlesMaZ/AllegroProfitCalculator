import json
import os
from pathlib import Path

class Config:
    def __init__(self, config_path = "config.json"):
        self.config_path = config_path
        self.data = self.load_config()

    def load_config(self) -> dict:
        if Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            # Domyślna konfiguracja
            default_config = {
                "api": {
                    "client_id": "YOUR_CLIENT_ID",
                    "client_secret": "YOUR_CLIENT_SECRET",
                    "access_token": "YOUR_ACCESS_TOKEN",
                    "base_url": "https://api.allegro.pl"
                },
                "database": {
                    "path": "allegro.db"
                },
                "sync": {
                    "interval_minutes": 15
                }
            }

            # Zapisz domyślną konfigurację do pliku
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=4)

            print(f"Utworzono domyślny plik konfiguracyjny: {self.config_path}")
            return default_config

    def save_config(self, data: dict):
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=4)
