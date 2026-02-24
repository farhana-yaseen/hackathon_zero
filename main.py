#!/usr/bin/env python3
"""
Main entry point for the hackathon-zero project.

This script starts the Silver Tier orchestration for the Personal AI Employee.
"""
import subprocess
import sys
import os
from pathlib import Path


def main():
    print("Starting Silver Tier Orchestration for Personal AI Employee...")

    # Define the vault path
    vault_path = os.path.join(os.path.dirname(__file__), "AI_Employee_Vault")

    # Check if the vault directory exists
    if not os.path.exists(vault_path):
        print(f"Error: Vault directory does not exist: {vault_path}")
        sys.exit(1)

    print(f"Using vault path: {vault_path}")
    print("Starting Silver Tier components...")
    print("- Watchers (Gmail, WhatsApp, File System)")
    print("- MCP Server for actions")
    print("- Human-in-the-loop approval system")
    print("- Automated scheduler")
    print()

    try:
        # Run the silver tier orchestration
        result = subprocess.run([
            sys.executable,
            os.path.join(vault_path, "silver_tier.py"),
            "--vault-path", vault_path
        ], check=True)

        if result.returncode == 0:
            print("\nSilver Tier orchestration completed successfully!")
        else:
            print(f"\nSilver Tier orchestration exited with code: {result.returncode}")

    except subprocess.CalledProcessError as e:
        print(f"Error running Silver Tier orchestration: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOrchestration interrupted by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()