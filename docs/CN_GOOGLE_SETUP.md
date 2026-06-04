# AutoVSF Google Cloud 设置指南

要使用 OCR 功能，您需要设置一个 Google Cloud 项目来获取 `credentials.json` 文件。

## 步骤 1：创建 Google Cloud 项目
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)。
2. 使用您的 Google 账户登录。
3. 创建一个新项目或选择现有项目。

## 步骤 2：启用 Google Drive API
1. 在顶部搜索栏中搜索 **"Google Drive API"**。
2. 选择相应结果并点击 **"Enable"**。

## 步骤 3：创建凭据文件 (credentials.json)
1. 导航至 **"APIs & Services"** > **"Credentials"**。
2. 点击 **"Create Credentials"** 并选择 **"OAuth client ID"**。
3. 如果是首次设置，您可能需要点击 **"Configure Consent Screen"**：
    - 选择 **External**。
    - 填写必填字段（应用名称、支持邮箱）。
4. 返回 **Create OAuth client ID** 页面：
    - **Application type**：选择 **Desktop app**。
    - **Name**：任意命名（例如 `AutoVSF-OCR`）。
    - 点击 **Create**。
5. 在弹出的对话框中点击 **"Download JSON"**。
6. 将下载的文件重命名为 `credentials.json` 并放置在项目根目录（与 `headless.py` 同级）。

## 步骤 4：发布应用 (重要)
为避免浏览器登录时出现"应用未经验证"的错误：
1. 在 [Google Cloud Console](https://console.cloud.google.com/) 中，前往 **"APIs & Services"** > **"Audience"**。
2. 找到 **"Publishing status"** 部分。
3. 点击 **"PUBLISH APP"** 并确认。
    - 这将把状态从"Testing"更改为"In production"，确保首次登录（创建 `token.json`）顺利进行。

---
*完成后，您可以运行 `headless.py` 并开始使用该工具！*
