# Personal AI Employee - Multi-Tier Automation System

## Overview
This project implements a Personal AI Employee system with three progressive tiers of functionality designed for real-world deployment. Each tier builds upon the previous one, adding more sophisticated automation, integrations, and intelligence.

**Three-Tier Architecture:**
- **Bronze Tier**: Basic email processing and task management
- **Silver Tier**: Advanced automation with multi-channel watchers and human-in-the-loop approvals
- **Golden Tier**: Enterprise-grade features with ERP integration, social media management, and executive reporting

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+ (optional, for MCP server)
- Git
- System with 4GB+ RAM
- Obsidian (optional, for vault visualization)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/hackathon-zero.git
   cd hackathon-zero
   ```

2. **Set up Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install --upgrade pip
   ```

3. **Install dependencies**
   ```bash
   pip install -r AI_Employee_Vault/requirements.txt
   ```

4. **Configure credentials**
   - Gmail: See `AI_Employee_Vault/setup_gmail_credentials.md`
   - LinkedIn: See `AI_Employee_Vault/setup_linkedin_api.md`
   - Golden Tier: Edit `AI_Employee_Vault/golden_tier_config.json`

5. **Run the application**
   ```bash
   # Run Bronze Tier
   python main.py --tier bronze

   # Run Silver Tier (default)
   python main.py --tier silver

   # Run Golden Tier
   python main.py --tier golden
   ```

## Tier Features

### 🥉 Bronze Tier
**Basic automation for personal productivity**

**Features:**
- Email processing from Gmail
- Simple task creation and tracking
- Dashboard updates
- Plan generation from emails
- Basic file organization

**Use Case:** Individual users who need basic email automation and task management

**Components:**
- `scripts/gmail_watcher.py` - Monitors Gmail inbox
- `scripts/claude_reasoning.py` - Processes emails and generates plans
- `Dashboard.md` - Central status dashboard

---

### 🥈 Silver Tier
**Advanced automation with multi-channel monitoring**

**Features:**
- Multi-channel watchers (Gmail, WhatsApp, LinkedIn, File System)
- MCP Server for automation tools
- Human-in-the-loop approval system
- Automated task scheduler
- File system monitoring
- Email sending capabilities

**Use Case:** Power users and small teams needing comprehensive automation

**Components:**
- `scripts/gmail_watcher.py` - Gmail monitoring
- `scripts/whatsapp_watcher.py` - WhatsApp message processing
- `scripts/linkedin_watcher.py` - LinkedIn activity monitoring
- `scripts/file_system_watcher.py` - File change detection
- `scripts/mcp_server.py` - Automation tools server
- `scripts/scheduler.py` - Task scheduling engine
- `scripts/approval_system.py` - Approval workflow manager
- `scripts/silver_tier.py` - Silver Tier orchestrator
- `scripts/run_watchers.py` - Watcher coordination

**MCP Server Tools:**
- `send_email` - Send emails through the system
- `create_task` - Create new tasks
- `schedule_meeting` - Schedule meetings
- `move_file` - Move files within vault
- `create_note` - Create notes in folders
- `request_human_approval` - Request human approval for actions
- `navigate_browser` - Navigate to URLs and perform browser actions
- `click_element` - Click webpage elements using CSS/XPath selectors
- `fill_form` - Fill forms with provided data
- `extract_data` - Extract data from webpage elements
- `create_calendar_event` - Create calendar events
- `update_calendar_event` - Update existing calendar events
- `delete_calendar_event` - Delete calendar events
- `list_calendar_events` - List events in date range
- `send_slack_message` - Send messages to Slack channels
- `read_slack_channel` - Read messages from Slack channels
- `search_slack_messages` - Search Slack messages by query
- `create_slack_channel` - Create new Slack channels
- `post_to_linkedin` - Post content to LinkedIn with visibility settings
- `monitor_linkedin_feed` - Monitor LinkedIn feed for posts and interactions
- `check_linkedin_notifications` - Check LinkedIn notifications
- `get_linkedin_profile_info` - Retrieve LinkedIn profile information

---

### 🥇 Golden Tier
**Enterprise-grade AI employee with advanced integrations**

**Features:**

#### 1. Cross-Domain Integration (Personal + Business)
- Syncs data between personal and business domains
- Contact deduplication and merging
- Calendar event synchronization
- Document sharing with access control
- Hourly automatic sync cycles

#### 2. Odoo ERP Integration
- Full accounting system integration via JSON-RPC APIs
- Invoice creation and management
- Payment recording
- Account balance queries
- Partner/customer management
- Financial report generation
- Complete operation audit trail

#### 3. Social Media Management
- Automated posting to Facebook, Instagram, and X (Twitter)
- Multi-platform content scheduling
- Engagement analytics and reporting
- Post performance tracking
- Platform-specific optimizations

#### 4. Executive Reporting
- **Weekly Audits**: Comprehensive system performance reports
  - Performance metrics tracking
  - Anomaly detection
  - Compliance checking
  - Recommendations generation
- **CEO Briefings**: Executive-level summaries
  - Key achievements identification
  - Risk and issue tracking
  - Financial highlights
  - Operational metrics
  - Strategic initiative tracking
  - Next week priorities

#### 5. Ralph Wiggum Loop
- Multi-step task verification system
- Automatic retry with configurable attempts
- Periodic verification checks
- Gentle nudging until task completion
- Comprehensive error recovery

#### 6. Enhanced Error Handling & Logging
- Multi-level logging (DEBUG, INFO, WARNING, ERROR)
- Daily log rotation
- Automatic error report generation
- Process health monitoring
- Detailed stack traces
- Operation audit trails

**Use Case:** Businesses and professionals needing enterprise-grade automation with ERP and social media integration

**Components:**
- `scripts/golden_tier.py` - Golden Tier orchestrator
- `scripts/cross_domain_sync.py` - Personal/Business sync service
- `scripts/odoo_integration_service.py` - ERP integration service
- `scripts/social_media_service.py` - Social media manager
- `scripts/audit_briefing_service.py` - Audit & briefing generator
- `scripts/test_golden_tier.py` - Golden Tier test suite

---

## Project Structure

```
hackathon-zero/
├── main.py                              ← Main entry point (supports all tiers)
├── main_golden.py                       ← Alternative Golden Tier entry point
├── README.md                            ← This file
├── GOLDEN_TIER_SUMMARY.md              ← Detailed Golden Tier documentation
├── INSTALLATION_GUIDE.md               ← Installation instructions
│
└── AI_Employee_Vault/                  ← Obsidian vault folder
    ├── .obsidian/                      ← Obsidian settings
    ├── scripts/                        ← All Python scripts
    │   ├── base_watcher.py
    │   ├── gmail_watcher.py
    │   ├── whatsapp_watcher.py
    │   ├── linkedin_watcher.py
    │   ├── file_system_watcher.py
    │   ├── mcp_server.py
    │   ├── scheduler.py
    │   ├── approval_system.py
    │   ├── claude_reasoning.py
    │   ├── run_watchers.py
    │   ├── silver_tier.py
    │   ├── golden_tier.py              ← Golden Tier orchestrator
    │   ├── cross_domain_sync.py
    │   ├── odoo_integration_service.py
    │   ├── social_media_service.py
    │   ├── audit_briefing_service.py
    │   ├── test_bronze_tier.py
    │   ├── test_silver_tier.py
    │   └── test_golden_tier.py
    │
    ├── Dashboard.md                    ← Central dashboard
    ├── Company_Handbook.md             ← Company information
    ├── golden_tier_config.json         ← Golden Tier configuration
    ├── credentials.json                ← Gmail OAuth credentials
    ├── token.pickle                    ← Gmail token cache
    ├── .env                            ← Environment variables
    ├── requirements.txt                ← Python dependencies
    │
    ├── Needs_Action/                   ← Items requiring attention
    ├── Plans/                          ← Generated action plans
    ├── Done/                           ← Completed tasks
    ├── Inbox/                          ← Incoming files to process
    ├── Pending_Approval/               ← Items awaiting approval
    ├── Approvals/                      ← Approval workflow files
    ├── Schedules/                      ← Scheduled task definitions
    ├── Sent_Emails/                    ← Archive of sent emails
    ├── WhatsApp_Sim/                   ← WhatsApp message simulations
    ├── LinkedIn_Posts/                 ← LinkedIn post archive
    ├── LinkedIn_Triggers/              ← LinkedIn automation triggers
    │
    ├── Cross_Domain/                   ← Cross-domain sync data (Golden)
    ├── Personal/                       ← Personal domain data (Golden)
    ├── Business/                       ← Business domain data (Golden)
    ├── Personal_Business_Sync/         ← Sync operations (Golden)
    ├── ERP_Integration/                ← Odoo ERP data (Golden)
    ├── Accounting/                     ← Accounting reports (Golden)
    ├── Social_Media/                   ← Social media data (Golden)
    ├── Social_Posts/                   ← Posted content (Golden)
    ├── Social_Analytics/               ← Analytics reports (Golden)
    ├── Audits/                         ← Weekly audit reports (Golden)
    ├── CEO_Briefings/                  ← Executive briefings (Golden)
    ├── Logs/                           ← System logs (Golden)
    └── Error_Reports/                  ← Error tracking (Golden)
```

## Configuration

### Environment Variables
Create a `.env` file in `AI_Employee_Vault/`:
```env
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
VAULT_PATH=./AI_Employee_Vault
LOG_LEVEL=INFO
```

### Golden Tier Configuration
Edit `AI_Employee_Vault/golden_tier_config.json`:

```json
{
  "odoo": {
    "url": "http://localhost:8069",
    "database": "odoo_db",
    "username": "admin",
    "password": "your_password"
  },
  "social_media": {
    "facebook": {
      "enabled": true,
      "access_token": "YOUR_FACEBOOK_TOKEN",
      "page_id": "YOUR_PAGE_ID"
    },
    "instagram": {
      "enabled": true,
      "access_token": "YOUR_INSTAGRAM_TOKEN"
    },
    "twitter": {
      "enabled": true,
      "bearer_token": "YOUR_TWITTER_BEARER_TOKEN",
      "api_key": "YOUR_API_KEY",
      "api_secret": "YOUR_API_SECRET",
      "access_token": "YOUR_ACCESS_TOKEN",
      "access_token_secret": "YOUR_ACCESS_TOKEN_SECRET"
    }
  },
  "cross_domain": {
    "sync_enabled": true,
    "sync_frequency_minutes": 60
  },
  "auditing": {
    "weekly_reports_day": "monday",
    "weekly_reports_time": "06:00"
  },
  "ralph_wiggum_loop": {
    "max_attempts": 5,
    "check_interval_seconds": 30
  }
}
```

### Credential Setup
1. **Gmail**: Follow `AI_Employee_Vault/setup_gmail_credentials.md` for OAuth setup
2. **LinkedIn**: Follow `AI_Employee_Vault/setup_linkedin_api.md` for API setup
3. **Odoo**: Install Odoo Community Edition locally or use cloud instance
4. **Social Media**: Obtain API credentials from respective platforms

## Usage

### Running Different Tiers

```bash
# Bronze Tier - Basic automation
python main.py --tier bronze

# Silver Tier - Advanced automation (default)
python main.py --tier silver

# Golden Tier - Enterprise features
python main.py --tier golden

# Specify custom vault path
python main.py --tier golden --vault-path /path/to/vault
```

### Testing

```bash
# Test Bronze Tier
python AI_Employee_Vault/scripts/test_bronze_tier.py AI_Employee_Vault

# Test Silver Tier
python AI_Employee_Vault/scripts/test_silver_tier.py AI_Employee_Vault

# Test Golden Tier
python AI_Employee_Vault/scripts/test_golden_tier.py AI_Employee_Vault
```

### Starting Services Individually

```bash
# Start Gmail watcher
python AI_Employee_Vault/scripts/gmail_watcher.py AI_Employee_Vault

# Start MCP server
python AI_Employee_Vault/scripts/mcp_server.py --vault-path AI_Employee_Vault --port 8080

# Start scheduler
python AI_Employee_Vault/scripts/scheduler.py AI_Employee_Vault start

# Start Golden Tier orchestrator
python AI_Employee_Vault/scripts/golden_tier.py --vault-path AI_Employee_Vault
```

## Production Deployment

### Option 1: Systemd Service (Linux)
```bash
# Create service file
sudo nano /etc/systemd/system/ai-employee.service

# Add configuration:
[Unit]
Description=AI Employee Golden Tier
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/hackathon-zero
ExecStart=/path/to/venv/bin/python main.py --tier golden
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable ai-employee
sudo systemctl start ai-employee
```

### Option 2: Docker Container
```bash
# Build image
docker build -t ai-employee .

# Run container
docker run -d \
  --name ai-employee \
  -v $(pwd)/AI_Employee_Vault:/app/AI_Employee_Vault \
  -e TIER=golden \
  ai-employee
```

### Option 3: Process Manager (PM2)
```bash
# Install PM2
npm install -g pm2

# Start with PM2
pm2 start main.py --name ai-employee --interpreter python3 -- --tier golden

# Save configuration
pm2 save

# Setup startup script
pm2 startup
```

## Monitoring & Maintenance

### Log Files
- **System Logs**: `AI_Employee_Vault/Logs/golden_tier_YYYYMMDD.log`
- **Error Reports**: `AI_Employee_Vault/Error_Reports/`
- **ERP Operations**: `AI_Employee_Vault/ERP_Integration/odoo_operation_log_*.json`
- **Social Media**: `AI_Employee_Vault/Social_Media/social_post_log_*.json`

### Weekly Reports
- **Audits**: Generated every Monday at 6:00 AM in `AI_Employee_Vault/Audits/`
- **CEO Briefings**: Generated every Monday at 6:00 AM in `AI_Employee_Vault/CEO_Briefings/`

### Health Checks
```bash
# Check running processes
ps aux | grep python | grep tier

# Check logs
tail -f AI_Employee_Vault/Logs/golden_tier_$(date +%Y%m%d).log

# Check MCP server
curl http://localhost:8080/mcp/health
```

## Troubleshooting

### Common Issues

**Permission Errors**
```bash
# Fix vault permissions
chmod -R 755 AI_Employee_Vault
```

**Gmail API Errors**
- Verify OAuth credentials in `credentials.json`
- Check token validity in `token.pickle`
- Ensure correct API scopes are enabled

**Odoo Connection Failed**
- Verify Odoo is running: `curl http://localhost:8069`
- Check database name and credentials in config
- Ensure XML-RPC is enabled in Odoo

**Social Media API Errors**
- Verify API tokens are valid and not expired
- Check rate limits for each platform
- Ensure proper permissions are granted

**High Memory Usage**
- Reduce number of concurrent watchers
- Adjust log retention settings
- Monitor process with `htop` or Task Manager

**File Watcher Not Responding**
- Check system inotify limits (Linux): `cat /proc/sys/fs/inotify/max_user_watches`
- Increase limit: `sudo sysctl fs.inotify.max_user_watches=524288`

## Architecture

### Bronze Tier Architecture
```
Gmail → gmail_watcher.py → Needs_Action/ → claude_reasoning.py → Plans/ → Dashboard.md
```

### Silver Tier Architecture
```
Gmail ────────┐
WhatsApp ─────┤
LinkedIn ─────┼→ run_watchers.py → Needs_Action/ → MCP Server → Actions
File System ──┤                                         ↓
              └────────────────────────────────→ approval_system.py
                                                        ↓
                                                   scheduler.py
```

### Golden Tier Architecture
```
                    ┌─→ cross_domain_sync.py → Personal/Business Sync
                    │
                    ├─→ odoo_integration_service.py → ERP Operations
                    │
golden_tier.py ─────┼─→ social_media_service.py → Social Platforms
                    │
                    ├─→ audit_briefing_service.py → Reports
                    │
                    └─→ Enhanced Logging → Logs/Error_Reports/
```

## API Reference

### MCP Server Endpoints (Silver/Golden Tier)

**Base URL**: `http://localhost:8080/mcp`

- `POST /mcp/send_email` - Send email
- `POST /mcp/create_task` - Create task
- `POST /mcp/schedule_meeting` - Schedule meeting
- `POST /mcp/move_file` - Move file
- `POST /mcp/create_note` - Create note
- `POST /mcp/request_human_approval` - Request approval

### Golden Tier Additional Endpoints

**Advanced MCP Server**: `http://localhost:8081/mcp`

- `POST /mcp/predict_outcome` - Predict action outcomes
- `POST /mcp/generate_report` - Generate analytics reports
- `GET /dashboard` - Get system dashboard data
- `GET /mcp/analytics` - Get analytics data
- `GET /mcp/tasks` - Get active tasks

**ML Prediction Engine**: `http://localhost:8082/predict`

- `POST /predict/email_response` - Predict email response times
- `POST /predict/task_completion` - Predict task completion times
- `POST /predict/meeting_time` - Predict best meeting times
- `POST /predict/workload_capacity` - Predict workload capacity
- `POST /predict/productivity_trends` - Predict productivity trends

## Security Considerations

### Credentials Management
- Never commit credentials to git
- Use environment variables for sensitive data
- Rotate API tokens regularly
- Use OAuth 2.0 where possible

### Network Security
- Use HTTPS for all external API calls
- Implement rate limiting
- Use VPN for sensitive operations
- Restrict MCP server access to localhost

### Data Privacy
- Encrypt sensitive data at rest
- Implement proper access controls
- Regular security audits
- GDPR compliance for EU users

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [Your Repo URL]
- Documentation: See `GOLDEN_TIER_SUMMARY.md` for detailed Golden Tier docs
- Email: [Your Email]

## Acknowledgments

Built with Claude Code and powered by Claude Sonnet 4.6.

---

**Version**: 1.0.0 (Golden Tier)
**Last Updated**: March 2026