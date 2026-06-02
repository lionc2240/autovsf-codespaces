#!/bin/bash
# install.sh - Tối ưu cho Ubuntu 24.04, dùng curl và đường dẫn tuyệt đối

set -e

# Xác định thư mục
REPO_DIR=$(pwd)
PARENT_DIR=$(dirname "$REPO_DIR")
VSF_DIR="$PARENT_DIR/VideoSubFinder"

echo "🚀 [1/4] Cài đặt thư viện hệ thống..."
sudo apt-get update
sudo apt-get install -y xvfb libxss1 libnss3 wget tar curl
# Sửa lỗi tên gói cho Ubuntu 24.04
sudo apt-get install -y libgtk-3-0 libasound2 || sudo apt-get install -y libgtk-3-0t64 libasound2t64

echo "🚀 [2/4] Cài đặt thư viện Python..."
pip install watchdog google-api-python-client google-auth-oauthlib google-auth httplib2 opencv-python psutil Pillow

echo "🚀 [3/4] Tải VideoSubFinder bằng curl..."
VSF_LINK="https://github.com/lionc2240/autovsf-codespaces/releases/download/v1.0.0/VideoSubFinder_6.10_ubu20.04.tar.xz"
VSF_FILE="VideoSubFinder_6.10_ubu20.04.tar.xz"

if [ ! -f "$VSF_DIR/VideoSubFinderWXW" ]; then
    echo "Đang tải vào: $PARENT_DIR"
    # Dùng curl -L để tự động chuyển hướng link GitHub
    curl -L -o "$PARENT_DIR/$VSF_FILE" "$VSF_LINK"
    
    echo "Đang giải nén..."
    tar -xf "$PARENT_DIR/$VSF_FILE" -C "$PARENT_DIR/"
    rm "$PARENT_DIR/$VSF_FILE"
    echo "✅ Tải và giải nén hoàn tất."
else
    echo "✅ VideoSubFinder đã có sẵn, bỏ qua bước tải."
fi

# Tối ưu hóa file khởi chạy
echo "Đang cấu hình file .run..."
cat <<EOF > "$VSF_DIR/VideoSubFinderWXW.run"
#!/bin/sh
export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:"\$PWD"
if [ -z "\$DISPLAY" ]; then
    xvfb-run -a ./VideoSubFinderWXW "\$@"
else
    ./VideoSubFinderWXW "\$@"
fi
EOF

echo "🚀 [4/4] Cấp quyền thực thi..."
chmod +x "$REPO_DIR/run.sh" "$REPO_DIR/headless.py" "$REPO_DIR/ocr.py" "$REPO_DIR/install.sh"
chmod +x "$VSF_DIR/VideoSubFinderWXW" "$VSF_DIR/VideoSubFinderWXW.run"

echo "==========================================================="
echo "🎉 CÀI ĐẶT THÀNH CÔNG!"
echo "Đường dẫn VSF: $VSF_DIR"
echo "Lệnh chạy quét video: python3 headless.py <video.mp4>"
echo "==========================================================="
