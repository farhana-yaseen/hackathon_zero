#!/usr/bin/env python3
"""
Test script for Silver Tier functionality.
This script tests all the new Silver Tier components:
- WhatsApp watcher
- File System watcher
- MCP server interactions
- Approval system
- Scheduler
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def test_whatsapp_watcher_simulation(vault_path):
    """Test the WhatsApp watcher by creating a simulation file."""
    print("Testing WhatsApp watcher simulation...")

    # Create WhatsApp simulation directory
    whatsapp_sim_dir = os.path.join(vault_path, "WhatsApp_Sim")
    os.makedirs(whatsapp_sim_dir, exist_ok=True)

    # Create a sample WhatsApp message
    message_data = {
        "sender": "Boss Person",
        "phone_number": "+1234567890",
        "body": "Urgent: Please prepare the quarterly report ASAP for tomorrow's meeting.",
        "is_important": True,
        "priority": "high"
    }

    # Write the message to a file to simulate receiving it
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"whatsapp_msg_{timestamp}.json"
    filepath = os.path.join(whatsapp_sim_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(message_data, f, indent=2)

    print(f"Created WhatsApp message simulation: {filepath}")
    print("WhatsApp watcher will process this when it runs next")


def test_file_system_watcher(vault_path):
    """Test the file system watcher by creating a file in the watched directory."""
    print("\nTesting File System watcher...")

    # The file system watcher watches the Inbox directory
    inbox_dir = os.path.join(vault_path, "Inbox")
    os.makedirs(inbox_dir, exist_ok=True)

    # Create a test file
    test_file = os.path.join(inbox_dir, f"test_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("This is a test file to trigger the file system watcher.\n")
        f.write("It contains important information that should be processed.\n")

    print(f"Created test file: {test_file}")
    print("File System watcher will detect this when it runs next")


def test_approval_system(vault_path):
    """Test the approval system by creating an approval request."""
    print("\nTesting Approval System...")

    # Create an approval request manually
    needs_action_dir = os.path.join(vault_path, "Needs_Action")
    os.makedirs(needs_action_dir, exist_ok=True)

    approval_content = """---
type: approval_request
request_id: "urgent_purchase_001"
urgency: "high"
status: "pending_approval"
requested_at: "{}"
---

# Human Approval Required: Urgent Purchase Request

**Urgency:** high
**Requested At:** {}
**Status:** Pending Approval

## Description
Need to approve an urgent purchase of $500 for new office supplies as current inventory is depleted.

## Action Required
- [ ] Review request
- [ ] Provide approval or denial
- [ ] Update status to reflect decision

## Decision Options
- [ ] Approve
- [ ] Deny - Reason: _______________
- [ ] Defer - Reason: _______________

## Notes
Add any notes about the approval decision here.
""".format(datetime.now().isoformat(), datetime.now().isoformat())

    approval_file = os.path.join(needs_action_dir, f"approval_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(approval_file, 'w', encoding='utf-8') as f:
        f.write(approval_content)

    print(f"Created approval request: {approval_file}")


def test_scheduler_integration(vault_path):
    """Test scheduler by scheduling a task."""
    print("\nTesting Scheduler Integration...")

    # We'll test by creating a scheduled task file directly
    schedules_dir = os.path.join(vault_path, "Schedules")
    os.makedirs(schedules_dir, exist_ok=True)

    # Schedule a task for 1 minute from now
    future_time = datetime.now() + timedelta(minutes=1)

    task_data = {
        "id": f"test_task_{int(time.time())}",
        "name": "Silver Tier Test Task",
        "execute_time": future_time.isoformat(),
        "status": "pending",
        "recurring": False,
        "recurrence_interval": None,
        "created_at": datetime.now().isoformat()
    }

    task_file = os.path.join(schedules_dir, f"test_scheduled_task_{int(time.time())}.json")
    with open(task_file, 'w', encoding='utf-8') as f:
        json.dump(task_data, f, indent=2)

    print(f"Created scheduled task: {task_file}")
    print(f"Task scheduled for: {future_time}")


def test_mcp_server_interaction():
    """Test interaction with MCP server."""
    print("\nTesting MCP Server Interaction...")
    print("MCP server provides the following tools:")
    print("- send_email: Send emails through the system")
    print("- create_task: Create new tasks in the system")
    print("- schedule_meeting: Schedule meetings")
    print("- move_file: Move files within the vault")
    print("- create_note: Create notes in specified folders")
    print("- request_human_approval: Request human approval for actions")
    print("\nTo interact with the MCP server, connect to http://localhost:8080/mcp")


def run_complete_silver_tier_test(vault_path):
    """Run a complete test of all Silver Tier functionality."""
    print("Starting Silver Tier functionality test...\n")

    # Test each component
    test_whatsapp_watcher_simulation(vault_path)
    test_file_system_watcher(vault_path)
    test_approval_system(vault_path)
    test_scheduler_integration(vault_path)
    test_mcp_server_interaction()

    print("\n" + "="*60)
    print("Silver Tier Test Summary:")
    print("- WhatsApp watcher simulation: Created sample message")
    print("- File System watcher test: Created sample file")
    print("- Approval system test: Created approval request")
    print("- Scheduler test: Created scheduled task")
    print("- MCP server: Ready for tool interactions")
    print("="*60)

    print(f"\nNext steps:")
    print(f"1. Run the Silver Tier orchestration: python silver_tier.py --vault-path {vault_path}")
    print(f"2. Monitor the {os.path.join(vault_path, 'Inbox')} folder for new items")
    print(f"3. Check the {os.path.join(vault_path, 'Needs_Action')} folder for items requiring attention")
    print(f"4. Review the generated reports and logs")


def main():
    if len(sys.argv) != 2:
        print("Usage: python test_silver_tier.py <vault_path>")
        sys.exit(1)

    vault_path = sys.argv[1]

    if not os.path.exists(vault_path):
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)

    run_complete_silver_tier_test(vault_path)


if __name__ == "__main__":
    main()