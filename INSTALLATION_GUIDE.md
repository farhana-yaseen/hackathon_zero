# Installation Guide: Personal AI Employee System

This guide provides comprehensive step-by-step instructions to deploy and run the Personal AI Employee system in a production environment.

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Prerequisites](#prerequisites)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Production Deployment](#production-deployment)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Hardware Requirements:
- CPU: 2 cores or more
- RAM: 4 GB or more
- Storage: 10 GB free space
- Network: Reliable internet connection

### Supported Operating Systems:
- Linux (Ubuntu 20.04+, CentOS 8+)
- macOS 10.15+
- Windows 10/11 (with WSL2 recommended)

### Software Requirements:
- Python 3.13 or higher
- Node.js 18.x or higher
- Git 2.0 or higher

## Prerequisites

Before installing, ensure you have the following accounts and credentials:

1. **Google Account** with Gmail access for email automation
2. **Access to WhatsApp Business API** (for production) or WhatsApp simulation environment
3. **API keys** for any additional services you plan to integrate
4. **System administrator access** to install dependencies

## Installation Steps

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-organization/hackathon-zero.git
cd hackathon-zero
```

### Step 2: Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Install Node.js Dependencies
```bash
npm install
```

### Step 5: Install Playwright (for browser automation)
```bash
playwright install
```

### Step 6: Set Up Directory Structure
The application expects the following directory structure:
```
├── AI_Employee_Vault/
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Plans/
│   ├── Done/
│   ├── WhatsApp_Sim/
│   ├── Schedules/
│   ├── Approvals/
│   ├── Sent_Emails/
│   └── Updates/
```

These directories are created automatically when you run the application, but you can create them manually if needed:
```bash
mkdir -p AI_Employee_Vault/{Inbox,Needs_Action,Plans,Done,WhatsApp_Sim,Schedules,Approvals,Sent_Emails,Updates}
```

## Configuration

### Step 1: Configure Gmail API Access
Follow the instructions in `setup_gmail_credentials.md` to set up OAuth credentials for Gmail access.

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create OAuth 2.0 credentials
5. Download the credentials JSON file
6. Place it in the appropriate location and configure the path in your environment

### Step 2: Environment Variables
Create a `.env` file in the root directory with the following variables:

```bash
# Gmail Configuration
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/gmail-credentials.json

# WhatsApp Configuration (if using production API)
WHATSAPP_API_URL=
WHATSAPP_API_TOKEN=

# Application Settings
VAULT_PATH=./AI_Employee_Vault
LOG_LEVEL=INFO
MAX_WORKERS=4

# Scheduling Configuration
SCHEDULER_TIMEZONE=UTC
```

### Step 3: Configure Schedules
Schedule configurations can be placed in the `Schedules/` directory. The system supports various scheduling formats:
- Cron-like expressions
- Natural language schedules (processed through NLP)
- Recurring task definitions

## Running the Application

### Development Mode
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Run the application
python main.py
```

### Production Mode
For production deployment, it's recommended to use a process manager:

#### Using systemd (Linux)
Create a service file `/etc/systemd/system/ai-employee.service`:
```ini
[Unit]
Description=Personal AI Employee Service
After=network.target

[Service]
Type=simple
User=ai-employee
WorkingDirectory=/path/to/hackathon-zero
Environment=PATH=/path/to/venv/bin
EnvironmentFile=/path/to/hackathon-zero/.env
ExecStart=/path/to/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-employee
sudo systemctl start ai-employee
sudo systemctl status ai-employee
```

#### Using Docker (Alternative)
Create a `Dockerfile`:
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y nodejs npm
RUN npm install

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t ai-employee .
docker run -d --name ai-employee-container \
  -v /local/path/to/AI_Employee_Vault:/app/AI_Employee_Vault \
  -v /path/to/credentials:/app/credentials \
  --env-file .env \
  ai-employee
```

## Production Deployment

### Security Considerations
1. **Credential Management**: Store all API keys and credentials securely using:
   - Environment variables
   - Secret management systems (HashiCorp Vault, AWS Secrets Manager)
   - Encrypted configuration files

2. **Network Security**:
   - Use VPN or private networks for inter-service communication
   - Implement proper firewall rules
   - Use HTTPS for all external communications

3. **Access Control**:
   - Implement role-based access control
   - Regular credential rotation
   - Audit logging for sensitive operations

### Performance Optimization
1. **Resource Allocation**:
   - Monitor CPU and memory usage
   - Adjust worker counts based on load
   - Implement connection pooling for database/API calls

2. **Caching**:
   - Cache frequently accessed data
   - Implement proper cache invalidation
   - Use Redis or Memcached for distributed caching

3. **Database Optimization** (if applicable):
   - Index frequently queried fields
   - Optimize slow queries
   - Implement read replicas for heavy read loads

### Scaling Strategies
1. **Horizontal Scaling**: Deploy multiple instances behind a load balancer
2. **Microservice Architecture**: Separate components into independent services
3. **Queue-Based Processing**: Use message queues for asynchronous processing
4. **Auto-scaling**: Implement cloud-based auto-scaling based on metrics

## Monitoring and Maintenance

### Logging
The application logs activities to help with monitoring:
- Action logs in the `Logs/` directory
- Error logs with stack traces
- Performance metrics
- Audit trails for important operations

### Health Checks
Implement health check endpoints for monitoring tools:
- `/health` - Basic service health
- `/ready` - Service readiness for traffic
- `/metrics` - Performance metrics

### Backup Strategy
Regularly backup:
- Configuration files
- Schedule definitions
- Approval workflows
- Processed data and results

### Maintenance Tasks
1. **Daily**:
   - Check logs for errors
   - Verify service availability
   - Monitor resource usage

2. **Weekly**:
   - Clean up old log files
   - Review processed items in Done/ directory
   - Check for failed tasks requiring manual intervention

3. **Monthly**:
   - Rotate credentials
   - Review and optimize performance
   - Update dependencies (after testing)

## Troubleshooting

### Common Issues

#### Issue: Gmail API Authentication Failure
**Symptoms**: Cannot connect to Gmail account
**Solution**:
1. Verify credentials file exists and has correct permissions
2. Check OAuth scopes are properly configured
3. Re-authenticate if token has expired

#### Issue: File System Watcher Not Responding
**Symptoms**: New files in Inbox/ not triggering actions
**Solution**:
1. Check directory permissions
2. Verify watchdog service is running
3. Increase file descriptor limits if needed

#### Issue: WhatsApp Integration Problems
**Symptoms**: WhatsApp messages not processed
**Solution**:
1. For simulation: Check WhatsApp_Sim/ directory structure
2. For production: Verify API credentials and rate limits

#### Issue: High Memory Usage
**Symptoms**: Process consuming excessive memory
**Solution**:
1. Implement proper cleanup of temporary files
2. Limit concurrent workers
3. Monitor for memory leaks in long-running processes

### Debugging Commands
```bash
# Check running processes
ps aux | grep python

# Monitor logs in real-time
tail -f AI_Employee_Vault/logs/app.log

# Check disk space
df -h

# Monitor network connections
netstat -tuln
```

### Support Resources
- Check the `README.md` files in individual modules
- Review the `Company_Handbook.md` for business logic
- Examine test files (`test_*.py`) for usage examples
- Consult the `SKILL.md` documentation for capabilities

---

**Note**: This system handles sensitive operations including email automation, file processing, and human-in-the-loop approvals. Ensure compliance with your organization's security policies and applicable regulations before deployment.