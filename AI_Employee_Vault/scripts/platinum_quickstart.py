#!/usr/bin/env python3
"""
Quick Start Script for Platinum Tier
Helps users get started quickly with Platinum agents
"""

import os
import sys
import json
import subprocess

def print_header(text):
    print("\n" + "=" * 80)
    print(text.center(80))
    print("=" * 80 + "\n")

def print_section(text):
    print("\n" + "-" * 80)
    print(text)
    print("-" * 80)

def check_file(filepath, description):
    if os.path.exists(filepath):
        print(f"[OK] {description}: {filepath}")
        return True
    else:
        print(f"[FAIL] {description}: NOT FOUND - {filepath}")
        return False

def main():
    print_header("Platinum Tier - Quick Start")

    # Get vault path
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = input("Enter vault path (default: ./AI_Employee_Vault): ").strip()
        vault_path = vault_path or "./AI_Employee_Vault"

    vault_path = os.path.abspath(vault_path)

    if not os.path.exists(vault_path):
        print(f"\n✗ Error: Vault path does not exist: {vault_path}")
        sys.exit(1)

    print(f"\nVault path: {vault_path}")

    # Check prerequisites
    print_section("Checking Prerequisites")

    all_good = True

    # Check Python
    try:
        result = subprocess.run(['python', '--version'], capture_output=True, text=True)
        print(f"[OK] Python: {result.stdout.strip()}")
    except:
        print("[FAIL] Python not found")
        all_good = False

    # Check Git
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        print(f"[OK] Git: {result.stdout.strip()}")
    except:
        print("[FAIL] Git not found")
        all_good = False

    # Check required files
    print_section("Checking Platinum Tier Files")

    required_files = [
        ('scripts/a2a_server.py', 'A2A Server'),
        ('scripts/a2a_client.py', 'A2A Client'),
        ('scripts/a2a_orchestrator.py', 'A2A Orchestrator'),
        ('scripts/platinum_cloud_agent.py', 'Cloud Agent'),
        ('scripts/platinum_local_agent.py', 'Local Agent'),
        ('scripts/test_a2a_protocol.py', 'Test Suite'),
        ('local_a2a_config.json', 'Local Config'),
        ('cloud_a2a_config.json', 'Cloud Config'),
        ('A2A_PROTOCOL.md', 'Protocol Spec'),
        ('PLATINUM_README.md', 'Documentation'),
        ('.gitignore', 'Security Rules'),
    ]

    for filepath, description in required_files:
        full_path = os.path.join(vault_path, filepath)
        if not check_file(full_path, description):
            all_good = False

    # Check directory structure
    print_section("Checking Directory Structure")

    required_dirs = [
        'Needs_Action/cloud',
        'Needs_Action/local',
        'Plans/cloud',
        'Plans/local',
        'Pending_Approval/cloud',
        'Pending_Approval/local',
        'In_Progress/cloud',
        'In_Progress/local',
        'Updates',
        'Signals',
    ]

    for dir_path in required_dirs:
        full_path = os.path.join(vault_path, dir_path)
        if os.path.exists(full_path):
            print(f"[OK] {dir_path}")
        else:
            print(f"[CREATING] {dir_path}...")
            os.makedirs(full_path, exist_ok=True)

    # Check configuration
    print_section("Checking Configuration")

    env_file = os.path.join(vault_path, '.env')
    if os.path.exists(env_file):
        print("[OK] .env file exists")
        with open(env_file, 'r') as f:
            content = f.read()
            if 'A2A_SECRET_KEY' in content:
                print("  [OK] A2A_SECRET_KEY configured")
            else:
                print("  [FAIL] A2A_SECRET_KEY not found in .env")
                all_good = False
    else:
        print("[FAIL] .env file not found")
        print("  Create .env with: A2A_SECRET_KEY=your-secret-key")
        all_good = False

    # Summary
    print_section("Summary")

    if all_good:
        print("[SUCCESS] All checks passed! Ready to start Platinum Tier.")
        print("\nNext Steps:")
        print("\n1. Local Agent (Start on your machine):")
        print(f"   python main_platinum.py --mode local --vault-path {vault_path}")
        print("\n2. Cloud Agent (Deploy to Oracle Cloud VM):")
        print("   - SSH into your VM")
        print("   - Clone repository")
        print("   - Run: bash scripts/deploy_cloud_agent.sh")
        print("\n3. Test A2A Protocol:")
        print(f"   python {vault_path}/scripts/test_a2a_protocol.py {vault_path}")
        print("\n4. Documentation:")
        print(f"   - Read: {vault_path}/PLATINUM_README.md")
        print(f"   - Protocol: {vault_path}/A2A_PROTOCOL.md")
        print(f"   - Status: {vault_path}/Platinum_Status.md")
    else:
        print("[FAIL] Some checks failed. Please fix the issues above.")
        sys.exit(1)

    print_header("Setup Complete")

if __name__ == '__main__':
    main()
