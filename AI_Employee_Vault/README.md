# Personal AI Employee - Bronze Tier

Welcome to your Personal AI Employee system! This Bronze Tier implementation includes:

## Components Created

### 1. Obsidian Vault Structure
- `/Inbox` - New items to process
- `/Needs_Action` - Items requiring attention
- `/Done` - Completed tasks
- `/Plans` - Active plans in progress
- `/Accounting` - Financial records
- `/Updates` - Daily reports

### 2. Core Files
- `Dashboard.md` - Real-time system overview
- `Company_Handbook.md` - Operational rules and policies
- `SKILL.md` - Template for creating Agent Skills

### 3. Gmail Watcher System
- `base_watcher.py` - Abstract base class for all watchers
- `gmail_watcher.py` - Monitors Gmail for new important emails
- `setup_gmail_credentials.md` - Instructions for Gmail API setup

### 4. Claude Reasoning Engine
- `claude_reasoning.py` - Processes items from Needs_Action
- Creates Plan.md files with checkboxes for tasks
- Moves completed items to Done folder

### 5. Testing Framework
- `test_bronze_tier.py` - Demonstrates the complete workflow
- `requirements.txt` - Python dependencies

## Setup Instructions

### 1. Install Dependencies
```bash
cd AI_Employee_Vault
pip install -r requirements.txt
```

### 2. Set up Gmail API Access
1. Follow instructions in `setup_gmail_credentials.md`
2. Place `credentials.json` in your vault directory

### 3. Run the Test
```bash
python test_bronze_tier.py ./AI_Employee_Vault
```

### 4. Manual Operations
- Check `Plans/Plan_*.md` for daily tasks
- Check off completed items with `[x]`
- Run `python claude_reasoning.py ./AI_Employee_Vault check` to move completed items to Done

## How It Works

1. **Watcher** monitors Gmail for new important emails
2. **Creates** markdown files in `/Needs_Action` with frontmatter
3. **Claude reasoning** processes new items and creates Plan.md
4. **Human/AI** completes tasks and checks boxes
5. **System** moves completed items to `/Done` and updates Dashboard

## Next Steps

When ready to advance to Silver Tier, you'll add:
- WhatsApp and File System watchers
- MCP servers for actions
- Human-in-the-loop approval system
- Automated scheduling