# Setting up Gmail API Credentials

To use the Gmail Watcher, you need to set up Google API credentials:

## Steps:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and click on it
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Desktop application" as the application type
   - Download the credentials JSON file
5. Rename the downloaded file to `credentials.json` and place it in your vault directory
6. Install required packages:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

## Required Python Packages:

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## First Time Setup:

When you run the Gmail Watcher for the first time, it will open a browser window asking you to log in to your Google account and grant permissions. After granting permissions, it will save the tokens to `token.pickle` in your vault directory.