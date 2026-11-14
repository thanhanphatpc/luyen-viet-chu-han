# luyen-viet-chu-han

Công cụ luyện viết chữ Hán offline (HSK 1–6), chạy trên GitHub Pages:
https://thanhanphatpc.github.io/luyen-viet-chu-han/

## Bố cục (tab menu)

1. Luyện viết · 2. Bài hằng ngày · 3. Bộ thủ · 4. Lượng từ · 5. Từ vựng · 6. Xuất GIF · 7. Ngữ pháp · 8. Từ loại — thanh tab dính trên cùng, trang nhớ tab mở gần nhất; link `?chu=` luôn mở tab 1. Bấm chữ ở tab nào cũng tự chuyển sang tab 1 để xem nét/luyện viết.

Phát âm: nút 🔊 đọc tiếng Trung; bấm thẳng vào nghĩa hoặc câu tiếng Anh (chữ xanh xám có 🔊) để nghe tiếng Anh (giọng en-US của máy).

Trên cùng có nút **Giao diện** ☀️ Sáng / 🌙 Tối / 🔄 Tự động (theo cài đặt máy) và **Cỡ chữ** A− / A+ (85–160%, bấm % để về 100%); trang nhớ lựa chọn trên từng máy. Trang hiển thị vừa khổ điện thoại.

Tab 1 có lưới **2663 chữ xếp theo độ thông dụng** (bảng tần suất chữ Hán hiện đại của Jun Da; 150 chữ đầu trùng với `data/150-chu-thong-dung.csv`):
- chia trang 150 chữ (18 trang), chọn trang bằng ô chọn hoặc nút ◀ ▶ ở đầu/cuối lưới; trang nhớ trang đang xem trên từng máy;
- ô tìm: gõ chữ Hán, pinyin không dấu (`zhao`, `xing2`) hoặc nghĩa tiếng Việt của chữ đơn (có dấu hoặc không dấu) — tìm trên cả 2663 chữ;
- bấm chữ để xem nét/luyện viết, nút **◀ Về lưới chữ** đưa về đúng ô vừa bấm;
- nút Hiện nghĩa; nút thêm các chữ đang hiện (trang hiện tại hoặc kết quả tìm) vào danh sách từ vựng.

## Mở thẳng một từ bằng link

```
https://thanhanphatpc.github.io/luyen-viet-chu-han/?chu=发展
```

Trang hiện dải chữ của từ (发 · 展), tự chạy hoạt hình nét chữ đầu; bấm từng chữ để xem/luyện viết.
Cũng dùng được dạng `#发展`, hoặc gõ cả từ vào ô ở mục 1 rồi bấm "Tải chữ".

## Bài học hằng ngày (Gemini 7:00 → tự cập nhật)

1. 7:00 Gemini soạn bài 3 từ, lưu Google Docs tên `DayN-ten-chu-de`, cuối bài có khối `### DATA-LUYEN-VIET`:
   ```
   Day3|发展|fāzhǎn|ĐT|phát triển|to develop|公司发展得很快。|Gōngsī fāzhǎn de hěn kuài.|Công ty phát triển rất nhanh.|The company is developing fast.
   ```
2. Tác vụ định kỳ của Claude đọc file Docs mới, chạy:
   ```
   python3 tools/add_lesson.py --input bai.txt --topic "Day3-kinh-doanh-ban-hang"
   ```
   rồi commit lên nhánh `main`.
3. Script ghi vào khối `LESSON-DATA` trong `index.html` (không sửa tay khối này):
   - `DAILY_LESSONS`: danh sách ngày học → hiện ở mục "📅 Bài học hằng ngày";
   - `EXTRA_HANZI`: dữ liệu nét cho chữ ngoài bộ 2663 chữ HSK, lấy từ gói npm `hanzi-writer-data`;
   - `EXTRA_META`: pinyin/nghĩa cho các chữ bổ sung.

Chạy lại cùng một Day sẽ ghi đè Day đó, nên an toàn khi chạy lại. Day1 = 07/11/2026.

## Danh sách từ vựng (tab 5)

- Mọi cách nạp (file Excel, dán tay, nút "Nạp cả ngày") đều **cộng dồn** vào danh sách cũ và tự loại trùng.
- Mỗi lần nạp báo `+N chữ mới (…)`; chữ mới của lần nạp gần nhất có viền xanh.
- Danh sách tự lưu trong trình duyệt (localStorage, khoá `lvch_vocab_v1`) — mở lại trang vẫn còn. Lưu theo từng trình duyệt/từng máy; Safari chế độ riêng tư không lưu.
- "Xoá danh sách" hỏi xác nhận rồi xoá cả bản đã lưu.

## Thống kê từ mới theo tuần

Cập nhật khi chạy `tools/add_lesson.py ... --readme`; trên trang web bảng 📊 ở mục Bài học hằng ngày luôn tự tính (tuần tính từ thứ Hai đến Chủ nhật; từ đã học ở ngày trước không tính lại).

<!-- WEEK-STATS:BEGIN (tự động sinh bởi tools/add_lesson.py) -->
| Tuần | Số bài | Từ mới | Chữ Hán mới |
|---|---:|---:|---:|
| 02/11 – 08/11/2026 | 2 | 6 | 12 |
| **Tổng cộng** | **2** | **6** | **12** |
<!-- WEEK-STATS:END -->

## Chữ ngoài bộ 2663 chữ HSK

- Chữ trong bài học hằng ngày: `tools/add_lesson.py` tự bổ sung dữ liệu nét vào `index.html` (dùng offline được ở mọi máy).
- Chữ anh tự nạp/gõ (Excel, dán tay, mục 1): khi có mạng, trang tự tải nét từ `cdn.jsdelivr.net/npm/hanzi-writer-data@2.0.1` và lưu vào trình duyệt (khoá `lvch_hz_cache_v1`) → lần sau dùng không cần mạng trên máy đó. Không có mạng → chip đỏ, có mạng mở lại là tự bổ sung. Chữ không có trong hanzi-writer-data thì báo "không tìm thấy".

## Từ vựng HSK 1–6 kèm câu ví dụ

- Nguồn: 49 file Excel "HSK1–6 từ vựng – câu ví dụ" của anh Thành, gộp thành `data/hsk-tu-vung.json` (5.068 từ/thành ngữ, trùng giữa các file chỉ giữ cấp thấp nhất).
- Mỗi từ đều có: Hán tự, pinyin, loại từ, nghĩa Việt, nghĩa Anh, câu ví dụ + pinyin câu + nghĩa Việt + nghĩa Anh, cấp HSK (`lvl`).
- Trường `auto` ghi phần Claude bổ sung (trang hiện nhãn xanh "Claude bổ sung"): `en`/`exEn` = dịch tiếng Anh (file HSK 4–6 không có), `exPy` = pinyin câu tạo bằng pypinyin (file thiếu), `all` = cả mục.
- 658 chữ trong bộ 2663 không nằm trong từ nào của file → Claude soạn thêm 1 từ thông dụng + câu ví dụ cho mỗi chữ (`lvl` = 0, nhãn "bổ sung").
- Tra 1 chữ: mục "Câu ví dụ" hiện tối đa 3 từ chứa chữ đó (ưu tiên chính chữ đó → từ thường cấp thấp → thành ngữ), bấm từ để mở cả từ. Tra từ ghép (ô nhập, `?chu=`, tab 5): hiện nghĩa + câu ví dụ của từ.
- Sửa `data/hsk-tu-vung.json` thì chạy lại: `python3 tools/build_hsk_words.py` (ghi khối `HSK-WORDS` trong `index.html`, không sửa tay).

## Ngữ pháp HSK 2.0 (tab 7)

- Nguồn: `data/ngu-phap-hsk-1-6.xlsx` (mỗi sheet một cấp HSK1…HSK6; cột STT, Điểm ngữ pháp, Cấu trúc, Giải nghĩa, Câu ví dụ, Pinyin, Dịch nghĩa, Ghi chú). Hiện có 161 điểm, 256 câu ví dụ.
- `data/ngu-phap-bo-sung.json`: phần Claude bổ sung theo từng câu — pinyin viết lại chuẩn (file gốc tách âm tiết, đọc sai 得/儿…) và câu dịch tiếng Anh; trang hiện nhãn "Claude bổ sung".
- Tab có nút chọn cấp, ô tìm (chữ Hán như 把 / 虽然, tiếng Việt không dấu, tiếng Anh), mở/thu gọn tất cả; mỗi câu có 🔊 và ✍️ (mở các chữ trong câu ở tab 1 để luyện viết).
- Sửa/thêm vào file Excel thì chạy lại: `python3 tools/build_grammar.py` (ghi khối `GRAMMAR-DATA` trong `index.html`, không sửa tay). Câu mới chưa có trong file bổ sung sẽ được báo ra để bổ sung tiếng Anh.

## Top 50 từ theo từ loại (tab 8)

- Nguồn: `data/top50-tu-loai-hsk.xlsx` (mỗi sheet một từ loại: Động từ, Tính từ, Danh từ, Trạng từ; cột STT, Hán tự, Pinyin, Từ loại, Nghĩa, Ví dụ, Pinyin ví dụ, Nghĩa ví dụ).
- `data/top50-tu-loai-bo-sung.json`: phần Claude bổ sung theo từng từ — pinyin từ chuẩn (thanh nhẹ 爸爸 bàba, 时候 shíhou…; 长 cháng), nghĩa tiếng Anh, pinyin câu viết lại, câu tiếng Anh.
- Tab có nút chọn từ loại, ô tìm (chữ Hán, pinyin không dấu, tiếng Việt, tiếng Anh — tìm trên mọi từ loại), nút thêm cả nhóm vào danh sách từ vựng (mục 5); bấm từ để luyện viết.
- Sửa file Excel thì chạy lại: `python3 tools/build_top50.py` (ghi khối `TOP50-DATA` trong `index.html`, không sửa tay).

## 214 bộ thủ (tab 3)

- Nguồn: `data/Danh_sach_214_Bo_Thu.xlsx` (STT, Bộ thủ, Số nét, Pinyin, Âm Hán Việt, Ý nghĩa).
- Xếp theo **mức dùng** = số chữ trong 2663 chữ HSK 1–6 thuộc bộ đó; dạng giản thể/biến thể (氵 讠 钅 ⺼ 罒…) tính vào bộ gốc, 阝 trái = 阜, phải = 邑. Trang cho đổi cách xếp (Khang Hy / số nét), tìm bộ, bấm bộ để xem và luyện các chữ thuộc bộ.
- Bảng đã xếp: `data/bo-thu-214.csv` (mở được bằng Excel).
- Sửa file Excel thì chạy lại: `python3 tools/build_radicals.py` (ghi khối `RADICAL-DATA` trong `index.html`, không sửa tay).

## 20 lượng từ thông dụng nhất (tab 4)

- Nguồn: `data/20-luong-tu-thong-dung-nhat.xlsx` (Lượng từ, Pinyin, Nghĩa Việt, Nghĩa Anh, Ứng dụng phổ biến, Ví dụ "câu (pinyin) nghĩa").
- Sửa file Excel thì chạy lại: `python3 tools/build_measure_words.py` (ghi khối `MEASURE-DATA` trong `index.html`, không sửa tay).
