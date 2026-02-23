#!/usr/bin/env python3
"""
Human-in-the-Loop Approval System for Personal AI Employee

This system manages approval requests and tracks their status.
"""

import os
import glob
import json
import re
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ApprovalSystem:
    def __init__(self, vault_path):
        self.vault_path = vault_path
        self.approvals_dir = os.path.join(vault_path, "Approvals")
        self.needs_action_dir = os.path.join(vault_path, "Needs_Action")

        # Ensure directories exist
        os.makedirs(self.approvals_dir, exist_ok=True)

    def find_pending_approvals(self):
        """Find all pending approval requests in the vault."""
        # Look for approval requests in Needs_Action folder
        pattern = os.path.join(self.needs_action_dir, "*approval_request*.md")
        approval_files = glob.glob(pattern)

        pending_approvals = []
        for file_path in approval_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter
            frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)

                # Check if status is pending approval
                status_match = re.search(r'status:\s*["\']?([^"\'\n\r]*)', frontmatter)
                if status_match and 'pending' in status_match.group(1).lower():
                    # Extract request details
                    request_id_match = re.search(r'request_id:\s*["\']?([^"\'\n\r]*)', frontmatter)
                    urgency_match = re.search(r'urgency:\s*["\']?([^"\'\n\r]*)', frontmatter)

                    pending_approvals.append({
                        'file_path': file_path,
                        'request_id': request_id_match.group(1) if request_id_match else 'Unknown',
                        'urgency': urgency_match.group(1) if urgency_match else 'Unknown',
                        'content': content
                    })

        return pending_approvals

    def approve_request(self, request_id, approver_notes=""):
        """Approve a specific request by updating its status."""
        approval_file = self._find_approval_file_by_id(request_id)
        if not approval_file:
            raise FileNotFoundError(f"No approval request found with ID: {request_id}")

        with open(approval_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update status to approved
        updated_content = self._update_approval_status(content, "approved", approver_notes)

        with open(approval_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        logger.info(f"Approved request: {request_id}")
        return True

    def deny_request(self, request_id, reason="", approver_notes=""):
        """Deny a specific request by updating its status."""
        approval_file = self._find_approval_file_by_id(request_id)
        if not approval_file:
            raise FileNotFoundError(f"No approval request found with ID: {request_id}")

        with open(approval_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update status to denied
        updated_content = self._update_approval_status(content, "denied", approver_notes, reason)

        with open(approval_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        logger.info(f"Denied request: {request_id}")
        return True

    def defer_request(self, request_id, reason="", approver_notes=""):
        """Defer a specific request by updating its status."""
        approval_file = self._find_approval_file_by_id(request_id)
        if not approval_file:
            raise FileNotFoundError(f"No approval request found with ID: {request_id}")

        with open(approval_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update status to deferred
        updated_content = self._update_approval_status(content, "deferred", approver_notes, reason)

        with open(approval_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        logger.info(f"Deferred request: {request_id}")
        return True

    def _find_approval_file_by_id(self, request_id):
        """Find an approval file by its request ID."""
        pattern = os.path.join(self.needs_action_dir, "*approval_request*.md")
        approval_files = glob.glob(pattern)

        for file_path in approval_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter
            frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)

                # Check if this file has the matching request_id
                request_id_match = re.search(r'request_id:\s*["\']?([^"\'\n\r]*)', frontmatter)
                if request_id_match and request_id_match.group(1) == request_id:
                    return file_path

        return None

    def _update_approval_status(self, content, status, approver_notes="", reason=""):
        """Update the status in the markdown content."""
        # Update frontmatter status
        frontmatter_updated = False
        lines = content.split('\n')
        updated_lines = []
        in_frontmatter = False
        frontmatter_lines = []

        for line in lines:
            if line.strip() == '---' and not in_frontmatter:
                in_frontmatter = True
                frontmatter_lines.append(line)
            elif line.strip() == '---' and in_frontmatter:
                # End of frontmatter, update the status
                in_frontmatter = False
                for fm_line in frontmatter_lines:
                    if fm_line.strip().startswith('status:'):
                        updated_lines.append(f'status: "{status}"')
                    else:
                        updated_lines.append(fm_line)
                frontmatter_updated = True
            elif in_frontmatter:
                frontmatter_lines.append(line)
            else:
                updated_lines.append(line)

        # If frontmatter wasn't found, add it at the beginning
        if not frontmatter_updated:
            updated_content = f"---\nstatus: \"{status}\"\n---\n{content}"
        else:
            updated_content = '\n'.join(updated_lines)

        # Add approval details to the content body
        approval_details = f"\n\n## Approval Decision\n"
        approval_details += f"- **Status:** {status.upper()}\n"
        approval_details += f"- **Decision Time:** {datetime.now().isoformat()}\n"
        if reason:
            approval_details += f"- **Reason:** {reason}\n"
        if approver_notes:
            approval_details += f"- **Notes:** {approver_notes}\n"

        # Add to the end of the content
        updated_content += approval_details

        # Move the file to appropriate folder based on status
        file_dir, file_name = os.path.split(self._find_approval_file_by_id(
            re.search(r'request_id:\s*["\']?([^"\'\n\r]*)', content).group(1)
        ))
        new_folder = "Done" if status == "approved" else "Inbox"
        new_path = os.path.join(self.vault_path, new_folder, file_name)

        # Remove the old file and save the new one
        os.remove(self._find_approval_file_by_id(
            re.search(r'request_id:\s*["\']?([^"\'\n\r]*)', content).group(1)
        ))
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        return updated_content

    def get_approval_summary(self):
        """Get a summary of all approval requests."""
        pending_approvals = self.find_pending_approvals()

        summary = {
            'total_pending': len(pending_approvals),
            'requests': []
        }

        for approval in pending_approvals:
            summary['requests'].append({
                'request_id': approval['request_id'],
                'urgency': approval['urgency'],
                'file_path': approval['file_path']
            })

        return summary

def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python approval_system.py <vault_path> [action] [request_id] [additional_params]")
        print("\nActions:")
        print("  list              - List all pending approvals")
        print("  approve <id>      - Approve a request by ID")
        print("  deny <id> [reason] - Deny a request by ID with optional reason")
        print("  defer <id> [reason] - Defer a request by ID with optional reason")
        print("  summary           - Get summary of approval requests")
        sys.exit(1)

    vault_path = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "list"

    approval_system = ApprovalSystem(vault_path)

    if action == "list":
        pending = approval_system.find_pending_approvals()
        if pending:
            print(f"Found {len(pending)} pending approval requests:\n")
            for req in pending:
                print(f"- ID: {req['request_id']}")
                print(f"  Urgency: {req['urgency']}")
                print(f"  File: {req['file_path']}")
                print()
        else:
            print("No pending approval requests found.")

    elif action == "approve":
        if len(sys.argv) < 4:
            print("Usage: python approval_system.py <vault_path> approve <request_id>")
            sys.exit(1)

        request_id = sys.argv[3]
        approval_system.approve_request(request_id)
        print(f"Successfully approved request: {request_id}")

    elif action == "deny":
        if len(sys.argv) < 4:
            print("Usage: python approval_system.py <vault_path> deny <request_id> [reason]")
            sys.exit(1)

        request_id = sys.argv[3]
        reason = sys.argv[4] if len(sys.argv) > 4 else ""
        approval_system.deny_request(request_id, reason)
        print(f"Successfully denied request: {request_id}")

    elif action == "defer":
        if len(sys.argv) < 4:
            print("Usage: python approval_system.py <vault_path> defer <request_id> [reason]")
            sys.exit(1)

        request_id = sys.argv[3]
        reason = sys.argv[4] if len(sys.argv) > 4 else ""
        approval_system.defer_request(request_id, reason)
        print(f"Successfully deferred request: {request_id}")

    elif action == "summary":
        summary = approval_system.get_approval_summary()
        print(f"Approval Summary:")
        print(f"  Total pending: {summary['total_pending']}")
        print(f"  Requests: {len(summary['requests'])}")
        for req in summary['requests']:
            print(f"    - {req['request_id']} ({req['urgency']})")

    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()