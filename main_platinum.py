#!/usr/bin/env python3
"""
Main Entry Point for Platinum Tier
Supports both Cloud and Local agent modes
"""

import os
import sys
import argparse
import logging

# Add scripts directory to path
scripts_dir = os.path.join(os.path.dirname(__file__), 'AI_Employee_Vault', 'scripts')
sys.path.insert(0, scripts_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Personal AI Employee - Platinum Tier')
    parser.add_argument('--tier', type=str, default='platinum',
                       choices=['bronze', 'silver', 'golden', 'platinum'],
                       help='Tier to run (default: platinum)')
    parser.add_argument('--mode', type=str, default='local',
                       choices=['cloud', 'local'],
                       help='Agent mode: cloud (always-on) or local (on-demand)')
    parser.add_argument('--vault-path', type=str, default='AI_Employee_Vault',
                       help='Path to AI Employee Vault')

    args = parser.parse_args()

    # Resolve vault path
    vault_path = os.path.abspath(args.vault_path)

    if not os.path.exists(vault_path):
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)

    logger.info(f"Starting AI Employee - Tier: {args.tier}, Mode: {args.mode}")
    logger.info(f"Vault path: {vault_path}")

    # Route to appropriate tier
    if args.tier == 'platinum':
        run_platinum_tier(args.mode, vault_path)
    elif args.tier == 'golden':
        run_golden_tier(vault_path)
    elif args.tier == 'silver':
        run_silver_tier(vault_path)
    elif args.tier == 'bronze':
        run_bronze_tier(vault_path)
    else:
        logger.error(f"Unknown tier: {args.tier}")
        sys.exit(1)


def run_platinum_tier(mode: str, vault_path: str):
    """Run Platinum Tier agent"""
    logger.info("=" * 80)
    logger.info("PLATINUM TIER - Phase 2: A2A Protocol")
    logger.info("=" * 80)

    if mode == 'cloud':
        logger.info("Starting Cloud Agent (Always-On)")
        from platinum_cloud_agent import PlatinumCloudAgent
        agent = PlatinumCloudAgent(vault_path)
        agent.start()

    elif mode == 'local':
        logger.info("Starting Local Agent (On-Demand)")
        from platinum_local_agent import PlatinumLocalAgent
        agent = PlatinumLocalAgent(vault_path)
        agent.start()

    else:
        logger.error(f"Unknown mode: {mode}")
        sys.exit(1)


def run_golden_tier(vault_path: str):
    """Run Golden Tier"""
    logger.info("Starting Golden Tier...")
    from golden_tier import run_golden_tier as run_golden
    run_golden(vault_path)


def run_silver_tier(vault_path: str):
    """Run Silver Tier"""
    logger.info("Starting Silver Tier...")
    from silver_tier import run_silver_tier as run_silver
    run_silver(vault_path)


def run_bronze_tier(vault_path: str):
    """Run Bronze Tier"""
    logger.info("Starting Bronze Tier...")
    from gmail_watcher import GmailWatcher
    watcher = GmailWatcher(vault_path)
    watcher.start()


if __name__ == '__main__':
    main()
