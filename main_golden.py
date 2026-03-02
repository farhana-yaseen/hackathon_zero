#!/usr/bin/env python3
"""
Main entry point for the hackathon-zero project.

This script starts the Golden Tier orchestration for the Personal AI Employee.
"""

import subprocess
import sys
import os
from pathlib import Path
import argparse


def main():
    parser = argparse.ArgumentParser(description="Golden Tier Orchestration for Personal AI Employee")
    parser.add_argument("--tier", choices=["bronze", "silver", "golden"], default="golden",
                        help="Select which tier to run (default: golden)")
    parser.add_argument("--vault-path", default=None,
                        help="Path to the vault directory (defaults to AI_Employee_Vault)")

    args = parser.parse_args()

    # Define the vault path
    vault_path = args.vault_path or os.path.join(os.path.dirname(__file__), "AI_Employee_Vault")

    # Check if the vault directory exists
    if not os.path.exists(vault_path):
        print(f"Error: Vault directory does not exist: {vault_path}")
        sys.exit(1)

    print(f"Using vault path: {vault_path}")

    if args.tier == "golden":
        print("Starting Golden Tier Orchestration for Personal AI Employee...")
        print("Golden Tier includes:")
        print("- Cross-domain integration (Personal + Business)")
        print("- Odoo ERP integration with JSON-RPC APIs")
        print("- Social media integrations (Facebook/Instagram/X)")
        print("- Weekly audit and CEO briefing generation")
        print("- Ralph Wiggum loop for multi-step task verification")
        print("- Enhanced error handling and logging")
        print()

        try:
            # Run the golden tier orchestration
            result = subprocess.run([
                sys.executable,
                os.path.join(vault_path, "scripts", "golden_tier.py"),
                "--vault-path", vault_path
            ], check=True)

            if result.returncode == 0:
                print("\nGolden Tier orchestration completed successfully!")
            else:
                print(f"\nGolden Tier orchestration exited with code: {result.returncode}")

        except subprocess.CalledProcessError as e:
            print(f"Error running Golden Tier orchestration: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nOrchestration interrupted by user.")
            sys.exit(0)

    elif args.tier == "silver":
        print("Starting Silver Tier Orchestration for Personal AI Employee...")
        print("- Watchers (Gmail, WhatsApp, File System)")
        print("- MCP Server for actions")
        print("- Human-in-the-loop approval system")
        print("- Automated scheduler")
        print()

        try:
            # Run the silver tier orchestration
            result = subprocess.run([
                sys.executable,
                os.path.join(vault_path, "scripts", "silver_tier.py"),
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

    elif args.tier == "bronze":
        print("Starting Bronze Tier Orchestration for Personal AI Employee...")
        print("- Basic email processing")
        print("- Simple task management")
        print("- Dashboard updates")
        print()

        try:
            # Run the bronze tier orchestration
            result = subprocess.run([
                sys.executable,
                os.path.join(vault_path, "scripts", "bronze_tier.py"),
                vault_path  # bronze tier script expects vault path as argument
            ], check=True)

            if result.returncode == 0:
                print("\nBronze Tier orchestration completed successfully!")
            else:
                print(f"\nBronze Tier orchestration exited with code: {result.returncode}")

        except subprocess.CalledProcessError as e:
            print(f"Error running Bronze Tier orchestration: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nOrchestration interrupted by user.")
            sys.exit(0)


if __name__ == "__main__":
    main()