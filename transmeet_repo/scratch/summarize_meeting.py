import os
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq()
model = "openai/gpt-oss-120b"

transcript_path = r"output\transcript_Meeting in General-20261030_182605-Meeting Recording.txt"
with open(transcript_path, "r", encoding="utf-8") as f:
    transcript = f.read()

print(f"Tổng số ký tự transcript: {len(transcript)} ký tự")

chunk_size = 9000
chunks = [transcript[i:i+chunk_size] for i in range(0, len(transcript), chunk_size)]
total_chunks = len(chunks)
print(f"Đã chia thành {total_chunks} phần nhỏ để xử lý tuần tự (tránh giới hạn TPM)...")

partial_summaries = []

for idx, chunk in enumerate(chunks):
    print(f"\n⏳ Đang tóm tắt đoạn {idx + 1}/{total_chunks}...")
    prompt = f"""Dưới đây là phần {idx + 1}/{total_chunks} của một buổi thảo luận / đào tạo kỹ thuật chuyên sâu về AI & RAG.
Hãy trích xuất và tóm tắt chi tiết các nội dung, kỹ thuật, ví dụ thực tế và thảo luận được nêu:

--- NỘI DUNG ---
{chunk}
--- HẾT NỘI DUNG ---

Yêu cầu: Viết bản tóm tắt chi tiết cho phần này (tiếng Việt), nêu rõ các giải pháp công nghệ, thuật ngữ và case study nếu có:"""

    max_retries = 5
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Bạn là chuyên gia phân tích kỹ thuật và thư ký cuộc họp chuyên nghiệp."},
                    {"role": "user", "content": prompt}
                ]
            )
            summary = resp.choices[0].message.content
            partial_summaries.append(summary)
            print(f"✅ Hoàn thành tóm tắt đoạn {idx + 1}/{total_chunks}")
            break
        except Exception as e:
            err = str(e)
            if "429" in err or "413" in err or "tokens" in err:
                wait_s = 35 + attempt * 10
                print(f"⚠️ Chạm giới hạn Groq TPM. Đang nghỉ {wait_s}s trước khi thử lại ({attempt + 1}/{max_retries})...")
                time.sleep(wait_s)
            elif attempt == max_retries - 1:
                raise e
            else:
                time.sleep(10)

    # Nghỉ 28 giây để Groq nạp lại hạn mức 8000 TPM
    if idx < total_chunks - 1:
        print("Đang chờ 28s để nạp lại hạn mức API...")
        time.sleep(28)

print("\n🚀 Đang tổng hợp các phần thành Biên bản cuộc họp hoàn chỉnh...")
time.sleep(25)

combined_text = "\n\n".join([f"### Tóm tắt phần {i+1}:\n{s}" for i, s in enumerate(partial_summaries)])

final_prompt = f"""Dưới đây là tóm tắt toàn bộ các phần từ một buổi họp / bài giảng kỹ thuật kéo dài 2 tiếng:

{combined_text}

Dựa vào các thông tin chi tiết trên, hãy soạn thảo một BIÊN BẢN CUỘC HỌP (Meeting Minutes) đầy đủ, chuyên nghiệp bằng Tiếng Việt theo định dạng Markdown chuẩn với cấu trúc sau:

# 📝 BIÊN BẢN CUỘC HỌP & ĐÀO TẠO KỸ THUẬT

- **Chủ đề**: Kiến trúc RAG Nâng Cao (Advanced RAG), Kỹ thuật Tối ưu Query, Routing Đa Cơ Sở Dữ Liệu và Đánh Giá Hệ Thống AI
- **Thời lượng**: ~2 tiếng
- **Mục tiêu**: Nâng cấp độ chính xác và khả năng xử lý truy vấn phức tạp của hệ thống Chatbot/RAG từ 70-80% lên >90%

---

## 1. 📌 Tổng quan các chủ đề thảo luận chính (Agenda Topics)
(Tóm tắt cụ thể các phần kiến thức: Luồng RAG cơ bản vs RAG nâng cao; Query Translation & Decomposition; Multi-turn Chatbot và Contextual History; Routing đa cơ sở dữ liệu SQL, Text, Graph; Multimodal RAG với hình ảnh/bản vẽ; Kỹ thuật Chunking, Embedding và Re-ranking).

## 2. ⚙️ Chi tiết các giải pháp & kỹ thuật kiến trúc
(Trình bày chi tiết cơ chế hoạt động của:
- Multi-query, Step-back question, RAG-Fusion, Recursive Query
- Bộ định tuyến Routing phân loại câu hỏi Dễ vs Khó
- Tích hợp Database MCP Server, Text-to-SQL tự động
- Đồ thị tri thức (Graph Database) với Cypher Query
- Xử lý bản vẽ/hình ảnh căn hộ với Gemini, Qwen-VL, BGE-M3 embedding)

## 3. 🏢 Các tình huống & Case Study thực tế trong doanh nghiệp
(Chi tiết các ví dụ thực tế được chia sẻ trong buổi họp: Phần mềm quản trị OneOffice/Base với phân quyền phòng ban; Bất động sản xác định hướng ban công từ bản vẽ mặt bằng; Cách thiết kế các kho dữ liệu text riêng cho từng bộ phận).

## 4. 📊 Phương pháp đánh giá hệ thống (Evaluation & Ground Truth)
(Cách chia nhỏ để đánh giá từng module độc lập, tầm quan trọng của việc xây dựng benchmark dữ liệu test thay vì chỉ đo lường kết quả đầu ra tổng thể).

## 5. 📋 Bảng kế hoạch hành động & Đề xuất (Action Items)
| STT | Nhiệm vụ / Hạng mục kỹ thuật | Mục tiêu | Trọng tâm cần lưu ý |
|---|---|---|---|

## 6. 🎯 Tổng kết (Executive Summary)
(Tóm tắt 3-5 câu cô đọng nhất về giá trị và định hướng sau buổi họp).
"""

for attempt in range(5):
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Bạn là thư ký trưởng am hiểu sâu sắc về AI, chuyên soạn thảo biên bản cuộc họp và báo cáo kiến trúc kỹ thuật cấp cao."},
                {"role": "user", "content": final_prompt}
            ]
        )
        final_minutes = resp.choices[0].message.content
        break
    except Exception as e:
        wait_s = 35 + attempt * 10
        print(f"⚠️ Chạm giới hạn token. Đang chờ {wait_s}s để thử lại ({attempt + 1}/5)...")
        time.sleep(wait_s)

output_file = r"output\meeting_minutes_Meeting in General-20261030_182605-Meeting Recording.md"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(final_minutes)

print(f"\n🎉 THÀNH CÔNG! Đã lưu biên bản hoàn chỉnh tại: {output_file}")

