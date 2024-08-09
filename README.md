# gdrive_upload
a tiny one file wrapper over google drive API to upload files into a google drive

## Setup Instructions
### Step 1: Install Required Libraries
First, you'll need to install the `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, and `google-api-python-client` libraries.

You can install them using pip:

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 2: Create a Google Cloud Project and Enable the Drive API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Once the project is created, go to the **API & Services > Library** section.
4. Search for "Google Drive API" and click on it.
5. Click the "Enable" button to enable the API for your project.
6. Go to **Credentials** on the left-hand menu, then click on "Create Credentials" and choose "OAuth 2.0 Client IDs".
7. Set up the OAuth consent screen (you can set it up as an internal app if you're just testing).
8. Create the OAuth 2.0 client ID, and choose "Desktop app" as the application type.
9. Download the JSON file with your credentials. Rename it to `credentials.json` and place it in your working directory.

#### (Optional) Step 2a: Set up a Service Account
1. **Create a Service Account:**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Navigate to **IAM & Admin > Service Accounts**.
   - Click "Create Service Account".
   - After creating, navigate to the service account, and click "Add Key" > "Create new key" > Select JSON format.
   - Download the key file. This is the correct `credentials.json` file for a service account.

2. **Use the Correct Script:**
   - TODO: Currently working on script to make this an option

### Step 3: Run the Script:
- When running for the first time, the script will open a browser window for you to authenticate with your Google account.
- After authentication, it will save a token.json file in your working directory, which will be used for subsequent runs.
