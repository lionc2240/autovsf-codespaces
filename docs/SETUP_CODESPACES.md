# 🎬 AutoVSF Codespaces Edition — Quick Start Guide

Welcome back! If you haven't used this tool in a while, here's everything you need to get the system up and running in 5 minutes.

🔗 **Repo:** [https://github.com/lionc2240/autovsf-codespaces.git](https://github.com/lionc2240/autovsf-codespaces.git)

> ⚠️ Note: The first time you launch a Codespace, it may take about 10 minutes to build the environment.

---

## 🚀 1. Initialize the Environment (Each new Codespace)

If you're creating a brand new Codespace, run this command to automatically install everything (Ubuntu libraries, Python packages, VideoSubFinder):

```bash
chmod +x install.sh && ./install.sh
```

---

## 🔑 2. Important Configuration (Required)

You need one file for the tool to work:
- **`credentials.json`**: Obtain from Google Cloud Console (Drive API). Upload this file to the project root directory.

---

## ⚡ 3. Quickest Way to Run (Headless CLI)

Since Codespaces has no display, you'll use commands to run the tool in the background:

### Full Pipeline (Scan Video + OCR):
```bash
python3 headless.py your_video_file.mp4
```

### Run OCR Only (if images already exist in `_out`):
```bash
python3 ocr.py <image_directory_path> [output_file.srt]
```

---

## ⚠️ 4. Google Authentication Trick (IMPORTANT)

Google has deprecated the old OOB code method, so the tool now uses **Manual Link Paste** authentication. When logging in for the first time, follow these 4 steps:

1.  **Open the link:** Click the **Auth URL** link printed in the terminal.
2.  **Sign in:** In your browser, click **Allow**. You'll see a blank error page (localhost).
3.  **Copy the error URL:** Copy the entire URL from the browser's address bar (e.g., `http://localhost:8080/?state=...&code=...`).
4.  **Paste into Terminal:** Go back to your Codespace, paste the full URL at the **Paste URL here** prompt, and press Enter.

✅ **Done!** The token will be saved to `token.json`. From the second video onward, you won't need to repeat this step.

---

## 📁 5. Where Are the Results?

- All output (images, temp srt files) is in the `your_video_out/` directory.
- The final subtitle file will have the same name as the video, with a `.srt` extension.

---

## 🧹 6. Clean Up to Save Space

Codespaces have disk space limits. After finishing, delete heavy image directories with:

```bash
rm -rf *_out/
```

---

*Happy subtitle extracting! Everything is optimized for standard Ubuntu 20.04 Focal.*
