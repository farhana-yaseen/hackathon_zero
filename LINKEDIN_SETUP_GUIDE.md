# LinkedIn Authentication Setup Guide

## Overview
To enable live posting to LinkedIn through the AI Employee system, you need to set up proper authentication with LinkedIn's API.

## Step 1: Create a LinkedIn Developer Application

1. Go to [LinkedIn Developers Portal](https://www.linkedin.com/developers/)
2. Click "Create App"
3. Fill in the required information:
   - **App name**: AI Employee LinkedIn Poster
   - **Company name**: Your Company Name
   - **App logo**: Upload any logo
   - **Privacy Policy URL**: You can use a placeholder like `https://yourwebsite.com/privacy`
   - **Terms of Service URL**: You can use a placeholder like `https://yourwebsite.com/terms`
   - **Website URL**: `https://yourwebsite.com`

## Step 2: Configure OAuth Settings

1. After creating your app, go to the "Auth" tab
2. Add your redirect URL:
   - For local development: `http://localhost:8080/callback` or `http://localhost:3000/callback`
   - Or any URL you'll be using for authentication

3. Make sure the following OAuth 2.0 scopes are enabled:
   - `r_basicprofile` - View basic profile information
   - `r_emailaddress` - View email address
   - `w_member_social` - Share with the member's social network
   - `rw_organization_admin` - Manage organization pages (optional, for company posts)

## Step 3: Get Your API Credentials

1. On your app's main page, note down:
   - **Client ID**: Will be needed for authentication
   - **Client Secret**: Will be needed for authentication

## Step 4: Generate Access Token

There are several ways to generate an access token:

### Method 1: OAuth 2.0 Flow (Recommended)
1. Use the OAuth flow to authenticate:
   ```
   https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&state=YOUR_STATE&scope=r_basicprofile,r_emailaddress,w_member_social
   ```

2. Exchange the authorization code for an access token:
   ```
   POST https://www.linkedin.com/oauth/v2/accessToken
   Content-Type: application/x-www-form-urlencoded

   grant_type=authorization_code&code=AUTHORIZATION_CODE&redirect_uri=YOUR_REDIRECT_URI&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET
   ```

### Method 2: Using LinkedIn API Explorer
1. Go to [LinkedIn API Explorer](https://www.linkedin.com/developers/tools/api-explorer)
2. Select your application
3. Choose the `POST /ugcPosts` endpoint
4. Click "Get Access Token" and select the appropriate scopes
5. Copy the access token

### Method 3: Using Third-Party Tools
You can also use tools like Postman or write a small script to handle the OAuth flow.

## Step 5: Configure the AI Employee System

1. Replace the placeholder in the `AI_Employee_Vault/linkedin_token.json` file:
   ```json
   {
     "access_token": "ACTUAL_ACCESS_TOKEN_YOU_GOT_FROM_LINKEDIN",
     "expires_in": 0,
     "refresh_token": "REFRESH_TOKEN_IF_AVAILABLE",
     "scope": "r_basicprofile,r_emailaddress,w_member_social"
   }
   ```

2. Make sure the file is saved in the correct location:
   `D:\hackthon\hackathon_zero\AI_Employee_Vault\linkedin_token.json`

## Step 6: Test the Integration

1. Run the LinkedIn watcher:
   ```bash
   python AI_Employee_Vault/scripts/linkedin_watcher.py AI_Employee_Vault
   ```

2. Create a test trigger file in `AI_Employee_Vault/LinkedIn_Triggers/`:
   ```json
   {
     "type": "tip",
     "audience": "professionals",
     "tip": "Consistency is key to success in any venture.",
     "explanation": "Small daily actions compound into significant results over time."
   }
   ```

## Important Security Notes

⚠️ **Keep your credentials secure:**
- Never commit `linkedin_token.json` to version control
- Use environment variables for production deployments
- Rotate your tokens periodically
- Limit the permissions to only what's necessary

## Troubleshooting

### Common Issues:
- **401 Unauthorized**: Invalid or expired access token
- **403 Forbidden**: Insufficient permissions/scopes
- **Rate Limits**: LinkedIn has API rate limits (typically 500 calls per day per application)

### Verification Steps:
1. Check that your access token has the correct scopes
2. Verify that your LinkedIn app has been approved (if in production)
3. Ensure your LinkedIn account has the right permissions for the actions you're trying to perform

## Sample API Call Test

To test if your credentials work, you can make a simple API call:

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "https://api.linkedin.com/v2/me"
```

This should return your profile information if the authentication is working.

---

**Note:** The AI Employee system is designed to work safely in simulation mode when no credentials are provided, creating documentation files instead of making actual posts. Once you add valid credentials, it will begin making live posts to your LinkedIn account.