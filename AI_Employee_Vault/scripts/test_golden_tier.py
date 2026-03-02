#!/usr/bin/env python3
"""
Test script for Golden Tier functionality.
This script tests the basic startup and initialization of Golden Tier components.
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

def test_golden_tier_startup(vault_path):
    """Test that Golden Tier components can start up properly."""
    print("Testing Golden Tier startup...")

    # Check that required directories exist
    required_dirs = [
        "Cross_Domain",
        "ERP_Integration",
        "Social_Media",
        "Audits",
        "CEO_Briefings",
        "Logs",
        "Error_Reports"
    ]

    print("\nChecking required directories...")
    all_dirs_exist = True
    for dir_name in required_dirs:
        dir_path = os.path.join(vault_path, dir_name)
        if os.path.exists(dir_path):
            print(f"  [OK] {dir_name}/ directory exists")
        else:
            print(f"  [MISSING] {dir_name}/ directory missing")
            all_dirs_exist = False

    # Check that golden_tier.py exists
    golden_tier_path = os.path.join(vault_path, "scripts", "golden_tier.py")
    if os.path.exists(golden_tier_path):
        print(f"  [OK] golden_tier.py exists")
    else:
        print(f"  [MISSING] golden_tier.py missing")
        all_dirs_exist = False

    # Check that config file exists
    config_path = os.path.join(vault_path, "golden_tier_config.json")
    if os.path.exists(config_path):
        print(f"  [OK] golden_tier_config.json exists")

        # Validate config structure
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            required_sections = ["odoo", "social_media", "cross_domain", "auditing", "ralph_wiggum_loop", "logging"]
            config_valid = True

            for section in required_sections:
                if section in config:
                    print(f"    [OK] Config section '{section}' exists")
                else:
                    print(f"    [MISSING] Config section '{section}' missing")
                    config_valid = False

            if config_valid:
                print("  [OK] Configuration file is valid")
            else:
                print("  [ERROR] Configuration file has missing sections")

        except json.JSONDecodeError:
            print("  [ERROR] Configuration file is not valid JSON")
            all_dirs_exist = False
    else:
        print(f"  [MISSING] golden_tier_config.json missing")
        all_dirs_exist = False

    if all_dirs_exist:
        print(f"\n[PASSED] Golden Tier startup test PASSED")
        print("  All required components are in place")
        print("  Run 'python main.py --tier golden' to start Golden Tier")
        return True
    else:
        print(f"\n[FAILED] Golden Tier startup test FAILED")
        print("  Some required components are missing")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_golden_tier.py <vault_path>")
        sys.exit(1)

    vault_path = sys.argv[1]

    if not os.path.exists(vault_path):
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)

    success = test_golden_tier_startup(vault_path)

    if success:
        print(f"\nGolden Tier is ready to run!")
        print(f"Command: python {os.path.join(os.path.dirname(__file__), 'main.py')} --tier golden --vault-path {vault_path}")
    else:
        print(f"\nGolden Tier is NOT ready. Please check the above issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()