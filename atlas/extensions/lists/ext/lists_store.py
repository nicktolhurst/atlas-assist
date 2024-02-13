import os
import json

class Store:
    def __init__(self, logger, store_file_name='store.json'):
        self.log = logger
        self.store_path = f'{os.path.dirname(os.path.abspath(__file__))}/{store_file_name}'
        self.lists = {}
        self.load()

    def save(self):
        with open(self.store_path, 'w') as f:
            json.dump(self.lists, f, indent=4)
        self.log.debug(f"Saved lists to {self.store_path}")

    def load(self):
        if os.path.exists(self.store_path):
            with open(self.store_path, 'r') as f:
                self.log.debug(f"Loaded lists from {self.store_path}")
                self.lists = json.load(f)
        else:
            self.log.warning(f"Store file not found at {self.store_path}. Creating new store.")