import os
import time
from datetime import datetime
from base_watcher import BaseWatcher
import logging
import json
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class WhatsAppWatcher(BaseWatcher):
    """
    Watches WhatsApp messages (simulated) and creates markdown files in the vault.
    In a real implementation, this would connect to WhatsApp Business API or use a third-party service.
    """

    def __init__(self, vault_path: str, interval: int = 30, whatsapp_api_key: str = None):
        super().__init__(vault_path, interval)
        self.whatsapp_api_key = whatsapp_api_key
        # In a real implementation, we'd initialize WhatsApp API connection here
        logger.info("WhatsApp watcher initialized")

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new WhatsApp messages.
        In a real implementation, this would query the WhatsApp API.
        For simulation purposes, we'll check for a special file that simulates incoming messages.
        """
        messages = []

        # Simulate checking for WhatsApp messages by looking for files in a special directory
        whatsapp_sim_dir = os.path.join(self.vault_path, "WhatsApp_Sim")
        os.makedirs(whatsapp_sim_dir, exist_ok=True)

        # Look for new message files in the simulation directory
        for filename in os.listdir(whatsapp_sim_dir):
            if filename.endswith(".json") and not filename.startswith("_"):
                filepath = os.path.join(whatsapp_sim_dir, filename)

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        message_data = json.load(f)

                    # Mark as processed by renaming
                    processed_filepath = os.path.join(whatsapp_sim_dir, f"_processed_{filename}")
                    os.rename(filepath, processed_filepath)

                    # Add timestamp if not present
                    if 'timestamp' not in message_data:
                        message_data['timestamp'] = datetime.now().isoformat()

                    messages.append(message_data)

                except Exception as e:
                    logger.error(f"Error processing WhatsApp message file {filename}: {str(e)}")

        return messages

    def create_markdown_file(self, message_data: Dict[str, Any]) -> str:
        """
        Create a markdown file for the WhatsApp message in the appropriate vault folder.
        """
        # Determine folder based on message content
        if any(keyword in message_data.get('body', '').lower() for keyword in ['urgent', 'asap', 'important']):
            folder = 'Needs_Action'
        else:
            folder = 'Inbox'

        # Sanitize filename
        sender = message_data.get('sender', 'unknown').replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')

        # Create frontmatter with message details
        frontmatter = f"""---
type: whatsapp_message
sender: "{message_data.get('sender', 'Unknown')}"
phone_number: "{message_data.get('phone_number', 'Unknown')}"
timestamp: "{message_data.get('timestamp', datetime.now().isoformat())}"
is_important: {message_data.get('is_important', False)}
priority: "{message_data.get('priority', 'normal')}"
---

"""

        # Generate suggested actions based on message content
        suggested_actions = self.generate_suggested_actions(message_data)

        # Combine everything
        content = f"""{frontmatter}

# WhatsApp Message from {message_data.get('sender', 'Unknown')}

**Phone Number:** {message_data.get('phone_number', 'Unknown')}
**Received:** {message_data.get('timestamp', datetime.now().isoformat())}

## Message
{message_data.get('body', '')}

## Suggested Actions
{suggested_actions}

## Manual Actions
- [ ] Review message content
- [ ] Determine appropriate response
- [ ] Take necessary action
- [ ] Mark as complete when done
"""

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"whatsapp_{timestamp}_{sender}"

        return self.write_to_vault(folder, filename, content)

    def generate_suggested_actions(self, message_data: Dict[str, Any]) -> str:
        """
        Generate suggested actions based on message content.
        """
        actions = []
        body = message_data.get('body', '').lower()

        # Check for common patterns that suggest specific actions
        if 'meeting' in body:
            actions.append("- [ ] Schedule meeting in calendar")
        if 'call' in body or 'phone' in body:
            actions.append("- [ ] Schedule callback")
        if 'urgent' in body or 'asap' in body or 'immediately' in body:
            actions.append("- [ ] Handle with priority")
        if 'payment' in body or 'money' in body or 'invoice' in body:
            actions.append("- [ ] Review payment details")
        if 'approval' in body or 'approve' in body:
            actions.append("- [ ] Review request for approval")

        # Add default actions if no specific ones were identified
        if not actions:
            actions.extend([
                "- [ ] Respond appropriately",
                "- [ ] File in appropriate category",
                "- [ ] Follow up if needed"
            ])

        return '\n'.join(actions)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python whatsapp_watcher.py <vault_path> [interval_seconds]")
        sys.exit(1)

    vault_path = sys.argv[1]
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30

    watcher = WhatsAppWatcher(vault_path, interval)

    if len(sys.argv) > 3:
        # Run once if a third argument is provided
        watcher.run_once()
    else:
        # Run continuously
        watcher.run_continuous()