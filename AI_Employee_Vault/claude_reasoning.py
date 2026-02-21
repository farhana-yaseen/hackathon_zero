#!/usr/bin/env python3
"""
Basic Claude Reasoning Loop for Personal AI Employee

This script demonstrates how Claude Code can read from /Needs_Action,
create Plan.md files with checkboxes, and move completed items to /Done.
"""

import os
import glob
from datetime import datetime
import re

def process_needs_action_items(vault_path):
    """
    Process all markdown files in the Needs_Action folder.
    Creates Plan.md files with checkboxes for each item.
    """
    needs_action_dir = os.path.join(vault_path, "Needs_Action")
    inbox_dir = os.path.join(vault_path, "Inbox")
    plans_dir = os.path.join(vault_path, "Plans")
    done_dir = os.path.join(vault_path, "Done")

    # Ensure directories exist
    os.makedirs(plans_dir, exist_ok=True)
    os.makedirs(done_dir, exist_ok=True)

    # Find all markdown files in Needs_Action and Inbox
    needs_action_files = glob.glob(os.path.join(needs_action_dir, "*.md"))
    inbox_files = glob.glob(os.path.join(inbox_dir, "*.md"))
    all_files = needs_action_files + inbox_files

    if not all_files:
        print("No files to process in Needs_Action or Inbox")
        return

    # Create a plan for today
    today = datetime.now().strftime("%Y-%m-%d")
    plan_filename = f"Plan_{today}.md"
    plan_path = os.path.join(plans_dir, plan_filename)

    plan_content = f"# Daily Plan - {today}\n\n"
    plan_content += "## Items to Process\n\n"

    for file_path in all_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract frontmatter and content
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            body = frontmatter_match.group(2)
        else:
            frontmatter = ""
            body = content

        # Extract subject/title from frontmatter or content
        subject_match = re.search(r'subject: "(.*?)"', frontmatter)
        if subject_match:
            subject = subject_match.group(1)
        else:
            # Look for a title in the content
            title_match = re.match(r'# (.*)', body)
            if title_match:
                subject = title_match.group(1)
            else:
                subject = os.path.basename(file_path).replace('.md', '')

        # Add to plan with checkbox
        plan_content += f"- [ ] {subject} ({os.path.basename(file_path)})\n"

        # Add details if available
        if frontmatter:
            plan_content += f"  - Type: {extract_value(frontmatter, 'type')}\n"
            plan_content += f"  - From: {extract_value(frontmatter, 'from')}\n"

        plan_content += "\n"

    # Add instructions for completing the plan
    plan_content += "\n## Instructions\n"
    plan_content += "- Review each item\n"
    plan_content += "- Complete the tasks\n"
    plan_content += "- Check off completed items\n"
    plan_content += "- Move completed files to Done folder\n"

    # Write the plan
    with open(plan_path, 'w', encoding='utf-8') as f:
        f.write(plan_content)

    print(f"Created plan: {plan_path}")
    print(f"Processing {len(all_files)} items...")

def extract_value(frontmatter, key):
    """Extract a value from YAML frontmatter."""
    match = re.search(rf'{key}: ["\']?(.*?)(?:["\']?\n|$)', frontmatter)
    return match.group(1) if match else "Not specified"

def check_completed_items(vault_path):
    """
    Check for completed items in Plans and move original files to Done.
    """
    plans_dir = os.path.join(vault_path, "Plans")
    done_dir = os.path.join(vault_path, "Done")
    needs_action_dir = os.path.join(vault_path, "Needs_Action")
    inbox_dir = os.path.join(vault_path, "Inbox")

    # Find today's plan or most recent plan
    plan_files = glob.glob(os.path.join(plans_dir, "Plan_*.md"))
    if not plan_files:
        print("No plan files found")
        return

    # Get the most recent plan
    plan_files.sort(key=os.path.getmtime, reverse=True)
    latest_plan = plan_files[0]

    with open(latest_plan, 'r', encoding='utf-8') as f:
        plan_content = f.read()

    # Find all completed items (those with [x])
    completed_items = re.findall(r'- \[x\] (.*?) \((.*?)\)', plan_content)

    for item_desc, filename in completed_items:
        # Look for the original file in Needs_Action or Inbox
        original_file_path = os.path.join(needs_action_dir, filename)
        if not os.path.exists(original_file_path):
            original_file_path = os.path.join(inbox_dir, filename)

        if os.path.exists(original_file_path):
            # Move to Done folder
            done_file_path = os.path.join(done_dir, filename)

            # Handle potential filename conflicts in Done folder
            counter = 1
            original_done_path = done_file_path
            while os.path.exists(done_file_path):
                name_part = filename.rsplit('.', 1)[0] if '.' in filename else filename
                ext_part = f".{filename.split('.')[1]}" if '.' in filename else ''
                done_file_path = os.path.join(done_dir, f"{name_part}_completed_{counter}{ext_part}")
                counter += 1

            os.rename(original_file_path, done_file_path)
            print(f"Moved completed item to Done: {filename}")
        else:
            print(f"Original file not found: {filename}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python claude_reasoning.py <vault_path>")
        print("  Use 'process' to create a new plan from Needs_Action/Inbox")
        print("  Use 'check' to check for completed items and move them to Done")
        sys.exit(1)

    vault_path = sys.argv[1]

    if len(sys.argv) > 2:
        action = sys.argv[2]
        if action == "process":
            process_needs_action_items(vault_path)
        elif action == "check":
            check_completed_items(vault_path)
        else:
            print("Invalid action. Use 'process' or 'check'")
    else:
        # Default: process new items
        process_needs_action_items(vault_path)