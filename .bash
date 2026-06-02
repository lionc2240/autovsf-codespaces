gcommit() {
# Kiểm tra xem đã có thay đổi nào được stage (git add) chưa
if git diff --cached --quiet; then
echo "No staged changes to commit."
return 1
fi

echo "Generating commit message..."

# Lấy diff và gửi qua gemini CLI để tạo message
# Lưu ý: Cần đảm bảo lệnh 'gemini' đã được cài đặt và có trong PATH của bạn
local msg=$(git diff --cached | gemini -p "Write a concise Conventional Commit message for this diff. Output ONLY the message.")

if [ -z "$msg" ]; then
echo "Error: Could not generate commit message."
return 1
fi

# Thực hiện commit
git commit -m "$msg"
}
