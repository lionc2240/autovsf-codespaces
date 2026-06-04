# 🎬 AutoVSF Codespaces 版 — 快速入门指南

欢迎回来！如果您很久没使用这个工具了，这里包含了在 5 分钟内让系统重新运行所需的一切。

🔗 **仓库：** [https://github.com/lionc2240/autovsf-codespaces.git](https://github.com/lionc2240/autovsf-codespaces.git)

> ⚠️ 注意：首次启动 Codespace 可能需要大约 10 分钟来构建环境。

---

## 🚀 1. 初始化环境 (每次新建 Codespace)

如果您创建的是全新的 Codespace，运行此命令自动安装所有内容（Ubuntu 库、Python 包、VideoSubFinder）：

```bash
chmod +x install.sh && ./install.sh
```

---

## 🔑 2. 重要配置 (必需)

工具正常工作只需要一个文件：
- **`credentials.json`**：从 Google Cloud Console（Drive API）获取。将此文件上传到项目根目录。

---

## ⚡ 3. 最快运行方式 (Headless CLI)

由于 Codespace 没有显示器，您需要使用命令让工具在后台运行：

### 完整流水线 (扫描视频 + OCR)：
```bash
python3 headless.py your_video_file.mp4
```

### 仅运行 OCR (如果 `_out` 中已有图像)：
```bash
python3 ocr.py <图像目录路径> [输出文件.srt]
```

---

## ⚠️ 4. Google 认证技巧 (重要)

Google 已弃用旧的 OOB 代码方法，因此本工具现在使用**手动链接粘贴**认证。首次登录时，请按照以下 4 个步骤操作：

1.  **打开链接：** 点击终端中打印的 **Auth URL** 链接。
2.  **登录：** 在浏览器中，点击 **Allow**。您将看到一个空白错误页面（localhost）。
3.  **复制错误 URL：** 从浏览器地址栏复制整个 URL（例如 `http://localhost:8080/?state=...&code=...`）。
4.  **粘贴到终端：** 返回 Codespace，将完整的 URL 粘贴到 **Paste URL here** 提示处，然后按 Enter。

✅ **完成！** Token 将保存到 `token.json`。从第二个视频开始，您无需重复此步骤。

---

## 📁 5. 结果在哪里？

- 所有输出（图像、临时 srt 文件）都在 `your_video_out/` 目录中。
- 最终字幕文件与视频同名，扩展名为 `.srt`。

---

## 🧹 6. 清理以节省空间

Codespace 有磁盘空间限制。完成后，使用以下命令删除占用空间大的图像目录：

```bash
rm -rf *_out/
```

---

*祝您提取字幕愉快！所有内容已针对标准 Ubuntu 20.04 Focal 进行了优化。*
