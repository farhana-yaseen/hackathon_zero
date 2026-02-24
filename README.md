# Hackathon Zero - Personal AI Employee

## Overview
This project implements a Personal AI Employee system with multiple tiers of functionality.

## Silver Tier Features
The Silver Tier includes advanced automation capabilities:

- **Multi-channel Watchers**: Monitors Gmail, WhatsApp, and file system changes
- **MCP Server**: Provides a suite of tools for automation (send_email, create_task, schedule_meeting, move_file, create_note, request_human_approval)
- **Approval System**: Handles human-in-the-loop approvals for important actions
- **Scheduler**: Automated task scheduling and execution
- **File System Monitoring**: Watches the Inbox directory for new files to process

## Components
- `gmail_watcher.py`: Monitors Gmail for new messages
- `whatsapp_watcher.py`: Processes WhatsApp messages from simulation files
- `file_system_watcher.py`: Watches for file changes in the Inbox
- `mcp_server.py`: Provides automation tools via HTTP/MCP interface
- `scheduler.py`: Manages scheduled tasks
- `approval_system.py`: Handles approval workflows
- `silver_tier.py`: Orchestrates all Silver Tier components
- `run_watchers.py`: Coordinates all watcher processes

## Usage
To start the Silver Tier orchestration:
```bash
python main.py
```

Or directly:
```bash
python AI_Employee_Vault/silver_tier.py --vault-path AI_Employee_Vault
```

## Directories
- `Inbox/`: Monitored for new files to process
- `Needs_Action/`: Items requiring human attention
- `Plans/`: Generated action plans
- `Done/`: Completed tasks
- `WhatsApp_Sim/`: WhatsApp message simulation files
- `Schedules/`: Scheduled task definitions
- `Approvals/`: Approval workflow files
- `Sent_Emails/`: Archive of sent emails