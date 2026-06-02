#!/bin/bash
# install.sh - Bản tối ưu cho repo autovsf-codespaces (chạy tại root)

set -e

echo "🚀 [1/4] Cài đặt thư viện hệ thống..."
sudo apt-get update
sudo apt-get install -y xvfb libgtk-3-0 libxss1 libasound2 libnss3 wget tar

echo "🚀 [2/4] Cài đặt thư viện Python..."
pip install watchdog google-api-python-client google-auth-oauthlib google-auth httplib2 opencv-python psutil Pillow

echo "🚀 [3/4] Tải và tối ưu hóa VideoSubFinder..."
VSF_LINK="https://github.com/lionc2240/autovsf-codespaces/releases/download/VideoSubFinder_6.10_ubu20.04.tar.xz/VideoSubFinder_6.10_ubu20.04.tar.xz"
VSF_FILE="VideoSubFinder_6.10_ubu20.04.tar.xz"

# Tải VSF vào thư mục cùng cấp với repo để tránh Git theo dõi
if [ ! -d "../VideoSubFinder" ]; then
    echo "Đang tải bản gốc vào thư mục cha..."
    wget -O ../$VSF_FILE $VSF_LINK
    echo "Đang giải nén..."
    tar -xf ../$VSF_FILE -C ../
    rm ../$VSF_FILE
fi

# Vá lỗi file .run
echo "Đang tối ưu hóa file khởi chạy..."
cat <<EOF > ../VideoSubFinder/VideoSubFinderWXW.run
#!/bin/sh
export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:"\$PWD"
if [ -z "\$DISPLAY" ]; then
    xvfb-run -a ./VideoSubFinderWXW "\$@"
else
    ./VideoSubFinderWXW "\$@"
fi
EOF

echo "🚀 [4/4] Cấp quyền thực thi..."
chmod +x run.sh headless.py ocr.py install.sh
chmod +x ../VideoSubFinder/VideoSubFinderWXW ../VideoSubFinder/VideoSubFinderWXW.run

echo "==========================================================="
echo "🎉 CÀI ĐẶT THÀNH CÔNG TẠI GỐC REPO!"
echo "==========================================================="
