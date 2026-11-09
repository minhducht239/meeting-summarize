import os
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq()
model = "openai/gpt-oss-120b"

transcript = open(r"output\transcript_Meeting in General-20261030_182605-Meeting Recording.txt", encoding="utf-8").read()
print(f"Total transcript length: {len(transcript)} characters")

# Split into chunks of ~16,000 chars
chunk_size = 18000
chunks = [transcript[i:i+chunk_size] for i in range(0, len(transcript), chunk_size)]
print(f"Split into {len(chunks)} chunks")

partial_summaries = []
for idx, chunk in enumerate(chunks):
    print(f"Summarizing chunk {idx + 1}/{len(chunks)}...")
    prompt = f"""Dưới đây là phần {idx + 1} của một buổi thảo luận / cuộc họp dài.
Hãy tóm tắt chi tiết các chủ đề, ý chính, thảo luận kỹ thuật, quyết định và phân tích được đề cập:

---
{chunk}
---
Tóm tắt chi tiết phần {idx + 1}:"""

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Bạn là chuyên gia ghi chép và tóm tắt cuộc họp/bài giảng kỹ thuật."},
            {"role": "user", "content": prompt}
        ]
    )
    partial_summaries.append(resp.choices[0].message.content)
    print(f"Chunk {idx + 1} completed!")
    if idx < len(chunks) - 1:
        print("Waiting 15 seconds to stay within Groq TPM limits...")
        time.sleep(15)

combined_text = "\n\n".join([f"### Tóm tắt phần {i+1}:\n{s}" for i, s in enumerate(partial_summaries)])
print("Generating final structured meeting minutes...")
time.sleep(10)

final_prompt = f"""Dưới đây là tổng hợp nội dung chi tiết từ một buổi họp / bài giảng kỹ thuật kéo dài 2 tiếng:

{combined_text}

Dựa vào các thông tin trên, hãy lập một BIÊN BẢN CUỘC HỌP (Meeting Minutes) chi tiết, chuyên nghiệp theo cấu trúc sau:
# 📝 Biên bản cuộc họp: Thảo luận Kiến trúc RAG Nâng cao & AI Chatbot

- **Chủ đề chính**: Kiến trúc RAG (Retrieval-Augmented Generation), Kỹ thuật xử lý Query, Routing Đa cơ sở dữ liệu và Đánh giá hệ thống AI
- **Thời lượng**: ~2 tiếng
- **Mục tiêu**: Nâng cấp hệ thống hỏi đáp AI từ cơ bản lên nâng cao (>80% độ chính xác)

## 📌 Các chủ đề thảo luận chính (Agenda Topics)
(Liệt kê chi tiết từng phần: RAG cơ bản vs nâng cao, Query Translation/Decomposition, Multi-turn Chatbot, Routing đa nguồn dữ liệu SQL/Text/Graph, Multimodal RAG với hình ảnh/bản vẽ, Chunking & Embedding)

##  Các kiến trúc & giải pháp kỹ thuật được đề xuất
(Tóm tắt rõ các phương án: Step-back, RAG-Fusion, Routing phân loại câu hỏi dễ/khó, MCP Server Database, Text-to-SQL)

## 💡 Các ví dụ thực tế được chia sẻ
(Chi tiết các case study: Phần mềm quản trị doanh nghiệp Base/OneOffice, Bất động sản với bản vẽ mặt bằng nhà/hướng ban công la bàn,...)

## ✅ Quyết định & Định hướng giải pháp
(Các kết luận và bài học rút ra)

## 📋 Nhiệm vụ & Hành động tiếp theo (Action Items)
| Việc cần làm | Người/Bộ phận phụ trách | Mục tiêu |
|---|---|---|

## 🎯 Tổng kết (Meeting Summary)
"""

resp = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "Bạn là thư ký chuyên nghiệp chuyên soạn thảo biên bản cuộc họp và tổng kết kỹ thuật."},
        {"role": "user", "content": final_prompt}
    ]
)

final_minutes = resp.choices[0].message.content
output_file = r"output\meeting_minutes_Meeting in General-20261030_182605-Meeting Recording.md"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(final_minutes)

print("SUCCESS! Final minutes saved to:", output_file)

