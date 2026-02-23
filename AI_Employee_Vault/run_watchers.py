#!/usr/bin/env python3
"""
Script to run all watchers simultaneously.
Supports Gmail, WhatsApp, and File System watchers.
"""

import os
import threading
import time
import sys
from gmail_watcher import GmailWatcher
from whatsapp_watcher import WhatsAppWatcher
from file_system_watcher import FileSystemWatcher

def run_gmail_watcher(vault_path):
    """Run the Gmail watcher in a separate thread."""
    try:
        watcher = GmailWatcher(vault_path, interval=300)  # Check every 5 minutes
        watcher.run_continuous()
    except KeyboardInterrupt:
        print("Gmail watcher stopped.")
    except Exception as e:
        print(f"Error in Gmail watcher: {str(e)}")

def run_whatsapp_watcher(vault_path):
    """Run the WhatsApp watcher in a separate thread."""
    try:
        watcher = WhatsAppWatcher(vault_path, interval=30)  # Check every 30 seconds
        watcher.run_continuous()
    except KeyboardInterrupt:
        print("WhatsApp watcher stopped.")
    except Exception as e:
        print(f"Error in WhatsApp watcher: {str(e)}")

def run_file_system_watcher(vault_path):
    """Run the File System watcher in a separate thread."""
    try:
        # Watch the vault's Inbox folder for new files
        watch_directory = os.path.join(vault_path, "Inbox")
        os.makedirs(watch_directory, exist_ok=True)

        watcher = FileSystemWatcher(vault_path, watch_directory, interval=10)  # Check every 10 seconds
        watcher.run_continuous()
    except KeyboardInterrupt:
        print("File System watcher stopped.")
    except Exception as e:
        print(f"Error in File System watcher: {str(e)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python run_watchers.py <vault_path>")
        sys.exit(1)

    vault_path = sys.argv[1]

    print("Starting Personal AI Employee watchers...")

    # Start Gmail watcher in a separate thread
    gmail_thread = threading.Thread(target=run_gmail_watcher, args=(vault_path,), daemon=True)
    gmail_thread.start()

    # Start WhatsApp watcher in a separate thread
    whatsapp_thread = threading.Thread(target=run_whatsapp_watcher, args=(vault_path,), daemon=True)
    whatsapp_thread.start()

    # Start File System watcher in a separate thread
    fs_thread = threading.Thread(target=run_file_system_watcher, args=(vault_path,), daemon=True)
    fs_thread.start()

    print("All watchers started. Press Ctrl+C to stop.")

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all watchers...")
        sys.exit(0)

if __name__ == "__main__":
    main()