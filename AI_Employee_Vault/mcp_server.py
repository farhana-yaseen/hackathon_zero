#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server for the Personal AI Employee.

This server handles actions that the AI employee can take, such as sending emails,
managing files, scheduling tasks, etc.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

from aiohttp import web, WSMsgType
import yaml

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServer:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.tools = {
            "send_email": self.send_email,
            "create_task": self.create_task,
            "schedule_meeting": self.schedule_meeting,
            "move_file": self.move_file,
            "create_note": self.create_note,
            "request_human_approval": self.request_human_approval,
        }
        self.app = web.Application()
        self.setup_routes()

    def setup_routes(self):
        """Setup HTTP routes for the MCP server."""
        self.app.router.add_get('/mcp', self.websocket_handler)
        self.app.router.add_post('/mcp/tools', self.tool_handler)

    async def websocket_handler(self, request):
        """Handle WebSocket connections for MCP protocol."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    response = await self.handle_request(data)
                    await ws.send_str(json.dumps(response))
                except json.JSONDecodeError:
                    error_response = {
                        "error": "Invalid JSON in request",
                        "id": data.get("id") if "data" in locals() else None
                    }
                    await ws.send_str(json.dumps(error_response))
                except Exception as e:
                    error_response = {
                        "error": f"Server error: {str(e)}",
                        "id": data.get("id") if "data" in locals() else None
                    }
                    await ws.send_str(json.dumps(error_response))
            elif msg.type == WSMsgType.ERROR:
                logger.error(f'WebSocket connection closed with exception {ws.exception()}')

        logger.info('WebSocket connection closed')
        return ws

    async def tool_handler(self, request):
        """Handle HTTP POST requests for MCP tools."""
        try:
            data = await request.json()
            response = await self.handle_request(data)
            return web.json_response(response)
        except Exception as e:
            logger.error(f"Error in tool handler: {str(e)}")
            return web.json_response({
                "error": f"Server error: {str(e)}"
            }, status=500)

    async def handle_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests."""
        request_id = data.get("id")
        method = data.get("method")
        params = data.get("params", {})

        logger.info(f"Handling request: {method} with params: {params}")

        if method == "initialize":
            return self.handle_initialize()
        elif method == "tools/list":
            return self.handle_list_tools()
        elif method == "call-tool":
            return await self.handle_call_tool(params)
        else:
            return {
                "id": request_id,
                "error": {"message": f"Unknown method: {method}"}
            }

    def handle_initialize(self) -> Dict[str, Any]:
        """Handle MCP initialization."""
        return {
            "id": None,
            "result": {
                "protocolVersion": "1.0",
                "serverInfo": {
                    "name": "Personal-AI-Employee-MCP",
                    "version": "0.1.0"
                },
                "capabilities": {
                    "tools": {
                        "listChanged": False
                    }
                }
            }
        }

    def handle_list_tools(self) -> Dict[str, Any]:
        """Return the list of available tools."""
        tools_info = []

        for tool_name, tool_func in self.tools.items():
            # Get docstring to describe the tool
            description = tool_func.__doc__ or f"Tool for {tool_name}"

            # Define parameters for each tool
            if tool_name == "send_email":
                parameters = {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Recipient email address"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body content"},
                        "cc": {"type": "string", "description": "CC recipients (optional)"},
                        "bcc": {"type": "string", "description": "BCC recipients (optional)"}
                    },
                    "required": ["to", "subject", "body"]
                }
            elif tool_name == "create_task":
                parameters = {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Task title"},
                        "description": {"type": "string", "description": "Task description"},
                        "due_date": {"type": "string", "description": "Due date (YYYY-MM-DD)"},
                        "priority": {"type": "string", "description": "Priority level (low, medium, high)", "default": "medium"}
                    },
                    "required": ["title", "description"]
                }
            elif tool_name == "schedule_meeting":
                parameters = {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Meeting title"},
                        "attendees": {"type": "array", "items": {"type": "string"}, "description": "List of attendee email addresses"},
                        "start_time": {"type": "string", "description": "Start time (ISO format)"},
                        "duration_minutes": {"type": "integer", "description": "Duration in minutes"},
                        "location": {"type": "string", "description": "Meeting location or link"}
                    },
                    "required": ["title", "attendees", "start_time"]
                }
            elif tool_name == "move_file":
                parameters = {
                    "type": "object",
                    "properties": {
                        "source_path": {"type": "string", "description": "Source file path"},
                        "destination_path": {"type": "string", "description": "Destination file path"},
                        "vault_folder": {"type": "string", "description": "Vault folder to move to (Inbox, Needs_Action, etc.)"}
                    },
                    "required": ["source_path", "vault_folder"]
                }
            elif tool_name == "create_note":
                parameters = {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Note title"},
                        "content": {"type": "string", "description": "Note content"},
                        "folder": {"type": "string", "description": "Vault folder to create note in", "default": "Inbox"}
                    },
                    "required": ["title", "content"]
                }
            elif tool_name == "request_human_approval":
                parameters = {
                    "type": "object",
                    "properties": {
                        "request_id": {"type": "string", "description": "Unique identifier for the request"},
                        "description": {"type": "string", "description": "Description of what needs approval"},
                        "urgency": {"type": "string", "description": "Urgency level (low, medium, high)", "default": "medium"}
                    },
                    "required": ["request_id", "description"]
                }
            else:
                parameters = {
                    "type": "object",
                    "properties": {},
                }

            tools_info.append({
                "name": tool_name,
                "description": description,
                "inputSchema": {
                    "type": "object",
                    "properties": parameters["properties"],
                    "required": parameters.get("required", [])
                }
            })

        return {
            "id": None,  # Initialization doesn't have an ID
            "result": {
                "tools": tools_info
            }
        }

    async def handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool with the provided parameters."""
        tool_name = params.get("name")
        tool_arguments = params.get("arguments", {})

        if tool_name not in self.tools:
            return {
                "id": params.get("id"),
                "error": {"message": f"Unknown tool: {tool_name}"}
            }

        try:
            result = await self.tools[tool_name](**tool_arguments)
            return {
                "id": params.get("id"),
                "result": result
            }
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {str(e)}")
            return {
                "id": params.get("id"),
                "error": {"message": f"Tool execution error: {str(e)}"}
            }

    async def send_email(self, to: str, subject: str, body: str, cc: Optional[str] = None, bcc: Optional[str] = None) -> Dict[str, Any]:
        """
        Send an email. In a real implementation, this would connect to an email service.
        For simulation, we'll create a markdown file representing the sent email.
        """
        logger.info(f"Sending email to: {to}, subject: {subject}")

        # Create a record of the sent email in the vault
        sent_dir = os.path.join(self.vault_path, "Sent_Emails")
        os.makedirs(sent_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sent_email_{timestamp}_{to.replace('@', '_at_').replace('.', '_dot_')}.md"
        filepath = os.path.join(sent_dir, filename)

        content = f"""---
type: sent_email
to: "{to}"
subject: "{subject}"
timestamp: "{datetime.now().isoformat()}"
cc: "{cc or ''}"
bcc: "{bcc or ''}"
---

# Sent Email

**To:** {to}
**Subject:** {subject}
**Timestamp:** {datetime.now().isoformat()}

## Email Content
{body}

## Status
- [x] Sent successfully
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            "status": "success",
            "message": f"Email sent to {to}",
            "record_path": filepath
        }

    async def create_task(self, title: str, description: str, due_date: Optional[str] = None, priority: str = "medium") -> Dict[str, Any]:
        """
        Create a task in the task management system.
        For simulation, we'll create a markdown file in the Plans folder.
        """
        logger.info(f"Creating task: {title}")

        plans_dir = os.path.join(self.vault_path, "Plans")
        os.makedirs(plans_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"task_{timestamp}_{title.replace(' ', '_').replace('/', '_')}.md"
        filepath = os.path.join(plans_dir, filename)

        content = f"""---
type: task
title: "{title}"
description: "{description}"
priority: "{priority}"
status: "pending"
created_at: "{datetime.now().isoformat()}"
due_date: "{due_date or ''}"
---

# Task: {title}

**Priority:** {priority}
**Status:** Pending
**Created:** {datetime.now().isoformat()}
**Due Date:** {due_date or 'Not specified'}

## Description
{description}

## Checklist
- [ ] Review task details
- [ ] Begin work on task
- [ ] Complete task
- [ ] Mark as done
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            "status": "success",
            "message": f"Task '{title}' created",
            "task_path": filepath
        }

    async def schedule_meeting(self, title: str, attendees: list, start_time: str, duration_minutes: int, location: Optional[str] = None) -> Dict[str, Any]:
        """
        Schedule a meeting in the calendar system.
        For simulation, we'll create a markdown file in the Updates folder.
        """
        logger.info(f"Scheduling meeting: {title} for {start_time}")

        updates_dir = os.path.join(self.vault_path, "Updates")
        os.makedirs(updates_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"meeting_{timestamp}_{title.replace(' ', '_').replace('/', '_')}.md"
        filepath = os.path.join(updates_dir, filename)

        content = f"""---
type: scheduled_meeting
title: "{title}"
attendees: {json.dumps(attendees)}
start_time: "{start_time}"
duration_minutes: {duration_minutes}
location: "{location or 'Not specified'}"
scheduled_at: "{datetime.now().isoformat()}"
---

# Scheduled Meeting: {title}

**Attendees:** {', '.join(attendees)}
**Start Time:** {start_time}
**Duration:** {duration_minutes} minutes
**Location:** {location or 'Not specified'}
**Scheduled At:** {datetime.now().isoformat()}

## Meeting Details
{title}

## Action Required
- [ ] Prepare for meeting
- [ ] Send calendar invites to attendees
- [ ] Prepare agenda
- [ ] Attend meeting
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            "status": "success",
            "message": f"Meeting '{title}' scheduled for {start_time}",
            "meeting_path": filepath
        }

    async def move_file(self, source_path: str, vault_folder: str, destination_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Move a file within the vault or to a specific location.
        """
        logger.info(f"Moving file from {source_path} to {vault_folder}")

        # Validate vault folder
        valid_folders = ["Inbox", "Needs_Action", "Done", "Plans", "Accounting", "Updates"]
        if vault_folder not in valid_folders:
            raise ValueError(f"Invalid vault folder: {vault_folder}. Must be one of {valid_folders}")

        # Determine the actual destination path
        if destination_path:
            dest_path = destination_path
        else:
            filename = os.path.basename(source_path)
            dest_dir = os.path.join(self.vault_path, vault_folder)
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, filename)

        # Perform the file move
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file does not exist: {source_path}")

        # Handle potential filename conflicts
        counter = 1
        original_dest_path = dest_path
        while os.path.exists(dest_path):
            name_part, ext = os.path.splitext(original_dest_path)
            dest_path = f"{name_part}_{counter}{ext}"
            counter += 1

        os.rename(source_path, dest_path)

        return {
            "status": "success",
            "message": f"File moved from {source_path} to {dest_path}",
            "new_path": dest_path
        }

    async def create_note(self, title: str, content: str, folder: str = "Inbox") -> Dict[str, Any]:
        """
        Create a note in the specified vault folder.
        """
        logger.info(f"Creating note: {title} in folder: {folder}")

        # Validate vault folder
        valid_folders = ["Inbox", "Needs_Action", "Done", "Plans", "Accounting", "Updates"]
        if folder not in valid_folders:
            raise ValueError(f"Invalid vault folder: {folder}. Must be one of {valid_folders}")

        # Create the note
        folder_path = os.path.join(self.vault_path, folder)
        os.makedirs(folder_path, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"note_{timestamp}_{title.replace(' ', '_').replace('/', '_')}.md"
        filepath = os.path.join(folder_path, filename)

        note_content = f"""---
type: note
title: "{title}"
created_at: "{datetime.now().isoformat()}"
---

# {title}

{content}

## Created
{datetime.now().isoformat()}
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(note_content)

        return {
            "status": "success",
            "message": f"Note '{title}' created in {folder}",
            "note_path": filepath
        }

    async def request_human_approval(self, request_id: str, description: str, urgency: str = "medium") -> Dict[str, Any]:
        """
        Request human approval for a specific action.
        Creates a special file that signals to humans that approval is needed.
        """
        logger.info(f"Requesting human approval for: {request_id}")

        # Create an approval request in the Needs_Action folder
        needs_action_dir = os.path.join(self.vault_path, "Needs_Action")
        os.makedirs(needs_action_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"approval_request_{timestamp}_{request_id.replace(' ', '_').replace('/', '_')}.md"
        filepath = os.path.join(needs_action_dir, filename)

        content = f"""---
type: approval_request
request_id: "{request_id}"
urgency: "{urgency}"
status: "pending_approval"
requested_at: "{datetime.now().isoformat()}"
---

# Human Approval Required: {request_id}

**Urgency:** {urgency}
**Requested At:** {datetime.now().isoformat()}
**Status:** Pending Approval

## Description
{description}

## Action Required
- [ ] Review request
- [ ] Provide approval or denial
- [ ] Update status to reflect decision

## Decision Options
- [ ] Approve
- [ ] Deny - Reason: _______________
- [ ] Defer - Reason: _______________

## Notes
Add any notes about the approval decision here.
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            "status": "success",
            "message": f"Approval request for '{request_id}' created and placed in Needs_Action",
            "request_path": filepath
        }


async def main():
    """Main function to start the MCP server."""
    import argparse

    parser = argparse.ArgumentParser(description="Start the Personal AI Employee MCP Server")
    parser.add_argument("--vault-path", required=True, help="Path to the vault directory")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the server on")

    args = parser.parse_args()

    server = MCPServer(args.vault_path)

    logger.info(f"Starting MCP server on port {args.port}")
    logger.info(f"Vault path: {args.vault_path}")

    runner = web.AppRunner(server.app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', args.port)
    await site.start()

    logger.info(f"MCP server running on http://localhost:{args.port}/mcp")

    try:
        # Keep the server running
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())