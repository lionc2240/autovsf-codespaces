#!/bin/bash
# run.sh - Khởi chạy AutoVSF trên Linux

# Đảm bảo các thư viện Python đã được cài đặt
# pip install watchdog google-api-python-client oauth2client httplib2 opencv-python psutil Pillow

if [ -z "$DISPLAY" ]; then
    echo "Phát hiện môi trường không có màn hình (headless). Sử dụng xvfb-run..."
    xvfb-run -a python3 autovsf/main.py "$@"
else
    python3 autovsf/main.py "$@"
fi
