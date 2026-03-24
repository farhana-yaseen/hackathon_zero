# Complete Guide to Running Your AI Employee Project

## Overview
This guide provides comprehensive instructions for running the Personal AI Employee system with all three tiers (Bronze, Silver, Golden) and all integrated capabilities including WhatsApp and LinkedIn automation.

## Step 1: Prerequisites Check

First, verify you have everything installed:

```bash
# Check Python version (need 3.13+)
python --version

# Check if you're in the project directory
cd D:\hackthon\hackathon_zero
pwd
```

## Step 2: Set Up Python Environment

```bash
# Create virtual environment (if not already done)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

## Step 3: Install Dependencies

```bash
# Install required packages
pip install -r AI_Employee_Vault/requirements.txt

# Install Playwright for browser automation
playwright install

# Common packages needed:
# - google-auth
# - google-auth-oauthlib
# - google-auth-httplib2
# - google-api-python-client
# - watchdog (for file system monitoring)
# - requests
# - playwright (for browser automation)
```

## Step 4: Configure Credentials

### For Bronze/Silver Tier (Gmail):
1. Get Gmail credentials:
   ```bash
   # Follow the guide
   cat AI_Employee_Vault/setup_gmail_credentials.md
   ```
2. Place credentials file:
   - Put `credentials.json` in `AI_Employee_Vault/`
   - First run will create `token.pickle` automatically

### For LinkedIn Integration:
1. Create LinkedIn Developer App:
   ```bash
   # Follow the guide
   cat AI_Employee_Vault/setup_linkedin_api.md
   ```
2. Configure LinkedIn credentials:
   - Create `linkedin_credentials.json` with your LinkedIn app credentials
   - Or configure via environment variables
   - For live posting, you need valid access tokens in `linkedin_token.json`

### For Live LinkedIn Posting (Optional):
1. Set up LinkedIn authentication:
   - Create a LinkedIn Developer App at https://www.linkedin.com/developers/
   - Generate an access token with appropriate permissions
   - Save it to `AI_Employee_Vault/linkedin_token.json`
   - See `LINKEDIN_SETUP_GUIDE.md` for detailed instructions

2. The system works in simulation mode without credentials:
   - Creates markdown files in `LinkedIn_Posts/`
   - Documents what would be posted
   - Does not make live posts to your account

### For Golden Tier (Additional):
1. Edit Golden Tier config:
   ```bash
   # Open the config file
   notepad AI_Employee_Vault/golden_tier_config.json
   ```
2. Update with your credentials:
   - Odoo URL and credentials (if using)
   - Social media API tokens (if using)
   - Keep defaults for testing

## Step 5: Choose Your Tier and Run

### Option A: Start with Bronze Tier (Recommended for First Time)

```bash
# Run Bronze Tier
python main.py --tier bronze
```

**What happens:**
- Watches your Gmail inbox
- Creates files in `Needs_Action/` for new emails
- Generates plans in `Plans/`
- Updates `Dashboard.md`

**To test it:**
1. Send yourself an email
2. Wait 30-60 seconds
3. Check `AI_Employee_Vault/Needs_Action/` for new files
4. Check `AI_Employee_Vault/Dashboard.md` for updates

### Option B: Run Silver Tier (More Features)

```bash
# Run Silver Tier
python main.py --tier silver
```

**What happens:**
- Starts multiple watchers (Gmail, WhatsApp, LinkedIn, File System)
- Starts MCP server on port 8080
- Starts scheduler
- Starts approval system

**To test it:**
1. Drop a file in `AI_Employee_Vault/Inbox/`
2. Send yourself an email
3. Check http://localhost:8080/mcp (MCP server)
4. Watch for files appearing in `Needs_Action/`
5. **WhatsApp**: Place JSON files in `AI_Employee_Vault/WhatsApp_Sim/`
6. **LinkedIn**: Configure credentials and start LinkedIn watcher

### Option C: Run Golden Tier (Full Features)

```bash
# Run Golden Tier
python main.py --tier golden
```

**What happens:**
- Starts all Silver Tier components
- Starts cross-domain sync service
- Starts Odoo integration (if configured)
- Starts social media service
- Starts audit/briefing service
- Enhanced logging to `Logs/`

**Note:** Odoo connection will fail if not installed locally - this is normal!

## Step 6: Verify It's Running

### Check Running Processes

```bash
# In a new terminal (keep the first one running)
# Check if Python processes are running
tasklist | findstr python

# You should see multiple python.exe processes
```

### Check Created Files

```bash
# Check if directories are being used
ls AI_Employee_Vault/Needs_Action/
ls AI_Employee_Vault/Logs/
ls AI_Employee_Vault/Plans/
ls AI_Employee_Vault/WhatsApp_Sim/
ls AI_Employee_Vault/LinkedIn_Posts/
```

### Check Logs (Golden Tier)

```bash
# View today's log
type AI_Employee_Vault\Logs\golden_tier_20260303.log

# Or tail the log (if you have tail installed)
tail -f AI_Employee_Vault/Logs/golden_tier_*.log
```

## Step 7: Test the System

### Test Bronze/Silver Tier:

1. **Send yourself a test email:**
   - Subject: "Test: Urgent task"
   - Body: "Please prepare a report for tomorrow's meeting"
2. **Wait 30-60 seconds**
3. **Check results:**
   ```bash
   # Check for new files
   ls AI_Employee_Vault/Needs_Action/

   # Open Dashboard
   notepad AI_Employee_Vault/Dashboard.md
   ```

### Test WhatsApp Functionality:

1. **Create a WhatsApp message simulation:**
   ```bash
   # Create a JSON file in WhatsApp_Sim directory
   echo {
   echo   "sender": "Test Contact",
   echo   "phone_number": "+1234567890",
   echo   "body": "This is a test WhatsApp message",
   echo   "is_important": true,
   echo   "priority": "high"
   echo } > AI_Employee_Vault/WhatsApp_Sim/test_msg.json
   ```
2. **Wait for processing (the WhatsApp watcher checks every 30 seconds)**
3. **Check results in `AI_Employee_Vault/Needs_Action/`**

### Test LinkedIn Functionality:

1. **Configure LinkedIn credentials** as described above
2. **Run the LinkedIn watcher separately:**
   ```bash
   python AI_Employee_Vault/scripts/linkedin_watcher.py AI_Employee_Vault
   ```
3. **Or use MCP server tools for LinkedIn automation**

### Test Golden Tier:

1. **Create a test file in Inbox:**
   ```bash
   echo "Test document for processing" > AI_Employee_Vault/Inbox/test_file.txt
   ```
2. **Check if it was processed:**
   ```bash
   # Should be moved to Predicted_Actions or Needs_Action
   ls AI_Employee_Vault/Predicted_Actions/
   ls AI_Employee_Vault/Needs_Action/
   ```
3. **Check logs:**
   ```bash
   type AI_Employee_Vault\Logs\golden_tier_*.log | findstr "test_file"
   ```

## Step 8: Stop the System

```bash
# Press Ctrl+C in the terminal where it's running
# You'll see shutdown messages

# Or if running in background, find and kill the process
tasklist | findstr python
taskkill /PID <process_id> /F
```

## MCP Server Tools Available

### Filesystem Tools (2)
- `move_file` - Move files within vault
- `create_note` - Create notes in folders

### Email/Scheduling Tools (4)
- `send_email` - Send emails through the system
- `create_task` - Create new tasks
- `schedule_meeting` - Schedule meetings
- `request_human_approval` - Request human approval for actions

### Browser Automation Tools (4)
- `navigate_browser` - Navigate to URLs and perform browser actions
- `click_element` - Click webpage elements using CSS/XPath selectors
- `fill_form` - Fill forms with provided data
- `extract_data` - Extract data from webpage elements

### Calendar Tools (4)
- `create_calendar_event` - Create calendar events
- `update_calendar_event` - Update existing calendar events
- `delete_calendar_event` - Delete calendar events
- `list_calendar_events` - List events in date range

### Slack Tools (4)
- `send_slack_message` - Send messages to Slack channels
- `read_slack_channel` - Read messages from Slack channels
- `search_slack_messages` - Search Slack messages by query
- `create_slack_channel` - Create new Slack channels

### LinkedIn Tools (4)
- `post_to_linkedin` - Post content to LinkedIn with visibility settings
- `monitor_linkedin_feed` - Monitor LinkedIn feed for posts and interactions
- `check_linkedin_notifications` - Check LinkedIn notifications
- `get_linkedin_profile_info` - Retrieve LinkedIn profile information

**Total MCP Tools: 22**

## Common First-Run Issues

### Issue 1: "Module not found"
```bash
# Solution: Install missing package
pip install <package_name>

# Or reinstall all
pip install -r AI_Employee_Vault/requirements.txt
```

### Issue 2: "Permission denied" on Gmail
```bash
# Solution: Delete token and re-authenticate
del AI_Employee_Vault\token.pickle
# Run again, it will open browser for authentication
```

### Issue 3: "Port already in use" (Silver/Golden)
```bash
# Solution: Kill process using the port
netstat -ano | findstr :8080
taskkill /PID <process_id> /F
```

### Issue 4: "Odoo connection failed" (Golden Tier)
```
This is NORMAL if you don't have Odoo installed
The system will continue without ERP integration
To fix: Install Odoo Community Edition or disable in config
```

### Issue 5: No files appearing in Needs_Action
```bash
# Check if Gmail watcher is running
# Check credentials.json exists
# Check token.pickle was created
# Try sending email again and wait 60 seconds
```

### Issue 6: WhatsApp messages not processing
- Check that `WhatsApp_Sim` directory exists
- Verify JSON message format is correct
- Ensure WhatsApp watcher is running

### Issue 7: LinkedIn tools not working
- Verify LinkedIn credentials are configured
- Check LinkedIn Developer app settings
- Ensure proper API permissions are granted

## Quick Start Commands Summary

```bash
# 1. Navigate to project
cd D:\hackthon\hackathon_zero

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Install dependencies
pip install -r AI_Employee_Vault/requirements.txt
playwright install

# 4. Run your chosen tier
python main.py --tier bronze    # Start simple
python main.py --tier silver    # More features
python main.py --tier golden    # Full features

# 5. In another terminal, test it
python AI_Employee_Vault/scripts/test_bronze_tier.py AI_Employee_Vault
python AI_Employee_Vault/scripts/test_silver_tier.py AI_Employee_Vault
python AI_Employee_Vault/scripts/test_golden_tier.py AI_Employee_Vault

# 6. Run specific watchers separately if needed
python AI_Employee_Vault/scripts/whatsapp_watcher.py AI_Employee_Vault
python AI_Employee_Vault/scripts/linkedin_watcher.py AI_Employee_Vault

# 7. Stop with Ctrl+C
```

## Recommended First Run

For your first time, I recommend:

1. **Start with Bronze Tier** to understand the basics
2. **Send yourself a test email** and watch it get processed
3. **Check the Dashboard.md** to see updates
4. **Try WhatsApp simulation** by placing JSON files in `WhatsApp_Sim/`
5. **Once comfortable, try Silver Tier** for more features
6. **Finally try Golden Tier** when you want full capabilities

## Monitoring Your System

### Open in Obsidian (Recommended)
```bash
# Open Obsidian and point it to:
D:\hackthon\hackathon_zero\AI_Employee_Vault

# Then open Dashboard.md as your starting point
```

### Watch Logs in Real-Time
```bash
# If you have tail installed
tail -f AI_Employee_Vault/Logs/golden_tier_*.log

# Or use PowerShell
Get-Content AI_Employee_Vault\Logs\golden_tier_*.log -Wait
```