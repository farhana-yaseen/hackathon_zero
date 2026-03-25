#!/usr/bin/env python3
"""
A2A Orchestrator - Integrates A2A protocol with AI Employee agents
Handles message routing, task delegation, and approval workflows
"""

import json
import os
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from threading import Thread
import sys

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from a2a_server import A2AServer
from a2a_client import A2AClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class A2AOrchestrator:
    """
    Orchestrates A2A communication for Cloud or Local agent
    Integrates with existing AI Employee infrastructure
    """

    def __init__(self, agent_id: str, vault_path: str, config_path: Optional[str] = None):
        """
        Initialize A2A Orchestrator

        Args:
            agent_id: 'cloud' or 'local'
            vault_path: Path to AI Employee Vault
            config_path: Optional path to config file
        """
        self.agent_id = agent_id
        self.vault_path = vault_path
        self.config = self._load_config(config_path)

        # Initialize A2A server and client
        self.server = A2AServer(agent_id, self.config, vault_path)
        self.client = A2AClient(agent_id, self.config, vault_path)

        # Register message handlers
        self._register_handlers()

        # Heartbeat thread
        self.heartbeat_thread = None
        self.running = False

        logger.info(f"A2A Orchestrator initialized for {agent_id} agent")

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load A2A configuration"""
        if not config_path:
            config_path = os.path.join(self.vault_path, f'{self.agent_id}_a2a_config.json')

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f).get('a2a', {})
                logger.info(f"Loaded config from {config_path}")
                return config
        else:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'server': {
                'host': '127.0.0.1' if self.agent_id == 'local' else '0.0.0.0',
                'port': 8090,
                'use_https': False
            },
            'timeouts': {
                'heartbeat_interval_seconds': 60 if self.agent_id == 'cloud' else 300
            }
        }

    def _register_handlers(self):
        """Register message handlers for different message types"""

        # Task delegation handler
        self.server.register_handler('task_delegation', self._handle_task_delegation)

        # Approval request handler
        self.server.register_handler('approval_request', self._handle_approval_request)

        # Approval response handler
        self.server.register_handler('approval_response', self._handle_approval_response)

        # Task status handler
        self.server.register_handler('task_status', self._handle_task_status)

        # Heartbeat handler
        self.server.register_handler('heartbeat', self._handle_heartbeat)

        # Command handler
        self.server.register_handler('command', self._handle_command)

        logger.info("Message handlers registered")

    # Message Handlers

    def _handle_task_delegation(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming task delegation"""
        try:
            task = message.get('task', {})
            task_id = task.get('task_id')

            logger.info(f"Received task delegation: {task_id}")

            # Write task to Needs_Action folder
            needs_action_path = os.path.join(
                self.vault_path,
                'Needs_Action',
                self.agent_id
            )
            os.makedirs(needs_action_path, exist_ok=True)

            task_file = os.path.join(needs_action_path, f"{task_id}.md")

            with open(task_file, 'w', encoding='utf-8') as f:
                f.write(f"---\n")
                f.write(f"task_id: {task_id}\n")
                f.write(f"task_type: {task.get('task_type')}\n")
                f.write(f"from_agent: {message.get('from_agent')}\n")
                f.write(f"priority: {message.get('priority', 'medium')}\n")
                f.write(f"timestamp: {message.get('timestamp')}\n")
                f.write(f"requires_approval: {task.get('requires_approval', False)}\n")
                f.write(f"---\n\n")
                f.write(f"# Task: {task.get('description')}\n\n")
                f.write(f"## Details\n\n")
                f.write(f"```json\n")
                f.write(json.dumps(task, indent=2))
                f.write(f"\n```\n")

            logger.info(f"Task written to: {task_file}")

            return {
                'status': 'accepted',
                'task_id': task_id,
                'file_path': task_file
            }

        except Exception as e:
            logger.error(f"Error handling task delegation: {e}")
            return {'status': 'error', 'message': str(e)}

    def _handle_approval_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming approval request"""
        try:
            approval_id = message.get('approval_id')
            action = message.get('action', {})

            logger.info(f"Received approval request: {approval_id}")

            # Write approval request to Pending_Approval folder
            approval_path = os.path.join(
                self.vault_path,
                'Pending_Approval',
                self.agent_id
            )
            os.makedirs(approval_path, exist_ok=True)

            approval_file = os.path.join(approval_path, f"{approval_id}.md")

            with open(approval_file, 'w', encoding='utf-8') as f:
                f.write(f"---\n")
                f.write(f"approval_id: {approval_id}\n")
                f.write(f"action_type: {action.get('action_type')}\n")
                f.write(f"from_agent: {message.get('from_agent')}\n")
                f.write(f"risk_level: {action.get('risk_level', 'medium')}\n")
                f.write(f"timestamp: {message.get('timestamp')}\n")
                f.write(f"requires_response_by: {message.get('requires_response_by', 'N/A')}\n")
                f.write(f"status: pending\n")
                f.write(f"---\n\n")
                f.write(f"# Approval Request: {action.get('description')}\n\n")
                f.write(f"## Action Details\n\n")
                f.write(f"**Type**: {action.get('action_type')}\n\n")
                f.write(f"**Risk Level**: {action.get('risk_level')}\n\n")
                f.write(f"**Estimated Impact**: {action.get('estimated_impact')}\n\n")
                f.write(f"## Draft Data\n\n")
                f.write(f"```json\n")
                f.write(json.dumps(action.get('draft_data', {}), indent=2))
                f.write(f"\n```\n\n")
                f.write(f"## Instructions\n\n")
                f.write(f"To approve: Move this file to `/In_Progress/local/` and update status to 'approved'\n\n")
                f.write(f"To reject: Update status to 'rejected' and add notes\n\n")
                f.write(f"To modify: Update draft_data and set status to 'modified'\n")

            logger.info(f"Approval request written to: {approval_file}")

            # TODO: Trigger notification (sound, desktop notification, etc.)

            return {
                'status': 'received',
                'approval_id': approval_id,
                'file_path': approval_file
            }

        except Exception as e:
            logger.error(f"Error handling approval request: {e}")
            return {'status': 'error', 'message': str(e)}

    def _handle_approval_response(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming approval response"""
        try:
            approval_id = message.get('approval_id')
            decision = message.get('decision')

            logger.info(f"Received approval response: {approval_id} - {decision}")

            # Write response to Updates folder
            updates_path = os.path.join(self.vault_path, 'Updates')
            os.makedirs(updates_path, exist_ok=True)

            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            response_file = os.path.join(updates_path, f"{timestamp}_approval_{approval_id}.md")

            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(f"---\n")
                f.write(f"type: approval_response\n")
                f.write(f"approval_id: {approval_id}\n")
                f.write(f"decision: {decision}\n")
                f.write(f"from_agent: {message.get('from_agent')}\n")
                f.write(f"timestamp: {message.get('timestamp')}\n")
                f.write(f"---\n\n")
                f.write(f"# Approval Response: {decision.upper()}\n\n")
                f.write(f"**Approval ID**: {approval_id}\n\n")
                f.write(f"**Decision**: {decision}\n\n")
                f.write(f"**Notes**: {message.get('notes', 'None')}\n\n")

                if message.get('modifications'):
                    f.write(f"## Modifications\n\n")
                    f.write(f"```json\n")
                    f.write(json.dumps(message.get('modifications'), indent=2))
                    f.write(f"\n```\n")

            logger.info(f"Approval response written to: {response_file}")

            return {
                'status': 'processed',
                'approval_id': approval_id,
                'decision': decision
            }

        except Exception as e:
            logger.error(f"Error handling approval response: {e}")
            return {'status': 'error', 'message': str(e)}

    def _handle_task_status(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming task status update"""
        try:
            task_id = message.get('task_id')
            status = message.get('status')

            logger.info(f"Received task status update: {task_id} - {status}")

            # Write status update to Updates folder
            updates_path = os.path.join(self.vault_path, 'Updates')
            os.makedirs(updates_path, exist_ok=True)

            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            status_file = os.path.join(updates_path, f"{timestamp}_task_{task_id}.md")

            with open(status_file, 'w', encoding='utf-8') as f:
                f.write(f"---\n")
                f.write(f"type: task_status\n")
                f.write(f"task_id: {task_id}\n")
                f.write(f"status: {status}\n")
                f.write(f"from_agent: {message.get('from_agent')}\n")
                f.write(f"timestamp: {message.get('timestamp')}\n")
                f.write(f"---\n\n")
                f.write(f"# Task Status Update: {status.upper()}\n\n")
                f.write(f"**Task ID**: {task_id}\n\n")
                f.write(f"**Status**: {status}\n\n")

                result = message.get('result')
                if result:
                    f.write(f"## Result\n\n")
                    f.write(f"```json\n")
                    f.write(json.dumps(result, indent=2))
                    f.write(f"\n```\n")

            logger.info(f"Task status written to: {status_file}")

            return {
                'status': 'acknowledged',
                'task_id': task_id
            }

        except Exception as e:
            logger.error(f"Error handling task status: {e}")
            return {'status': 'error', 'message': str(e)}

    def _handle_heartbeat(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming heartbeat"""
        from_agent = message.get('from_agent')
        logger.debug(f"Received heartbeat from {from_agent}")

        # Update last heartbeat timestamp
        self.server.last_heartbeat[from_agent] = datetime.utcnow()

        return {
            'status': 'alive',
            'agent_id': self.agent_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    def _handle_command(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming command"""
        command = message.get('command')
        logger.info(f"Received command: {command}")

        # Delegate to server's command handler
        return self.server._execute_command(message)

    # Heartbeat Management

    def _heartbeat_loop(self):
        """Send periodic heartbeats to remote agent"""
        interval = self.config.get('timeouts', {}).get('heartbeat_interval_seconds', 60)

        while self.running:
            try:
                # Check if remote is healthy
                is_healthy = self.client.check_remote_health()

                if is_healthy:
                    # Send heartbeat
                    metrics = {
                        'uptime_seconds': int(time.time()),  # TODO: Track actual uptime
                        'active_tasks': len(self.server._get_active_tasks()),
                        'message_queue_size': len(self.server.message_queue)
                    }

                    self.client.send_heartbeat(metrics)
                    logger.debug(f"Heartbeat sent to remote agent")
                else:
                    logger.warning(f"Remote agent not healthy, skipping heartbeat")

            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")

            # Sleep until next heartbeat
            time.sleep(interval)

    # Public Methods

    def start(self):
        """Start A2A orchestrator"""
        logger.info(f"Starting A2A orchestrator for {self.agent_id} agent")

        self.running = True

        # Start A2A server in background
        self.server.start_background()

        # Start heartbeat thread
        self.heartbeat_thread = Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()

        logger.info("A2A orchestrator started successfully")

    def stop(self):
        """Stop A2A orchestrator"""
        logger.info("Stopping A2A orchestrator")
        self.running = False

        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)

        logger.info("A2A orchestrator stopped")

    # Convenience methods for sending messages

    def delegate_task(self, task: Dict[str, Any]) -> bool:
        """Delegate task to remote agent"""
        response = self.client.send_task_delegation(task)
        return response is not None

    def request_approval(self, action: Dict[str, Any], approval_id: str = None) -> bool:
        """Request approval from remote agent"""
        if not approval_id:
            import uuid
            approval_id = str(uuid.uuid4())

        approval = {
            'approval_id': approval_id,
            'action': action
        }

        response = self.client.send_approval_request(approval)
        return response is not None

    def send_approval_decision(self, approval_id: str, decision: str,
                              modifications: Dict = None, notes: str = "") -> bool:
        """Send approval decision to remote agent"""
        response = self.client.send_approval_response(
            approval_id, decision, modifications, notes
        )
        return response is not None

    def update_task_status(self, task_id: str, status: str, result: Dict = None) -> bool:
        """Update task status to remote agent"""
        response = self.client.send_task_status(task_id, status, result)
        return response is not None


if __name__ == '__main__':
    # Example usage
    if len(sys.argv) < 3:
        print("Usage: python a2a_orchestrator.py <agent_id> <vault_path>")
        sys.exit(1)

    agent_id = sys.argv[1]  # 'cloud' or 'local'
    vault_path = sys.argv[2]

    # Create and start orchestrator
    orchestrator = A2AOrchestrator(agent_id, vault_path)
    orchestrator.start()

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        orchestrator.stop()
        print("\nOrchestrator stopped")
