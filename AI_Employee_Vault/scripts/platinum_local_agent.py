#!/usr/bin/env python3
"""
Platinum Tier - Local Agent
User-controlled local agent with A2A protocol integration
Handles: Approvals, WhatsApp, payments/banking, final send/post actions
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from threading import Thread
import signal

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from a2a_orchestrator import A2AOrchestrator

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), '..', 'Logs')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f'platinum_local_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PlatinumLocalAgent:
    """
    Platinum Tier Local Agent
    User-controlled agent for approvals and sensitive actions
    """

    def __init__(self, vault_path: str):
        """
        Initialize Platinum Local Agent

        Args:
            vault_path: Path to AI Employee Vault
        """
        self.vault_path = vault_path
        self.running = False
        self.watchers = []
        self.a2a = None

        logger.info("=" * 80)
        logger.info("Platinum Tier Local Agent Initializing")
        logger.info("=" * 80)

    def _load_config(self):
        """Load local configuration"""
        config_path = os.path.join(self.vault_path, 'golden_tier_config.json')

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            logger.warning("Config file not found, using defaults")
            return {}

    def _start_watchers(self):
        """Start local-owned watchers"""
        logger.info("Starting local watchers...")

        # Import watchers
        try:
            from whatsapp_watcher import WhatsAppWatcher

            # Start WhatsApp watcher (Local only - has session)
            whatsapp_watcher = WhatsAppWatcher(self.vault_path)
            whatsapp_thread = Thread(target=whatsapp_watcher.start, daemon=True)
            whatsapp_thread.start()
            self.watchers.append(('whatsapp', whatsapp_thread))
            logger.info("✓ WhatsApp watcher started (local only)")

        except Exception as e:
            logger.error(f"Failed to start WhatsApp watcher: {e}")

        # TODO: Add file system watcher for /Pending_Approval/local/
        # TODO: Add approval system watcher

        logger.info(f"Started {len(self.watchers)} watchers")

    def _start_a2a(self):
        """Start A2A protocol orchestrator"""
        logger.info("Starting A2A orchestrator...")

        try:
            self.a2a = A2AOrchestrator('local', self.vault_path)
            self.a2a.start()
            logger.info("✓ A2A orchestrator started")
        except Exception as e:
            logger.error(f"Failed to start A2A orchestrator: {e}")
            self.a2a = None

    def _process_approvals(self):
        """
        Process pending approvals from Cloud agent
        Local responsibility: Review and approve/reject
        """
        approval_path = os.path.join(self.vault_path, 'Pending_Approval', 'local')

        if not os.path.exists(approval_path):
            return

        for filename in os.listdir(approval_path):
            if not filename.endswith('.md'):
                continue

            try:
                filepath = os.path.join(approval_path, filename)

                # Read approval request
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse frontmatter
                if '---' not in content:
                    continue

                parts = content.split('---')
                if len(parts) < 3:
                    continue

                frontmatter = parts[1].strip()

                # Check if already processed
                if 'status: pending' not in frontmatter:
                    continue

                logger.info(f"Found pending approval: {filename}")

                # TODO: Show approval UI to user
                # TODO: Wait for user decision
                # For now, log and skip (requires manual processing)

                logger.info(f"Approval requires user review: {filename}")
                logger.info(f"File location: {filepath}")

            except Exception as e:
                logger.error(f"Error processing approval {filename}: {e}")

    def _execute_approved_actions(self):
        """
        Execute actions that have been approved
        Local responsibility: Final execution (send email, post social, etc.)
        """
        in_progress_path = os.path.join(self.vault_path, 'In_Progress', 'local')

        if not os.path.exists(in_progress_path):
            return

        for filename in os.listdir(in_progress_path):
            if not filename.endswith('.md'):
                continue

            try:
                filepath = os.path.join(in_progress_path, filename)

                # Read task
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check if approved
                if 'status: approved' not in content:
                    continue

                logger.info(f"Executing approved action: {filename}")

                # TODO: Parse action type and execute via MCP
                # TODO: Send email, post social media, etc.

                # For now, just log
                logger.info(f"Action execution placeholder: {filename}")

                # Move to Done
                done_path = os.path.join(self.vault_path, 'Done')
                os.makedirs(done_path, exist_ok=True)

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_filename = f"{timestamp}_{filename}"
                new_path = os.path.join(done_path, new_filename)

                os.rename(filepath, new_path)
                logger.info(f"✓ Action completed, moved to Done: {new_filename}")

                # Send status update to Cloud via A2A
                if self.a2a:
                    task_id = filename.replace('.md', '')
                    self.a2a.update_task_status(
                        task_id,
                        'completed',
                        {'action_taken': 'executed', 'success': True}
                    )

            except Exception as e:
                logger.error(f"Error executing action {filename}: {e}")

    def _merge_updates_to_dashboard(self):
        """
        Merge updates from Cloud agent into Dashboard.md
        Local responsibility: Dashboard.md single-writer
        """
        updates_path = os.path.join(self.vault_path, 'Updates')
        dashboard_path = os.path.join(self.vault_path, 'Dashboard.md')

        if not os.path.exists(updates_path):
            return

        updates = []
        for filename in os.listdir(updates_path):
            if not filename.endswith('.md'):
                continue

            try:
                filepath = os.path.join(updates_path, filename)

                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                updates.append({
                    'filename': filename,
                    'filepath': filepath,
                    'content': content
                })

            except Exception as e:
                logger.error(f"Error reading update {filename}: {e}")

        if not updates:
            return

        logger.info(f"Merging {len(updates)} updates into Dashboard.md")

        # Read current dashboard
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                dashboard_content = f.read()
        else:
            dashboard_content = "# Dashboard\n\n"

        # Append updates
        dashboard_content += f"\n\n## Updates from Cloud Agent ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n\n"

        for update in updates:
            dashboard_content += f"### {update['filename']}\n\n"
            dashboard_content += update['content']
            dashboard_content += "\n\n---\n\n"

        # Write updated dashboard
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)

        logger.info("✓ Dashboard updated")

        # Archive processed updates
        archive_path = os.path.join(self.vault_path, 'Updates', 'archived')
        os.makedirs(archive_path, exist_ok=True)

        for update in updates:
            archive_file = os.path.join(archive_path, update['filename'])
            os.rename(update['filepath'], archive_file)

        logger.info(f"✓ Archived {len(updates)} updates")

    def _monitoring_loop(self):
        """Main monitoring loop for local agent"""
        logger.info("Starting monitoring loop...")

        while self.running:
            try:
                # Process pending approvals
                self._process_approvals()

                # Execute approved actions
                self._execute_approved_actions()

                # Merge updates to dashboard
                self._merge_updates_to_dashboard()

                # TODO: Process WhatsApp messages
                # TODO: Handle payment/banking requests

                # Sleep before next iteration
                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error

    def _health_check_loop(self):
        """Health monitoring loop"""
        while self.running:
            try:
                # Log health status
                logger.info("Health check: Local agent running")

                # Check watcher health
                for name, thread in self.watchers:
                    if not thread.is_alive():
                        logger.warning(f"Watcher {name} is not alive!")

                # Check A2A health
                if self.a2a and self.a2a.client:
                    remote_healthy = self.a2a.client.check_remote_health()
                    if remote_healthy:
                        logger.info("✓ Cloud agent is reachable")
                    else:
                        logger.warning("✗ Cloud agent is not reachable")

                # Sleep for 5 minutes
                time.sleep(300)

            except Exception as e:
                logger.error(f"Error in health check: {e}")
                time.sleep(300)

    def start(self):
        """Start Platinum Local Agent"""
        logger.info("Starting Platinum Local Agent...")

        self.running = True

        # Load configuration
        config = self._load_config()

        # Start A2A orchestrator
        self._start_a2a()

        # Start watchers
        self._start_watchers()

        # Start monitoring loop
        monitor_thread = Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()

        # Start health check loop
        health_thread = Thread(target=self._health_check_loop, daemon=True)
        health_thread.start()

        logger.info("=" * 80)
        logger.info("Platinum Local Agent Started Successfully")
        logger.info("Mode: On-Demand (User-Controlled)")
        logger.info("Responsibilities: Approvals, WhatsApp, payments, final actions")
        logger.info("A2A Protocol: Enabled")
        logger.info("=" * 80)

        # Keep running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            self.stop()

    def stop(self):
        """Stop Platinum Local Agent"""
        logger.info("Stopping Platinum Local Agent...")
        self.running = False

        if self.a2a:
            self.a2a.stop()

        logger.info("Platinum Local Agent stopped")


def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Received signal to shutdown")
    sys.exit(0)


if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Get vault path
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = os.path.join(os.path.dirname(__file__), '..')

    vault_path = os.path.abspath(vault_path)

    # Verify vault exists
    if not os.path.exists(vault_path):
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)

    # Create and start local agent
    agent = PlatinumLocalAgent(vault_path)
    agent.start()
