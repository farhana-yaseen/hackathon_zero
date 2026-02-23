#!/usr/bin/env python3
"""
Automated Scheduling System for Personal AI Employee

This system manages scheduled tasks and events, executing them at specified times.
"""

import os
import glob
import json
import re
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Callable
import logging
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ScheduledTask:
    id: str
    name: str
    execute_time: datetime
    action: Callable
    args: tuple = ()
    kwargs: dict = None
    recurring: bool = False
    recurrence_interval: timedelta = None  # For recurring tasks
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None

class Scheduler:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.tasks: List[ScheduledTask] = []
        self.running = False
        self.scheduler_thread = None
        self.created_at = datetime.now()

        # Ensure schedules directory exists
        self.schedules_dir = os.path.join(vault_path, "Schedules")
        os.makedirs(self.schedules_dir, exist_ok=True)

    def add_task(self, name: str, execute_time: datetime, action: Callable,
                 args: tuple = (), kwargs: dict = None, recurring: bool = False,
                 recurrence_interval: timedelta = None) -> str:
        """Add a new scheduled task."""
        task_id = f"task_{int(time.time())}_{len(self.tasks)}"

        task = ScheduledTask(
            id=task_id,
            name=name,
            execute_time=execute_time,
            action=action,
            args=args,
            kwargs=kwargs or {},
            recurring=recurring,
            recurrence_interval=recurrence_interval,
            status=TaskStatus.PENDING,
            created_at=datetime.now()
        )

        self.tasks.append(task)
        logger.info(f"Added task '{name}' (ID: {task_id}) scheduled for {execute_time}")

        # Save task to file for persistence
        self._save_task_to_file(task)

        return task_id

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        for task in self.tasks:
            if task.id == task_id:
                task.status = TaskStatus.CANCELLED
                logger.info(f"Cancelled task '{task.name}' (ID: {task_id})")

                # Update the task file
                self._update_task_file(task)
                return True

        logger.warning(f"Task with ID {task_id} not found")
        return False

    def get_due_tasks(self) -> List[ScheduledTask]:
        """Get all tasks that are due for execution."""
        now = datetime.now()
        due_tasks = []

        for task in self.tasks:
            if (task.status == TaskStatus.PENDING and
                task.execute_time <= now and
                task.execute_time >= self.created_at):
                due_tasks.append(task)

        return due_tasks

    def execute_task(self, task: ScheduledTask) -> bool:
        """Execute a single task."""
        try:
            task.status = TaskStatus.RUNNING
            logger.info(f"Executing task '{task.name}' (ID: {task.id})")

            # Execute the action
            result = task.action(*task.args, **task.kwargs)

            task.status = TaskStatus.COMPLETED
            logger.info(f"Completed task '{task.name}' (ID: {task.id})")

            # Update the task file
            self._update_task_file(task)

            # Handle recurring tasks
            if task.recurring and task.recurrence_interval:
                new_execute_time = task.execute_time + task.recurrence_interval
                task.execute_time = new_execute_time
                task.status = TaskStatus.PENDING
                logger.info(f"Rescheduled recurring task '{task.name}' for {new_execute_time}")

                # Update the task file again
                self._update_task_file(task)

            return True
        except Exception as e:
            task.status = TaskStatus.FAILED
            logger.error(f"Failed to execute task '{task.name}' (ID: {task.id}): {str(e)}")

            # Update the task file
            self._update_task_file(task)
            return False

    def start(self):
        """Start the scheduler in a background thread."""
        if self.running:
            logger.warning("Scheduler is already running")
            return

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Scheduler started")

    def stop(self):
        """Stop the scheduler."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=2)  # Wait up to 2 seconds for graceful shutdown
        logger.info("Scheduler stopped")

    def _run_scheduler(self):
        """Main scheduler loop."""
        logger.info("Scheduler loop started")

        while self.running:
            try:
                # Check for due tasks
                due_tasks = self.get_due_tasks()

                for task in due_tasks:
                    self.execute_task(task)

                # Sleep for a short time before checking again
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(5)  # Sleep longer on error

        logger.info("Scheduler loop ended")

    def get_task_status(self, task_id: str) -> TaskStatus:
        """Get the status of a specific task."""
        for task in self.tasks:
            if task.id == task_id:
                return task.status

        return None

    def get_all_tasks(self) -> List[Dict]:
        """Get information about all tasks."""
        task_list = []
        for task in self.tasks:
            task_list.append({
                'id': task.id,
                'name': task.name,
                'execute_time': task.execute_time.isoformat(),
                'status': task.status.value,
                'recurring': task.recurring,
                'created_at': task.created_at.isoformat()
            })

        return task_list

    def _save_task_to_file(self, task: ScheduledTask):
        """Save task information to a file in the schedules directory."""
        task_data = {
            'id': task.id,
            'name': task.name,
            'execute_time': task.execute_time.isoformat(),
            'status': task.status.value,
            'recurring': task.recurring,
            'recurrence_interval': task.recurrence_interval.total_seconds() if task.recurrence_interval else None,
            'created_at': task.created_at.isoformat()
        }

        filename = f"scheduled_task_{task.id}.json"
        filepath = os.path.join(self.schedules_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(task_data, f, indent=2)

    def _update_task_file(self, task: ScheduledTask):
        """Update the task file with current status."""
        self._save_task_to_file(task)

    def load_tasks_from_files(self):
        """Load tasks from saved files."""
        pattern = os.path.join(self.schedules_dir, "scheduled_task_*.json")
        task_files = glob.glob(pattern)

        for file_path in task_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)

                # For now, we'll just register that the task exists by loading it into our tracking
                # In a real implementation, we'd reconstruct the callable actions
                logger.info(f"Loaded task from file: {task_data['name']} (ID: {task_data['id']})")
            except Exception as e:
                logger.error(f"Error loading task from file {file_path}: {str(e)}")

def demo_action(name: str, message: str = "Default message"):
    """Demo action for testing the scheduler."""
    logger.info(f"Demo action executed: {name} - {message}")
    return f"Action '{name}' completed at {datetime.now()}"

def schedule_daily_report(vault_path: str):
    """Schedule a daily report generation task."""
    def generate_daily_report():
        # Create a daily report in the Updates folder
        updates_dir = os.path.join(vault_path, "Updates")
        os.makedirs(updates_dir, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        report_filename = f"daily_report_{today}.md"
        report_path = os.path.join(updates_dir, report_filename)

        # Count items in each folder
        folders = ["Inbox", "Needs_Action", "Done", "Plans", "Accounting", "Updates"]
        folder_counts = {}
        for folder in folders:
            folder_path = os.path.join(vault_path, folder)
            if os.path.exists(folder_path):
                count = len([f for f in os.listdir(folder_path) if f.endswith('.md')])
                folder_counts[folder] = count

        report_content = f"""---
type: daily_report
date: "{today}"
generated_at: "{datetime.now().isoformat()}"
---

# Daily Report - {today}

## Summary
- Inbox: {folder_counts.get('Inbox', 0)} items
- Needs Action: {folder_counts.get('Needs_Action', 0)} items
- Done: {folder_counts.get('Done', 0)} items
- Plans: {folder_counts.get('Plans', 0)} items
- Accounting: {folder_counts.get('Accounting', 0)} items
- Updates: {folder_counts.get('Updates', 0)} items

## Generated
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        logger.info(f"Daily report generated: {report_path}")

    return generate_daily_report

def main():
    import sys
    from datetime import datetime, timedelta

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scheduler.py <vault_path> [action] [parameters]")
        print("\nActions:")
        print("  start              - Start the scheduler (continuous mode)")
        print("  add_demo_task      - Add a demo task for testing")
        print("  list_tasks         - List all scheduled tasks")
        print("  status <task_id>   - Get status of a specific task")
        print("  cancel <task_id>   - Cancel a scheduled task")
        print("  schedule_report    - Schedule a daily report")
        sys.exit(1)

    vault_path = sys.argv[1]

    # Initialize scheduler
    scheduler = Scheduler(vault_path)

    # Load existing tasks
    scheduler.load_tasks_from_files()

    if len(sys.argv) < 3:
        action = "interactive"
    else:
        action = sys.argv[2]

    if action == "start":
        print("Starting scheduler...")
        scheduler.start()

        try:
            # Keep running
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            print("\nStopping scheduler...")
            scheduler.stop()
            print("Scheduler stopped.")

    elif action == "add_demo_task":
        # Schedule a demo task for 1 minute from now
        execute_time = datetime.now() + timedelta(minutes=1)
        task_id = scheduler.add_task(
            name="Demo Task",
            execute_time=execute_time,
            action=demo_action,
            args=("Demo Task", "This is a test of the scheduler"),
            kwargs={}
        )
        print(f"Added demo task with ID: {task_id}")
        print(f"Scheduled for: {execute_time}")

    elif action == "list_tasks":
        tasks = scheduler.get_all_tasks()
        if tasks:
            print(f"Found {len(tasks)} scheduled tasks:\n")
            for task in tasks:
                print(f"- ID: {task['id']}")
                print(f"  Name: {task['name']}")
                print(f"  Execute Time: {task['execute_time']}")
                print(f"  Status: {task['status']}")
                print(f"  Recurring: {task['recurring']}")
                print()
        else:
            print("No scheduled tasks found.")

    elif action == "status":
        if len(sys.argv) < 4:
            print("Usage: python scheduler.py <vault_path> status <task_id>")
            sys.exit(1)

        task_id = sys.argv[3]
        status = scheduler.get_task_status(task_id)
        if status:
            print(f"Task {task_id} status: {status.value}")
        else:
            print(f"Task {task_id} not found.")

    elif action == "cancel":
        if len(sys.argv) < 4:
            print("Usage: python scheduler.py <vault_path> cancel <task_id>")
            sys.exit(1)

        task_id = sys.argv[3]
        result = scheduler.cancel_task(task_id)
        if result:
            print(f"Task {task_id} cancelled successfully.")
        else:
            print(f"Failed to cancel task {task_id}.")

    elif action == "schedule_report":
        # Schedule a daily report to run every day at 9 AM
        now = datetime.now()
        tomorrow_9am = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

        # Create the report generation function
        report_func = schedule_daily_report(vault_path)

        task_id = scheduler.add_task(
            name="Daily Report Generation",
            execute_time=tomorrow_9am,
            action=report_func,
            recurring=True,
            recurrence_interval=timedelta(days=1)  # Every day
        )

        print(f"Scheduled daily report with ID: {task_id}")
        print(f"First run scheduled for: {tomorrow_9am}")
        print("This task will repeat daily.")

    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()