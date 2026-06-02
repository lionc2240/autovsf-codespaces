#!/bin/bash
# quick_install.sh - Tự động thiết lập môi trường AutoVSF cho Linux/Codespaces

set -e # Dừng nếu có lỗi

echo "🚀 [1/3] Cập nhật hệ thống và cài đặt Xvfb (màn hình ảo)..."
sudo apt-get update
sudo apt-get install -y xvfb libgtk-3-0 libxss1 libasound2 libnss3

echo "🚀 [2/3] Cài đặt các thư viện Python..."
pip install watchdog google-api-python-client google-auth-oauthlib google-auth httplib2 opencv-python psutil Pillow

echo "🚀 [3/3] Thiết lập quyền thực thi cho Tool..."
chmod +x run.sh headless.py ocr.py

# Kiểm tra nếu VideoSubFinder đã được giải nén
if [ -d "../VideoSubFinder" ]; then
    chmod +x ../VideoSubFinder/VideoSubFinderWXW ../VideoSubFinder/VideoSubFinderWXW.run
    echo "✅ VideoSubFinder đã sẵn sàng."
else
    echo "⚠️ Lưu ý: Bạn cần giải nén file VideoSubFinder_6.10_ubu20.04.tar.xz vào thư mục gốc."
fi

echo "==========================================================="
echo "🎉 HOÀN TẤT CÀI ĐẶT!"
echo "Hướng dẫn sử dụng:"
echo "1. Đảm bảo có file 'autovsf/credentials.json'."
echo "2. Chạy quét video: python3 headless.py <video.mp4>"
echo "==========================================================="
