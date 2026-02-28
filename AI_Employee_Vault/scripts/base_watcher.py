import os
import time
import json
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseWatcher(ABC):
    """
    Abstract base class for all watchers.
    Watchers monitor external systems and create markdown files in the vault.
    """

    def __init__(self, vault_path: str, interval: int = 60):
        self.vault_path = vault_path
        self.interval = interval  # seconds between checks
        self.last_check = None

        # Ensure required directories exist
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure all necessary vault directories exist."""
        dirs = ['Inbox', 'Needs_Action', 'Done', 'Plans', 'Accounting', 'Updates']
        for dir_name in dirs:
            path = os.path.join(self.vault_path, dir_name)
            os.makedirs(path, exist_ok=True)

    @abstractmethod
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check the external system for updates.
        Returns a list of items that need to be processed.
        """
        pass

    @abstractmethod
    def create_markdown_file(self, item: Dict[str, Any]) -> str:
        """
        Create a markdown file for the given item.
        Returns the path to the created file.
        """
        pass

    def run_once(self):
        """Run a single check cycle."""
        logger.info(f"Running {self.__class__.__name__} check...")
        try:
            items = self.check_for_updates()
            for item in items:
                file_path = self.create_markdown_file(item)
                logger.info(f"Created file: {file_path}")

            self.last_check = datetime.now()
            logger.info(f"Completed {len(items)} items")
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {str(e)}")

    def run_continuous(self):
        """Run the watcher continuously."""
        logger.info(f"Starting continuous {self.__class__.__name__}...")
        while True:
            self.run_once()
            time.sleep(self.interval)

    def write_to_vault(self, folder: str, filename: str, content: str) -> str:
        """Write content to a markdown file in the specified vault folder."""
        path = os.path.join(self.vault_path, folder, f"{filename}.md")

        # Handle filename conflicts
        counter = 1
        original_path = path
        while os.path.exists(path):
            name_part = filename.rsplit('.', 1)[0] if '.' in filename else filename
            path = os.path.join(self.vault_path, folder, f"{name_part}_{counter}.md")
            counter += 1

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        return path