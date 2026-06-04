# Google Cloud Setup Guide for AutoVSF

To use the OCR feature, you need to set up a project on Google Cloud Console to obtain a `credentials.json` file.

## Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Sign in with your Google account.
3. Create a new project or select an existing one.

## Step 2: Enable the Google Drive API
1. In the top search bar, search for **"Google Drive API"**.
2. Select the corresponding result and click **"Enable"**.

## Step 3: Create Authentication Credentials (credentials.json)
1. Navigate to **"APIs & Services"** > **"Credentials"** from the left menu.
2. Click **"Create Credentials"** at the top and select **"OAuth client ID"**.
3. If this is your first time, you may need to click **"Configure Consent Screen"**:
    - Select **External**.
    - Fill in the required fields (App name, Support email).
4. Go back to the **Create OAuth client ID** page:
    - **Application type**: Select **Desktop app**.
    - **Name**: Choose any name (e.g., `AutoVSF-OCR`).
    - Click **Create**.
5. A dialog will appear — click **"Download JSON"**.
6. Rename the downloaded file to `credentials.json` and place it in the project root directory (same level as `headless.py`).

## Step 4: Set the Publishing Status (Important)
To allow the program to automatically open the browser and authenticate without seeing an "App not verified" error:
1. In [Google Cloud Console](https://console.cloud.google.com/), go to **"APIs & Services"** > **"Audience"**.
2. Find the **"Publishing status"** section.
3. Click **"PUBLISH APP"** and confirm.
    - This changes the status from "Testing" to "In production", ensuring the first-time login (creating `token.json`) goes smoothly.

---
*Once complete, you can run `headless.py` and start using the tool!*
