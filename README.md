# luyen-viet-chu-han

Công cụ luyện viết chữ Hán offline (HSK 1–6), chạy trên GitHub Pages:
https://thanhanphatpc.github.io/luyen-viet-chu-han/

## Mở thẳng một từ bằng link

```
https://thanhanphatpc.github.io/luyen-viet-chu-han/?chu=发展
```

Trang hiện dải chữ của từ (发 · 展), tự chạy hoạt hình nét chữ đầu; bấm từng chữ để xem/luyện viết.
Cũng dùng được dạng `#发展`, hoặc gõ cả từ vào ô ở mục 1 rồi bấm "Tải chữ".

## Bài học hằng ngày (Gemini 7:00 → tự cập nhật)

1. 7:00 Gemini soạn bài 3 từ, lưu Google Docs tên `DayN-ten-chu-de`, cuối bài có khối `### DATA-LUYEN-VIET`:
   ```
   Day3|发展|fāzhǎn|ĐT|phát triển|to develop|公司发展得很快。|Gōngsī fāzhǎn de hěn kuài.|Công ty phát triển rất nhanh.
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
