"""
Script chạy TransMeet để chuyển file ghi âm thành văn bản và tóm tắt cuộc họp.
Tự động nạp API key từ file .env.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Tự động nạp API key từ file .env
load_dotenv()

from transmeet import generate_meeting_transcript_and_minutes

SUPPORTED_EXTENSIONS = [".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac", ".mp4", ".mkv", ".mov", ".webm"]

def find_audio_file():
    """Tự động tìm file âm thanh trong thư mục hiện tại nếu không chỉ định."""
    current_dir = Path(".")
    for ext in SUPPORTED_EXTENSIONS:
        files = list(current_dir.glob(f"*{ext}"))
        if files:
            return files[0]
    return None

def main():
    # 1. Kiểm tra API Key
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not groq_key and not openai_key:
        print(" Vui lòng mở file .env và điền key")
        return

    # Mặc định ưu tiên dùng Groq
    client_choice = "groq" if groq_key else "openai"
    transcription_model = "whisper-large-v3-turbo" if client_choice == "groq" else "whisper-1"
    llm_model = "openai/gpt-oss-120b" if client_choice == "groq" else "gpt-4o-mini"

    # 2. Xác định file âm thanh đầu vào
    if len(sys.argv) > 1:
        audio_file = Path(sys.argv[1])
    else:
        audio_file = find_audio_file()

    if not audio_file or not audio_file.exists():
        print(" Chưa tìm thấy file âm thanh để xử lý!")
        print(f" Cách 1: Copy file ghi âm ({', '.join(SUPPORTED_EXTENSIONS)}) vào thư mục này rồi chạy lại script.")
        print(' Cách 2: Truyền đường dẫn file, ví dụ:')
        print('   .\\venv\\Scripts\\python.exe run_transmeet.py "D:\\duong_dan\\cuoc_hop.mp3"')
        return

    print(f" Đã phát hiện file âm thanh: {audio_file.name}")
    print(f" Đang sử dụng engine: {client_choice.upper()} ({transcription_model} + {llm_model})")
    print(" Đang tiến hành chuyển âm thanh thành văn bản và tạo biên bản tóm tắt...")

    output_dir = "output"
    try:
        transcript, meeting_minutes = generate_meeting_transcript_and_minutes(
            meeting_audio_file=str(audio_file),
            output_dir=output_dir,
            transcription_client=client_choice,
            transcription_model=transcription_model,
            llm_client=client_choice,
            llm_model=llm_model
        )

        base_name = audio_file.stem
        transcript_path = Path(output_dir) / f"transcript_{base_name}.txt"
        minutes_path = Path(output_dir) / f"meeting_minutes_{base_name}.md"

        print("\n" + "="*50)
        print(" HOÀN THÀNH!")
        print("="*50)
        print(f" Bản gỡ băng (Transcript): {transcript_path}")
        print(f" Biên bản cuộc họp (Minutes): {minutes_path}")
        print("\n--- TRÍCH ĐOẠN BIÊN BẢN TÓM TẮT ---")
        preview = meeting_minutes[:800] if meeting_minutes else "Không có nội dung."
        print(preview + ("\n..." if len(meeting_minutes or "") > 800 else ""))

    except Exception as e:
        print(f" Xảy ra lỗi trong quá trình xử lý: {e}")

if __name__ == "__main__":
    main()
