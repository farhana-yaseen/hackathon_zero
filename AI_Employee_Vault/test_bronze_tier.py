#!/usr/bin/env python3
"""
Test script for Bronze Tier functionality.
Simulates a new email by creating an .md file in /Needs_Action,
then triggers Claude to process it.
"""

import os
from datetime import datetime
import subprocess
import sys

def simulate_new_email(vault_path):
    """Create a simulated email in the Needs_Action folder."""
    needs_action_dir = os.path.join(vault_path, "Needs_Action")

    # Create a test email markdown file
    email_content = """---
type: email
from: "boss@company.com"
to: "employee@company.com"
subject: "Urgent: Quarterly Report Needed ASAP"
date: "2026-02-21T10:30:00Z"
is_important: True
labels: ["IMPORTANT", "URGENT"]
id: "test_email_12345"
---

# Email from boss@company.com

**Subject:** Urgent: Quarterly Report Needed ASAP

**Date:** Sat, 21 Feb 2026 10:30:00 GMT

**Labels:** IMPORTANT, URGENT

## Email Body
Hi,

We need the quarterly financial report by end of day today. This is critical for the board meeting tomorrow.

Please prioritize this above all other tasks.

Thanks,
Boss

## Suggested Actions
- [ ] Compile financial data
- [ ] Create report document
- [ ] Review with finance team
- [ ] Submit to boss by 5 PM

## Manual Actions
- [ ] Review content
- [ ] Determine priority
- [ ] Take appropriate action
- [ ] Mark as complete when done
"""

    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_email_{timestamp}_urgent_report.md"

    filepath = os.path.join(needs_action_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(email_content)

    print(f"Created test email: {filepath}")
    return filepath

def run_claude_reasoning(vault_path):
    """Run Claude reasoning to process the new email."""
    print("\nRunning Claude reasoning to process the new email...")

    try:
        result = subprocess.run([
            sys.executable, "claude_reasoning.py", vault_path
        ], cwd=vault_path, capture_output=True, text=True)

        if result.returncode == 0:
            print("Claude reasoning completed successfully!")
            print(result.stdout)
        else:
            print(f"Error in Claude reasoning: {result.stderr}")

    except Exception as e:
        print(f"Error running Claude reasoning: {str(e)}")

def verify_system_status(vault_path):
    """Verify the system worked correctly."""
    print("\nVerifying system status...")

    # Check if a plan was created
    plans_dir = os.path.join(vault_path, "Plans")
    plan_files = [f for f in os.listdir(plans_dir) if f.startswith("Plan_") and f.endswith(".md")]

    if plan_files:
        print(f"[OK] Plan created: {plan_files[0]}")

        # Show plan content
        plan_path = os.path.join(plans_dir, plan_files[0])
        with open(plan_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print("\nPlan content preview:")
            print("-" * 40)
            print('\n'.join(content.split('\n')[:15]))  # Show first 15 lines
            if len(content.split('\n')) > 15:
                print("... (truncated)")
            print("-" * 40)
    else:
        print("[ERROR] No plan file was created")

    # Check Dashboard update
    dashboard_path = os.path.join(vault_path, "Dashboard.md")
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        dashboard_content = f.read()

    print("[OK] Dashboard.md exists and is accessible")

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_bronze_tier.py <vault_path>")
        sys.exit(1)

    vault_path = sys.argv[1]

    print("Testing Bronze Tier functionality...\n")

    # Step 1: Simulate a new email
    email_file = simulate_new_email(vault_path)

    # Step 2: Run Claude reasoning
    run_claude_reasoning(vault_path)

    # Step 3: Verify system worked
    verify_system_status(vault_path)

    print("\nBronze Tier test completed!")
    print("\nNext steps:")
    print("1. Review the generated Plan.md in the Plans folder")
    print("2. Manually check off completed items")
    print("3. Run 'python claude_reasoning.py <vault_path> check' to move completed items to Done")
    print("4. Monitor Dashboard.md for updates")

if __name__ == "__main__":
    main()