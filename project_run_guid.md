● Complete Guide to Running Your AI Employee Project

  Step 1: Prerequisites Check

  First, verify you have everything installed:

  # Check Python version (need 3.13+)
  python --version

  # Check if you're in the project directory
  cd D:\hackthon\hackathon_zero
  pwd

  Step 2: Set Up Python Environment

  # Create virtual environment (if not already done)
  python -m venv venv

  # Activate virtual environment
  # On Windows:
  venv\Scripts\activate

  # You should see (venv) in your terminal prompt

  Step 3: Install Dependencies

  # Install required packages
  pip install -r AI_Employee_Vault/requirements.txt

  # Common packages needed:
  # - google-auth
  # - google-auth-oauthlib
  # - google-auth-httplib2
  # - google-api-python-client
  # - watchdog (for file system monitoring)
  # - requests

  Step 4: Configure Credentials

  For Bronze/Silver Tier (Gmail):

  1. Get Gmail credentials:
  # Follow the guide
  cat AI_Employee_Vault/setup_gmail_credentials.md
  2. Place credentials file:
    - Put credentials.json in AI_Employee_Vault/
    - First run will create token.pickle automatically

  For Golden Tier (Additional):

  1. Edit Golden Tier config:
  # Open the config file
  notepad AI_Employee_Vault/golden_tier_config.json
  2. Update with your credentials:
    - Odoo URL and credentials (if using)
    - Social media API tokens (if using)
    - Keep defaults for testing

  Step 5: Choose Your Tier and Run

  Option A: Start with Bronze Tier (Recommended for First Time)

  # Run Bronze Tier
  python main.py --tier bronze

  What happens:
  - Watches your Gmail inbox
  - Creates files in Needs_Action/ for new emails
  - Generates plans in Plans/
  - Updates Dashboard.md

  To test it:
  1. Send yourself an email
  2. Wait 30-60 seconds
  3. Check AI_Employee_Vault/Needs_Action/ for new files
  4. Check AI_Employee_Vault/Dashboard.md for updates

  Option B: Run Silver Tier (More Features)

  # Run Silver Tier
  python main.py --tier silver

  What happens:
  - Starts multiple watchers (Gmail, WhatsApp, LinkedIn, File System)
  - Starts MCP server on port 8080
  - Starts scheduler
  - Starts approval system

  To test it:
  1. Drop a file in AI_Employee_Vault/Inbox/
  2. Send yourself an email
  3. Check http://localhost:8080/mcp (MCP server)
  4. Watch for files appearing in Needs_Action/

  Option C: Run Golden Tier (Full Features)

  # Run Golden Tier
  python main.py --tier golden

  What happens:
  - Starts all Silver Tier components
  - Starts cross-domain sync service
  - Starts Odoo integration (if configured)
  - Starts social media service
  - Starts audit/briefing service
  - Enhanced logging to Logs/

  Note: Odoo connection will fail if not installed locally - this is normal!

  Step 6: Verify It's Running

  Check Running Processes

  # In a new terminal (keep the first one running)
  # Check if Python processes are running
  tasklist | findstr python

  # You should see multiple python.exe processes

  Check Created Files

  # Check if directories are being used
  ls AI_Employee_Vault/Needs_Action/
  ls AI_Employee_Vault/Logs/
  ls AI_Employee_Vault/Plans/

  Check Logs (Golden Tier)

  # View today's log
  type AI_Employee_Vault\Logs\golden_tier_20260303.log

  # Or tail the log (if you have tail installed)
  tail -f AI_Employee_Vault/Logs/golden_tier_*.log

  Step 7: Test the System

  Test Bronze/Silver Tier:

  1. Send yourself a test email:
    - Subject: "Test: Urgent task"
    - Body: "Please prepare a report for tomorrow's meeting"
  2. Wait 30-60 seconds
  3. Check results:
  # Check for new files
  ls AI_Employee_Vault/Needs_Action/

  # Open Dashboard
  notepad AI_Employee_Vault/Dashboard.md

  Test Golden Tier:

  1. Create a test file in Inbox:
  echo "Test document for processing" > AI_Employee_Vault/Inbox/test_file.txt
  2. Check if it was processed:
  # Should be moved to Predicted_Actions or Needs_Action
  ls AI_Employee_Vault/Predicted_Actions/
  ls AI_Employee_Vault/Needs_Action/
  3. Check logs:
  type AI_Employee_Vault\Logs\golden_tier_*.log | findstr "test_file"

  Step 8: Stop the System

  # Press Ctrl+C in the terminal where it's running
  # You'll see shutdown messages

  # Or if running in background, find and kill the process
  tasklist | findstr python
  taskkill /PID <process_id> /F

  Common First-Run Issues

  Issue 1: "Module not found"

  # Solution: Install missing package
  pip install <package_name>

  # Or reinstall all
  pip install -r AI_Employee_Vault/requirements.txt

  Issue 2: "Permission denied" on Gmail

  # Solution: Delete token and re-authenticate
  del AI_Employee_Vault\token.pickle
  # Run again, it will open browser for authentication

  Issue 3: "Port already in use" (Silver/Golden)

  # Solution: Kill process using the port
  netstat -ano | findstr :8080
  taskkill /PID <process_id> /F

  Issue 4: "Odoo connection failed" (Golden Tier)

  # This is NORMAL if you don't have Odoo installed
  # The system will continue without ERP integration
  # To fix: Install Odoo Community Edition or disable in config

  Issue 5: No files appearing in Needs_Action

  # Check if Gmail watcher is running
  # Check credentials.json exists
  # Check token.pickle was created
  # Try sending email again and wait 60 seconds

  Quick Start Commands Summary

  # 1. Navigate to project
  cd D:\hackthon\hackathon_zero

  # 2. Activate virtual environment
  venv\Scripts\activate

  # 3. Run your chosen tier
  python main.py --tier bronze    # Start simple
  python main.py --tier silver    # More features
  python main.py --tier golden    # Full features

  # 4. In another terminal, test it
  python AI_Employee_Vault/scripts/test_bronze_tier.py AI_Employee_Vault
  python AI_Employee_Vault/scripts/test_silver_tier.py AI_Employee_Vault
  python AI_Employee_Vault/scripts/test_golden_tier.py AI_Employee_Vault

  # 5. Stop with Ctrl+C

  Recommended First Run

  For your first time, I recommend:

  1. Start with Bronze Tier to understand the basics
  2. Send yourself a test email and watch it get processed
  3. Check the Dashboard.md to see updates
  4. Once comfortable, try Silver Tier for more features
  5. Finally try Golden Tier when you want full capabilities

  Monitoring Your System

  Open in Obsidian (Recommended)

  # Open Obsidian and point it to:
  D:\hackthon\hackathon_zero\AI_Employee_Vault

  # Then open Dashboard.md as your starting point

  Watch Logs in Real-Time

  # If you have tail installed
  tail -f AI_Employee_Vault/Logs/golden_tier_*.log

  # Or use PowerShell
  Get-Content AI_Employee_Vault\Logs\golden_tier_*.log -Wait