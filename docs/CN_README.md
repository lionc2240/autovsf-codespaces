
> 📖 **中文版 README** — 默认英文版: [README.md](../README.md) | **[Tiếng Việt](VIE_README.md)**

---

<p align="center">
<img src="/images/autovsf-codespaces.jpg" width="50%" alt="AUTOVSF CODESPACES Banner">
</p>

# AutoVSF - VideoSubFinder & OCR 流水线 (Codespaces 版)

通过 VideoSubFinder 和 Google Drive API OCR 从视频中提取硬字幕。此版本专门针对 **GitHub Codespaces** 和 **Linux 无头 (Headless) 环境** 进行了优化。

🔗 **主版本 (Windows)：** [![GitHub](https://img.shields.io/badge/GitHub-在_GitHub_上查看-blue?logo=github)](https://github.com/lionc2240/autovsf)
🔗 **Colab 版：** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lionc2240/autovsf-colab/blob/main/AutoVSF_Colab_Edition.ipynb?hl=vi)


🔗 **仓库：** [https://github.com/lionc2240/autovsf-codespaces.git](https://github.com/lionc2240/autovsf-codespaces.git)

---

## 📖 `install.sh` 做了什么？

👉 **详见：** [docs/CN_INSTALL_WHAT_AND_HOW.md](CN_INSTALL_WHAT_AND_HOW.md)

摘要：`install.sh` 自动检测 Ubuntu 版本，安装系统库（xvfb、ffmpeg 等），下载 **VideoSubFinder 6.10**，处理 Ubuntu 24.04 Noble 的库兼容性问题，安装 Python 包（Google Drive API、OpenCV），并创建一个 `.run` 封装脚本以在无头环境中启动 VideoSubFinder。

---

## 🐧 GitHub Codespaces 指南

Codespaces 环境已自动预配置，无需手动安装库。

👉 **详见：** [docs/CN_SETUP_CODESPACES.md](CN_SETUP_CODESPACES.md)

### 1. Google Cloud 设置 (OCR 必需)
您需要 `credentials.json` 文件才能使用 Google Drive 作为 OCR 引擎。

👉 **详见：** [docs/CN_GOOGLE_SETUP.md](CN_GOOGLE_SETUP.md)

1. 在 [Google Cloud Console](https://console.cloud.google.com/) 上创建项目。
2. 启用 **Google Drive API**。
3. 在 **Credentials** 下创建 **OAuth client ID**（Application type: Desktop app）。
4. 下载 JSON 文件，重命名为 `credentials.json`，放在项目根目录。
5. **重要：** 在 OAuth Consent Screen 部分点击 **PUBLISH APP**，以避免认证错误。

### 2. 一键运行 (扫描视频 + OCR)
一条命令即可扫描视频并生成字幕文件：
```bash
python3 headless.py video-test_0.5.mp4
```

### 3. 仅运行 OCR
如果您已经在输出目录（`_out/RGBImages`）中有了图像：
```bash
python3 ocr.py <图像目录路径> [输出文件名.srt]
```

### ⚠️ Codespaces 上的 Google 认证 (重要提示)
由于 Google 已弃用旧的 OOB 重定向方法，本工具使用 **手动链接粘贴** 认证：
1. 运行工具时，点击终端中显示的 **Auth URL** 链接。
2. 登录并点击 **Allow**。
3. 浏览器将重定向到一个错误页面（例如 `http://localhost:8080/?state=...`）。
4. **复制整个 URL** 从浏览器地址栏。
5. 返回终端，在 **Paste URL here** 提示处粘贴并按 Enter。
6. Token 将保存到 `token.json` 供后续使用。

---

## 🌟 主要特点
- **Codespaces 优化：** 在 Linux 无头环境中流畅运行。
- **速度优化：** 多线程 OCR 处理 — 数百张图像只需数秒。
- **自动化：** 从视频输入到完整 `.srt` 文件输出的端到端流水线。
- **智能：** 实时剩余时间估算、自动 token 管理和临时目录清理。

---

## 📸 截图

<p align="center">
  <img src="../images/autovsf-codespaces_running.jpg" width="55%" alt="AutoVSF Codespaces Running">
</p>

<p align="center">
  <img src="../images/autovsf-codespaces_ocr.jpg" width="55%" alt="AutoVSF Codespaces OCR">
</p>

---

## ⚠️ 一般注意事项
- 确保您的 Google Cloud 项目已设置为 **In Production** 状态。
- VideoSubFinder 的默认图像输出目录是 `RGBImages`。
- 始终保护好您的 `credentials.json` 文件。
