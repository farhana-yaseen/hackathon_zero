---
type: approval_request
message_id: 6df1e9ed-9cc4-4241-9c59-707da3e307d0
from_agent: cloud
to_agent: local
timestamp: 2026-03-25T21:31:43.240335Z
delivery_method: vault_fallback
---

# Approval Request

```json
{
  "type": "approval_request",
  "message_id": "6df1e9ed-9cc4-4241-9c59-707da3e307d0",
  "timestamp": "2026-03-25T21:31:43.240335Z",
  "from_agent": "cloud",
  "to_agent": "local",
  "approval_id": "test_approval_001",
  "action": {
    "action_type": "send_email",
    "description": "Test approval",
    "draft_data": {
      "test": "data"
    },
    "risk_level": "low"
  }
}
```
