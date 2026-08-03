# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** K4 — Ecommerce Policy Retrieval
**Thành viên:** Hồ Thúy Hằng, Trần Minh Hiền, Hoàng Thành Vinh, Ngô Thị Thảo Linh
**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán…).

**Phạm vi cụ thể nhóm tập trung:**
> Chính sách TikTok Shop và Shopee tập trung vào hủy/đổi trả/hoàn tiền, điều kiện người bán, logistics và thực thi đối với nhà sáng tạo.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | TikTok cancellation/returns/refunds | TikTok Shop Academy | 2026 / not-stated | 17.455 | `customer_role=seller`, `category=returns-refunds`, `language=vi` |
| 2 | TikTok creator enforcement | TikTok Shop Academy | 2026 / not-stated | 9.027 | `customer_role=creator`, `category=creator-policy`, `language=vi` |
| 3 | TikTok prohibited products | TikTok Shop Academy | 2025 / not-stated | 25.841 | `customer_role=seller`, `category=prohibited-products`, `language=vi` |
| 4 | TikTok logistics terms | TikTok Shop Academy | 2025 / not-stated | 47.915 | `customer_role=seller`, `category=logistics`, `language=vi` |
| 5 | Shopee account login issue | Shopee Help | not-stated | 5.940 | `customer_role=buyer`, `category=account`, `language=vi` |
| 6 | Shopee order status | Shopee Help | not-stated | 2.215 | `customer_role=buyer`, `category=orders`, `language=vi` |
| 7 | Shopee SPayLater overdue invoice | Shopee Help | not-stated | 4.034 | `customer_role=buyer`, `category=spaylater`, `language=vi` |
| 8 | Shopee service terms | Shopee Help | not-stated | 110.814 | `customer_role=buyer`, `category=returns-policy`, `language=vi` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [ ] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [ ] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `tiktok-creator-enforcement-policy` | Xác định file gốc và hỗ trợ delete/filter theo tài liệu. |
| `customer_role` | string | `creator`, `seller`, `buyer` | Tách tài liệu theo đối tượng; bắt buộc cho Q4. |
| `category` | string | `returns-refunds`, `logistics` | Giảm nhiễu giữa các chủ đề chính sách. |
| `source_url` | string | URL trang chính thức | Provenance và kiểm chứng gold answer. |
| `retrieved_at` | date | `2026-08-03` | Theo dõi thời điểm crawl. |
| `document_version` | string | `not-stated` | Phân biệt phiên bản khi nguồn cập nhật. |
| `chunk_index` | integer | `23` | Xác định vị trí chunk trong file gốc. |

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

**Thành viên 1 — Hồ Thúy Hằng (2A202601806)**
- **Loại chiến lược:** ParentChildChunker
- **Mô tả & lý do chọn:** Parent dùng section lớn để giữ điều kiện và ngoại lệ; child dùng chunk nhỏ để retrieval. Strategy đạt 6/10 vì parent context giúp Q4 nhưng Q2/Q3 vẫn phụ thuộc xếp hạng child.

**Thành viên 2 — Trần Minh Hiền (2A202601300)**
- **Loại chiến lược:** RecursiveChunker
- **Mô tả & lý do chọn:** Ưu tiên tách theo separator, phù hợp văn bản nhiều đoạn và heading dạng phẳng. Chunk rất nhỏ nên bắt được bằng chứng số liệu nhưng tạo 6.973 chunk và dễ mất coherence.

**Thành viên 3 — Hoàng Thành Vinh (2A202601124)**
- **Loại chiến lược:** DocumentStructuredChunker
- **Mô tả & lý do chọn:** Tách theo Markdown/heading đánh số, sau đó chia section dài theo paragraph và gắn lại heading. Strategy đạt 7/10, cân bằng tốt hơn giữa số chunk và ngữ cảnh.

**Thành viên 4 — Ngô Thị Thảo Linh (2A202601318)**
- **Loại chiến lược:** SemanticChunker
- **Mô tả & lý do chọn:** Gom các câu liền kề có similarity cao để giữ các ý cùng chủ đề. Strategy tạo 1.640 chunk và đạt 6/10; Q2/Q4 cho thấy semantic similarity chưa đủ để đảm bảo bằng chứng cụ thể.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Hồ Thúy Hằng | ParentChildChunker | 6/10 | Giữ parent context khi agent trả lời | Child vẫn có thể xếp hạng sai |
| Trần Minh Hiền | RecursiveChunker | 6/10 | Bắt tốt chuỗi số liệu khi chunk nhỏ | 6.973 chunk, nhiều mảnh thiếu coherence |
| Hoàng Thành Vinh | DocumentStructuredChunker | 7/10 | Giữ heading/section và giảm số chunk | Một số section vẫn cạnh tranh theo chủ đề |
| Ngô Thị Thảo Linh | SemanticChunker | 6/10 | Gom câu theo độ tương đồng | Không đảm bảo số liệu/điều kiện lọt top-k |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> DocumentStructuredChunker đạt điểm cao nhất (7/10) và tạo ít chunk hơn nhiều so với RecursiveChunker. Tuy nhiên, Parent–Child có lợi thế khi agent cần context dài; chiến lược tốt nhất thực tế nên kết hợp heading-aware chunking với hybrid lexical rerank cho các mốc như “48 giờ” và “15 ngày”.

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
| 2 | Nhà bán hàng có thể hủy đơn đến thời điểm nào? | DocumentStructuredChunker (400) | Chưa | Lần chạy mới top-3 bị các chunk logistics và phần mở đầu cạnh tranh; agent báo context không đủ. |
| 3 | Nếu yêu cầu trả hàng bị từ chối thì làm gì? | DocumentStructuredChunker (400) | Có | Top-1 chứa đúng thời hạn **48 giờ**; agent trả lời đúng. |
| 4 | Khi vi phạm, creator có thể bị xử lý thế nào? | DocumentStructuredChunker (400) + filter `customer_role=creator` | Có một phần | Top-3 chứa hai biện pháp; agent trả lời đúng một phần danh sách. |
| 5 | Đơn nhiều sản phẩm + voucher có được hủy một phần không? | DocumentStructuredChunker (400) | Có | Top-1 và agent trả lời đúng: không được hủy một phần. |

Kết quả mới nhất được lưu tại [`bench_results_document_structured.txt`](../bench_results_document_structured.txt). DocumentStructuredChunker với `chunk_size=400` tạo **669 chunks**; có bằng chứng đầy đủ trong top-3 cho Q1, Q3 và Q5, bằng chứng một phần cho Q4, còn Q2 thất bại. Agent đạt đầy đủ **3/5 query**, Q4 trả lời một phần.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Query 4 dùng `customer_role=creator`, nhờ đó top-3 chỉ lấy từ tài liệu dành cho nhà sáng tạo. Filter xác định đúng tài liệu, nhưng cần tăng độ đầy đủ của chunk/hoặc top-k để agent liệt kê hết các biện pháp.

### So sánh A/B giữa hai strategy và kiểm tra bằng chứng ở mức chunk

Ba file [`bench_results_recursive.txt`](../bench_results_recursive.txt), [`bench_results_document_structured.txt`](../bench_results_document_structured.txt) và [`bench_results.txt`](../bench_results.txt) dùng cùng corpus, 5 query, embedding thật `openrouter/openai/text-embedding-3-small` và LLM `openrouter/deepseek/deepseek-v4-flash`; chỉ thay chunker.

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
| Q1 | `chunk_23` (0.7775), `chunk_25` (0.7139), `chunk_32` (0.7056) | Có — `15 ngày` trong chunk 23 | Trả lời đúng 15 ngày | 2/2 |
| Q2 | `tiktok-logistics-terms::chunk_41` (0.7316), `chunk_13` (0.7146), `tiktok-cancellation-returns-refunds::chunk_4` (0.7091) | Không — không có điều kiện hủy | Báo context không đủ | 0/2 |
| Q3 | `chunk_24` (0.7997), `chunk_36` (0.7631), `chunk_34` (0.7153) | Có — `48 giờ` trong chunk 24 | Trả lời đúng quy trình | 2/2 |
| Q4, filter `customer_role=creator` | `chunk_4` (0.6596), `chunk_17` (0.5804), `chunk_10` (0.5716) | Có một phần — hai biện pháp cụ thể | Trả lời đúng một phần danh sách | 1/2 |
| Q5 | `chunk_14` (0.7818), `chunk_11` (0.7760), `chunk_13` (0.7719) | Có — `không được yêu cầu hủy một phần` trong chunk 11 | Trả lời đúng ngoại lệ | 2/2 |
| **Tổng** | **669 chunks** | **Q1, Q3, Q5 đầy đủ; Q4 một phần** | | **7/10** |

#### Kết quả riêng — ParentChildChunker (parent=1200, child=400, overlap=50; có parent context)

| Query | Top-3 chunk và score | Có chuỗi bằng chứng? | Agent | Điểm |
|---|---|---|---|---:|
| Q1 | `chunk_18` (0.7570), `chunk_19` (0.7006), `chunk_25` (0.6857) | Có — `15 ngày` trong chunk 18 | Trả lời đúng 15 ngày | 2/2 |
| Q2 | `tiktok-logistics-terms::chunk_87` (0.7012), `tiktok-prohibited-products::chunk_6` (0.6819), `tiktok-logistics-terms::chunk_89` (0.6801) | Không — không có điều kiện hủy cụ thể | Báo context không đủ | 0/2 |
| Q3 | `chunk_27` (0.7781), `chunk_28` (0.7574), `chunk_26` (0.7536) | Không — top-3 không có `48 giờ` | Báo context không đủ | 0/2 |
| Q4, filter `customer_role=creator` | `chunk_14` (0.5593), `chunk_7` (0.5453), `chunk_17` (0.5437) | Có — chunk 7 chứa danh sách biện pháp | Agent liệt kê được 7 biện pháp, grounded | 2/2 |
| Q5 | `chunk_9` (0.7760), `chunk_59` (0.7529), `chunk_10` (0.6428) | Có — section 3.2.1 và điều kiện hủy một phần | Trả lời đúng ngoại lệ | 2/2 |
| **Tổng** | **642 chunks** | **Q1, Q4, Q5 đầy đủ** | | **6/10** |

#### Kết quả riêng — SemanticChunker (`max_chunk_size=400`)

| Query | Top-3 chunk và score | Có chuỗi bằng chứng? | Agent | Điểm |
|---|---|---|---|---:|
| Q1 | top-1 (0.8147), top-2 (0.7444), top-3 (0.7148) | Có — `15 ngày` ở top-1 | Trả lời đúng | 2/2 |
| Q2 | top-1 (0.7086), top-2 (0.6985), top-3 (0.6921) | Không — không có điều kiện trước `Đã vận chuyển` | Báo context không đủ | 0/2 |
| Q3 | top-1 (0.8343), top-2 (0.7790), top-3 (0.7730) | Có — `48 giờ` ở top-1 | Trả lời đúng | 2/2 |
| Q4, filter `customer_role=creator` | top-1 (0.6175), top-2 (0.5952), top-3 (0.5502) | Có một phần — chỉ thấy hành động thực thi/đóng băng hoa hồng | Trả lời một phần, chưa liệt kê đủ | 1/2 |
| Q5 | top-1 (0.7811), top-2 (0.7529), top-3 (0.7527) | Có — `không được yêu cầu hủy một phần` ở top-1 | Trả lời đúng | 2/2 |
| **Tổng** | **1.640 chunks** | **Q1, Q3, Q5 đầy đủ; Q2, Q4 thất bại** | | **6/10** |

Lưu ý: `bench.py --strategy semantic` hiện dùng fallback token-overlap để chia câu vì chưa truyền embedding function vào chunker; embedding thật vẫn được dùng ở bước retrieval.

| Query | RecursiveChunker (6.973 chunks) | DocumentStructuredChunker (638 chunks) | Bằng chứng đặc trưng cần có trong top-3 |
|---|---|---|---|
| Q1 | 2/2 — top-1 có “trong vòng 15 ngày”, agent đúng | 2/2 — chunk 23 có “trong vòng 15 ngày”, agent đúng | `15 ngày` |
| Q2 | 0/2 — ba chunk chỉ là tiêu đề, agent báo thiếu context | 0/2 — top-3 là logistics/mở đầu, không có điều kiện hủy | `trước khi đơn hàng chuyển sang trạng thái` |
| Q3 | 2/2 — chunk 49 có “48 giờ”, agent đúng | 2/2 — chunk 24 có “48 giờ”, agent đúng | `lần thứ hai trong vòng 48 giờ` |
| Q4 (filter creator) | 0/2 — filter đúng doc nhưng top-3 không có biện pháp cụ thể | 1/2 — top-3 có “Hạn chế quyền truy cập” và “Tạm ngưng tính năng kiếm tiền”, agent mới trả lời một phần | `Hạn chế quyền truy cập`, `Tạm ngưng tính năng kiếm tiền` |
| Q5 | 2/2 — chunk 27 có “không được yêu cầu hủy một phần”, agent đúng | 2/2 — chunk 11 có cùng bằng chứng, agent đúng | `không được yêu cầu hủy một phần` |
| **Tổng** | **6/10** | **7/10** | |

| Strategy | Số chunks | Có bằng chứng đầy đủ trong top-3 | Điểm |
|---|---:|---:|---:|
| RecursiveChunker | 6.973 | 3/5 | 6/10 |
| DocumentStructuredChunker | 669 | 3/5 đầy đủ + Q4 một phần | 7/10 |
| ParentChildChunker | 642 | 3/5 đầy đủ (Q1, Q4, Q5) | 6/10 |
| SemanticChunker | 1.640 | 3/5 đầy đủ | 6/10 |

**Failure case 1 — Q2:** RecursiveChunker top-3 có cùng `doc_id` nhưng chỉ chứa tiêu đề “Chính sách hủy đơn hàng...” (score 0.7575, 0.7575, 0.7245). Sau khi nhận diện thêm heading dạng đánh số, DocumentStructuredChunker vẫn bị các chunk logistics/mở đầu cạnh tranh (0.7316, 0.7146, 0.7091), nên không lấy được section 3.1. Đây là lỗi precision ở mức chunk: đúng chủ đề nhưng sai section.

**Failure case 2 — Q4 với DocumentStructuredChunker:** filter `customer_role=creator` giảm nhiễu đúng đối tượng, nhưng top-3 chỉ chứa hai biện pháp và agent không liệt kê toàn bộ danh sách gold. Filter cải thiện precision tài liệu nhưng không bảo đảm recall của mọi chunk trong section “Hành động thực thi”.

**Failure case 3 — Q3 với ParentChildChunker:** parent context giúp Q4 lấy được cả section “Hành động thực thi”, nhưng Q3 lại có top-3 là các chunk 4.2.1/4.2.2 (score 0.7781, 0.7574, 0.7536), không chứa chuỗi `48 giờ`. Parent context chỉ có ích sau khi child đúng được xếp hạng; cần tăng child overlap hoặc rerank bằng lexical evidence để câu trả lời định lượng không bị bỏ sót.

**A/B filter:** Hai file hiện có kết quả Q4 ở nhánh **có filter**. Nhánh không filter chưa được ghi riêng trong output, vì vậy không kết luận rằng filter làm thay đổi thứ hạng; cần chạy lại Q4 với `metadata_filter=None` và giữ nguyên strategy/embedder để hoàn tất phép A/B.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> - Đúng `doc_id` chưa đủ: RecursiveChunker có thể trả đúng tài liệu nhưng sai section, không chứa bằng chứng trả lời.
> - DocumentStructuredChunker giảm số chunk và giữ heading tốt hơn; Parent–Child giúp agent nhận parent context nhưng vẫn cần rerank child.
> - Các query số liệu như `48 giờ` cần lexical evidence/reranking vì cosine similarity ưu tiên chủ đề hơn con số chính xác.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng corpus và embedder nhưng chunk boundary quyết định bằng chứng nào lọt top-k. Chunk nhỏ bắt tốt câu số liệu nhưng tạo nhiều nhiễu; chunk theo heading giữ coherence tốt hơn nhưng section cùng chủ đề vẫn cạnh tranh.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ chuẩn hóa heading khi crawl, giữ section numbering và thêm hybrid retrieval (vector search + lexical rerank). Với query bắt buộc filter, nhóm sẽ chạy A/B có và không có filter, đồng thời lưu top-k evidence để tái lập failure analysis.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 9 / 10 |
| Thiết kế chiến lược (Strategy Design) | 14 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 8 / 10 |
| Thuyết trình (Demo) | 4 / 5 |
| **Tổng phần nhóm** | **35 / 40** |
