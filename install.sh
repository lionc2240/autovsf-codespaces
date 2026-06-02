#!/bin/bash
# install.sh - Thiết lập tự động AutoVSF cho Codespaces

set -e # Dừng nếu có lỗi

echo "🚀 [1/4] Cập nhật hệ thống và cài đặt Xvfb (màn hình ảo)..."
sudo apt-get update
sudo apt-get install -y xvfb libgtk-3-0 libxss1 libasound2 libnss3 wget tar

echo "🚀 [2/4] Cài đặt các thư viện Python..."
pip install watchdog google-api-python-client google-auth-oauthlib google-auth httplib2 opencv-python psutil Pillow

echo "🚀 [3/4] Tải và giải nén VideoSubFinder từ GitHub Release..."
# Link Release bạn cung cấp
VSF_LINK="https://github.com/lionc2240/autovsf-codespaces/releases/download/VideoSubFinder_6.10_ubu20.04.tar.xz/VideoSubFinder_6.10_ubu20.04.tar.xz"
VSF_FILE="VideoSubFinder_6.10_ubu20.04.tar.xz"

# Chuyển ra thư mục gốc để giải nén
cd ..
if [ ! -d "VideoSubFinder" ]; then
    echo "Đang tải VideoSubFinder..."
    wget -O $VSF_FILE $VSF_LINK
    echo "Đang giải nén..."
    tar -xf $VSF_FILE
    rm $VSF_FILE
    echo "✅ Đã tải và giải nén VideoSubFinder."
else
    echo "✅ Thư mục VideoSubFinder đã tồn tại, bỏ qua bước tải."
fi

echo "🚀 [4/4] Thiết lập quyền thực thi cho Tool..."
cd autovsf
chmod +x run.sh headless.py ocr.py install.sh
chmod +x ../VideoSubFinder/VideoSubFinderWXW ../VideoSubFinder/VideoSubFinderWXW.run

echo "==========================================================="
echo "🎉 HOÀN TẤT CÀI ĐẶT TRÊN CODESPACES MỚI!"
echo ""
echo "Hướng dẫn sử dụng nhanh:"
echo "1. Upload file 'credentials.json' vào thư mục 'autovsf/'."
echo "2. Chạy toàn bộ quy trình: python3 headless.py <video.mp4>"
echo "3. Chỉ chạy OCR: python3 ocr.py <thư_mục_ảnh>"
echo "==========================================================="
