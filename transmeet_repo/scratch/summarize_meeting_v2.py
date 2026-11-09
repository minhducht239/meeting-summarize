import os
import time
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq()
model = "openai/gpt-oss-120b"

transcript_path = r"output\transcript_Meeting in General-20261030_182605-Meeting Recording.txt"
with open(transcript_path, "r", encoding="utf-8") as f:
    transcript = f.read()

cache_dir = Path(r"output\chunk_summaries")
cache_dir.mkdir(parents=True, exist_ok=True)

chunk_size = 9000
chunks = [transcript[i:i+chunk_size] for i in range(0, len(transcript), chunk_size)]
total_chunks = len(chunks)
print(f"Tổng số phần: {total_chunks}")

partial_summaries = []

for idx, chunk in enumerate(chunks):
    cache_file = cache_dir / f"summary_part_{idx + 1}.txt"
    if cache_file.exists():
        print(f" Đã có sẵn cache phần {idx + 1}/{total_chunks}, đang nạp từ file...")
        with open(cache_file, "r", encoding="utf-8") as cf:
            partial_summaries.append(cf.read())
        continue

    print(f"\n⏳ Đang tóm tắt đoạn {idx + 1}/{total_chunks}...")
    prompt = f"""Dưới đây là phần {idx + 1}/{total_chunks} của một buổi thảo luận / đào tạo kỹ thuật chuyên sâu về AI & RAG.
Hãy tóm tắt cô đọng (khoảng 300 - 450 từ) các nội dung kỹ thuật, kiến trúc, case study và quyết định quan trọng:

--- NỘI DUNG ---
{chunk}
--- HẾT NỘI DUNG ---

Tóm tắt cô đọng phần {idx + 1}:"""

    for attempt in range(5):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Bạn là chuyên gia phân tích kỹ thuật và thư ký cuộc họp chuyên nghiệp."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800
            )
            summary = resp.choices[0].message.content
            partial_summaries.append(summary)
            with open(cache_file, "w", encoding="utf-8") as cf:
                cf.write(summary)
            print(f" Hoàn thành và lưu cache phần {idx + 1}/{total_chunks}")
            break
        except Exception as e:
            wait_s = 30 + attempt * 10
            print(f"⚠️ Thử lại sau {wait_s}s do giới hạn token: {e}")
            time.sleep(wait_s)

    if idx < total_chunks - 1:
        print("Đang nghỉ 28s trước đoạn tiếp theo...")
        time.sleep(28)

print("\n🚀 Đang tổng hợp các phần thành Biên bản cuộc họp hoàn chỉnh...")
time.sleep(25)

combined_text = "\n\n".join([f"### Tóm tắt phần {i+1}:\n{s}" for i, s in enumerate(partial_summaries)])
print(f"Độ dài bản tổng hợp các phần: {len(combined_text)} ký tự (~{len(combined_text)//4} tokens)")

final_prompt = f"""Dưới đây là tổng hợp nội dung chi tiết từ 5 phần của một buổi họp / bài giảng kỹ thuật 2 tiếng:

{combined_text}

Dựa vào các thông tin trên, hãy lập một BIÊN BẢN CUỘC HỌP (Meeting Minutes) chi tiết, chuyên nghiệp bằng Tiếng Việt theo cấu trúc sau:

# 📝 BIÊN BẢN CUỘC HỌP & ĐÀO TẠO KỸ THUẬT: ADVANCED RAG & AI CHATBOT

- **Chủ đề chính**: Kiến trúc RAG Nâng Cao, Kỹ Thuật Viết Lại Truy Vấn, Routing Đa Cơ Sở Dữ Liệu và Đánh Giá Hệ Thống
- **Thời lượng**: ~2 tiếng
- **Mục tiêu**: Nâng cấp độ chính xác và khả năng xử lý truy vấn phức tạp của hệ thống Chatbot/RAG từ 70-80% lên >90%

---

## 1. 📌 Tổng quan các chủ đề thảo luận chính (Agenda Topics)
(Tóm tắt cụ thể: RAG cơ bản vs nâng cao; Query Translation & Decomposition; Multi-turn Chatbot và Contextual History; Routing đa cơ sở dữ liệu SQL, Text, Graph; Multimodal RAG với hình ảnh/bản vẽ; Kỹ thuật Chunking, Embedding và Re-ranking).

## 2. ⚙️ Chi tiết các giải pháp & kỹ thuật kiến trúc
(Trình bày chi tiết cơ chế:
- Multi-query, Step-back question, RAG-Fusion, Recursive Query
- Bộ định tuyến Routing phân loại câu hỏi Dễ vs Khó
- Tích hợp Database MCP Server, Text-to-SQL tự động
- Đồ thị tri thức (Graph Database) với Cypher Query
- Xử lý bản vẽ/hình ảnh căn hộ với Gemini, Qwen-VL, BGE-M3 embedding)

## 3. 🏢 Các tình huống & Case Study thực tế trong doanh nghiệp
(Chi tiết các ví dụ: Phần mềm quản trị OneOffice/Base với phân quyền phòng ban; Bất động sản xác định hướng ban công từ bản vẽ mặt bằng; Cách thiết kế các kho dữ liệu text riêng cho từng bộ phận).

## 4. 📊 Phương pháp đánh giá hệ thống (Evaluation & Ground Truth)
(Cách chia nhỏ để đánh giá từng module độc lập, tầm quan trọng của việc xây dựng benchmark dữ liệu test).

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
                {"role": "system", "content": "Bạn là thư ký trưởng am hiểu sâu sắc về AI, chuyên soạn thảo biên bản cuộc họp và báo cáo kỹ thuật cấp cao."},
                {"role": "user", "content": final_prompt}
            ]
        )
        final_minutes = resp.choices[0].message.content
        output_file = r"output\meeting_minutes_Meeting in General-20261030_182605-Meeting Recording.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_minutes)
        print(f"\n🎉 THÀNH CÔNG! Đã lưu biên bản hoàn chỉnh tại: {output_file}")
        break
    except Exception as e:
        wait_s = 35 + attempt * 10
        print(f"⚠️ Chạm giới hạn token. Đang chờ {wait_s}s để thử lại ({attempt + 1}/5): {e}")
        time.sleep(wait_s)

