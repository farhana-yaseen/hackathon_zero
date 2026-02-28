#!/usr/bin/env python3
"""
LinkedIn OAuth Authentication Helper
Helps you get an access token for the LinkedIn API.
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser
import threading

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from LinkedIn."""

    auth_code = None

    def do_GET(self):
        """Handle the OAuth callback."""
        query = urlparse(self.path).query
        params = parse_qs(query)

        if 'code' in params:
            OAuthCallbackHandler.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                    <h1>Authentication Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
            """)
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                    <h1>Authentication Failed</h1>
                    <p>No authorization code received.</p>
                </body>
                </html>
            """)

    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


def get_access_token_manual():
    """Guide user through manual token generation."""
    print("\n" + "="*60)
    print("MANUAL TOKEN GENERATION")
    print("="*60)
    print("\nFollow these steps:")
    print("\n1. Go to: https://www.linkedin.com/developers/")
    print("2. Select your app")
    print("3. Go to the 'Auth' tab")
    print("4. Note your Client ID and Client Secret")
    print("\n5. Generate a token using LinkedIn's OAuth 2.0 flow:")
    print("   - Use this URL format:")
    print("   https://www.linkedin.com/oauth/v2/authorization?")
    print("   response_type=code&client_id=YOUR_CLIENT_ID&")
    print("   redirect_uri=http://localhost:8080/callback&")
    print("   scope=r_liteprofile%20w_member_social")
    print("\n6. After authorization, exchange the code for an access token")
    print("   using LinkedIn's token endpoint")
    print("\nOR use LinkedIn's OAuth Test Console:")
    print("https://www.linkedin.com/developers/tools/oauth")

    print("\n" + "="*60)
    token = input("\nPaste your access token here: ").strip()

    if not token:
        print("No token provided. Exiting.")
        return None

    return token


def save_token(token, vault_path):
    """Save the access token to a file."""
    from datetime import datetime

    token_data = {
        "access_token": token,
        "expires_in": 5184000,  # 60 days
        "created_at": datetime.now().isoformat()
    }

    token_path = os.path.join(vault_path, 'linkedin_token.json')

    with open(token_path, 'w') as f:
        json.dump(token_data, f, indent=2)

    print(f"\n✓ Token saved to: {token_path}")
    print("\nIMPORTANT: Keep this file secure and add it to .gitignore!")


def main():
    if len(sys.argv) != 2:
        print("Usage: python authenticate_linkedin.py <vault_path>")
        sys.exit(1)

    vault_path = sys.argv[1]

    if not os.path.exists(vault_path):
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)

    print("\n" + "="*60)
    print("LINKEDIN AUTHENTICATION HELPER")
    print("="*60)
    print("\nThis script helps you authenticate with LinkedIn API.")
    print("\nYou'll need:")
    print("1. A LinkedIn Developer App")
    print("2. Client ID and Client Secret")
    print("3. 'Share on LinkedIn' product access")

    print("\n" + "="*60)
    print("Choose authentication method:")
    print("1. Manual (paste access token)")
    print("2. Exit")

    choice = input("\nEnter choice: ").strip()

    if choice == '1':
        token = get_access_token_manual()
        if token:
            save_token(token, vault_path)
            print("\n✓ Authentication complete!")
            print("\nYou can now run the LinkedIn watcher:")
            print(f"  python linkedin_watcher.py {vault_path}")
    else:
        print("Exiting.")


if __name__ == "__main__":
    main()
