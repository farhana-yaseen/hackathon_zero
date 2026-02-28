import os
import time
import json
import requests
from datetime import datetime
from base_watcher import BaseWatcher
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class LinkedInWatcher(BaseWatcher):
    """
    Watches for business triggers and automatically posts to LinkedIn.
    Generates sales-focused content to drive business engagement.
    """

    def __init__(self, vault_path: str, interval: int = 3600, access_token: str = None):
        super().__init__(vault_path, interval)
        self.access_token = access_token or self.load_access_token()
        self.api_base = "https://api.linkedin.com/v2"
        self.post_templates = self.load_post_templates()
        logger.info("LinkedIn watcher initialized")

    def load_access_token(self):
        """Load LinkedIn access token from credentials file."""
        token_path = os.path.join(self.vault_path, 'linkedin_token.json')

        if os.path.exists(token_path):
            try:
                with open(token_path, 'r') as f:
                    data = json.load(f)
                    return data.get('access_token')
            except Exception as e:
                logger.error(f"Error loading LinkedIn token: {e}")

        logger.warning("No LinkedIn access token found. Please authenticate first.")
        return None

    def load_post_templates(self):
        """Load post templates for different business scenarios."""
        return {
            'product_launch': [
                "🚀 Exciting news! We're launching {product_name}. {description} Learn more: {link}",
                "Introducing {product_name} - {description}. Ready to transform your business? {link}",
                "Big announcement! {product_name} is here. {description} Check it out: {link}"
            ],
            'success_story': [
                "💼 Success Story: {customer_name} achieved {result} using our solution. {details}",
                "Client spotlight: How {customer_name} {achievement}. {details}",
                "Real results: {customer_name} saw {result}. {details}"
            ],
            'industry_insight': [
                "📊 Industry Insight: {topic}. {insight} What's your take?",
                "Trending in {industry}: {topic}. {insight}",
                "Did you know? {topic}. {insight} #BusinessGrowth"
            ],
            'offer': [
                "🎯 Limited Time Offer: {offer_details}. Don't miss out! {link}",
                "Special promotion: {offer_details}. Act now: {link}",
                "Exclusive deal: {offer_details}. Claim yours: {link}"
            ],
            'tip': [
                "💡 Business Tip: {tip}. {explanation} #BusinessTips",
                "Pro tip for {audience}: {tip}. {explanation}",
                "Quick win: {tip}. {explanation} Try it today!"
            ]
        }

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for business triggers that should generate LinkedIn posts.
        In a real implementation, this would monitor business metrics, events, etc.
        For demo purposes, we check a trigger file.
        """
        posts_to_create = []

        # Check for post trigger files
        trigger_dir = os.path.join(self.vault_path, "LinkedIn_Triggers")
        os.makedirs(trigger_dir, exist_ok=True)

        for filename in os.listdir(trigger_dir):
            if filename.endswith('.json') and not filename.startswith('_'):
                filepath = os.path.join(trigger_dir, filename)

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        trigger_data = json.load(f)

                    # Mark as processed
                    processed_filepath = os.path.join(trigger_dir, f"_processed_{filename}")
                    os.rename(filepath, processed_filepath)

                    posts_to_create.append(trigger_data)

                except Exception as e:
                    logger.error(f"Error processing trigger file {filename}: {e}")

        return posts_to_create

    def generate_post_content(self, trigger_data: Dict[str, Any]) -> str:
        """Generate LinkedIn post content based on trigger data."""
        post_type = trigger_data.get('type', 'tip')
        templates = self.post_templates.get(post_type, self.post_templates['tip'])

        # Select template (rotate through them)
        import random
        template = random.choice(templates)

        # Fill in template with data
        try:
            content = template.format(**trigger_data)
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            content = trigger_data.get('content', 'Check out our latest update!')

        return content

    def post_to_linkedin(self, content: str, person_urn: str = None) -> Dict[str, Any]:
        """
        Post content to LinkedIn.

        Args:
            content: The text content to post
            person_urn: LinkedIn person URN (format: urn:li:person:XXXXX)

        Returns:
            Response data from LinkedIn API
        """
        if not self.access_token:
            logger.error("No access token available. Cannot post to LinkedIn.")
            return {'error': 'No access token'}

        # Get person URN if not provided
        if not person_urn:
            person_urn = self.get_person_urn()
            if not person_urn:
                return {'error': 'Could not get person URN'}

        # Prepare post data
        post_data = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

        try:
            response = requests.post(
                f"{self.api_base}/ugcPosts",
                headers=headers,
                json=post_data,
                timeout=30
            )

            if response.status_code == 201:
                logger.info("Successfully posted to LinkedIn")
                return response.json()
            else:
                logger.error(f"LinkedIn API error: {response.status_code} - {response.text}")
                return {'error': response.text, 'status_code': response.status_code}

        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {e}")
            return {'error': str(e)}

    def get_person_urn(self) -> str:
        """Get the authenticated user's person URN."""
        if not self.access_token:
            return None

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(
                f"{self.api_base}/me",
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                person_id = data.get('id')
                return f"urn:li:person:{person_id}"
            else:
                logger.error(f"Error getting person URN: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting person URN: {e}")
            return None

    def create_markdown_file(self, post_data: Dict[str, Any]) -> str:
        """Create a markdown file documenting the LinkedIn post."""
        content = post_data.get('content', '')
        post_type = post_data.get('type', 'general')

        # Generate post content if not provided
        if not content:
            content = self.generate_post_content(post_data)

        # Post to LinkedIn
        result = self.post_to_linkedin(content)

        # Determine status
        if 'error' in result:
            status = 'failed'
            post_id = 'N/A'
            error_msg = result.get('error', 'Unknown error')
        else:
            status = 'posted'
            post_id = result.get('id', 'N/A')
            error_msg = None

        # Create frontmatter
        frontmatter = f"""---
type: linkedin_post
post_type: {post_type}
status: {status}
post_id: "{post_id}"
timestamp: "{datetime.now().isoformat()}"
---

"""

        # Create markdown content
        markdown_content = f"""{frontmatter}

# LinkedIn Post - {post_type.replace('_', ' ').title()}

**Status:** {status.upper()}

**Post ID:** {post_id}

**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Content Posted

{content}

## Trigger Data

```json
{json.dumps(post_data, indent=2)}
```

## API Response

```json
{json.dumps(result, indent=2)}
```

"""

        if error_msg:
            markdown_content += f"""
## Error Details

{error_msg}

**Note:** If authentication failed, make sure you have:
1. Created a LinkedIn Developer App
2. Generated an access token
3. Saved it to `linkedin_token.json`
"""

        # Save to vault
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_{timestamp}_{post_type}"

        folder = 'LinkedIn_Posts'
        return self.write_to_vault(folder, filename, markdown_content)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python linkedin_watcher.py <vault_path>")
        sys.exit(1)

    vault_path = sys.argv[1]
    watcher = LinkedInWatcher(vault_path)
    watcher.run_once()
