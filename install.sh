#!/bin/bash
# install.sh - Bản đặc biệt sửa lỗi thiếu thư viện cho Ubuntu 24.04 (Noble)

set -e

REPO_DIR=$(pwd)
PARENT_DIR=$(dirname "$REPO_DIR")
VSF_DIR="$PARENT_DIR/VideoSubFinder"

echo "🚀 [1/4] Cài đặt trọn bộ thư viện hệ thống và Codecs..."
sudo apt-get update
# Cài đặt ffmpeg (để có hầu hết các codecs) và các thư viện đồ họa
sudo apt-get install -y xvfb libxss1 libnss3 wget tar curl ffmpeg libwavpack1

# Sửa lỗi tên gói cho Ubuntu 24.04 (gtk và asound)
sudo apt-get install -y libgtk-3-0 libasound2 || sudo apt-get install -y libgtk-3-0t64 libasound2t64

echo "🚀 [2/4] Cài đặt thư viện Python..."
pip install watchdog google-api-python-client google-auth-oauthlib google-auth httplib2 opencv-python psutil Pillow

echo "🚀 [3/4] Tải/Kiểm tra VideoSubFinder..."
VSF_LINK="https://github.com/lionc2240/autovsf-codespaces/releases/download/v1.0.0/VideoSubFinder_6.10_ubu20.04.tar.xz"
VSF_FILE="VideoSubFinder_6.10_ubu20.04.tar.xz"

if [ ! -f "$VSF_DIR/VideoSubFinderWXW" ]; then
    echo "Đang tải bản gốc..."
    curl -L -o "$PARENT_DIR/$VSF_FILE" "$VSF_LINK"
    tar -xf "$PARENT_DIR/$VSF_FILE" -C "$PARENT_DIR/"
    rm "$PARENT_DIR/$VSF_FILE"
fi

# Tối ưu hóa file .run với LD_LIBRARY_PATH để nhận diện các file .so đi kèm
echo "Đang cấu hình file khởi chạy..."
cat <<EOF > "$VSF_DIR/VideoSubFinderWXW.run"
#!/bin/sh
# Thêm thư mục hiện tại vào thư viện để ưu tiên các file .so có sẵn trong folder
export LD_LIBRARY_PATH="\$PWD:\$LD_LIBRARY_PATH"
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
echo "Đã bổ sung libwavpack1 và ffmpeg cho Ubuntu 24.04."
echo "==========================================================="
