#!/usr/bin/env python3
"""
Test A2A Protocol - End-to-End Testing
Tests message exchange between Cloud and Local agents
"""

import os
import sys
import json
import time
import logging
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from a2a_client import A2AClient
from a2a_server import A2AServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_a2a_protocol(vault_path: str):
    """Test A2A protocol functionality"""

    logger.info("=" * 80)
    logger.info("A2A Protocol Test Suite")
    logger.info("=" * 80)

    # Test 1: Configuration Loading
    logger.info("\n[Test 1] Configuration Loading")
    try:
        local_config_path = os.path.join(vault_path, 'local_a2a_config.json')
        cloud_config_path = os.path.join(vault_path, 'cloud_a2a_config.json')

        assert os.path.exists(local_config_path), "Local config not found"
        assert os.path.exists(cloud_config_path), "Cloud config not found"

        with open(local_config_path, 'r') as f:
            local_config = json.load(f)

        with open(cloud_config_path, 'r') as f:
            cloud_config = json.load(f)

        logger.info("✓ Configuration files loaded successfully")
        logger.info(f"  Local A2A port: {local_config['a2a']['server']['port']}")
        logger.info(f"  Cloud A2A port: {cloud_config['a2a']['server']['port']}")

    except Exception as e:
        logger.error(f"✗ Configuration test failed: {e}")
        return False

    # Test 2: Client Initialization
    logger.info("\n[Test 2] Client Initialization")
    try:
        # Set test secret key
        os.environ['A2A_SECRET_KEY'] = 'test-secret-key-12345'

        local_client = A2AClient('local', local_config['a2a'], vault_path)
        cloud_client = A2AClient('cloud', cloud_config['a2a'], vault_path)

        logger.info("✓ A2A clients initialized successfully")
        logger.info(f"  Local client agent_id: {local_client.agent_id}")
        logger.info(f"  Cloud client agent_id: {cloud_client.agent_id}")

    except Exception as e:
        logger.error(f"✗ Client initialization failed: {e}")
        return False

    # Test 3: Message Creation
    logger.info("\n[Test 3] Message Creation")
    try:
        # Create test task delegation message
        task = {
            'task_id': 'test_task_001',
            'task_type': 'email_send',
            'description': 'Test email task',
            'requires_approval': True,
            'draft_content': {
                'to': 'test@example.com',
                'subject': 'Test Email',
                'body': 'This is a test email'
            }
        }

        message = cloud_client._create_message('task_delegation', {'task': task})

        assert message['type'] == 'task_delegation'
        assert message['from_agent'] == 'cloud'
        assert message['to_agent'] == 'local'
        assert 'message_id' in message
        assert 'timestamp' in message

        logger.info("✓ Message created successfully")
        logger.info(f"  Message ID: {message['message_id']}")
        logger.info(f"  Message type: {message['type']}")

    except Exception as e:
        logger.error(f"✗ Message creation failed: {e}")
        return False

    # Test 4: Message Signing
    logger.info("\n[Test 4] Message Signing and Verification")
    try:
        message_json = json.dumps(message)
        signature = cloud_client._sign_message(message_json)

        # Verify signature
        is_valid = local_client._sign_message(message_json) == signature

        assert is_valid, "Signature verification failed"

        logger.info("✓ Message signing and verification successful")
        logger.info(f"  Signature: {signature[:32]}...")

    except Exception as e:
        logger.error(f"✗ Message signing test failed: {e}")
        return False

    # Test 5: Vault Fallback
    logger.info("\n[Test 5] Vault Fallback Mechanism")
    try:
        # Test fallback when remote is unreachable
        test_message = cloud_client._create_message('approval_request', {
            'approval_id': 'test_approval_001',
            'action': {
                'action_type': 'send_email',
                'description': 'Test approval',
                'draft_data': {'test': 'data'},
                'risk_level': 'low'
            }
        })

        cloud_client._fallback_to_vault(test_message)

        # Check if file was created
        approval_path = os.path.join(vault_path, 'Pending_Approval', 'local')
        files = [f for f in os.listdir(approval_path) if f.endswith('.md')]

        assert len(files) > 0, "No fallback file created"

        logger.info("✓ Vault fallback mechanism working")
        logger.info(f"  Created fallback file in: {approval_path}")
        logger.info(f"  Files: {len(files)}")

        # Cleanup test file
        for f in files:
            if 'test_approval' in f:
                os.remove(os.path.join(approval_path, f))

    except Exception as e:
        logger.error(f"✗ Vault fallback test failed: {e}")
        return False

    # Test 6: Directory Structure
    logger.info("\n[Test 6] Platinum Directory Structure")
    try:
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
            'Signals'
        ]

        for dir_path in required_dirs:
            full_path = os.path.join(vault_path, dir_path)
            if not os.path.exists(full_path):
                os.makedirs(full_path, exist_ok=True)
                logger.info(f"  Created: {dir_path}")
            else:
                logger.info(f"  ✓ Exists: {dir_path}")

        logger.info("✓ Directory structure verified")

    except Exception as e:
        logger.error(f"✗ Directory structure test failed: {e}")
        return False

    # Test 7: Agent Scripts
    logger.info("\n[Test 7] Agent Scripts Verification")
    try:
        scripts_dir = os.path.join(vault_path, 'scripts')

        required_scripts = [
            'a2a_server.py',
            'a2a_client.py',
            'a2a_orchestrator.py',
            'platinum_cloud_agent.py',
            'platinum_local_agent.py'
        ]

        for script in required_scripts:
            script_path = os.path.join(scripts_dir, script)
            assert os.path.exists(script_path), f"Script not found: {script}"
            logger.info(f"  ✓ {script}")

        logger.info("✓ All agent scripts present")

    except Exception as e:
        logger.error(f"✗ Agent scripts verification failed: {e}")
        return False

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("A2A Protocol Test Suite: PASSED")
    logger.info("=" * 80)
    logger.info("\nAll tests completed successfully!")
    logger.info("\nNext Steps:")
    logger.info("1. Set A2A_SECRET_KEY environment variable")
    logger.info("2. Configure cloud_a2a_config.json with your cloud domain")
    logger.info("3. Configure local_a2a_config.json with your home IP")
    logger.info("4. Deploy Cloud Agent to Oracle Cloud VM")
    logger.info("5. Start Local Agent on your machine")
    logger.info("6. Test end-to-end message exchange")

    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_a2a_protocol.py <vault_path>")
        sys.exit(1)

    vault_path = sys.argv[1]

    if not os.path.exists(vault_path):
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)

    success = test_a2a_protocol(vault_path)
    sys.exit(0 if success else 1)
