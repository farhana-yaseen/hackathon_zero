import os
import pickle
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from base_watcher import BaseWatcher
import logging

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send']

class GmailWatcher(BaseWatcher):
    """
    Watches Gmail inbox for new emails and creates markdown files in the vault.
    """

    def __init__(self, vault_path: str, interval: int = 60, max_emails_per_run: int = 10):
        super().__init__(vault_path, interval)
        
        self.max_emails_per_run = max_emails_per_run
        self.service = self.authenticate_gmail()

    def authenticate_gmail(self):
        """Authenticate with Gmail API using OAuth2."""
        creds = None
        # The file token.pickle stores the user's access and refresh tokens.
        token_path = os.path.join(self.vault_path, 'token.pickle')

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                credentials_path = os.path.join(self.vault_path, 'credentials.json')
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(
                        "credentials.json not found. Please create it via Google API Console."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def check_for_updates(self):
        """Check Gmail for new unread emails and sent emails."""
        try:
            # Calculate the time window (last check or last hour if no previous check)
            if self.last_check:
                query_time = self.last_check
            else:
                query_time = datetime.now() - timedelta(hours=1)

            # Format the query time for Gmail API
            query_time_str = query_time.strftime('%Y/%m/%d %H:%M:%S')

            emails = []

            # Query for unread emails (received)
            query_received = f'is:unread after:{query_time_str}'
            results_received = self.service.users().messages().list(
                userId='me', q=query_received, maxResults=self.max_emails_per_run).execute()
            messages_received = results_received.get('messages', [])

            for msg in messages_received:
                email_data = self.get_email_details(msg['id'])
                if email_data:
                    email_data['email_type'] = 'received'
                    emails.append(email_data)

            # Query for sent emails
            query_sent = f'in:sent after:{query_time_str}'
            results_sent = self.service.users().messages().list(
                userId='me', q=query_sent, maxResults=self.max_emails_per_run).execute()
            messages_sent = results_sent.get('messages', [])

            for msg in messages_sent:
                email_data = self.get_email_details(msg['id'])
                if email_data:
                    email_data['email_type'] = 'sent'
                    emails.append(email_data)

            return emails
        except Exception as e:
            logger.error(f"Error checking Gmail: {str(e)}")
            return []

    def get_email_details(self, msg_id):
        """Retrieve details for a specific email message."""
        try:
            message = self.service.users().messages().get(userId='me', id=msg_id).execute()

            # Extract headers
            headers = {item['name'].lower(): item['value'] for item in message['payload']['headers']}

            # Extract body
            body = self.extract_body(message)

            # Determine importance based on various factors
            is_important = self.is_important_email(headers, message)

            email_data = {
                'id': msg_id,
                'from': headers.get('from', 'Unknown'),
                'to': headers.get('to', 'Unknown'),
                'subject': headers.get('subject', '(No Subject)'),
                'date': headers.get('date', ''),
                'body': body[:2000],  # Limit body length
                'is_important': is_important,
                'labels': message.get('labelIds', []),
                'size_estimate': message.get('sizeEstimate', 0),
                'snippet': message.get('snippet', ''),
            }

            return email_data
        except Exception as e:
            logger.error(f"Error getting email details: {str(e)}")
            return None

    def extract_body(self, message):
        """Extract the body of the email."""
        body = ""
        payload = message['payload']

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8')
                    break
                elif part['mimeType'] == 'text/html' and not body:
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8')
        else:
            if 'body' in payload and 'data' in payload['body']:
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8')

        return body

    def is_important_email(self, headers, message):
        """Determine if an email is important based on various criteria."""
        # Check for important labels
        important_labels = ['IMPORTANT', 'CATEGORY_PERSONAL', 'CATEGORY_SOCIAL', 'CATEGORY_UPDATES', 'CATEGORY_FORUMS']
        if any(label in message.get('labelIds', []) for label in important_labels):
            return True

        # Check sender (from known contacts or frequent correspondents)
        from_addr = headers.get('from', '').lower()
        important_senders = [
            'boss@company.com',  # Example - customize based on your needs
            'ceo@company.com',
            'accounts@company.com'
        ]
        if any(sender in from_addr for sender in important_senders):
            return True

        # Check subject for urgency indicators
        subject = headers.get('subject', '').lower()
        urgent_indicators = ['urgent', 'asap', 'important', 'critical', 'immediate', 'attention']
        if any(indicator in subject for indicator in urgent_indicators):
            return True

        return False

    def create_markdown_file(self, email_data):
        """Create a markdown file for the email in the appropriate vault folder."""
        # Determine folder based on email type and importance
        email_type = email_data.get('email_type', 'received')

        if email_type == 'sent':
            folder = 'Sent'
        elif email_data['is_important']:
            folder = 'Needs_Action'
        else:
            folder = 'Inbox'

        # Sanitize filename
        subject = email_data['subject'][:50].replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        if not subject:
            subject = "no_subject"

        # Create frontmatter with email details
        frontmatter = f"""---
type: email
email_type: {email_type}
from: "{email_data['from']}"
to: "{email_data['to']}"
subject: "{email_data['subject']}"
date: "{email_data['date']}"
is_important: {email_data['is_important']}
labels: {email_data['labels']}
id: "{email_data['id']}"
---

"""

        # Create suggested actions based on content
        suggested_actions = self.generate_suggested_actions(email_data)

        # Adjust header based on email type
        if email_type == 'sent':
            header = f"# Email sent to {email_data['to']}"
        else:
            header = f"# Email from {email_data['from']}"

        # Combine everything
        content = f"""{frontmatter}

{header}

**Subject:** {email_data['subject']}

**Date:** {email_data['date']}

**Labels:** {', '.join(email_data['labels'])}

## Email Body
{email_data['body']}

## Suggested Actions
{suggested_actions}

## Manual Actions
- [ ] Review content
- [ ] Determine priority
- [ ] Take appropriate action
- [ ] Mark as complete when done
"""

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if email_type == 'sent':
            filename = f"sent_{timestamp}_{subject}"
        else:
            filename = f"email_{timestamp}_{subject}"

        return self.write_to_vault(folder, filename, content)

    def generate_suggested_actions(self, email_data):
        """Generate suggested actions based on email content."""
        actions = []
        subject = email_data['subject'].lower()
        body = email_data['body'].lower()

        # Check for common patterns that suggest specific actions
        if 'meeting' in subject or 'meeting' in body:
            actions.append("- [ ] Schedule meeting in calendar")
        if 'payment' in subject or 'invoice' in subject or 'payment' in body or 'invoice' in body:
            actions.append("- [ ] Review payment details")
            actions.append("- [ ] Process payment if approved")
        if 'approval' in subject or 'approve' in body:
            actions.append("- [ ] Review request for approval")
        if 'urgent' in subject or 'asap' in subject:
            actions.append("- [ ] Handle with priority")

        # Add default actions
        if not actions:
            actions.extend([
                "- [ ] Respond appropriately",
                "- [ ] File in appropriate category",
                "- [ ] Follow up if needed"
            ])

        return '\n'.join(actions)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python gmail_watcher.py <vault_path>")
        sys.exit(1)

    vault_path = sys.argv[1]
    watcher = GmailWatcher(vault_path)
    watcher.run_once()