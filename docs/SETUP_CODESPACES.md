# 🎬 AutoVSF Codespaces Edition - Hướng dẫn sử dụng sau 6 tháng

Chào bạn! Nếu bạn đang đọc file này sau một thời gian dài không sử dụng, đây là những gì bạn cần làm để khởi động lại hệ thống trong 5 phút.

🔗 **Repo:** [https://github.com/lionc2240/autovsf-codespaces.git](https://github.com/lionc2240/autovsf-codespaces.git)

---

## 🚀 1. Khởi tạo lại môi trường (Mỗi lần tạo Codespace mới)

Nếu bạn tạo một Codespace mới hoàn toàn, hãy dán lệnh này để tự động cài đặt tất cả (Thư viện Ubuntu Focal, Python, VideoSubFinder):

```bash
chmod +x install.sh && ./install.sh
```

---

## 🔑 2. Cấu hình Quan trọng (Bắt buộc)

Bạn cần 1 file duy nhất để tool hoạt động:
- **`credentials.json`**: Lấy từ Google Cloud Console (Drive API). Hãy upload file này vào đúng thư mục gốc của repo này.

---

## ⚡ 3. Cách chạy nhanh nhất (Headless CLI)

Vì Codespaces không có màn hình, bạn sẽ dùng lệnh để tool tự chạy ngầm:

### Quét Video + OCR tự động (Full Quy trình):
```bash
python3 headless.py ten_video_cua_ban.mp4
```

### Chỉ chạy riêng bước OCR (Nếu đã có ảnh trong thư mục _out):
```bash
python3 ocr.py <duong_dan_thu_muc_anh> [file_ket_qua.srt]
```

---

## ⚠️ 4. Tuyệt chiêu "Vượt rào" xác thực Google (QUAN TRỌNG)

Google đã chặn phương thức dán mã (OOB), nên khi tool yêu cầu đăng nhập lần đầu, hãy làm đúng 4 bước "mẹo" sau:

1.  **Mở link:** Nhấn vào link **Auth URL** tool in ra trên terminal.
2.  **Đăng nhập:** Trên trình duyệt, nhấn **Allow**. Bạn sẽ thấy trang báo lỗi trắng (localhost).
3.  **Copy Link lỗi:** Copy toàn bộ địa chỉ URL trên thanh địa chỉ (ví dụ: `http://localhost:8080/?state=...&code=...`).
4.  **Dán vào Terminal:** Quay lại Codespace, dán toàn bộ cái link đó vào dòng **Paste URL here** rồi nhấn Enter.

✅ **Xong!** Token sẽ được lưu vào `token.json`, từ video thứ 2 trở đi bạn không phải làm lại bước này.

---

## 📁 5. Kết quả nằm ở đâu?

- Mọi kết quả (ảnh, file srt tạm) nằm trong thư mục: `tên_video_out/`.
- File phụ đề cuối cùng sẽ cùng tên với video, định dạng `.srt`.

---

## 🧹 6. Dọn dẹp để tiết kiệm dung lượng

Codespaces có giới hạn ổ đĩa. Sau khi xong việc, hãy xóa các thư mục ảnh nặng bằng lệnh:
```bash
rm -rf *_out/
```

---

*Chúc bạn 6 tháng tới làm việc hiệu quả! Mọi thứ đã được tối ưu cho Ubuntu 20.04 Focal chuẩn.*
