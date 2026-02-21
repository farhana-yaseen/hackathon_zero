#!/usr/bin/env python3
"""
Script to run all watchers simultaneously.
Currently supports Gmail watcher, with others to be added in Silver/Gold tiers.
"""

import os
import threading
import time
import sys
from gmail_watcher import GmailWatcher

def run_gmail_watcher(vault_path):
    """Run the Gmail watcher in a separate thread."""
    try:
        watcher = GmailWatcher(vault_path, interval=300)  # Check every 5 minutes
        watcher.run_continuous()
    except KeyboardInterrupt:
        print("Gmail watcher stopped.")
    except Exception as e:
        print(f"Error in Gmail watcher: {str(e)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python run_watchers.py <vault_path>")
        sys.exit(1)

    vault_path = sys.argv[1]

    print("Starting Personal AI Employee watchers...")

    # Start Gmail watcher in a separate thread
    gmail_thread = threading.Thread(target=run_gmail_watcher, args=(vault_path,), daemon=True)
    gmail_thread.start()

    print("Watchers started. Press Ctrl+C to stop.")

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all watchers...")
        sys.exit(0)

if __name__ == "__main__":
    main()