#!/bin/bash
# install.sh - Bản sửa lỗi tương thích sâu cho Ubuntu 24.04

set -e

REPO_DIR=$(pwd)
PARENT_DIR=$(dirname "$REPO_DIR")
VSF_DIR="$PARENT_DIR/VideoSubFinder"

echo "🚀 [1/4] Cài đặt trọn bộ thư viện hệ thống và Codecs..."
sudo apt-get update
sudo apt-get install -y xvfb libxss1 libnss3 wget tar curl ffmpeg libwavpack1 libx264-dev libx265-dev libnuma1

# Sửa lỗi tên gói cho Ubuntu 24.04 (gtk và asound)
sudo apt-get install -y libgtk-3-0 libasound2 || sudo apt-get install -y libgtk-3-0t64 libasound2t64

echo "🚀 [2/4] Tạo liên kết thư viện (Symlink) cho Ubuntu 24.04..."
# Đánh lừa VSF rằng libx264.so.155 đang tồn tại (thực tế dùng bản mới hơn của hệ thống)
LIBX264_PATH=$(find /usr/lib/x86_64-linux-gnu -name "libx264.so.*" | head -n 1)
if [ -n "$LIBX264_PATH" ]; then
    sudo ln -sf "$LIBX264_PATH" /usr/lib/x86_64-linux-gnu/libx264.so.155
    echo "✅ Đã tạo symlink cho libx264."
fi

echo "🚀 [3/4] Cài đặt thư viện Python..."
pip install watchdog google-api-python-client google-auth-oauthlib google-auth httplib2 opencv-python psutil Pillow

echo "🚀 [4/4] Cấu hình và Cấp quyền..."
# Tải VSF nếu chưa có
VSF_LINK="https://github.com/lionc2240/autovsf-codespaces/releases/download/v1.0.0/VideoSubFinder_6.10_ubu20.04.tar.xz"
VSF_FILE="VideoSubFinder_6.10_ubu20.04.tar.xz"

if [ ! -f "$VSF_DIR/VideoSubFinderWXW" ]; then
    curl -L -o "$PARENT_DIR/$VSF_FILE" "$VSF_LINK"
    tar -xf "$PARENT_DIR/$VSF_FILE" -C "$PARENT_DIR/"
    rm "$PARENT_DIR/$VSF_FILE"
fi

# Cấu hình file khởi chạy
cat <<EOF > "$VSF_DIR/VideoSubFinderWXW.run"
#!/bin/sh
export LD_LIBRARY_PATH="\$PWD:\$LD_LIBRARY_PATH"
if [ -z "\$DISPLAY" ]; then
    xvfb-run -a ./VideoSubFinderWXW "\$@"
else
    ./VideoSubFinderWXW "\$@"
fi
EOF

chmod +x "$REPO_DIR/run.sh" "$REPO_DIR/headless.py" "$REPO_DIR/ocr.py" "$REPO_DIR/install.sh"
chmod +x "$VSF_DIR/VideoSubFinderWXW" "$VSF_DIR/VideoSubFinderWXW.run"

echo "==========================================================="
echo "🎉 CÀI ĐẶT THÀNH CÔNG!"
echo "Đã vá lỗi libx264 cho Ubuntu 24.04."
echo "==========================================================="
