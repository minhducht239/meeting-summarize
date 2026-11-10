TransMeet

Hệ thống tự động chuyển đổi file ghi âm cuộc họp (âm thanh/video như `.mp4`, `.mp3`, `.wav`) thành văn bản và tạo biên bản tóm tắt cuộc họp (Meeting Minutes) chi tiết.

---

##  Tính năng chính

-  **Hỗ trợ đa định dạng**: Chấp nhận cả file âm thanh (`.mp3`, `.wav`, `.m4a`) và file video (`.mp4`, `.mkv`, `.mov`) mà không cần convert thủ công.
-  **Gỡ băng siêu tốc**: Sử dụng mô hình **Whisper-large-v3-turbo** qua Groq API (xử lý cuộc họp 2 tiếng trong vòng chưa đầy 30 giây).
-  **Tóm tắt chuyên nghiệp bằng LLM**: Sử dụng `openai/gpt-oss-120b` (hoặc `gpt-4o-mini`) để trích xuất:
  - Thông tin và thành phần tham gia cuộc họp.
  - Các chủ đề cốt lõi đã thảo luận (Agenda Topics).
  - Các quyết định quan trọng đã chốt (Key Decisions).
  - Bảng phân công nhiệm vụ cụ thể (**Action Items**: Task, Assignee, Deadline).
  - Rủi ro, khúc mắc và tổng kết cuộc họp.
-  **Tự động chia nhỏ (Chunking) & Tối ưu TPM**: Tự động chia nhỏ video/audio dài hàng giờ để tránh giới hạn kích thước file và tránh vượt quá hạn mức Token Per Minute (TPM) của LLM.

---

##  Cài đặt & Sử dụng

### 1. Cài đặt môi trường
Yêu cầu hệ thống đã cài đặt [FFmpeg](https://ffmpeg.org/) và Python 3.10+.

```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Cài đặt thư viện
pip install -r transmeet_repo/requirements.txt
pip install python-dotenv
pip install -e transmeet_repo
```

### 2. Cấu hình API Key
Tạo file `.env` từ `.env.example`:
```bash
cp .env.example .env
```
Điền key của bạn vào file `.env`:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 3. Chạy chương trình
Đặt file ghi âm/video vào thư mục dự án và chạy:
```powershell
python run_transmeet.py
```
Hoặc chỉ định trực tiếp đường dẫn file:
```powershell
python run_transmeet.py "path/to/meeting.mp4"
```

Kết quả sẽ được tự động xuất ra thư mục `output/`:
- `transcript_<tên_file>.txt`: Toàn bộ lời thoại gỡ băng.
- `meeting_minutes_<tên_file>.md`: Biên bản cuộc họp chuẩn Markdown.
