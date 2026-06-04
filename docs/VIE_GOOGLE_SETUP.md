# Hướng dẫn thiết lập Google Cloud cho AutoVSF

Để sử dụng tính năng OCR, bạn cần thiết lập một dự án trên Google Cloud Console để lấy file `credentials.json`.

## Bước 1: Tạo Dự án Google Cloud
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/).
2. Đăng nhập bằng tài khoản Google của bạn.
3. Tạo một dự án mới (New Project) hoặc chọn một dự án đã có.

## Bước 2: Bật Google Drive API
1. Trên thanh tìm kiếm ở phía trên cùng, tìm từ khóa **"Google Drive API"**.
2. Chọn kết quả tương ứng và nhấn nút **"Enable"**.

## Bước 3: Tạo file xác thực (credentials.json)
1. Truy cập vào mục **"APIs & Services"** > **"Credentials"** từ menu bên trái.
2. Nhấn **"Create Credentials"** ở phía trên và chọn **"OAuth client ID"**.
3. Nếu đây là lần đầu, bạn có thể cần nhấn **"Configure Consent Screen"**:
    - Chọn **External**.
    - Điền các thông tin bắt buộc (Tên app, Email hỗ trợ).
4. Quay lại trang **Create OAuth client ID**:
    - **Application type**: Chọn **Desktop app**.
    - **Name**: Đặt tên tùy ý (ví dụ: `AutoVSF-OCR`).
    - Nhấn **Create**.
5. Một hộp thoại hiện ra, hãy nhấn **"Download JSON"**.
6. Đổi tên file vừa tải về thành `credentials.json` và lưu vào thư mục chứa mã nguồn của dự án (cùng cấp với file `main.py`).

## Bước 4: Thiết lập trạng thái xác thực (Quan trọng)
Để chương trình có thể tự động mở trình duyệt và xác thực mà không gặp lỗi "App not verified":
1. Tại [Google Cloud Console](https://console.cloud.google.com/), truy cập mục **"APIs & Services"** > **"Audience"**.
2. Tìm phần **"Publishing status"**.
3. Nhấn nút **"PUBLISH APP"** và xác nhận.
    - Việc này sẽ chuyển trạng thái từ "Testing" sang "In production", giúp quá trình đăng nhập lần đầu (tạo `token.json`) diễn ra trơn tru.

---
*Sau khi hoàn tất, bạn có thể khởi động `main.py` và bắt đầu sử dụng!*
