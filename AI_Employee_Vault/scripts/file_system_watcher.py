import os
import time
import hashlib
from datetime import datetime
from base_watcher import BaseWatcher
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class FileSystemWatcher(BaseWatcher):
    """
    Watches a specified directory for file changes and creates markdown files in the vault.
    """

    def __init__(self, vault_path: str, watch_directory: str, interval: int = 10):
        super().__init__(vault_path, interval)
        self.watch_directory = watch_directory
        self.file_hashes = {}
        self.initialize_file_tracking()

        logger.info(f"File system watcher initialized for: {watch_directory}")

    def initialize_file_tracking(self):
        """
        Initialize the file hash tracking for the watched directory.
        """
        if os.path.exists(self.watch_directory):
            for root, dirs, files in os.walk(self.watch_directory):
                for file in files:
                    filepath = os.path.join(root, file)
                    if os.path.isfile(filepath):  # Skip directories
                        try:
                            with open(filepath, 'rb') as f:
                                content = f.read()
                                file_hash = hashlib.md5(content).hexdigest()
                                self.file_hashes[filepath] = file_hash
                        except Exception as e:
                            logger.warning(f"Could not hash file {filepath}: {str(e)}")
        else:
            logger.warning(f"Watch directory does not exist: {self.watch_directory}")

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for file changes in the watched directory.
        Returns a list of file change events.
        """
        changes = []

        if not os.path.exists(self.watch_directory):
            logger.warning(f"Watch directory does not exist: {self.watch_directory}")
            return changes

        # Walk through the watched directory
        for root, dirs, files in os.walk(self.watch_directory):
            for file in files:
                filepath = os.path.join(root, file)

                # Skip if it's a directory
                if not os.path.isfile(filepath):
                    continue

                try:
                    # Calculate current file hash
                    with open(filepath, 'rb') as f:
                        content = f.read()
                        current_hash = hashlib.md5(content).hexdigest()

                    # Check if file is new or modified
                    if filepath not in self.file_hashes:
                        # Skip files created by watchers to avoid recursion
                        filename = os.path.basename(filepath)
                        if filename.startswith('fs_created_') or filename.startswith('email_') or filename.startswith('sent_') or filename.startswith('whatsapp_'):
                            self.file_hashes[filepath] = current_hash
                            continue

                        # New file
                        change_event = {
                            'type': 'created',
                            'filepath': filepath,
                            'timestamp': datetime.now().isoformat(),
                            'size': len(content),
                            'extension': os.path.splitext(filepath)[1]
                        }
                        changes.append(change_event)
                        logger.info(f"New file detected: {filepath}")
                    elif self.file_hashes[filepath] != current_hash:
                        # Modified file
                        change_event = {
                            'type': 'modified',
                            'filepath': filepath,
                            'timestamp': datetime.now().isoformat(),
                            'size': len(content),
                            'extension': os.path.splitext(filepath)[1]
                        }
                        changes.append(change_event)
                        logger.info(f"Modified file detected: {filepath}")

                    # Update hash
                    self.file_hashes[filepath] = current_hash

                except Exception as e:
                    logger.error(f"Error processing file {filepath}: {str(e)}")

        # Check for deleted files
        existing_paths = {os.path.join(root, file)
                         for root, dirs, files in os.walk(self.watch_directory)
                         for file in files if os.path.isfile(os.path.join(root, file))}

        for tracked_path in list(self.file_hashes.keys()):
            if tracked_path not in existing_paths:
                # File was deleted
                change_event = {
                    'type': 'deleted',
                    'filepath': tracked_path,
                    'timestamp': datetime.now().isoformat(),
                    'size': 0,
                    'extension': os.path.splitext(tracked_path)[1]
                }
                changes.append(change_event)
                del self.file_hashes[tracked_path]
                logger.info(f"Deleted file detected: {tracked_path}")

        return changes

    def create_markdown_file(self, change_data: Dict[str, Any]) -> str:
        """
        Create a markdown file for the file system change in the appropriate vault folder.
        """
        # Determine folder based on file extension and change type
        extension = change_data.get('extension', '').lower()
        change_type = change_data.get('type', 'unknown')

        # Prioritize certain file types or change types
        if change_type == 'created' and extension in ['.pdf', '.doc', '.docx', '.xls', '.xlsx']:
            folder = 'Needs_Action'
        elif change_type == 'modified' and extension in ['.pdf', '.doc', '.docx', '.xls', '.xlsx']:
            folder = 'Needs_Action'
        elif change_type == 'deleted':
            folder = 'Inbox'  # Deleted files go to Inbox for review
        else:
            folder = 'Inbox'

        # Sanitize filename
        filename_clean = os.path.basename(change_data['filepath']).replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')

        # Create frontmatter with file details
        frontmatter = f"""---
type: file_change
filepath: "{change_data['filepath']}"
change_type: "{change_data['type']}"
timestamp: "{change_data['timestamp']}"
size_bytes: {change_data['size']}
extension: "{change_data['extension']}"
---

"""

        # Generate suggested actions based on file type and change
        suggested_actions = self.generate_suggested_actions(change_data)

        # Combine everything
        content = f"""{frontmatter}

# File System Event: {change_data['type'].title()} - {filename_clean}

**Path:** {change_data['filepath']}
**Change Type:** {change_data['type'].title()}
**Size:** {change_data['size']} bytes
**Extension:** {change_data['extension']}
**Timestamp:** {change_data['timestamp']}

## Description
A file system event occurred for the file "{filename_clean}" in the monitored directory.

## Suggested Actions
{suggested_actions}

## Manual Actions
- [ ] Review the file change
- [ ] Determine if action is needed
- [ ] Take appropriate action
- [ ] Mark as complete when done
"""

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        event_type = change_data['type']
        filename = f"fs_{event_type}_{timestamp}_{filename_clean.replace('.', '_')}"

        return self.write_to_vault(folder, filename, content)

    def generate_suggested_actions(self, change_data: Dict[str, Any]) -> str:
        """
        Generate suggested actions based on file type and change type.
        """
        actions = []
        extension = change_data.get('extension', '').lower()
        change_type = change_data.get('type', 'unknown')

        if change_type == 'created':
            if extension in ['.pdf', '.doc', '.docx', '.txt']:
                actions.append("- [ ] Review document content")
            elif extension in ['.xls', '.xlsx', '.csv']:
                actions.append("- [ ] Review spreadsheet data")
            elif extension in ['.jpg', '.jpeg', '.png', '.gif']:
                actions.append("- [ ] Review image content")
            actions.append("- [ ] Determine if filing is needed")

        elif change_type == 'modified':
            if extension in ['.pdf', '.doc', '.docx', '.txt']:
                actions.append("- [ ] Review document changes")
            elif extension in ['.xls', '.xlsx', '.csv']:
                actions.append("- [ ] Review spreadsheet updates")
            actions.append("- [ ] Verify changes are appropriate")

        elif change_type == 'deleted':
            actions.append("- [ ] Verify deletion was intentional")
            actions.append("- [ ] Check if backup is needed")
            actions.append("- [ ] Confirm if this affects ongoing work")

        # Add default actions if no specific ones were identified
        if not actions:
            actions.extend([
                "- [ ] Assess impact of change",
                "- [ ] Take appropriate action",
                "- [ ] Document if necessary"
            ])

        return '\n'.join(actions)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python file_system_watcher.py <vault_path> <watch_directory> [interval_seconds]")
        sys.exit(1)

    vault_path = sys.argv[1]
    watch_directory = sys.argv[2]
    interval = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    watcher = FileSystemWatcher(vault_path, watch_directory, interval)

    if len(sys.argv) > 4:
        # Run once if a fourth argument is provided
        watcher.run_once()
    else:
        # Run continuously
        watcher.run_continuous()