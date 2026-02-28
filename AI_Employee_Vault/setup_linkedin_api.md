# Setting up LinkedIn API for Automated Posting

## Overview
This guide helps you set up LinkedIn API access for the LinkedIn Watcher to automatically post business content.

## Steps to Get LinkedIn API Access

### 1. Create a LinkedIn Developer App

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Click "Create app"
3. Fill in the required information:
   - **App name**: AI Employee LinkedIn Poster
   - **LinkedIn Page**: Select your company page (or create one)
   - **App logo**: Upload any logo
   - **Legal agreement**: Accept the terms

### 2. Configure App Settings

1. In your app dashboard, go to the "Auth" tab
2. Add OAuth 2.0 redirect URLs:
   - `http://localhost:8080/callback`
   - `http://localhost:3000/callback`
3. Under "Products", request access to:
   - **Share on LinkedIn** (required for posting)
   - **Sign In with LinkedIn** (required for authentication)

### 3. Get Your Credentials

1. In the "Auth" tab, note down:
   - **Client ID**
   - **Client Secret**
2. Save these securely

### 4. Generate Access Token

#### Option A: Using LinkedIn OAuth Playground (Easiest)

1. Go to [LinkedIn OAuth Test Console](https://www.linkedin.com/developers/tools/oauth)
2. Select your app
3. Select scopes: `w_member_social`, `r_liteprofile`
4. Click "Request Access Token"
5. Copy the access token

#### Option B: Manual OAuth Flow

Run the authentication script:
```bash
python authenticate_linkedin.py
```

This will:
1. Open a browser for LinkedIn login
2. Ask you to authorize the app
3. Save the access token to `linkedin_token.json`

### 5. Save Access Token

Create a file `linkedin_token.json` in your vault directory:

```json
{
  "access_token": "YOUR_ACCESS_TOKEN_HERE",
  "expires_in": 5184000,
  "created_at": "2026-03-01T00:00:00"
}
```

**Important:** Keep this file secure and never commit it to git!

## Testing the LinkedIn Watcher

### 1. Create a Test Trigger

Create a file in `AI_Employee_Vault/LinkedIn_Triggers/test_post.json`:

```json
{
  "type": "product_launch",
  "product_name": "AI Employee System",
  "description": "Automate your business workflows with AI-powered watchers",
  "link": "https://github.com/yourusername/ai-employee"
}
```

### 2. Run the Watcher

```bash
cd AI_Employee_Vault/scripts
python linkedin_watcher.py ../
```

### 3. Check Results

- The post will be published to LinkedIn
- A markdown file will be created in `LinkedIn_Posts/` folder
- The trigger file will be marked as processed

## Post Types and Templates

### Product Launch
```json
{
  "type": "product_launch",
  "product_name": "Your Product",
  "description": "What it does",
  "link": "https://yourlink.com"
}
```

### Success Story
```json
{
  "type": "success_story",
  "customer_name": "ABC Company",
  "result": "50% increase in sales",
  "details": "Using our AI solution, they automated their workflow"
}
```

### Industry Insight
```json
{
  "type": "industry_insight",
  "topic": "AI in Business",
  "insight": "Companies using AI see 40% productivity gains",
  "industry": "Technology"
}
```

### Special Offer
```json
{
  "type": "offer",
  "offer_details": "Get 30% off our premium plan",
  "link": "https://yoursite.com/offer"
}
```

### Business Tip
```json
{
  "type": "tip",
  "tip": "Automate repetitive tasks to save 10+ hours per week",
  "explanation": "Focus on high-value work while AI handles the routine",
  "audience": "entrepreneurs"
}
```

## Troubleshooting

### Error: "Invalid access token"
- Your token may have expired (LinkedIn tokens expire after 60 days)
- Generate a new token using the steps above

### Error: "Insufficient permissions"
- Make sure your app has "Share on LinkedIn" product access
- Check that you requested the correct scopes: `w_member_social`

### Error: "Rate limit exceeded"
- LinkedIn has posting limits (typically 100 posts per day)
- Reduce posting frequency in your watcher

### Posts not appearing
- Check if your LinkedIn account is in good standing
- Verify the post was created in the LinkedIn_Posts folder
- Check the API response in the markdown file for errors

## Best Practices

1. **Don't spam**: Post 2-5 times per day maximum
2. **Quality content**: Use meaningful, valuable content
3. **Engage**: Respond to comments on your posts
4. **Monitor**: Check the markdown files for API errors
5. **Test first**: Use a dummy account for testing

## Security Notes

- Never share your access token
- Add `linkedin_token.json` to `.gitignore`
- Rotate tokens regularly
- Use a separate LinkedIn account for testing
- Don't commit credentials to version control

## For Hackathon Demo

If you're demonstrating this for a hackathon:
1. Use a dummy LinkedIn account
2. Create sample trigger files
3. Show the markdown output files
4. Explain the OAuth flow
5. Demonstrate different post types
