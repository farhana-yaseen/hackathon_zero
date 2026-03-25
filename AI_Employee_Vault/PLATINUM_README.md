# Platinum Tier - Complete Implementation Guide

## Overview

**Platinum Tier** is the production-grade AI Employee with:
- **Always-on Cloud Agent** running 24/7 on Oracle Cloud
- **On-demand Local Agent** for approvals and sensitive actions
- **A2A Protocol** for real-time agent communication
- **Vault-based delegation** with Git sync fallback
- **Work-zone specialization** for security and efficiency

---

## Quick Start

### Prerequisites
- Python 3.11+
- Git
- Oracle Cloud account (free tier)
- Domain name (optional, for HTTPS)

### Local Agent Setup (5 minutes)

```bash
# 1. Navigate to vault
cd AI_Employee_Vault

# 2. Run setup script
bash scripts/setup_local_agent.sh

# 3. Start local agent
python ../main_platinum.py --mode local --vault-path .
```

### Cloud Agent Deployment (15 minutes)

```bash
# 1. SSH into Oracle Cloud VM
ssh ubuntu@<VM_IP>

# 2. Clone repository
git clone <YOUR_REPO_URL> AI_Employee_Vault
cd AI_Employee_Vault

# 3. Run deployment script
bash scripts/deploy_cloud_agent.sh

# 4. Service starts automatically
sudo systemctl status platinum-cloud-agent
```

---

## Architecture

### Work-Zone Specialization

**Cloud Agent Responsibilities:**
- ✓ Email triage and draft replies
- ✓ Social media post drafts
- ✓ Draft accounting actions (Odoo)
- ✓ 24/7 monitoring
- ✗ NO access to: WhatsApp sessions, banking, payment tokens

**Local Agent Responsibilities:**
- ✓ Approval workflows
- ✓ WhatsApp session management
- ✓ Banking and payment execution
- ✓ Final send/post actions
- ✓ Dashboard.md updates

### Communication Flow

```
Cloud Agent                    Local Agent
    │                              │
    ├─ Detects email              │
    ├─ Drafts reply               │
    │                              │
    ├─ A2A: approval_request ────►│
    │                              ├─ Shows to user
    │                              ├─ User approves
    │◄──── A2A: approval_response─┤
    │                              │
    │                              ├─ Executes send
    │◄──── A2A: task_status ──────┤
    │                              │
    ├─ Logs completion            ├─ Moves to /Done/
```

---

## Directory Structure

```
AI_Employee_Vault/
├── Needs_Action/
│   ├── cloud/          ← Cloud agent work items
│   └── local/          ← Local agent work items
├── Plans/
│   ├── cloud/
│   └── local/
├── Pending_Approval/
│   ├── cloud/
│   └── local/          ← Approval requests for user
├── In_Progress/
│   ├── cloud/          ← Cloud agent claimed tasks
│   └── local/          ← Local agent claimed tasks
├── Updates/            ← Cloud writes updates here
├── Signals/            ← Agent coordination signals
├── Done/               ← Completed tasks
├── Dashboard.md        ← Local agent updates (single-writer)
├── Platinum_Status.md  ← Platinum tier status
├── A2A_PROTOCOL.md     ← Protocol specification
├── local_a2a_config.json
├── cloud_a2a_config.json
├── .gitignore          ← Security rules
└── scripts/
    ├── a2a_server.py
    ├── a2a_client.py
    ├── a2a_orchestrator.py
    ├── platinum_cloud_agent.py
    ├── platinum_local_agent.py
    ├── test_a2a_protocol.py
    ├── setup_local_agent.sh
    └── deploy_cloud_agent.sh
```

---

## Security

### Secrets Management

**NEVER synced to Git:**
- `.env` files
- `token.pickle` (Gmail)
- `credentials.json` (OAuth)
- `*token*.json` (all tokens)
- `WhatsApp_Session/` (session data)
- `banking_credentials.json`
- `payment_tokens.json`

**Synced to Git:**
- `*.md` files (all markdown)
- Configuration files (no secrets)
- Task files in work folders
- Plans and updates

### Authentication

**A2A Protocol:**
- HMAC-SHA256 message signing
- Shared secret key (A2A_SECRET_KEY)
- Timestamp validation (5-minute window)
- HTTPS for cloud agent

**Git Sync:**
- SSH keys or personal access tokens
- Automatic sync every 5 minutes (cloud)
- Manual or scheduled sync (local)

---

## Configuration

### Environment Variables

Create `.env` in vault root:

```bash
# A2A Protocol (REQUIRED)
A2A_SECRET_KEY=your-32-char-secret-key-here

# Gmail API (if using)
GOOGLE_APPLICATION_CREDENTIALS=credentials.json

# Vault Path
VAULT_PATH=/path/to/AI_Employee_Vault

# Logging
LOG_LEVEL=INFO
```

### Local Agent Config

Edit `local_a2a_config.json`:

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
      "url": "https://your-domain.com/a2a/v1",
      "fallback_to_vault": true
    }
  }
}
```

### Cloud Agent Config

Edit `cloud_a2a_config.json`:

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
      "url": "http://YOUR_HOME_IP:8090/a2a/v1",
      "fallback_to_vault": true
    }
  }
}
```

---

## Deployment

### Oracle Cloud VM Setup

1. **Create Free Tier Account:**
   - Go to https://cloud.oracle.com
   - Sign up for free tier (no credit card required)

2. **Launch VM Instance:**
   - Compute → Instances → Create Instance
   - Image: Ubuntu 22.04
   - Shape: VM.Standard.E2.1.Micro (Always Free)
   - Add SSH key
   - Note public IP address

3. **Configure Firewall:**
   ```bash
   # On Oracle Cloud Console
   Networking → Virtual Cloud Networks → Security Lists
   Add Ingress Rule: Port 8090, Source: 0.0.0.0/0
   ```

4. **SSH and Deploy:**
   ```bash
   ssh ubuntu@<VM_PUBLIC_IP>
   git clone <YOUR_REPO> AI_Employee_Vault
   cd AI_Employee_Vault
   bash scripts/deploy_cloud_agent.sh
   ```

### Git Repository Setup

1. **Create Private Repository:**
   - GitHub, GitLab, or Bitbucket
   - Make it PRIVATE (contains work data)

2. **Initialize Vault:**
   ```bash
   cd AI_Employee_Vault
   git init
   git add .
   git commit -m "Initial Platinum setup"
   git remote add origin <YOUR_REPO_URL>
   git push -u origin master
   ```

3. **Configure Both Agents:**
   ```bash
   # Cloud VM
   cd AI_Employee_Vault
   git config user.email "cloud@example.com"
   git config user.name "Cloud Agent"

   # Local Machine
   cd AI_Employee_Vault
   git config user.email "local@example.com"
   git config user.name "Local Agent"
   ```

---

## Testing

### Run Test Suite

```bash
cd AI_Employee_Vault/scripts
python test_a2a_protocol.py ../
```

**Expected Output:**
```
[Test 1] Configuration Loading ✓
[Test 2] Client Initialization ✓
[Test 3] Message Creation ✓
[Test 4] Message Signing and Verification ✓
[Test 5] Vault Fallback Mechanism ✓
[Test 6] Platinum Directory Structure ✓
[Test 7] Agent Scripts Verification ✓

A2A Protocol Test Suite: PASSED
```

### Demo Workflow

**Scenario:** Email arrives while Local is offline

1. **Start Cloud Agent:**
   ```bash
   # On cloud VM
   sudo systemctl start platinum-cloud-agent
   sudo journalctl -u platinum-cloud-agent -f
   ```

2. **Send Test Email:**
   - Send email to your Gmail account
   - Cloud agent detects and drafts reply

3. **Check Approval Request:**
   ```bash
   # Cloud writes to vault
   ls AI_Employee_Vault/Pending_Approval/local/
   # Should see: email_<id>_approval.md
   ```

4. **Start Local Agent:**
   ```bash
   # On your machine
   python main_platinum.py --mode local
   ```

5. **Approve Draft:**
   - Local agent detects approval request
   - Review draft in `/Pending_Approval/local/`
   - Move to `/In_Progress/local/` and update status to 'approved'

6. **Verify Send:**
   - Local agent executes send
   - Moves to `/Done/`
   - Sends status update to Cloud

7. **Check Logs:**
   ```bash
   # Cloud
   tail -f AI_Employee_Vault/Logs/platinum_cloud_*.log

   # Local
   tail -f AI_Employee_Vault/Logs/platinum_local_*.log
   ```

---

## Monitoring

### Health Checks

```bash
# Cloud agent health
curl https://your-domain.com/a2a/v1/health

# Local agent health
curl http://localhost:8090/a2a/v1/health
```

### Service Management

```bash
# Cloud VM
sudo systemctl start platinum-cloud-agent
sudo systemctl stop platinum-cloud-agent
sudo systemctl restart platinum-cloud-agent
sudo systemctl status platinum-cloud-agent

# View logs
sudo journalctl -u platinum-cloud-agent -f
```

### Git Sync Status

```bash
# Check sync status
cd AI_Employee_Vault
git status
git log --oneline -10

# Manual sync
git pull
git add -A
git commit -m "Manual sync"
git push
```

---

## Troubleshooting

### Cloud Agent Not Starting

```bash
# Check service status
sudo systemctl status platinum-cloud-agent

# Check logs
sudo journalctl -u platinum-cloud-agent -n 50

# Restart service
sudo systemctl restart platinum-cloud-agent
```

### A2A Connection Failed

```bash
# Test connectivity
curl https://your-domain.com/a2a/v1/health

# Check firewall
sudo ufw status

# Verify secret key matches
cat .env | grep A2A_SECRET_KEY
```

### Git Sync Conflicts

```bash
# Pull with rebase
git pull --rebase

# If conflicts, resolve manually
git status
# Edit conflicted files
git add <resolved-files>
git rebase --continue

# Push changes
git push
```

### Approval Not Showing

```bash
# Check pending approvals
ls Pending_Approval/local/

# Check A2A logs
tail -f Logs/platinum_local_*.log

# Manually trigger sync
git pull
```

---

## Performance

### Resource Usage

**Cloud Agent:**
- CPU: ~5-10% (idle), ~30% (active)
- RAM: ~200-300 MB
- Disk: ~500 MB (vault + logs)
- Network: ~1-5 MB/day (sync)

**Local Agent:**
- CPU: ~5% (idle), ~20% (active)
- RAM: ~150-250 MB
- Disk: ~500 MB (vault + logs)

### Optimization

- Adjust heartbeat interval (default: 60s cloud, 300s local)
- Configure log retention (default: 30 days)
- Tune Git sync frequency (default: 5 minutes)

---

## Costs

### Oracle Cloud (Free Tier)
- VM: $0/month (Always Free)
- Storage: $0/month (up to 200 GB)
- Network: $0/month (up to 10 TB outbound)

### Optional Costs
- Domain name: ~$10-15/year
- SSL certificate: $0 (Let's Encrypt)
- Git hosting: $0 (GitHub/GitLab free tier)

**Total: ~$10-15/year (domain only)**

---

## Next Steps

1. ✓ Complete Phase 2 implementation
2. ✓ Deploy cloud agent to Oracle Cloud
3. ✓ Configure local agent
4. ✓ Test A2A communication
5. ✓ Run demo workflow
6. → Integrate with existing Golden Tier features
7. → Add web UI for approvals (optional)
8. → Implement mobile notifications (optional)

---

## Support

**Documentation:**
- `A2A_PROTOCOL.md` - Protocol specification
- `PLATINUM_PHASE2_COMPLETE.md` - Implementation details
- `Platinum_Status.md` - Current status

**Logs:**
- Cloud: `/home/ubuntu/AI_Employee_Vault/Logs/`
- Local: `AI_Employee_Vault/Logs/`

**Testing:**
- `scripts/test_a2a_protocol.py`

---

**Version:** Platinum Phase 2
**Status:** Production Ready
**Last Updated:** 2026-03-26
