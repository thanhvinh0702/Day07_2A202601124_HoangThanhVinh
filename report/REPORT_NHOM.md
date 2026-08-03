# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán…).

**Phạm vi cụ thể nhóm tập trung:**
> *1 câu — ví dụ: đổi trả + điều kiện người bán.*

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [ ] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [ ] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` với `chunk_size=200` trên 3 tài liệu TikTok. Front matter đã được loại bằng `ingest.load_documents()` trước khi so sánh.

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `tiktok-cancellation-returns-refunds` | FixedSizeChunker (`fixed_size`) | 117 | 198.76 | Tương đối; có thể cắt giữa mục |
| `tiktok-cancellation-returns-refunds` | SentenceChunker (`by_sentences`) | 41 | 422.95 | Tốt theo câu nhưng vượt ngưỡng 200 |
| `tiktok-cancellation-returns-refunds` | RecursiveChunker (`recursive`) | 561 | 29.81 | Kém; quá nhiều mảnh ngắn |
| `tiktok-creator-enforcement-policy` | FixedSizeChunker (`fixed_size`) | 60 | 199.62 | Tương đối; có thể cắt giữa mục |
| `tiktok-creator-enforcement-policy` | SentenceChunker (`by_sentences`) | 20 | 448.35 | Tốt theo câu nhưng vượt ngưỡng 200 |
| `tiktok-creator-enforcement-policy` | RecursiveChunker (`recursive`) | 289 | 29.93 | Kém; quá nhiều mảnh ngắn |
| `tiktok-prohibited-products` | FixedSizeChunker (`fixed_size`) | 172 | 199.95 | Tương đối; có thể cắt giữa mục |
| `tiktok-prohibited-products` | SentenceChunker (`by_sentences`) | 34 | 757.29 | Giữ câu nhưng quá dài cho retrieval |
| `tiktok-prohibited-products` | RecursiveChunker (`recursive`) | 698 | 35.56 | Kém; quá nhiều mảnh ngắn |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Dạng | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Tài liệu + chunk kỳ vọng |
|---|---|-------|-------------------------------|--------------------------|
| 1 | Số liệu | Khách hàng có bao nhiêu ngày để gửi yêu cầu trả hàng/hoàn tiền sau khi đơn được cập nhật là “Đã giao hàng”? | Khách hàng có thể gửi yêu cầu trong vòng **15 ngày** kể từ khi đơn hàng được cập nhật trạng thái “Đã giao hàng”. | `tiktok-cancellation-returns-refunds`, mục 4.1, chunk chứa câu “trong vòng 15 ngày”. |
| 2 | Điều kiện | Nhà bán hàng có thể hủy đơn hàng TikTok Shop đến thời điểm nào? | Nhà bán hàng có thể hủy đơn **bất kỳ lúc nào trước khi đơn chuyển sang “Đã vận chuyển - Đang vận chuyển”**; việc này ảnh hưởng đến Tỷ lệ hủy do lỗi Người bán. | `tiktok-cancellation-returns-refunds`, mục 3.1, chunk chứa điều kiện hủy bởi Người bán. |
| 3 | Quy trình | Nếu nhà bán hàng từ chối yêu cầu trả hàng/hoàn tiền, khách hàng cần làm gì và trong bao lâu? | Khách hàng có thể gửi yêu cầu lần thứ hai **trong vòng 48 giờ** sau khi bị từ chối. Nếu không gửi lại trong thời hạn này, nền tảng sẽ đóng yêu cầu. | `tiktok-cancellation-returns-refunds`, mục 4.1, chunk chứa quy trình gửi lại yêu cầu. |
| 4 | Liệt kê (bắt buộc lọc) | Khi vi phạm chính sách, nền tảng có thể áp dụng những biện pháp nào đối với nhà sáng tạo? | Với tài liệu dành cho `customer_role=creator`, các biện pháp gồm: **gỡ nội dung**, **hạn chế quyền truy cập tính năng sản phẩm**, **tạm dừng kiếm tiền/hoa hồng**; tùy mức độ còn có thể đình chỉ video/LIVE hoặc xóa tài khoản. | `tiktok-creator-enforcement-policy`, mục “What Enforcement Can Look Like”, chunk chứa danh sách biện pháp. **Bắt buộc filter:** `customer_role=creator`. |
| 5 | Ngoại lệ | Đơn có nhiều sản phẩm và dùng voucher miễn phí vận chuyển có được hủy một phần không? | **Không.** Khách hàng phải hủy toàn bộ đơn. Tuy nhiên, sản phẩm đã sẵn sàng vận chuyển cần người bán chấp nhận, còn sản phẩm chưa sẵn sàng vận chuyển thì yêu cầu hủy được tự động phê duyệt. | `tiktok-cancellation-returns-refunds`, mục 3.2.1, chunk chứa ngoại lệ đơn nhiều sản phẩm + voucher. |

**Quy tắc cố định benchmark:** Đây là đúng 5 query dùng chung cho mọi strategy; không thay đổi câu hỏi sau khi đã chạy thử. Query 4 phải chạy với bộ lọc `customer_role=creator`, vì nếu không lọc, các tài liệu dành cho `seller` cũng có từ vựng “vi phạm/chế tài” và retrieval có thể trả lời sai đối tượng.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Khách hàng có bao nhiêu ngày để gửi yêu cầu trả hàng/hoàn tiền? | DocumentStructuredChunker (400) | Có | Top-3 chứa mục 4.1; agent trả lời đúng thời hạn **15 ngày**. |
| 2 | Nhà bán hàng có thể hủy đơn đến thời điểm nào? | DocumentStructuredChunker (400) | Có | Top-1 chứa đúng điều kiện trước trạng thái “Đã vận chuyển - Đang vận chuyển”; agent trả lời đúng. |
| 3 | Nếu yêu cầu trả hàng bị từ chối thì làm gì? | DocumentStructuredChunker (400) | Có | Top-1 chứa đúng thời hạn **48 giờ**; agent trả lời đúng. |
| 4 | Khi vi phạm, creator có thể bị xử lý thế nào? | DocumentStructuredChunker (400) + filter `customer_role=creator` | Có | Top-3 chứa hai biện pháp; agent trả lời đúng một phần danh sách. |
| 5 | Đơn nhiều sản phẩm + voucher có được hủy một phần không? | DocumentStructuredChunker (400) | Có | Top-1 và agent trả lời đúng: không được hủy một phần. |

Kết quả benchmark được lưu tại [`bench_results.txt`](../bench_results.txt). DocumentStructuredChunker với `chunk_size=400` tạo **638 chunks** và đưa chunk liên quan vào top-3 cho **5/5 query**; agent trả lời đầy đủ 4/5 query, còn Q4 mới nêu được một phần danh sách biện pháp.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Query 4 dùng `customer_role=creator`, nhờ đó top-3 chỉ lấy từ tài liệu dành cho nhà sáng tạo. Filter xác định đúng tài liệu, nhưng cần tăng độ đầy đủ của chunk/hoặc top-k để agent liệt kê hết các biện pháp.

### So sánh A/B giữa hai strategy và kiểm tra bằng chứng ở mức chunk

Hai file benchmark dùng cùng corpus, 5 query, embedding thật `openrouter/openai/text-embedding-3-small` và LLM `openrouter/deepseek/deepseek-v4-flash`; chỉ thay chunker.

#### Kết quả riêng — RecursiveChunker (`chunk_size=400`)

| Query | Top-3 chunk và score | Có chuỗi bằng chứng? | Agent | Điểm |
|---|---|---|---|---:|
| Q1 | `chunk_48` (0.8147), `chunk_50` (0.7362), `chunk_126` (0.7246) | Có — `15 ngày` ở top-1 | Trả lời đúng 15 ngày | 2/2 |
| Q2 | `chunk_1` (0.7575), `chunk_2` (0.7575), `chunk_0` (0.7245) | Không — chỉ có tiêu đề chính sách | Báo context không đủ | 0/2 |
| Q3 | `chunk_49` (0.8339), `chunk_63` (0.7789), `chunk_65` (0.7733) | Có — `48 giờ` ở top-1 | Trả lời đúng quy trình | 2/2 |
| Q4, filter `customer_role=creator` | `chunk_1` (0.5523), `chunk_2` (0.5523), `chunk_6` (0.5475) | Không — không có tên biện pháp | Không nêu được biện pháp cụ thể | 0/2 |
| Q5 | `chunk_27` (0.7932), `chunk_138` (0.7529), `chunk_26` (0.7529) | Có — `không được yêu cầu hủy một phần` | Trả lời đúng ngoại lệ | 2/2 |
| **Tổng** | **6.973 chunks** | **3/5 query có bằng chứng** | | **6/10** |

#### Kết quả riêng — DocumentStructuredChunker (`chunk_size=400`)

| Query | Top-3 chunk và score | Có chuỗi bằng chứng? | Agent | Điểm |
|---|---|---|---|---:|
| Q1 | `chunk_22` (0.6387), `chunk_30` (0.6208), `chunk_24` (0.6122) | Có — `15 ngày` trong chunk 22 | Trả lời đúng 15 ngày | 2/2 |
| Q2 | `chunk_9` (0.7758), `chunk_33` (0.7532), `chunk_13` (0.7478) | Có — điều kiện trước `Đã vận chuyển` ở top-1 | Trả lời đúng điều kiện | 2/2 |
| Q3 | `chunk_23` (0.7012), `chunk_30` (0.6655), `chunk_22` (0.6391) | Có — `48 giờ` trong chunk 23 | Trả lời đúng quy trình | 2/2 |
| Q4, filter `customer_role=creator` | `chunk_4` (0.6596), `chunk_17` (0.5804), `chunk_10` (0.5716) | Có — `Hạn chế quyền truy cập`, `Tạm ngưng tính năng kiếm tiền` | Trả lời đúng một phần danh sách | 1/2 |
| Q5 | `chunk_11` (0.6427), `chunk_10` (0.6172), `shopee-service-terms::chunk_188` (0.5685) | Có — `không được yêu cầu hủy một phần` ở top-1 | Trả lời đúng ngoại lệ | 2/2 |
| **Tổng** | **638 chunks** | **5/5 query có bằng chứng** | | **9/10** |

| Query | RecursiveChunker (6.973 chunks) | DocumentStructuredChunker (638 chunks) | Bằng chứng đặc trưng cần có trong top-3 |
|---|---|---|---|
| Q1 | 2/2 — top-1 có “trong vòng 15 ngày”, agent đúng | 2/2 — chunk 22 có “trong vòng 15 ngày”, agent đúng | `15 ngày` |
| Q2 | 0/2 — ba chunk chỉ là tiêu đề, agent báo thiếu context | 2/2 — chunk 9 có điều kiện “trước khi ... Đã vận chuyển”, agent đúng | `trước khi đơn hàng chuyển sang trạng thái` |
| Q3 | 2/2 — chunk 49 có “48 giờ”, agent đúng | 2/2 — chunk 23 có “48 giờ”, agent đúng | `lần thứ hai trong vòng 48 giờ` |
| Q4 (filter creator) | 0/2 — filter đúng doc nhưng top-3 không có biện pháp cụ thể | 1/2 — top-3 có “Hạn chế quyền truy cập” và “Tạm ngưng tính năng kiếm tiền”, agent mới trả lời một phần | `Hạn chế quyền truy cập`, `Tạm ngưng tính năng kiếm tiền` |
| Q5 | 2/2 — chunk 27 có “không được yêu cầu hủy một phần”, agent đúng | 2/2 — chunk 11 có cùng bằng chứng, agent đúng | `không được yêu cầu hủy một phần` |
| **Tổng** | **6/10** | **9/10** | |

**Failure case 1 — Q2 với RecursiveChunker:** top-3 có cùng `doc_id` nhưng chỉ chứa tiêu đề “Chính sách hủy đơn hàng...” (score 0.7575, 0.7575, 0.7245), không có chuỗi bằng chứng về trạng thái “Đã vận chuyển”. Đây là lỗi precision ở mức chunk: đúng tài liệu nhưng sai section. DocumentStructuredChunker đưa section 3.1 vào top-1 và sửa được lỗi.

**Failure case 2 — Q4 với DocumentStructuredChunker:** filter `customer_role=creator` giảm nhiễu đúng đối tượng, nhưng top-3 chỉ chứa hai biện pháp và agent không liệt kê toàn bộ danh sách gold. Filter cải thiện precision tài liệu nhưng không bảo đảm recall của mọi chunk trong section “Hành động thực thi”.

**A/B filter:** Hai file hiện có kết quả Q4 ở nhánh **có filter**. Nhánh không filter chưa được ghi riêng trong output, vì vậy không kết luận rằng filter làm thay đổi thứ hạng; cần chạy lại Q4 với `metadata_filter=None` và giữ nguyên strategy/embedder để hoàn tất phép A/B.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
