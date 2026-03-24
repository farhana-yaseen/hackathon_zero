#!/usr/bin/env python3
"""
LinkedIn Automation using Playwright
Integrates with the AI Employee system for LinkedIn posting and monitoring
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright
import tempfile

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LinkedInPlaywrightAutomation:
    def __init__(self, vault_path: str, credentials: dict = None):
        """
        Initialize LinkedIn automation with Playwright

        Args:
            vault_path: Path to the AI Employee vault
            credentials: LinkedIn credentials dictionary with 'email' and 'password'
        """
        self.vault_path = vault_path
        self.credentials = credentials or {}
        self.browser = None
        self.page = None
        self.is_logged_in = False

        # Create necessary directories
        self.linkedin_posts_dir = os.path.join(vault_path, "LinkedIn_Posts")
        self.linkedin_triggers_dir = os.path.join(vault_path, "LinkedIn_Triggers")
        self.browser_actions_dir = os.path.join(vault_path, "Browser_Actions")

        for directory in [self.linkedin_posts_dir, self.linkedin_triggers_dir, self.browser_actions_dir]:
            os.makedirs(directory, exist_ok=True)

    async def setup_browser(self):
        """Set up the Playwright browser instance."""
        logger.info("Setting up Playwright browser...")

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Set to True for production
            slow_mo=100  # Slow down actions for reliability
        )
        self.page = await self.browser.new_page()

        # Set viewport size
        await self.page.set_viewport_size({"width": 1920, "height": 1080})

        logger.info("Browser setup complete")
        return True

    async def login(self, email: str = None, password: str = None):
        """
        Login to LinkedIn

        Args:
            email: LinkedIn email (if not provided in credentials)
            password: LinkedIn password (if not provided in credentials)
        """
        email = email or self.credentials.get('email')
        password = password or self.credentials.get('password')

        if not email or not password:
            raise ValueError("LinkedIn credentials not provided")

        logger.info("Attempting LinkedIn login...")

        # Navigate to LinkedIn login page
        await self.page.goto("https://www.linkedin.com/login")

        # Fill in email
        await self.page.fill("#username", email)

        # Fill in password
        await self.page.fill("#password", password)

        # Click login button
        await self.page.click('button[type="submit"]')

        # Wait for login to complete
        try:
            # Wait for the feed page to load (indicates successful login)
            await self.page.wait_for_url("**/feed**", timeout=10000)
            self.is_logged_in = True
            logger.info("LinkedIn login successful")

            # Record the login action
            await self._record_browser_action("linkedin_login", {
                "status": "success",
                "timestamp": datetime.now().isoformat()
            })

        except Exception as e:
            # Check if we're still on login page (login failed)
            current_url = self.page.url
            if "login" in current_url:
                logger.error(f"LinkedIn login failed: {str(e)}")

                # Record the failed login action
                await self._record_browser_action("linkedin_login", {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })

                return False
            else:
                # If we're not on login page, assume login succeeded
                self.is_logged_in = True
                logger.info("LinkedIn login appeared successful")

        return self.is_logged_in

    async def create_post(self, content: str, visibility="PUBLIC"):
        """
        Create a LinkedIn post

        Args:
            content: Content of the post
            visibility: Post visibility ("PUBLIC", "CONNECTIONS_ONLY", etc.)
        """
        if not self.is_logged_in:
            raise Exception("Must be logged in to LinkedIn to create posts")

        logger.info(f"Creating LinkedIn post with visibility: {visibility}")

        # Click on the post creation area
        try:
            # Wait for the post textbox to be available
            await self.page.wait_for_selector("div[contenteditable='true'][data-test-id='artdeco-text-input-content-editable']", timeout=10000)
            textbox = await self.page.query_selector("div[contenteditable='true'][data-test-id='artdeco-text-input-content-editable']")

            if textbox:
                # Clear existing content and type new content
                await textbox.click()
                await self.page.keyboard.press("Control+A")  # Select all
                await self.page.keyboard.press("Delete")    # Delete selected
                await textbox.type(content)

                # Add a short delay to ensure content is typed
                await self.page.wait_for_timeout(1000)

                # Find and click the visibility button (usually a globe icon for public)
                if visibility == "PUBLIC":
                    # Look for the audience selector button
                    visibility_button = await self.page.query_selector("button[aria-label='Change who can see this post']")
                    if visibility_button:
                        await visibility_button.click()

                        # Select public visibility
                        public_option = await self.page.query_selector("button[aria-label='Public']")
                        if public_option:
                            await public_estimator
                            await self.page.wait_for_timeout(500)

                # Click the post button
                post_button = await self.page.query_selector("button[aria-label='Post']")
                if post_button:
                    await post_button.click()

                    # Wait for post to be published
                    await self.page.wait_for_timeout(2000)

                    # Record the post action
                    post_id = f"post_{int(time.time())}"
                    await self._record_linkedin_post(content, post_id, visibility)

                    logger.info(f"LinkedIn post created successfully: {post_id}")
                    return {"status": "success", "post_id": post_id}
                else:
                    logger.error("Could not find post button")
                    return {"status": "failed", "error": "Could not find post button"}
            else:
                logger.error("Could not find post textbox")
                return {"status": "failed", "error": "Could not find post textbox"}

        except Exception as e:
            logger.error(f"Error creating LinkedIn post: {str(e)}")
            return {"status": "failed", "error": str(e)}

    async def monitor_feed(self, max_posts=10):
        """
        Monitor LinkedIn feed for new posts/interactions

        Args:
            max_posts: Maximum number of posts to check
        """
        if not self.is_logged_in:
            raise Exception("Must be logged in to LinkedIn to monitor feed")

        logger.info(f"Monitoring LinkedIn feed for up to {max_posts} posts")

        try:
            # Navigate to the feed if not already there
            current_url = self.page.url
            if "feed" not in current_url:
                await self.page.goto("https://www.linkedin.com/feed/")
                await self.page.wait_for_timeout(2000)

            # Scroll down to load more posts
            for _ in range(3):
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                await self.page.wait_for_timeout(2000)

            # Get posts from the feed
            post_selectors = [
                "article[data-id]",  # Main article posts
                "div.feed-shared-update-v2",  # Shared updates
            ]

            posts = []
            for selector in post_selectors:
                elements = await self.page.query_selector_all(selector)
                for element in elements[:max_posts]:  # Limit to max_posts
                    try:
                        # Extract post information
                        post_text_elem = await element.query_selector("p, span, div")
                        post_text = ""
                        if post_text_elem:
                            post_text = await post_text_elem.text_content()
                            post_text = post_text.strip()[:200]  # Limit length

                        posts.append({
                            "preview": post_text,
                            "timestamp": datetime.now().isoformat(),
                            "source": "feed_monitor"
                        })

                        if len(posts) >= max_posts:
                            break

                    except Exception as e:
                        logger.warning(f"Could not extract post info: {str(e)}")
                        continue

                if len(posts) >= max_posts:
                    break

            logger.info(f"Found {len(posts)} posts in feed")

            # Record the monitoring action
            await self._record_browser_action("feed_monitoring", {
                "posts_found": len(posts),
                "timestamp": datetime.now().isoformat()
            })

            return posts

        except Exception as e:
            logger.error(f"Error monitoring LinkedIn feed: {str(e)}")
            return []

    async def check_notifications(self):
        """
        Check LinkedIn notifications
        """
        if not self.is_logged_in:
            raise Exception("Must be logged in to LinkedIn to check notifications")

        logger.info("Checking LinkedIn notifications")

        try:
            # Click on the notification bell icon
            notification_button = await self.page.query_selector("li-icon[type='notifications-icon']")
            if notification_button:
                await notification_button.click()
                await self.page.wait_for_timeout(2000)

                # Get notification count
                notification_elements = await self.page.query_selector_all("div.notifications-list__item")
                notification_count = len(notification_elements)

                # Get recent notifications
                notifications = []
                for elem in notification_elements[:5]:  # Get first 5 notifications
                    try:
                        text_elem = await elem.query_selector("span")
                        if text_elem:
                            text = await text_elem.text_content()
                            notifications.append({
                                "text": text.strip(),
                                "timestamp": datetime.now().isoformat()
                            })
                    except Exception:
                        continue

                logger.info(f"Found {notification_count} notifications")

                # Record the notification check
                await self._record_browser_action("notification_check", {
                    "count": notification_count,
                    "timestamp": datetime.now().isoformat()
                })

                return {
                    "count": notification_count,
                    "notifications": notifications
                }
            else:
                logger.warning("Could not find notification button")
                return {"count": 0, "notifications": []}

        except Exception as e:
            logger.error(f"Error checking LinkedIn notifications: {str(e)}")
            return {"count": 0, "notifications": []}

    async def get_profile_info(self):
        """
        Get LinkedIn profile information
        """
        if not self.is_logged_in:
            raise Exception("Must be logged in to LinkedIn to get profile info")

        logger.info("Getting LinkedIn profile information")

        try:
            # Navigate to profile page
            await self.page.goto("https://www.linkedin.com/in/your-profile-url")  # This would need to be customized
            await self.page.wait_for_timeout(2000)

            # Extract profile information
            profile_info = {}

            # Get name
            name_elem = await self.page.query_selector("h1")
            if name_elem:
                profile_info["name"] = await name_elem.text_content()

            # Get headline
            headline_elem = await self.page.query_selector("h2")
            if headline_elem:
                profile_info["headline"] = await headline_elem.text_content()

            # Get connection count
            conn_elem = await self.page.query_selector("span[t-dir='ltr']")
            if conn_elem:
                profile_info["connections"] = await conn_elem.text_content()

            logger.info(f"Retrieved profile info for: {profile_info.get('name', 'Unknown')}")

            # Record the profile check
            await self._record_browser_action("profile_check", {
                "profile_name": profile_info.get("name", "Unknown"),
                "timestamp": datetime.now().isoformat()
            })

            return profile_info

        except Exception as e:
            logger.error(f"Error getting LinkedIn profile info: {str(e)}")
            return {}

    async def _record_linkedin_post(self, content: str, post_id: str, visibility: str):
        """Record a LinkedIn post to the vault."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_{timestamp}_{post_id}.md"
        filepath = os.path.join(self.linkedin_posts_dir, filename)

        content_md = f"""---
type: linkedin_post
post_id: "{post_id}"
visibility: "{visibility}"
created_at: "{datetime.now().isoformat()}"
status: "published"
---

# LinkedIn Post

**Visibility:** {visibility}
**Created At:** {datetime.now().isoformat()}

## Content
{content}

## Status
- [x] Post published
- [ ] Monitor engagement
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content_md)

        logger.info(f"LinkedIn post recorded: {filepath}")

    async def _record_browser_action(self, action_type: str, details: dict):
        """Record a browser action to the vault."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"browser_action_{action_type}_{timestamp}.json"
        filepath = os.path.join(self.browser_actions_dir, filename)

        action_record = {
            "type": "browser_action",
            "action": action_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(action_record, f, indent=2)

        logger.info(f"Browser action recorded: {filepath}")

    async def close(self):
        """Close the browser and cleanup."""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        logger.info("Browser closed and cleanup complete")


class LinkedInMCPAdapter:
    """
    Adapter to integrate LinkedIn Playwright automation with MCP server
    """
    def __init__(self, vault_path: str, credentials: dict = None):
        self.automation = LinkedInPlaywrightAutomation(vault_path, credentials)
        self.is_setup = False

    async def setup(self):
        """Setup the LinkedIn automation."""
        if not self.is_setup:
            await self.automation.setup_browser()
            self.is_setup = True
        return True

    async def post_to_linkedin(self, content: str, visibility: str = "PUBLIC") -> dict:
        """
        MCP-compatible method to post to LinkedIn

        Args:
            content: Content to post
            visibility: Visibility setting (PUBLIC, CONNECTIONS_ONLY, etc.)
        """
        try:
            await self.setup()

            # Attempt login if not already logged in
            if not self.automation.is_logged_in:
                email = self.automation.credentials.get('email')
                password = self.automation.credentials.get('password')

                if email and password:
                    login_success = await self.automation.login(email, password)
                    if not login_success:
                        return {
                            "status": "error",
                            "message": "Failed to login to LinkedIn"
                        }
                else:
                    return {
                        "status": "error",
                        "message": "LinkedIn credentials not provided"
                    }

            # Create the post
            result = await self.automation.create_post(content, visibility)

            return {
                "status": result["status"],
                "message": f"LinkedIn post {result['status']}: {result.get('post_id', 'unknown')}" if result["status"] == "success" else f"Failed to create LinkedIn post: {result.get('error', 'unknown error')}",
                "post_id": result.get("post_id")
            }

        except Exception as e:
            logger.error(f"Error in LinkedIn post MCP: {str(e)}")
            return {
                "status": "error",
                "message": f"Error posting to LinkedIn: {str(e)}"
            }

    async def monitor_linkedin_feed(self, max_posts: int = 10) -> dict:
        """
        MCP-compatible method to monitor LinkedIn feed

        Args:
            max_posts: Maximum number of posts to check
        """
        try:
            await self.setup()

            # Attempt login if not already logged in
            if not self.automation.is_logged_in:
                email = self.automation.credentials.get('email')
                password = self.automation.credentials.get('password')

                if email and password:
                    login_success = await self.automation.login(email, password)
                    if not login_success:
                        return {
                            "status": "error",
                            "message": "Failed to login to LinkedIn"
                        }
                else:
                    return {
                        "status": "error",
                        "message": "LinkedIn credentials not provided"
                    }

            # Monitor the feed
            posts = await self.automation.monitor_feed(max_posts)

            return {
                "status": "success",
                "message": f"Monitored LinkedIn feed, found {len(posts)} posts",
                "posts": posts,
                "count": len(posts)
            }

        except Exception as e:
            logger.error(f"Error in LinkedIn monitor MCP: {str(e)}")
            return {
                "status": "error",
                "message": f"Error monitoring LinkedIn: {str(e)}"
            }

    async def check_linkedin_notifications(self) -> dict:
        """
        MCP-compatible method to check LinkedIn notifications
        """
        try:
            await self.setup()

            # Attempt login if not already logged in
            if not self.automation.is_logged_in:
                email = self.automation.credentials.get('email')
                password = self.automation.credentials.get('password')

                if email and password:
                    login_success = await self.automation.login(email, password)
                    if not login_success:
                        return {
                            "status": "error",
                            "message": "Failed to login to LinkedIn"
                        }
                else:
                    return {
                        "status": "error",
                        "message": "LinkedIn credentials not provided"
                    }

            # Check notifications
            notifications = await self.automation.check_notifications()

            return {
                "status": "success",
                "message": f"Checked LinkedIn notifications, found {notifications['count']} notifications",
                "count": notifications["count"],
                "notifications": notifications["notifications"]
            }

        except Exception as e:
            logger.error(f"Error in LinkedIn notifications MCP: {str(e)}")
            return {
                "status": "error",
                "message": f"Error checking LinkedIn notifications: {str(e)}"
            }

    async def get_linkedin_profile_info(self) -> dict:
        """
        MCP-compatible method to get LinkedIn profile information

        Returns:
            dict: Profile information and status
        """
        try:
            await self.setup()

            # Attempt login if not already logged in
            if not self.automation.is_logged_in:
                email = self.automation.credentials.get('email')
                password = self.automation.credentials.get('password')

                if email and password:
                    login_success = await self.automation.login(email, password)
                    if not login_success:
                        return {
                            "status": "error",
                            "message": "Failed to login to LinkedIn"
                        }
                else:
                    return {
                        "status": "error",
                        "message": "LinkedIn credentials not provided"
                    }

            # Get profile info
            profile_info = await self.automation.get_profile_info()

            return {
                "status": "success",
                "message": f"Retrieved LinkedIn profile information for {profile_info.get('name', 'Unknown')}",
                "profile_info": profile_info
            }

        except Exception as e:
            logger.error(f"Error in LinkedIn profile info MCP: {str(e)}")
            return {
                "status": "error",
                "message": f"Error getting LinkedIn profile info: {str(e)}"
            }

    async def cleanup(self):
        """Cleanup resources."""
        await self.automation.close()


# Example usage and testing
async def main():
    """Example usage of the LinkedIn Playwright automation."""
    vault_path = "AI_Employee_Vault"  # Adjust as needed

    # Example credentials (these would come from secure storage in production)
    credentials = {
        "email": "your_linkedin_email@example.com",
        "password": "your_linkedin_password"
    }

    # Initialize the LinkedIn automation
    linkedin_auto = LinkedInPlaywrightAutomation(vault_path, credentials)

    try:
        # Setup browser
        await linkedin_auto.setup_browser()

        # Login (this would need real credentials)
        # login_success = await linkedin_auto.login()

        print("LinkedIn Playwright automation is ready!")
        print(f"Browser actions will be recorded in: {linkedin_auto.browser_actions_dir}")
        print(f"Posts will be recorded in: {linkedin_auto.linkedin_posts_dir}")

        # Example MCP adapter usage
        mcp_adapter = LinkedInMCPAdapter(vault_path, credentials)

        # Example post (won't actually post without real credentials)
        # post_result = await mcp_adapter.post_to_linkedin(
        #     "This is a test post from the AI Employee system!",
        #     "PUBLIC"
        # )
        # print(f"Post result: {post_result}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await linkedin_auto.close()


if __name__ == "__main__":
    asyncio.run(main())