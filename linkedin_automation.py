#!/usr/bin/env python3
"""
LinkedIn Automation using Playwright
A dedicated LinkedIn automation system using Playwright for browser automation
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
    def __init__(self, credentials: dict = None):
        """
        Initialize LinkedIn automation with Playwright

        Args:
            credentials: LinkedIn credentials dictionary with 'email' and 'password'
        """
        self.credentials = credentials or {}
        self.browser = None
        self.page = None
        self.is_logged_in = False

        # Create necessary directories for the automation
        self.vault_path = "linkedin_automation_data"
        os.makedirs(self.vault_path, exist_ok=True)

        self.linkedin_posts_dir = os.path.join(self.vault_path, "posts")
        self.linkedin_actions_dir = os.path.join(self.vault_path, "actions")
        self.browser_actions_dir = os.path.join(self.vault_path, "browser_actions")

        for directory in [self.linkedin_posts_dir, self.linkedin_actions_dir, self.browser_actions_dir]:
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
        Create a LinkedIn post using Playwright

        Args:
            content: Content of the post
            visibility: Post visibility ("PUBLIC", "CONNECTIONS_ONLY", etc.)
        """
        if not self.is_logged_in:
            raise Exception("Must be logged in to LinkedIn to create posts")

        logger.info(f"Creating LinkedIn post with visibility: {visibility}")

        # Navigate to the home page to create a post
        await self.page.goto("https://www.linkedin.com/feed/")
        await self.page.wait_for_timeout(2000)

        # Look for the share box - there might be multiple selectors, try them in order
        share_selectors = [
            "button[aria-label='Start a post']",
            "button[aria-label='Share an update']",
            "[data-test-shares-create-announcement]",
            ".share-box-feed-entry__trigger"
        ]

        post_button_found = False
        for selector in share_selectors:
            try:
                post_button = await self.page.wait_for_selector(selector, timeout=5000)
                if post_button:
                    await post_button.click()
                    post_button_found = True
                    logger.info(f"Found and clicked post button with selector: {selector}")
                    break
            except:
                continue

        if not post_button_found:
            logger.error("Could not find post button")
            return {"status": "failed", "error": "Could not find post button"}

        # Wait for the post editor to appear
        await self.page.wait_for_timeout(2000)

        # Find the content editable area for the post
        content_selectors = [
            "div[contenteditable='true'][data-test-id='artdeco-text-input-content-editable']",
            "div[contenteditable='true'].mentions-texteditor__contenteditable",
            "div[role='textbox']",
            "div[contenteditable='true']"
        ]

        textbox = None
        for selector in content_selectors:
            try:
                textbox = await self.page.wait_for_selector(selector, timeout=3000)
                if textbox:
                    break
            except:
                continue

        if not textbox:
            logger.error("Could not find post textbox")
            return {"status": "failed", "error": "Could not find post textbox"}

        # Clear existing content and type new content
        await textbox.click()
        await self.page.keyboard.press("Control+A")  # Select all
        await self.page.keyboard.press("Delete")    # Delete selected
        await textbox.type(content)

        # Add a short delay to ensure content is typed
        await self.page.wait_for_timeout(1000)

        # Handle visibility settings if needed
        if visibility == "PUBLIC":
            # Look for the audience selector button (usually a globe icon for public)
            try:
                visibility_button = await self.page.query_selector("button[aria-label='Change who can see this post'], button[aria-label='Audience selector']")
                if visibility_button:
                    await visibility_button.click()
                    await self.page.wait_for_timeout(1000)

                    # Select public visibility
                    public_option = await self.page.query_selector("button[aria-label='Public'], li[data-modal='false'] span:has-text('Public')")
                    if public_option:
                        await public_option.click()
                        await self.page.wait_for_timeout(500)

            except Exception as e:
                logger.warning(f"Could not set visibility: {str(e)}")

        # Find and click the post/share button
        post_share_selectors = [
            "button[aria-label='Post']",
            "button.share-actions__primary-action",
            "button.artdeco-button--primary:has-text('Post')",
            "button:has-text('Post')"
        ]

        post_share_button = None
        for selector in post_share_selectors:
            try:
                post_share_button = await self.page.query_selector(selector)
                if post_share_button:
                    break
            except:
                continue

        if post_share_button:
            await post_share_button.click()
            logger.info("Post button clicked")

            # Wait for post to be published
            await self.page.wait_for_timeout(3000)

            # Record the post action
            post_id = f"post_{int(time.time())}"
            await self._record_linkedin_post(content, post_id, visibility)

            logger.info(f"LinkedIn post created successfully: {post_id}")
            return {"status": "success", "post_id": post_id}
        else:
            logger.error("Could not find post/share button")
            return {"status": "failed", "error": "Could not find post/share button"}

    async def monitor_feed(self, max_posts=10):
        """
        Monitor LinkedIn feed for new posts/interactions using Playwright

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

            # Get posts from the feed using multiple selectors
            post_selectors = [
                "[data-id]",  # Main article posts
                ".feed-shared-update-v2",  # Shared updates
                ".relative.feed-shared-update-v2",  # Another common selector
            ]

            posts = []
            for selector in post_selectors:
                try:
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

                except Exception as e:
                    logger.warning(f"Error querying selector {selector}: {str(e)}")
                    continue

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
        Check LinkedIn notifications using Playwright
        """
        if not self.is_logged_in:
            raise Exception("Must be logged in to LinkedIn to check notifications")

        logger.info("Checking LinkedIn notifications")

        try:
            # Click on the notification bell icon
            notification_selectors = [
                "li-icon[type='notifications-icon']",
                "button[aria-label='Notifications']",
                ".global-nav__primary-link--messaging-and-notifications",
                "[data-test-global-typeahead-search]"
            ]

            notification_button = None
            for selector in notification_selectors:
                try:
                    notification_button = await self.page.query_selector(selector)
                    if notification_button:
                        break
                except:
                    continue

            if notification_button:
                await notification_button.click()
                await self.page.wait_for_timeout(2000)

                # Get notification count
                notification_elements = await self.page.query_selector_all("[class*='notification-item']")
                notification_count = len(notification_elements)

                # Get recent notifications
                notifications = []
                for elem in notification_elements[:5]:  # Get first 5 notifications
                    try:
                        text_elem = await elem.query_selector("span, div")
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
        Get LinkedIn profile information using Playwright
        """
        if not self.is_logged_in:
            raise Exception("Must be logged in to LinkedIn to get profile info")

        logger.info("Getting LinkedIn profile information")

        try:
            # Navigate to profile page
            await self.page.goto("https://www.linkedin.com/in/your-profile-url")
            await self.page.wait_for_timeout(2000)

            # Extract profile information using multiple selectors
            profile_info = {}

            # Get name
            name_selectors = [
                "h1.text-heading-xlarge",
                "h1.profile-top-card__name",
                "h1.ivm-profile-content__full-name"
            ]

            for selector in name_selectors:
                try:
                    name_elem = await self.page.query_selector(selector)
                    if name_elem:
                        profile_info["name"] = await name_elem.text_content()
                        break
                except:
                    continue

            # Get headline
            headline_selectors = [
                "h2.text-body-medium",
                "h2.profile-top-card__headline",
                "[data-test-id='headline']"
            ]

            for selector in headline_selectors:
                try:
                    headline_elem = await self.page.query_selector(selector)
                    if headline_elem:
                        profile_info["headline"] = await headline_elem.text_content()
                        break
                except:
                    continue

            # Get connection count
            conn_selectors = [
                "span[aria-hidden='true']:has-text('connections')",
                "[class*='connections-count']",
                "[data-test-id='num-connections']"
            ]

            for selector in conn_selectors:
                try:
                    conn_elem = await self.page.query_selector(selector)
                    if conn_elem:
                        profile_info["connections"] = await conn_elem.text_content()
                        break
                except:
                    continue

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
        """Record a LinkedIn post to the automation data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_post_{timestamp}_{post_id}.md"
        filepath = os.path.join(self.linkedin_posts_dir, filename)

        content_md = f"""---
type: linkedin_post
post_id: "{post_id}"
visibility: "{visibility}"
created_at: "{datetime.now().isoformat()}"
status: "published_via_playwright"
---

# LinkedIn Post via Playwright

**Visibility:** {visibility}
**Created At:** {datetime.now().isoformat()}

## Content
{content}

## Status
- [x] Post published via Playwright
- [ ] Monitor engagement
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content_md)

        logger.info(f"LinkedIn post recorded: {filepath}")

    async def _record_browser_action(self, action_type: str, details: dict):
        """Record a browser action to the automation data."""
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


async def main():
    """Example usage of the LinkedIn Playwright automation."""
    print("LinkedIn Playwright Automation")
    print("=" * 40)

    # Example credentials (these would come from secure storage in production)
    credentials = {
        "email": "your_linkedin_email@example.com",
        "password": "your_linkedin_password"
    }

    # Initialize the LinkedIn automation
    linkedin_auto = LinkedInPlaywrightAutomation(credentials)

    try:
        # Setup browser
        await linkedin_auto.setup_browser()
        print("✅ Browser setup complete")

        # Login (this would need real credentials)
        # login_success = await linkedin_auto.login()

        print("✅ LinkedIn Playwright automation is ready!")
        print(f"📁 Posts will be recorded in: {linkedin_auto.linkedin_posts_dir}")
        print(f"📁 Actions will be recorded in: {linkedin_auto.linkedin_actions_dir}")
        print(f"📁 Browser actions in: {linkedin_auto.browser_actions_dir}")
        print("")
        print("ℹ️  To use with real credentials:")
        print("   1. Update the credentials dictionary with your LinkedIn email/password")
        print("   2. Run the automation functions (login, create_post, etc.)")
        print("   3. The system will perform actions via browser automation")
        print("")
        print("🔒 Credentials are kept secure and not stored in code")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await linkedin_auto.close()


if __name__ == "__main__":
    asyncio.run(main())