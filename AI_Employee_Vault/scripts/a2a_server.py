#!/usr/bin/env python3
"""
A2A (Agent-to-Agent) Protocol Server
Enables real-time communication between Cloud and Local AI agents
"""

import json
import hmac
import hashlib
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from flask import Flask, request, jsonify
from threading import Thread, Lock
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class A2AServer:
    """Agent-to-Agent Protocol Server"""

    def __init__(self, agent_id: str, config: Dict[str, Any], vault_path: str):
        """
        Initialize A2A server

        Args:
            agent_id: 'cloud' or 'local'
            config: A2A configuration dictionary
            vault_path: Path to AI Employee Vault
        """
        self.agent_id = agent_id
        self.config = config
        self.vault_path = vault_path
        self.app = Flask(f'a2a_server_{agent_id}')
        self.message_handlers: Dict[str, Callable] = {}
        self.message_queue = []
        self.message_lock = Lock()
        self.secret_key = self._load_secret_key()
        self.last_heartbeat: Dict[str, datetime] = {}

        # Setup routes
        self._setup_routes()

        logger.info(f"A2A Server initialized for agent: {agent_id}")

    def _load_secret_key(self) -> str:
        """Load shared secret key from environment"""
        import os
        secret_env = self.config.get('auth', {}).get('secret_key_env', 'A2A_SECRET_KEY')
        secret = os.environ.get(secret_env)

        if not secret:
            logger.warning(f"A2A secret key not found in env var {secret_env}, using default (INSECURE)")
            secret = "default-insecure-key-change-me"

        return secret

    def _setup_routes(self):
        """Setup Flask routes for A2A endpoints"""

        @self.app.route('/a2a/v1/messages', methods=['POST'])
        def receive_message():
            """Receive A2A message"""
            try:
                # Verify signature
                signature = request.headers.get('X-Message-Signature')
                if not signature:
                    return jsonify({'error': 'Missing signature'}), 401

                message_json = request.get_data(as_text=True)
                if not self._verify_signature(message_json, signature):
                    return jsonify({'error': 'Invalid signature'}), 401

                # Parse message
                message = json.loads(message_json)

                # Validate timestamp (reject messages older than 5 minutes)
                msg_timestamp = datetime.fromisoformat(message['timestamp'].replace('Z', '+00:00'))
                if datetime.utcnow() - msg_timestamp.replace(tzinfo=None) > timedelta(minutes=5):
                    return jsonify({'error': 'Message too old'}), 400

                # Route message to handler
                message_type = message.get('type')
                handler = self.message_handlers.get(message_type)

                if handler:
                    result = handler(message)
                    return jsonify({
                        'status': 'success',
                        'message_id': message.get('message_id'),
                        'result': result
                    }), 200
                else:
                    # Queue message for later processing
                    with self.message_lock:
                        self.message_queue.append(message)

                    return jsonify({
                        'status': 'queued',
                        'message_id': message.get('message_id')
                    }), 202

            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/a2a/v1/status', methods=['GET'])
        def get_status():
            """Get agent status"""
            try:
                status = self._get_agent_status()
                return jsonify(status), 200
            except Exception as e:
                logger.error(f"Error getting status: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/a2a/v1/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'agent_id': self.agent_id,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 200

        @self.app.route('/a2a/v1/tasks', methods=['GET'])
        def list_tasks():
            """List active tasks"""
            try:
                tasks = self._get_active_tasks()
                return jsonify({'tasks': tasks}), 200
            except Exception as e:
                logger.error(f"Error listing tasks: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/a2a/v1/approvals', methods=['GET'])
        def list_approvals():
            """List pending approvals (Local agent only)"""
            if self.agent_id != 'local':
                return jsonify({'error': 'Endpoint only available on local agent'}), 403

            try:
                approvals = self._get_pending_approvals()
                return jsonify({'approvals': approvals}), 200
            except Exception as e:
                logger.error(f"Error listing approvals: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/a2a/v1/commands', methods=['POST'])
        def execute_command():
            """Execute command"""
            try:
                # Verify signature
                signature = request.headers.get('X-Message-Signature')
                if not signature:
                    return jsonify({'error': 'Missing signature'}), 401

                command_json = request.get_data(as_text=True)
                if not self._verify_signature(command_json, signature):
                    return jsonify({'error': 'Invalid signature'}), 401

                command = json.loads(command_json)
                result = self._execute_command(command)

                return jsonify({
                    'status': 'success',
                    'result': result
                }), 200

            except Exception as e:
                logger.error(f"Error executing command: {e}")
                return jsonify({'error': str(e)}), 500

    def _sign_message(self, message_json: str) -> str:
        """Sign message with HMAC-SHA256"""
        signature = hmac.new(
            self.secret_key.encode(),
            message_json.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _verify_signature(self, message_json: str, signature: str) -> bool:
        """Verify message signature"""
        expected = self._sign_message(message_json)
        return hmac.compare_digest(signature, expected)

    def register_handler(self, message_type: str, handler: Callable):
        """Register message handler for specific message type"""
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")

    def _get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        import os

        status = {
            'agent_id': self.agent_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'status': 'healthy',
            'uptime_seconds': 0,  # TODO: Track actual uptime
            'message_queue_size': len(self.message_queue),
            'registered_handlers': list(self.message_handlers.keys()),
            'vault_path': self.vault_path
        }

        return status

    def _get_active_tasks(self) -> list:
        """Get list of active tasks from In_Progress folders"""
        import os
        tasks = []

        in_progress_path = os.path.join(self.vault_path, 'In_Progress', self.agent_id)
        if os.path.exists(in_progress_path):
            for filename in os.listdir(in_progress_path):
                if filename.endswith('.md'):
                    tasks.append({
                        'task_id': filename.replace('.md', ''),
                        'filename': filename,
                        'agent': self.agent_id
                    })

        return tasks

    def _get_pending_approvals(self) -> list:
        """Get list of pending approvals (Local agent only)"""
        import os
        approvals = []

        approval_path = os.path.join(self.vault_path, 'Pending_Approval', 'local')
        if os.path.exists(approval_path):
            for filename in os.listdir(approval_path):
                if filename.endswith('.md'):
                    approvals.append({
                        'approval_id': filename.replace('.md', ''),
                        'filename': filename
                    })

        return approvals

    def _execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command"""
        cmd_type = command.get('command')

        if cmd_type == 'pause_watchers':
            # TODO: Implement watcher pause
            return {'status': 'paused', 'message': 'Watchers paused'}

        elif cmd_type == 'resume_watchers':
            # TODO: Implement watcher resume
            return {'status': 'resumed', 'message': 'Watchers resumed'}

        elif cmd_type == 'force_sync':
            # TODO: Implement force sync
            return {'status': 'synced', 'message': 'Vault sync triggered'}

        elif cmd_type == 'restart_service':
            # TODO: Implement service restart
            return {'status': 'restarting', 'message': 'Service restart initiated'}

        else:
            raise ValueError(f"Unknown command: {cmd_type}")

    def start(self, host: str = None, port: int = None, use_https: bool = False):
        """Start A2A server"""
        server_config = self.config.get('server', {})
        host = host or server_config.get('host', '127.0.0.1')
        port = port or server_config.get('port', 8090)
        use_https = use_https or server_config.get('use_https', False)

        if use_https:
            cert_path = server_config.get('cert_path')
            key_path = server_config.get('key_path')

            if not cert_path or not key_path:
                logger.error("HTTPS enabled but cert/key paths not configured")
                raise ValueError("Missing SSL certificate configuration")

            ssl_context = (cert_path, key_path)
            logger.info(f"Starting A2A server on https://{host}:{port}")
            self.app.run(host=host, port=port, ssl_context=ssl_context)
        else:
            logger.info(f"Starting A2A server on http://{host}:{port}")
            self.app.run(host=host, port=port)

    def start_background(self, host: str = None, port: int = None):
        """Start A2A server in background thread"""
        server_config = self.config.get('server', {})
        host = host or server_config.get('host', '127.0.0.1')
        port = port or server_config.get('port', 8090)

        thread = Thread(target=self.app.run, kwargs={'host': host, 'port': port}, daemon=True)
        thread.start()
        logger.info(f"A2A server started in background on http://{host}:{port}")
        return thread


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) < 3:
        print("Usage: python a2a_server.py <agent_id> <vault_path>")
        sys.exit(1)

    agent_id = sys.argv[1]  # 'cloud' or 'local'
    vault_path = sys.argv[2]

    # Load config
    import os
    config_file = f'{agent_id}_a2a_config.json'
    config_path = os.path.join(vault_path, config_file)

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f).get('a2a', {})
    else:
        # Default config
        config = {
            'server': {
                'host': '127.0.0.1' if agent_id == 'local' else '0.0.0.0',
                'port': 8090,
                'use_https': False
            }
        }

    # Create and start server
    server = A2AServer(agent_id, config, vault_path)
    server.start()
