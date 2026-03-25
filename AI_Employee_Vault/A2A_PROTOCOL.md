---
protocol: A2A (Agent-to-Agent)
version: 1.0
tier: platinum_phase2
---

# A2A Protocol Specification

## Overview

The Agent-to-Agent (A2A) Protocol enables real-time communication between Cloud and Local AI agents using HTTP-based messaging with MCP tool integration.

---

## Architecture

```
┌─────────────────┐         HTTPS/HTTP          ┌─────────────────┐
│  Cloud Agent    │◄──────────────────────────►│  Local Agent    │
│  (Always-On)    │    A2A Protocol Messages    │  (On-Demand)    │
└─────────────────┘                             └─────────────────┘
        │                                                │
        │ Fallback: Vault Sync (Git)                   │
        └────────────────────────────────────────────────┘
```

---

## Message Types

### 1. Task Delegation
**Cloud → Local**: Delegate task requiring approval/execution

```json
{
  "type": "task_delegation",
  "message_id": "uuid-v4",
  "timestamp": "2026-03-26T10:30:00Z",
  "from_agent": "cloud",
  "to_agent": "local",
  "priority": "high|medium|low",
  "task": {
    "task_id": "task_uuid",
    "task_type": "email_send|whatsapp_send|payment|social_post",
    "description": "Send email reply to client",
    "requires_approval": true,
    "draft_content": {
      "to": "client@example.com",
      "subject": "Re: Project Update",
      "body": "Draft email content..."
    },
    "context": {
      "original_email_id": "email_123",
      "urgency": "high",
      "deadline": "2026-03-26T18:00:00Z"
    }
  }
}
```

### 2. Task Status Update
**Local → Cloud**: Update task status

```json
{
  "type": "task_status",
  "message_id": "uuid-v4",
  "timestamp": "2026-03-26T10:35:00Z",
  "from_agent": "local",
  "to_agent": "cloud",
  "task_id": "task_uuid",
  "status": "approved|rejected|completed|failed|in_progress",
  "result": {
    "action_taken": "email_sent",
    "success": true,
    "details": "Email sent successfully at 10:35 AM"
  }
}
```

### 3. Approval Request
**Cloud → Local**: Request approval for action

```json
{
  "type": "approval_request",
  "message_id": "uuid-v4",
  "timestamp": "2026-03-26T10:30:00Z",
  "from_agent": "cloud",
  "to_agent": "local",
  "approval_id": "approval_uuid",
  "action": {
    "action_type": "send_email|post_social|create_invoice|make_payment",
    "description": "Send draft email reply",
    "draft_data": { /* action-specific data */ },
    "risk_level": "low|medium|high",
    "estimated_impact": "Responds to client inquiry"
  },
  "requires_response_by": "2026-03-26T12:00:00Z"
}
```

### 4. Approval Response
**Local → Cloud**: Respond to approval request

```json
{
  "type": "approval_response",
  "message_id": "uuid-v4",
  "timestamp": "2026-03-26T10:40:00Z",
  "from_agent": "local",
  "to_agent": "cloud",
  "approval_id": "approval_uuid",
  "decision": "approved|rejected|modified",
  "modifications": { /* if decision is 'modified' */ },
  "notes": "Approved with minor edits to tone"
}
```

### 5. Heartbeat
**Bidirectional**: Agent health check

```json
{
  "type": "heartbeat",
  "message_id": "uuid-v4",
  "timestamp": "2026-03-26T10:30:00Z",
  "from_agent": "cloud|local",
  "status": "healthy|degraded|error",
  "metrics": {
    "uptime_seconds": 86400,
    "active_tasks": 5,
    "pending_approvals": 2,
    "error_count_24h": 0
  }
}
```

### 6. Sync Request
**Bidirectional**: Request vault sync

```json
{
  "type": "sync_request",
  "message_id": "uuid-v4",
  "timestamp": "2026-03-26T10:30:00Z",
  "from_agent": "cloud|local",
  "sync_scope": "full|incremental|specific_folders",
  "folders": ["/Needs_Action", "/Pending_Approval"]
}
```

### 7. Command
**Bidirectional**: Execute command on remote agent

```json
{
  "type": "command",
  "message_id": "uuid-v4",
  "timestamp": "2026-03-26T10:30:00Z",
  "from_agent": "local",
  "to_agent": "cloud",
  "command": "pause_watchers|resume_watchers|force_sync|restart_service",
  "parameters": {}
}
```

---

## HTTP Endpoints

### Cloud Agent Endpoints
**Base URL**: `https://cloud-agent.example.com/a2a/v1`

- `POST /messages` - Receive A2A messages
- `GET /status` - Get agent status
- `GET /tasks` - List active tasks
- `POST /commands` - Execute commands
- `GET /health` - Health check endpoint

### Local Agent Endpoints
**Base URL**: `http://localhost:8090/a2a/v1`

- `POST /messages` - Receive A2A messages
- `GET /status` - Get agent status
- `GET /approvals` - List pending approvals
- `POST /commands` - Execute commands
- `GET /health` - Health check endpoint

---

## Authentication

### Shared Secret Method
- Both agents share a pre-configured secret key
- Each message includes HMAC signature
- Signature verified on receipt

```python
import hmac
import hashlib

def sign_message(message_json, secret_key):
    signature = hmac.new(
        secret_key.encode(),
        message_json.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature

def verify_signature(message_json, signature, secret_key):
    expected = sign_message(message_json, secret_key)
    return hmac.compare_digest(signature, expected)
```

### Request Headers
```
Content-Type: application/json
X-Agent-ID: cloud|local
X-Message-Signature: <hmac-sha256-hex>
X-Timestamp: <iso8601-timestamp>
```

---

## Fallback Behavior

### When Local Agent is Offline
1. Cloud agent sends message via HTTP
2. If connection fails, Cloud writes to `/Pending_Approval/local/`
3. Cloud writes notification to `/Updates/`
4. When Local comes online, processes vault files first
5. Local sends status updates via A2A when available

### When Cloud Agent is Offline
1. Local agent sends message via HTTP
2. If connection fails, Local writes to `/Needs_Action/cloud/`
3. When Cloud comes online, processes vault files first
4. Cloud sends acknowledgment via A2A when available

---

## Message Flow Examples

### Example 1: Email Draft Approval (Real-Time)

```
1. Cloud detects email → drafts reply
2. Cloud → Local: approval_request (A2A)
3. Local shows approval UI to user
4. User approves
5. Local → Cloud: approval_response (A2A)
6. Local executes send via MCP
7. Local → Cloud: task_status (A2A, completed)
8. Cloud logs completion
```

### Example 2: Email Draft Approval (Local Offline)

```
1. Cloud detects email → drafts reply
2. Cloud → Local: approval_request (A2A) → FAILS
3. Cloud writes to /Pending_Approval/local/email_draft_123.md
4. Cloud writes to /Updates/email_draft_notification.md
5. [Local comes online]
6. Local reads /Pending_Approval/local/
7. User approves
8. Local executes send via MCP
9. Local → Cloud: task_status (A2A, completed)
10. Cloud logs completion
```

---

## Security Rules

1. **Never transmit secrets**: Credentials, tokens, sessions stay local
2. **HTTPS only for Cloud**: Cloud agent must use TLS
3. **Localhost only for Local**: Local agent binds to 127.0.0.1
4. **Message signing**: All messages must be signed with HMAC
5. **Timestamp validation**: Reject messages older than 5 minutes
6. **Rate limiting**: Max 100 messages/minute per agent
7. **Message size limit**: Max 10MB per message

---

## Implementation Priority

### Phase 2.1: Core A2A Server
- [ ] A2A message server (HTTP endpoints)
- [ ] Message signing and verification
- [ ] Message queue and routing
- [ ] Heartbeat mechanism

### Phase 2.2: Task Delegation
- [ ] Task delegation messages
- [ ] Approval request/response flow
- [ ] Task status tracking
- [ ] Fallback to vault sync

### Phase 2.3: Advanced Features
- [ ] Command execution
- [ ] Real-time notifications
- [ ] Message persistence
- [ ] Conflict resolution

---

## Configuration

### Cloud Agent Config (`cloud_a2a_config.json`)
```json
{
  "a2a": {
    "enabled": true,
    "server": {
      "host": "0.0.0.0",
      "port": 8090,
      "use_https": true,
      "cert_path": "/etc/letsencrypt/live/domain/fullchain.pem",
      "key_path": "/etc/letsencrypt/live/domain/privkey.pem"
    },
    "local_agent": {
      "url": "http://user-home-ip:8090/a2a/v1",
      "fallback_to_vault": true
    },
    "auth": {
      "secret_key_env": "A2A_SECRET_KEY"
    },
    "timeouts": {
      "message_timeout_seconds": 30,
      "heartbeat_interval_seconds": 60
    }
  }
}
```

### Local Agent Config (`local_a2a_config.json`)
```json
{
  "a2a": {
    "enabled": true,
    "server": {
      "host": "127.0.0.1",
      "port": 8090,
      "use_https": false
    },
    "cloud_agent": {
      "url": "https://cloud-agent.example.com/a2a/v1",
      "fallback_to_vault": true
    },
    "auth": {
      "secret_key_env": "A2A_SECRET_KEY"
    },
    "timeouts": {
      "message_timeout_seconds": 30,
      "heartbeat_interval_seconds": 300
    }
  }
}
```

---

**Protocol Version**: 1.0
**Status**: Specification Complete
**Next**: Implementation
