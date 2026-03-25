# Platinum Tier Phase 2 - Quick Reference Card

## 🚀 Quick Commands

### Start Agents
```bash
# Local Agent
python main_platinum.py --mode local --vault-path AI_Employee_Vault

# Cloud Agent (on VM)
sudo systemctl start platinum-cloud-agent
```

### Check Status
```bash
# Local health
curl http://localhost:8090/a2a/v1/health

# Cloud health
curl http://<VM_IP>:8090/a2a/v1/health

# Service status (cloud)
sudo systemctl status platinum-cloud-agent
```

### View Logs
```bash
# Local logs
tail -f AI_Employee_Vault/Logs/platinum_local_*.log

# Cloud logs
sudo journalctl -u platinum-cloud-agent -f
```

### Git Sync
```bash
# Pull changes
git pull

# Push changes
git add -A && git commit -m "Sync" && git push

# Check status
git status
```

---

## 📁 Directory Structure

```
AI_Employee_Vault/
├── Needs_Action/
│   ├── cloud/          ← Cloud agent picks up work here
│   └── local/          ← Local agent picks up work here
├── Pending_Approval/
│   ├── cloud/
│   └── local/          ← User reviews approvals here
├── In_Progress/
│   ├── cloud/          ← Cloud agent working on
│   └── local/          ← Local agent working on
├── Updates/            ← Cloud writes updates here
├── Done/               ← Completed tasks
└── Dashboard.md        ← Local agent updates (single-writer)
```

---

## 🔐 Security Rules

**NEVER Synced:**
- `.env` files
- `*token*.json`
- `*credential*.json`
- `WhatsApp_Session/`
- `banking_credentials.json`

**Always Synced:**
- `*.md` files
- Configuration files (no secrets)
- Task files
- Plans and updates

---

## 📨 Message Types

1. **task_delegation** - Cloud → Local: Delegate work
2. **approval_request** - Cloud → Local: Request approval
3. **approval_response** - Local → Cloud: Send decision
4. **task_status** - Bidirectional: Update progress
5. **heartbeat** - Bidirectional: Health check
6. **sync_request** - Bidirectional: Trigger sync
7. **command** - Bidirectional: Execute command

---

## 🔄 Workflow Example

```
1. Email arrives → Cloud detects
2. Cloud drafts reply
3. Cloud → Local: approval_request (A2A or vault)
4. User reviews in /Pending_Approval/local/
5. User approves
6. Local executes send
7. Local → Cloud: task_status (completed)
8. Task moved to /Done/
```

---

## 🛠️ Troubleshooting

**Agent won't start:**
```bash
# Check logs
sudo journalctl -u platinum-cloud-agent -n 50

# Restart
sudo systemctl restart platinum-cloud-agent
```

**A2A not connecting:**
```bash
# Verify secret key matches
cat .env | grep A2A_SECRET_KEY

# Test connectivity
curl http://<VM_IP>:8090/a2a/v1/health
```

**Git conflicts:**
```bash
git pull --rebase
# Resolve conflicts
git add <files>
git rebase --continue
git push
```

---

## 📊 Resource Usage

**Cloud Agent:**
- RAM: ~200-300 MB
- CPU: ~5-10%
- Network: ~1-5 MB/day

**Local Agent:**
- RAM: ~150-250 MB
- CPU: ~5%

---

## 🔗 Important URLs

**Documentation:**
- `PLATINUM_README.md` - Complete guide
- `A2A_PROTOCOL.md` - Protocol spec
- `DEPLOYMENT_CHECKLIST.md` - Deployment steps

**Endpoints:**
- Local: `http://localhost:8090/a2a/v1/`
- Cloud: `http://<VM_IP>:8090/a2a/v1/`

---

## ⚡ Quick Tests

```bash
# Test A2A protocol
python scripts/test_a2a_protocol.py AI_Employee_Vault

# Quick start check
python scripts/platinum_quickstart.py AI_Employee_Vault

# Health check
curl http://localhost:8090/a2a/v1/health
```

---

## 📞 Support

**Logs Location:**
- Cloud: `/home/ubuntu/AI_Employee_Vault/Logs/`
- Local: `AI_Employee_Vault/Logs/`

**Service Management:**
```bash
sudo systemctl start|stop|restart|status platinum-cloud-agent
```

---

**Version:** Phase 2 Complete
**Date:** 2026-03-26
