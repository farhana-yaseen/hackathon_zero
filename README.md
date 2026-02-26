# Personal AI Employee - Production Deployment Guide

## Overview
This project implements a Personal AI Employee system with multiple tiers of functionality designed for real-world deployment. The Silver Tier includes advanced automation capabilities with human-in-the-loop approval systems.

## Quick Start (Production Ready)

### Prerequisites
- Python 3.13+
- Node.js 18+
- Git
- System with 4GB+ RAM

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/hackathon-zero.git
   cd hackathon-zero
   ```

2. **Set up Python virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install --upgrade pip
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   npm install
   playwright install
   ```

4. **Configure credentials** (See `setup_gmail_credentials.md` for Gmail setup)

5. **Run the application**
   ```bash
   python main.py
   ```

## Real-World Deployment Options

### Option 1: Systemd Service (Linux Production)
```bash
# Create system service
sudo nano /etc/systemd/system/ai-employee.service
# Start service: sudo systemctl start ai-employee
```

### Option 2: Docker Container
```bash
# Build and run containerized version
docker build -t ai-employee .
docker run -d --name ai-employee -v credentials:/app/credentials ai-employee
```

### Option 3: Process Manager (PM2)
```bash
# Install PM2 globally
npm install -g pm2
# Start application with PM2
pm2 start main.py --name ai-employee --interpreter python3
```

## Silver Tier Features

### Core Capabilities
- **Multi-channel Watchers**: Monitors Gmail, WhatsApp, and file system changes
- **MCP Server**: Provides tools for automation (send_email, create_task, schedule_meeting, move_file, create_note, request_human_approval)
- **Approval System**: Handles human-in-the-loop approvals for important actions
- **Scheduler**: Automated task scheduling and execution
- **File System Monitoring**: Watches the Inbox directory for new files to process

### Directories Structure
- `Inbox/`: Monitored for new files to process
- `Needs_Action/`: Items requiring human attention
- `Plans/`: Generated action plans
- `Done/`: Completed tasks
- `WhatsApp_Sim/`: WhatsApp message simulation files
- `Schedules/`: Scheduled task definitions
- `Approvals/`: Approval workflow files
- `Sent_Emails/`: Archive of sent emails

## Configuration

### Environment Variables
Create a `.env` file with:
```
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
VAULT_PATH=./AI_Employee_Vault
LOG_LEVEL=INFO
```

### Credential Setup
1. **Gmail**: Follow `setup_gmail_credentials.md` for OAuth setup
2. **WhatsApp**: Configure API credentials for production use
3. **Additional Services**: Add API keys as needed

## Production Considerations

### Security
- Store credentials securely using environment variables or secret management
- Use VPN/private networking for sensitive operations
- Implement proper access controls

### Monitoring
- Log all operations for audit purposes
- Monitor system resources and performance
- Set up alerts for critical failures

### Maintenance
- Regular backup of configuration and processed data
- Periodic credential rotation
- Update dependencies regularly

## Usage

### Starting the Service
```bash
# Development
python main.py

# Production (systemd)
sudo systemctl start ai-employee

# With PM2
pm2 start main.py --name ai-employee --interpreter python3
```

### Stopping the Service
```bash
# Find process ID and kill, or use:
sudo systemctl stop ai-employee  # For systemd
pm2 stop ai-employee             # For PM2
```

## Troubleshooting

Common issues and solutions:

- **Permission errors**: Check file permissions for the AI_Employee_Vault directory
- **Gmail API errors**: Verify OAuth credentials and scopes
- **High memory usage**: Adjust MAX_WORKERS environment variable
- **File watcher not responding**: Check system inotify limits on Linux

For detailed troubleshooting, see `INSTALLATION_GUIDE.md`.

## Architecture Components

- `gmail_watcher.py`: Monitors Gmail for new messages
- `whatsapp_watcher.py`: Processes WhatsApp messages from simulation files
- `file_system_watcher.py`: Watches for file changes in the Inbox
- `mcp_server.py`: Provides automation tools via HTTP/MCP interface
- `scheduler.py`: Manages scheduled tasks
- `approval_system.py`: Handles approval workflows
- `silver_tier.py`: Orchestrates all Silver Tier components
- `run_watchers.py`: Coordinates all watcher processes