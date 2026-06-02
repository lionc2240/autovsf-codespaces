# AutoVSF - VideoSubFinder & OCR Pipeline (Codespaces Edition)

Công cụ hỗ trợ trích xuất phụ đề cứng từ video thông qua VideoSubFinder và nhận diện chữ (OCR) bằng Google Drive API. Phiên bản này được tối ưu hóa đặc biệt cho môi trường **GitHub Codespaces** và **Linux Headless**.

🔗 **Repository:** [https://github.com/lionc2240/autovsf-codespaces.git](https://github.com/lionc2240/autovsf-codespaces.git)

---

## 🐧 Hướng dẫn cho GitHub Codespaces / Linux CLI

Môi trường Codespaces không có màn hình hiển thị (Headless), vì vậy bạn sẽ sử dụng bộ công cụ dòng lệnh (CLI) để đạt hiệu quả cao nhất.

### 1. Cài đặt môi trường
Chạy lệnh sau để cài đặt các thư viện cần thiết:
```bash
pip install watchdog google-api-python-client google-auth-oauthlib google-auth httplib2 opencv-python psutil Pillow
```

### 2. Thiết lập Google Cloud (Bắt buộc cho OCR)
Bạn cần file `credentials.json` để tool có thể sử dụng Google Drive làm bộ máy OCR.
1. Tạo dự án trên [Google Cloud Console](https://console.cloud.google.com/).
2. Bật **Google Drive API**.
3. Tại mục **Credentials**, tạo **OAuth client ID** (Application type: Desktop app).
4. Tải file JSON về, đổi tên thành `credentials.json` và bỏ vào thư mục `autovsf/`.
5. **Quan trọng:** Nhấn **PUBLISH APP** trong mục OAuth Consent Screen để tránh lỗi xác thực.

### 3. Khởi chạy toàn bộ (Scan Video + OCR)
Chỉ cần 1 lệnh duy nhất để quét video và tạo file phụ đề:
```bash
python3 autovsf/headless.py video-test_0.5.mp4
```

### 4. Chỉ chạy riêng bước OCR
Nếu bạn đã có ảnh trong thư mục kết quả (`_out/RGBImages`):
```bash
python3 autovsf/ocr.py <đường_dẫn_thư_mục_ảnh> [tên_file_output.srt]
```

### ⚠️ Cách xác thực Google trên Codespaces (Mẹo quan trọng)
Do Google chặn phương thức đăng nhập cũ (OOB), tool sử dụng phương thức **Manual Link Paste**:
1. Khi chạy tool, nhấn vào link **Auth URL** hiện ra trên terminal.
2. Đăng nhập và nhấn **Allow**.
3. Trình duyệt sẽ chuyển đến một trang báo lỗi (ví dụ: `http://localhost:8080/?state=...`).
4. **Copy toàn bộ địa chỉ URL** của trang lỗi đó từ thanh địa chỉ trình duyệt.
5. Quay lại Terminal, dán vào dòng **Paste URL here** và nhấn Enter.
6. Token sẽ được lưu vào `autovsf/token.json` để sử dụng mãi mãi về sau.

---

## 💻 Hướng dẫn cho Windows (Giao diện GUI)

### Cài đặt nhanh (One-Click)
Mở PowerShell (Admin) và dán:
```powershell
irm https://raw.githubusercontent.com/lionc2240/autovsf/main/install.ps1 | iex
```

### Chạy giao diện
```powershell
python main.py
```
- **Tab 1 (VSF):** Tách ảnh phụ đề tự động. Hỗ trợ tạo Crop Profile trực quan.
- **Tab 2 (OCR):** Tự động tải ảnh lên Drive và ghép thành file `.srt`.
- **Tab 3 (Settings):** Quản lý cấu hình và `credentials.json`.

---

## 🌟 Tính năng nổi bật
- **Đa nền tảng:** Chạy mượt mà trên cả Windows (GUI) và Linux (CLI/Headless).
- **Tối ưu tốc độ:** Hỗ trợ đa luồng (multi-threading) cho OCR, xử lý hàng trăm ảnh chỉ trong vài giây.
- **Tự động hóa:** Tích hợp quy trình từ lúc đọc video đến lúc xuất file `.srt` hoàn chỉnh.
- **Thông minh:** ETA thời gian thực, tự động quản lý token và dọn dẹp thư mục tạm.

---

## ⚠️ Lưu ý chung
- Đảm bảo dự án Google Cloud đã được chuyển sang trạng thái **In Production**.
- Thư mục ảnh mặc định từ VideoSubFinder là `RGBImages`.
- Luôn giữ file `credentials.json` bảo mật.
