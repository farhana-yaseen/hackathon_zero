#!/usr/bin/env python3
"""
Silver Tier Orchestration for Personal AI Employee

This script orchestrates all Silver Tier components:
- Watchers (Gmail, WhatsApp, File System)
- MCP Server for actions
- Human-in-the-loop approval system
- Automated scheduler
"""

import os
import sys
import threading
import time
import logging
import subprocess
import signal
import argparse
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SilverTierOrchestrator:
    def __init__(self, vault_path):
        self.vault_path = vault_path
        self.processes = []
        self.threads = []
        self.running = False

    def start_watchers(self):
        """Start all watcher processes."""
        logger.info("Starting watchers...")

        # Start run_watchers.py as a subprocess
        watcher_script = os.path.join(self.vault_path, "run_watchers.py")
        process = subprocess.Popen([sys.executable, watcher_script, self.vault_path])
        self.processes.append(process)
        logger.info("Watchers started")

    def start_mcp_server(self, port=8080):
        """Start the MCP server."""
        logger.info(f"Starting MCP server on port {port}...")

        mcp_script = os.path.join(self.vault_path, "mcp_server.py")
        env = os.environ.copy()
        env['VAULT_PATH'] = self.vault_path

        process = subprocess.Popen([
            sys.executable, mcp_script,
            "--vault-path", self.vault_path,
            "--port", str(port)
        ])
        self.processes.append(process)
        logger.info(f"MCP server started on port {port}")

    def start_scheduler(self):
        """Start the scheduler."""
        logger.info("Starting scheduler...")

        scheduler_script = os.path.join(self.vault_path, "scheduler.py")
        process = subprocess.Popen([sys.executable, scheduler_script, self.vault_path, "start"])
        self.processes.append(process)
        logger.info("Scheduler started")

    def start_orchestration(self):
        """Start all Silver Tier components."""
        logger.info("Starting Silver Tier orchestration...")

        # Create necessary directories
        os.makedirs(os.path.join(self.vault_path, "WhatsApp_Sim"), exist_ok=True)
        os.makedirs(os.path.join(self.vault_path, "Schedules"), exist_ok=True)
        os.makedirs(os.path.join(self.vault_path, "Approvals"), exist_ok=True)
        os.makedirs(os.path.join(self.vault_path, "Sent_Emails"), exist_ok=True)

        # Start all components
        self.start_watchers()
        self.start_mcp_server(port=8080)
        self.start_scheduler()

        self.running = True
        logger.info("All Silver Tier components started successfully!")

    def stop_orchestration(self):
        """Stop all Silver Tier components."""
        logger.info("Stopping Silver Tier orchestration...")

        self.running = False

        # Terminate all processes
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)  # Wait up to 5 seconds for graceful termination
            except subprocess.TimeoutExpired:
                process.kill()  # Force kill if not terminated gracefully

        self.processes.clear()
        logger.info("All Silver Tier components stopped.")

    def monitor_processes(self):
        """Monitor the health of running processes."""
        while self.running:
            for i, process in enumerate(self.processes[:]):  # Copy the list to safely modify it
                if process.poll() is not None:  # Process has terminated
                    logger.warning(f"Process {i} has terminated unexpectedly with code {process.returncode}")
                    # In a production system, you might want to restart the process
                    # For now, we'll just remove it from our tracking
                    self.processes.remove(process)

            time.sleep(5)  # Check every 5 seconds

def main():
    parser = argparse.ArgumentParser(description="Silver Tier Orchestration for Personal AI Employee")
    parser.add_argument("--vault-path", required=True, help="Path to the vault directory")
    parser.add_argument("--port", type=int, default=8080, help="Port for MCP server")

    args = parser.parse_args()

    if not os.path.exists(args.vault_path):
        print(f"Error: Vault path does not exist: {args.vault_path}")
        sys.exit(1)

    orchestrator = SilverTierOrchestrator(args.vault_path)

    def signal_handler(signum, frame):
        print("\nReceived interrupt signal. Shutting down...")
        orchestrator.stop_orchestration()
        sys.exit(0)

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start orchestration
        orchestrator.start_orchestration()

        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=orchestrator.monitor_processes, daemon=True)
        monitor_thread.start()

        print("\nSilver Tier components are running.")
        print("Press Ctrl+C to stop all components.")
        print(f"MCP Server available at: http://localhost:{args.port}/mcp")
        print(f"Vault path: {args.vault_path}")
        print()

        # Keep the main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nInterrupt received. Stopping orchestration...")
    except Exception as e:
        logger.error(f"Error in orchestration: {str(e)}")
    finally:
        orchestrator.stop_orchestration()

if __name__ == "__main__":
    main()