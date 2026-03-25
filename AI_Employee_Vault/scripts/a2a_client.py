#!/usr/bin/env python3
"""
A2A (Agent-to-Agent) Protocol Client
Client library for sending messages between agents
"""

import json
import hmac
import hashlib
import uuid
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class A2AClient:
    """Agent-to-Agent Protocol Client"""

    def __init__(self, agent_id: str, config: Dict[str, Any], vault_path: str):
        """
        Initialize A2A client

        Args:
            agent_id: 'cloud' or 'local'
            config: A2A configuration dictionary
            vault_path: Path to AI Employee Vault
        """
        self.agent_id = agent_id
        self.config = config
        self.vault_path = vault_path
        self.secret_key = self._load_secret_key()
        self.timeout = config.get('timeouts', {}).get('message_timeout_seconds', 30)

        # Determine remote agent URL
        if agent_id == 'cloud':
            self.remote_url = config.get('local_agent', {}).get('url')
        else:
            self.remote_url = config.get('cloud_agent', {}).get('url')

        self.fallback_to_vault = config.get('cloud_agent' if agent_id == 'local' else 'local_agent', {}).get('fallback_to_vault', True)

        logger.info(f"A2A Client initialized for agent: {agent_id}")
        logger.info(f"Remote agent URL: {self.remote_url}")

    def _load_secret_key(self) -> str:
        """Load shared secret key from environment"""
        secret_env = self.config.get('auth', {}).get('secret_key_env', 'A2A_SECRET_KEY')
        secret = os.environ.get(secret_env)

        if not secret:
            logger.warning(f"A2A secret key not found in env var {secret_env}, using default (INSECURE)")
            secret = "default-insecure-key-change-me"

        return secret

    def _sign_message(self, message_json: str) -> str:
        """Sign message with HMAC-SHA256"""
        signature = hmac.new(
            self.secret_key.encode(),
            message_json.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _create_message(self, message_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create A2A message with standard fields"""
        message = {
            'type': message_type,
            'message_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'from_agent': self.agent_id,
            'to_agent': 'local' if self.agent_id == 'cloud' else 'cloud',
            **payload
        }
        return message

    def send_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send A2A message to remote agent

        Returns response dict if successful, None if failed
        Falls back to vault if enabled and remote is unreachable
        """
        try:
            # Serialize and sign message
            message_json = json.dumps(message, indent=2)
            signature = self._sign_message(message_json)

            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'X-Agent-ID': self.agent_id,
                'X-Message-Signature': signature,
                'X-Timestamp': message['timestamp']
            }

            # Send message
            url = f"{self.remote_url}/messages"
            response = requests.post(url, data=message_json, headers=headers, timeout=self.timeout)

            if response.status_code in [200, 202]:
                logger.info(f"Message sent successfully: {message['type']} (ID: {message['message_id']})")
                return response.json()
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                if self.fallback_to_vault:
                    self._fallback_to_vault(message)
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error sending message: {e}")
            if self.fallback_to_vault:
                self._fallback_to_vault(message)
            return None
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None

    def _fallback_to_vault(self, message: Dict[str, Any]):
        """Fallback to vault-based communication when A2A fails"""
        try:
            message_type = message['type']
            to_agent = message['to_agent']

            # Determine target folder based on message type
            if message_type == 'approval_request':
                folder = os.path.join(self.vault_path, 'Pending_Approval', to_agent)
            elif message_type == 'task_delegation':
                folder = os.path.join(self.vault_path, 'Needs_Action', to_agent)
            else:
                folder = os.path.join(self.vault_path, 'Updates')

            # Ensure folder exists
            os.makedirs(folder, exist_ok=True)

            # Write message to file
            filename = f"{message['message_id']}_{message_type}.md"
            filepath = os.path.join(folder, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"---\n")
                f.write(f"type: {message_type}\n")
                f.write(f"message_id: {message['message_id']}\n")
                f.write(f"from_agent: {message['from_agent']}\n")
                f.write(f"to_agent: {message['to_agent']}\n")
                f.write(f"timestamp: {message['timestamp']}\n")
                f.write(f"delivery_method: vault_fallback\n")
                f.write(f"---\n\n")
                f.write(f"# {message_type.replace('_', ' ').title()}\n\n")
                f.write(f"```json\n")
                f.write(json.dumps(message, indent=2))
                f.write(f"\n```\n")

            logger.info(f"Message written to vault (fallback): {filepath}")

        except Exception as e:
            logger.error(f"Error in vault fallback: {e}")

    # Convenience methods for specific message types

    def send_task_delegation(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send task delegation message"""
        message = self._create_message('task_delegation', {'task': task})
        return self.send_message(message)

    def send_approval_request(self, approval: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send approval request message"""
        message = self._create_message('approval_request', approval)
        return self.send_message(message)

    def send_approval_response(self, approval_id: str, decision: str,
                              modifications: Optional[Dict] = None,
                              notes: str = "") -> Optional[Dict[str, Any]]:
        """Send approval response message"""
        payload = {
            'approval_id': approval_id,
            'decision': decision,
            'notes': notes
        }
        if modifications:
            payload['modifications'] = modifications

        message = self._create_message('approval_response', payload)
        return self.send_message(message)

    def send_task_status(self, task_id: str, status: str,
                        result: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Send task status update message"""
        payload = {
            'task_id': task_id,
            'status': status
        }
        if result:
            payload['result'] = result

        message = self._create_message('task_status', payload)
        return self.send_message(message)

    def send_heartbeat(self, metrics: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Send heartbeat message"""
        payload = {
            'status': 'healthy',
            'metrics': metrics or {}
        }
        message = self._create_message('heartbeat', payload)
        return self.send_message(message)

    def send_command(self, command: str, parameters: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Send command to remote agent"""
        payload = {
            'command': command,
            'parameters': parameters or {}
        }
        message = self._create_message('command', payload)
        return self.send_message(message)

    def get_remote_status(self) -> Optional[Dict[str, Any]]:
        """Get status from remote agent"""
        try:
            url = f"{self.remote_url}/status"
            response = requests.get(url, timeout=self.timeout)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get remote status: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting remote status: {e}")
            return None

    def check_remote_health(self) -> bool:
        """Check if remote agent is healthy"""
        try:
            url = f"{self.remote_url}/health"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) < 3:
        print("Usage: python a2a_client.py <agent_id> <vault_path>")
        sys.exit(1)

    agent_id = sys.argv[1]  # 'cloud' or 'local'
    vault_path = sys.argv[2]

    # Load config
    config_file = f'{agent_id}_a2a_config.json'
    config_path = os.path.join(vault_path, config_file)

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f).get('a2a', {})
    else:
        print(f"Config file not found: {config_path}")
        sys.exit(1)

    # Create client
    client = A2AClient(agent_id, config, vault_path)

    # Test heartbeat
    print("Sending heartbeat...")
    response = client.send_heartbeat({'test': True})
    print(f"Response: {response}")

    # Check remote health
    print("\nChecking remote health...")
    is_healthy = client.check_remote_health()
    print(f"Remote agent healthy: {is_healthy}")
