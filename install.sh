#!/bin/bash
# install.sh - Bản vạn năng (Đã sửa lỗi dpkg-deb và tối ưu cho Focal/Noble)

set -e

REPO_DIR=$(pwd)
PARENT_DIR=$(dirname "$REPO_DIR")
VSF_DIR="$PARENT_DIR/VideoSubFinder"
LIBS_DIR="$VSF_DIR/legacy_libs"
OS_CODENAME=$(lsb_release -sc)

echo "🌍 Phát hiện hệ điều hành: Ubuntu $OS_CODENAME"

echo "🚀 [1/4] Cài đặt công cụ hỗ trợ..."
sudo apt-get update
# Đã xóa dpkg-deb vì nó nằm trong gói dpkg có sẵn
sudo apt-get install -y xvfb libxss1 libnss3 wget tar curl ffmpeg

# Xử lý thư viện đồ họa và codecs theo phiên bản
if [[ "$OS_CODENAME" == "noble" ]]; then
    echo "⚠️  Phát hiện Ubuntu 24.04 (Noble). Đang kích hoạt chế độ vá lỗi..."
    sudo apt-get install -y libgtk-3-0t64 libasound2t64 libnuma1
    
    mkdir -p "$LIBS_DIR"
    cd "$LIBS_DIR"
    declare -A DEBS=(
        ["libaom0"]="http://azure.archive.ubuntu.com/ubuntu/pool/main/a/aom/libaom0_1.0.0.errata1-3+deb11u1ubuntu0.1_amd64.deb"
        ["libvpx6"]="http://azure.archive.ubuntu.com/ubuntu/pool/main/libv/libvpx/libvpx6_1.8.2-1ubuntu0.4_amd64.deb"
        ["libx264-155"]="http://azure.archive.ubuntu.com/ubuntu/pool/main/x/x264/libx264-155_0.155.2917+git0a84d98-2_amd64.deb"
        ["libx265-179"]="http://azure.archive.ubuntu.com/ubuntu/pool/main/x/x265/libx265-179_3.2.1-1build1_amd64.deb"
        ["libflite1"]="http://azure.archive.ubuntu.com/ubuntu/pool/main/f/flite/libflite1_2.1-release-3_amd64.deb"
        ["libwavpack1"]="http://azure.archive.ubuntu.com/ubuntu/pool/main/w/wavpack/libwavpack1_5.2.0-1ubuntu0.1_amd64.deb"
    )
    for pkg in "${!DEBS[@]}"; do
        curl -L -o "$pkg.deb" "${DEBS[$pkg]}"
        dpkg -x "$pkg.deb" .
        find usr/lib/x86_64-linux-gnu/ -name "*.so*" -exec mv {} . \;
        rm "$pkg.deb"
    done
    rm -rf usr/
    cd "$REPO_DIR"
else
    echo "✅ Môi trường Focal (20.04) chuẩn. Cài đặt trực tiếp từ kho hệ thống..."
    sudo apt-get install -y libgtk-3-0 libasound2 libnuma1 libaom0 libvpx6 libx264-155 libx265-179 libflite1 libwavpack1 || true
fi

echo "🚀 [2/4] Cài đặt thư viện Python..."
pip install watchdog google-api-python-client google-auth-oauthlib google-auth httplib2 opencv-python psutil Pillow

echo "🚀 [3/4] Tải và cấu hình VideoSubFinder..."
VSF_LINK="https://github.com/lionc2240/autovsf-codespaces/releases/download/VideoSubFinder_6.10_ubu20.04.tar.xz/VideoSubFinder_6.10_ubu20.04.tar.xz"
VSF_FILE="VideoSubFinder_6.10_ubu20.04.tar.xz"

if [ ! -d "$VSF_DIR" ]; then
    echo "Đang tải VideoSubFinder..."
    curl -L -o "$PARENT_DIR/$VSF_FILE" "$VSF_LINK"
    tar -xf "$PARENT_DIR/$VSF_FILE" -C "$PARENT_DIR/"
    rm "$PARENT_DIR/$VSF_FILE"
fi

# Cấu hình file .run
cat <<EOF > "$VSF_DIR/VideoSubFinderWXW.run"
#!/bin/sh
export LD_LIBRARY_PATH="$LIBS_DIR:\$PWD:\$LD_LIBRARY_PATH"
if [ -z "\$DISPLAY" ]; then
    xvfb-run -a ./VideoSubFinderWXW "\$@"
else
    ./VideoSubFinderWXW "\$@"
fi
EOF

echo "🚀 [4/4] Cấp quyền thực thi..."
chmod +x run.sh headless.py ocr.py install.sh
chmod +x "$VSF_DIR/VideoSubFinderWXW" "$VSF_DIR/VideoSubFinderWXW.run"

echo "==========================================================="
echo "🎉 CÀI ĐẶT HOÀN TẤT TRÊN $OS_CODENAME!"
echo "==========================================================="
