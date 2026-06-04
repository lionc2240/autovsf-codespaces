
> 📖 **Bản README tiếng Việt** — Bản README tiếng Anh (mặc định): [README.md](../README.md)

---

<p align="center">
<img src="/images/autovsf-codespaces.jpg" width="50%" alt="AUTOVSF CODESPACES Banner">
</p>

# AutoVSF - VideoSubFinder & OCR Pipeline (Codespaces Edition)

Công cụ hỗ trợ trích xuất phụ đề cứng từ video thông qua VideoSubFinder và nhận diện chữ (OCR) bằng Google Drive API. Phiên bản này được tối ưu hóa đặc biệt cho môi trường **GitHub Codespaces** và **Linux Headless**.

🔗 **Repository:** [https://github.com/lionc2240/autovsf-codespaces.git](https://github.com/lionc2240/autovsf-codespaces.git)

---

## 📖 `install.sh` đã làm gì?

👉 **Xem giải thích chi tiết tại:** [docs/VIE_INSTALL_WHAT_AND_HOW.md](VIE_INSTALL_WHAT_AND_HOW.md)

Tóm tắt: `install.sh` tự động phát hiện phiên bản Ubuntu, cài đặt thư viện hệ thống (xvfb, ffmpeg, ...), tải **VideoSubFinder 6.10**, xử lý tương thích thư viện cho Ubuntu 24.04 Noble, cài đặt gói Python (Google Drive API, OpenCV), và tạo wrapper script `.run` để chạy VideoSubFinder trong môi trường headless.

---

## 🐧 Hướng dẫn cho GitHub Codespaces

Môi trường Codespaces đã được cấu hình tự động. Bạn không cần cài đặt thêm bất kỳ thư viện nào thủ công.

👉 **Xem hướng dẫn chi tiết tại:** [docs/VIE_SETUP_CODESPACES.md](VIE_SETUP_CODESPACES.md)

### 1. Thiết lập Google Cloud (Bắt buộc cho OCR)
Bạn cần file `credentials.json` để tool có thể sử dụng Google Drive làm bộ máy OCR.

👉 **Xem hướng dẫn chi tiết tại:** [docs/VIE_GOOGLE_SETUP.md](VIE_GOOGLE_SETUP.md)

1. Tạo dự án trên [Google Cloud Console](https://console.cloud.google.com/).
2. Bật **Google Drive API**.
3. Tại mục **Credentials**, tạo **OAuth client ID** (Application type: Desktop app).
4. Tải file JSON về, đổi tên thành `credentials.json` và bỏ vào thư mục gốc.
5. **Quan trọng:** Nhấn **PUBLISH APP** trong mục OAuth Consent Screen để tránh lỗi xác thực.

### 2. Khởi chạy toàn bộ (Scan Video + OCR)
Chỉ cần 1 lệnh duy nhất để quét video và tạo file phụ đề:
```bash
python3 headless.py video-test_0.5.mp4
```

### 3. Chỉ chạy riêng bước OCR
Nếu bạn đã có ảnh trong thư mục kết quả (`_out/RGBImages`):
```bash
python3 ocr.py <đường_dẫn_thư_mục_ảnh> [tên_file_output.srt]
```

### ⚠️ Cách xác thực Google trên Codespaces (Mẹo quan trọng)
Do Google chặn phương thức đăng nhập cũ (OOB), tool sử dụng phương thức **Manual Link Paste**:
1. Khi chạy tool, nhấn vào link **Auth URL** hiện ra trên terminal.
2. Đăng nhập và nhấn **Allow**.
3. Trình duyệt sẽ chuyển đến một trang báo lỗi (ví dụ: `http://localhost:8080/?state=...`).
4. **Copy toàn bộ địa chỉ URL** của trang lỗi đó từ thanh địa chỉ trình duyệt.
5. Quay lại Terminal, dán vào dòng **Paste URL here** và nhấn Enter.
6. Token sẽ được lưu vào `token.json` để sử dụng mãi mãi về sau.

---

## 🌟 Tính năng nổi bật
- **Tối ưu cho Codespaces:** Chạy mượt mà trong môi trường Linux Headless.
- **Tối ưu tốc độ:** Hỗ trợ đa luồng (multi-threading) cho OCR, xử lý hàng trăm ảnh chỉ trong vài giây.
- **Tự động hóa:** Tích hợp quy trình từ lúc đọc video đến lúc xuất file `.srt` hoàn chỉnh.
- **Thông minh:** ETA thời gian thực, tự động quản lý token và dọn dẹp thư mục tạm.

---

## ⚠️ Lưu ý chung
- Đảm bảo dự án Google Cloud đã được chuyển sang trạng thái **In Production**.
- Thư mục ảnh mặc định từ VideoSubFinder là `RGBImages`.
- Luôn giữ file `credentials.json` bảo mật.
