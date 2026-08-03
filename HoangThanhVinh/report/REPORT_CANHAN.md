# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Hoàng Thành Vinh
**Nhóm:** K4 — Ecommerce Policy Retrieval
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector có hướng gần nhau, nghĩa là hai văn bản có nội dung/ngữ nghĩa tương tự. Giá trị càng gần 1 thì mức tương đồng càng cao; giá trị gần 0 thể hiện ít liên quan.

**Ví dụ có độ tương tự CAO:**
- Câu A: Tôi thích chó
- Câu B: Tôi yêu chó
- Tại sao tương đồng: cùng thể hiện 1 ý nghĩa, chỉ là khác câu từ

**Ví dụ có độ tương tự THẤP:**
- Câu A: Tôi yêu chó 
- Câu B: Tôi ghét chó
- Tại sao khác: Thể hiện 2 ngữ nghĩa hoàn toàn khác nhau

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> vì nó tập trung vào hướng của vector, trong khi Euclidean distance còn bị ảnh hưởng bởi độ lớn của vector.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> [(10000 - 50)/ 450] + 1
> 23

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Bước dịch giữa hai chunk: 500−100=400 Số chunk: N=[(10000−100) / 400] + 1 = 25.
Overlap giúp giữ lại ngữ cảnh tại ranh giới giữa các chunk. Overlap càng lớn thì ngữ cảnh được bảo toàn tốt hơn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex tách sau dấu `.`, `!`, `?` khi theo sau là khoảng trắng hoặc xuống dòng. Các câu rỗng được loại bỏ, văn bản rỗng trả về danh sách rỗng, sau đó gom tối đa `max_sentences_per_chunk` câu vào một chunk.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử các separator theo thứ tự ưu tiên: đoạn, dòng, câu, khoảng trắng và cuối cùng là cắt cứng. Base case là text đã ngắn hơn `chunk_size`, không còn separator, hoặc separator rỗng; các trường hợp này trả về chunk trực tiếp hoặc cắt theo kích thước.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được chuyển thành record gồm id, content, metadata và embedding rồi lưu trong list. Khi search, query được embed một lần, tính dot product với các embedding đã lưu và dùng `nlargest` để trả về top-k theo score giảm dần.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Filter metadata được áp dụng trước khi tính similarity, nên các chunk không phù hợp không cạnh tranh trong top-k. `delete_document` lọc lại list theo `metadata["doc_id"]`, so sánh kích thước trước/sau để trả về True nếu có chunk bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent lấy top-k record (có thể kèm metadata filter), ghép id và context vào prompt với instruction chỉ dùng context. Với Parent–Child, prompt ưu tiên `parent_context` để giữ đủ điều kiện/ngoại lệ; LLM nhận prompt này và tạo câu trả lời grounded.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0 -- .venv/bin/python3
cachedir: .pytest_cache
rootdir: .
plugins: anyio-4.14.2
collecting ... collected 42 items

tests/test_solution.py ..........................................        [100%]

============================== 42 passed in 0.04s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Khách hàng có bao nhiêu ngày trả hàng? | Thời hạn gửi yêu cầu hoàn tiền | cao | cao | Đúng |
| 2 | Nhà bán hàng hủy đơn trước khi vận chuyển | Nhà bán hàng đóng gói sản phẩm | thấp | thấp | Đúng |
| 3 | Hủy một phần đơn có voucher miễn phí vận chuyển | Hủy toàn bộ đơn có voucher miễn phí vận chuyển | cao | cao | Đúng |
| 4 | Nhà sáng tạo bị hạn chế kiếm tiền | Chính sách đăng bán của người bán | thấp | thấp | Đúng |
| 5 | Sản phẩm bị cấm bán | Sản phẩm cần phê duyệt ngành hàng | trung bình | trung bình | Đúng một phần |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Các chunk cùng chủ đề nhưng không chứa đáp án vẫn có score cao, như Q2 lấy các chunk logistics thay vì câu điều kiện hủy. Điều này cho thấy embedding đo tương đồng ngữ nghĩa/chủ đề chứ không đảm bảo chuỗi số liệu hoặc điều kiện chính xác xuất hiện trong context.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Thời hạn gửi yêu cầu trả hàng/hoàn tiền | Câu chứa “15 ngày” | 0.8147 | Có | Agent trả lời đúng 15 ngày. |
| 2 | Thời điểm người bán được hủy đơn | Chunk chính sách/logistics, thiếu điều kiện | 0.7086 | Không | Agent nói context không đủ. |
| 3 | Xử lý khi yêu cầu bị từ chối | Câu chứa “48 giờ” | 0.8343 | Có | Agent trả lời đúng gửi lại trong 48 giờ. |
| 4 | Biện pháp xử lý creator (filter `customer_role=creator`) | Chunk chỉ nêu hành động thực thi chung | 0.6177 | Không đủ | Agent chưa liệt kê được biện pháp cụ thể. |
| 5 | Ngoại lệ voucher và nhiều sản phẩm | Câu “không được yêu cầu hủy một phần” | 0.7811 | Có | Agent trả lời đúng phải hủy toàn bộ đơn. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 3 / 5 đầy đủ (Q1, Q3, Q5)

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Chunk theo heading giữ được section chính sách tốt hơn chunk recursive quá nhỏ. Parent–Child có thể cung cấp context dài cho LLM, nhưng vẫn cần rerank hoặc lexical evidence để không bỏ sót các mốc như “48 giờ”.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 4 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 6 / 10 |
| **Tổng phần cá nhân** | **55 / 60** |
