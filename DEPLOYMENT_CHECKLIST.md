# Platinum Tier - Deployment Checklist

## Pre-Deployment Checklist

### Local Environment Setup
- [ ] Python 3.11+ installed
- [ ] Git installed and configured
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with `A2A_SECRET_KEY`
- [ ] `local_a2a_config.json` configured
- [ ] Gmail credentials configured (if using email features)
- [ ] WhatsApp session configured (if using WhatsApp)

### Cloud Environment Setup
- [ ] Oracle Cloud account created (free tier)
- [ ] VM instance launched (Ubuntu 22.04)
- [ ] SSH access configured
- [ ] Firewall rules configured (port 8090)
- [ ] Domain name configured (optional, for HTTPS)
- [ ] SSL certificates obtained (Let's Encrypt, optional)

### Git Repository Setup
- [ ] Private Git repository created
- [ ] Repository cloned on both local and cloud
- [ ] `.gitignore` configured
- [ ] Initial commit pushed
- [ ] SSH keys or access tokens configured

---

## Deployment Steps

### Phase 1: Local Agent Setup (15 minutes)

**Step 1.1: Prepare Environment**
```bash
cd AI_Employee_Vault
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
- [ ] Virtual environment activated
- [ ] Dependencies installed

**Step 1.2: Configure Environment**
```bash
# Create .env file
cat > .env << EOF
A2A_SECRET_KEY=$(openssl rand -hex 32)
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
VAULT_PATH=$(pwd)
LOG_LEVEL=INFO
EOF
```
- [ ] `.env` file created
- [ ] `A2A_SECRET_KEY` generated
- [ ] Save this key for cloud deployment!

**Step 1.3: Update Configuration**
Edit `local_a2a_config.json`:
- [ ] Set `cloud_agent.url` to your cloud domain
- [ ] Verify `server.port` is 8090
- [ ] Verify `server.host` is 127.0.0.1

**Step 1.4: Test Local Setup**
```bash
python scripts/platinum_quickstart.py .
python scripts/test_a2a_protocol.py .
```
- [ ] Quick start checks passed
- [ ] A2A protocol tests passed

**Step 1.5: Start Local Agent**
```bash
python ../main_platinum.py --mode local --vault-path .
```
- [ ] Local agent started successfully
- [ ] No errors in logs
- [ ] A2A server listening on localhost:8090

---

### Phase 2: Cloud Agent Deployment (30 minutes)

**Step 2.1: Provision Oracle Cloud VM**
1. Go to https://cloud.oracle.com
2. Sign up for free tier account
3. Navigate to: Compute → Instances → Create Instance
4. Configure:
   - Name: `platinum-cloud-agent`
   - Image: Ubuntu 22.04
   - Shape: VM.Standard.E2.1.Micro (Always Free)
   - Add your SSH public key
5. Launch instance
6. Note the public IP address

- [ ] VM instance created
- [ ] Public IP noted: ________________
- [ ] SSH key added

**Step 2.2: Configure Firewall**
In Oracle Cloud Console:
1. Networking → Virtual Cloud Networks
2. Select your VCN → Security Lists
3. Add Ingress Rule:
   - Source CIDR: 0.0.0.0/0
   - Destination Port: 8090
   - Protocol: TCP

- [ ] Firewall rule added for port 8090

**Step 2.3: SSH into VM**
```bash
ssh ubuntu@<VM_PUBLIC_IP>
```
- [ ] SSH connection successful

**Step 2.4: Clone Repository**
```bash
git clone <YOUR_REPO_URL> AI_Employee_Vault
cd AI_Employee_Vault
```
- [ ] Repository cloned

**Step 2.5: Run Deployment Script**
```bash
bash scripts/deploy_cloud_agent.sh
```

The script will:
- Update system packages
- Install Python and dependencies
- Create virtual environment
- Generate `.env` with A2A_SECRET_KEY
- Configure Git sync (cron job every 5 minutes)
- Create systemd service
- Configure firewall
- Start the service

- [ ] Deployment script completed
- [ ] `A2A_SECRET_KEY` copied from cloud `.env`
- [ ] Service started successfully

**Step 2.6: Verify Cloud Agent**
```bash
sudo systemctl status platinum-cloud-agent
sudo journalctl -u platinum-cloud-agent -n 50
```
- [ ] Service is active and running
- [ ] No errors in logs

**Step 2.7: Test Cloud Endpoint**
```bash
curl http://localhost:8090/a2a/v1/health
```
Expected response:
```json
{"status": "healthy", "agent_id": "cloud", "timestamp": "..."}
```
- [ ] Health endpoint responding

---

### Phase 3: Connect Agents (10 minutes)

**Step 3.1: Update Local Config**
On your local machine, edit `local_a2a_config.json`:
```json
{
  "a2a": {
    "cloud_agent": {
      "url": "http://<VM_PUBLIC_IP>:8090/a2a/v1"
    }
  }
}
```
- [ ] Cloud URL updated in local config

**Step 3.2: Update Cloud Config**
On cloud VM, edit `cloud_a2a_config.json`:
```json
{
  "a2a": {
    "local_agent": {
      "url": "http://<YOUR_HOME_IP>:8090/a2a/v1"
    }
  }
}
```
Note: You may need to use a dynamic DNS service or VPN for home IP.
- [ ] Local URL updated in cloud config (or set to fallback-only)

**Step 3.3: Sync A2A Secret Key**
Copy the `A2A_SECRET_KEY` from cloud `.env` to local `.env`:
```bash
# On cloud VM
cat .env | grep A2A_SECRET_KEY

# On local machine
# Update .env with the same key
```
- [ ] Secret keys match on both agents

**Step 3.4: Restart Both Agents**
```bash
# Cloud
sudo systemctl restart platinum-cloud-agent

# Local
# Stop and restart local agent
python ../main_platinum.py --mode local --vault-path .
```
- [ ] Both agents restarted
- [ ] No errors in logs

**Step 3.5: Test A2A Communication**
```bash
# On local machine
curl http://localhost:8090/a2a/v1/health

# Test cloud from local
curl http://<VM_PUBLIC_IP>:8090/a2a/v1/health
```
- [ ] Both health endpoints responding
- [ ] Agents can reach each other

---

### Phase 4: Git Sync Setup (10 minutes)

**Step 4.1: Initialize Git Repository**
```bash
cd AI_Employee_Vault
git init
git add .
git commit -m "Initial Platinum Tier setup"
```
- [ ] Git repository initialized
- [ ] Initial commit created

**Step 4.2: Create Remote Repository**
Create a private repository on GitHub/GitLab/Bitbucket
- [ ] Private repository created
- [ ] Repository URL noted: ________________

**Step 4.3: Push to Remote**
```bash
git remote add origin <YOUR_REPO_URL>
git push -u origin master
```
- [ ] Code pushed to remote

**Step 4.4: Configure Cloud Git Sync**
On cloud VM:
```bash
cd AI_Employee_Vault
git config user.email "cloud@example.com"
git config user.name "Cloud Agent"
git pull
```
- [ ] Git configured on cloud
- [ ] Can pull from remote

**Step 4.5: Configure Local Git Sync**
On local machine:
```bash
cd AI_Employee_Vault
git config user.email "local@example.com"
git config user.name "Local Agent"
```
- [ ] Git configured on local

**Step 4.6: Verify Auto-Sync**
Cloud agent has cron job for auto-sync (every 5 minutes):
```bash
crontab -l | grep "Cloud agent sync"
```
- [ ] Cron job configured

---

### Phase 5: End-to-End Testing (15 minutes)

**Test 1: Vault Fallback**
1. Stop local agent
2. On cloud, create test file:
   ```bash
   echo "Test approval" > Pending_Approval/local/test_approval.md
   git add -A && git commit -m "Test" && git push
   ```
3. On local, pull changes:
   ```bash
   git pull
   ls Pending_Approval/local/
   ```
- [ ] File synced via Git
- [ ] Vault fallback working

**Test 2: A2A Real-Time (if both agents can reach each other)**
1. Start both agents
2. Check logs for heartbeat messages
3. Verify agents are communicating
- [ ] Heartbeats visible in logs
- [ ] A2A communication working

**Test 3: Email Draft Workflow (if Gmail configured)**
1. Send test email to your Gmail
2. Cloud agent should detect and draft reply
3. Check `Pending_Approval/local/` for approval request
4. Approve and verify send
- [ ] Email detected by cloud
- [ ] Draft created
- [ ] Approval request received
- [ ] Send executed by local

---

## Post-Deployment Checklist

### Monitoring Setup
- [ ] Cloud agent logs accessible: `sudo journalctl -u platinum-cloud-agent -f`
- [ ] Local agent logs accessible: `tail -f Logs/platinum_local_*.log`
- [ ] Health endpoints bookmarked
- [ ] Git sync status monitoring configured

### Security Verification
- [ ] `.gitignore` preventing secret sync
- [ ] No secrets in Git history: `git log --all --full-history -- "*secret*"`
- [ ] A2A authentication working
- [ ] Firewall rules verified

### Documentation Review
- [ ] Read `PLATINUM_README.md`
- [ ] Review `A2A_PROTOCOL.md`
- [ ] Understand `Platinum_Status.md`
- [ ] Bookmark troubleshooting section

### Backup Setup
- [ ] Git repository backed up
- [ ] Cloud VM snapshot created (optional)
- [ ] Local vault backed up

---

## Troubleshooting Quick Reference

### Cloud Agent Won't Start
```bash
sudo systemctl status platinum-cloud-agent
sudo journalctl -u platinum-cloud-agent -n 100
# Check for Python errors, missing dependencies
```

### A2A Connection Failed
```bash
# Test connectivity
curl http://<VM_IP>:8090/a2a/v1/health

# Check firewall
sudo ufw status

# Verify secret key
cat .env | grep A2A_SECRET_KEY
```

### Git Sync Conflicts
```bash
git status
git pull --rebase
# Resolve conflicts manually
git add <resolved-files>
git rebase --continue
git push
```

### Logs Not Appearing
```bash
# Check log directory
ls -la Logs/

# Check permissions
chmod 755 Logs/

# Restart agent
sudo systemctl restart platinum-cloud-agent
```

---

## Success Criteria

All items below should be ✓ for successful deployment:

- [ ] Local agent running and healthy
- [ ] Cloud agent running and healthy
- [ ] A2A communication working (or vault fallback working)
- [ ] Git sync operational
- [ ] No secrets in Git repository
- [ ] Health endpoints responding
- [ ] Logs being generated
- [ ] Test workflow completed successfully

---

## Maintenance Schedule

### Daily
- Check agent health endpoints
- Review error logs

### Weekly
- Review completed tasks in `/Done/`
- Check Git sync status
- Review cloud VM resource usage

### Monthly
- Rotate logs (automatic)
- Review and clean old tasks
- Update dependencies if needed
- Review security settings

---

## Support Resources

**Documentation:**
- `PLATINUM_README.md` - Complete guide
- `A2A_PROTOCOL.md` - Protocol specification
- `IMPLEMENTATION_SUMMARY.md` - What was built
- `Platinum_Status.md` - Current status

**Scripts:**
- `platinum_quickstart.py` - Quick start helper
- `test_a2a_protocol.py` - Test suite
- `setup_local_agent.sh` - Local setup
- `deploy_cloud_agent.sh` - Cloud deployment

**Logs:**
- Cloud: `/home/ubuntu/AI_Employee_Vault/Logs/`
- Local: `AI_Employee_Vault/Logs/`

---

**Deployment Checklist Version:** 1.0
**Last Updated:** 2026-03-26
**Status:** Ready for Production
