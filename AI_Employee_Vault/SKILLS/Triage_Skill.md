# Agent Skill: Triage & Intake
**Role:** Digital Front Desk
**Primary Objective:** Categorize incoming data from /Needs_Action.

### Instructions:
1. Scan `/Needs_Action` for new files created by Python Watchers.
2. Read the metadata. If it is an Email, move it to `/Comms/Inbox`. If it is a Receipt, move it to `/Accounting/Inbox`.
3. Update `Dashboard.md` with the count of pending items.

### Required Tools:
- mcp:filesystem (read/write/move)