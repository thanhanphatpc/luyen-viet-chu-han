#!/usr/bin/env python3
"""
Sinh mục "20 lượng từ thông dụng nhất" từ file Excel, ghi vào index.html (khối MEASURE-DATA).

Cách dùng:
    python3 tools/build_measure_words.py [--xlsx data/20-luong-tu-thong-dung-nhat.xlsx]

Cột Excel: Lượng từ | Pinyin | Nghĩa Việt | Nghĩa Anh | Ứng dụng phổ biến | Ví dụ | Ví dụ (tiếng Anh, không bắt buộc)
Cột "Ví dụ" dạng: câu tiếng Trung (pinyin) nghĩa tiếng Việt — script tự tách 3 phần.
Thứ tự giữ nguyên như file (thông dụng nhất ở trên). Chạy lại an toàn (ghi đè khối cũ).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'index.html')
BEGIN = '<!-- MEASURE-DATA:BEGIN'
END = '<!-- MEASURE-DATA:END -->'
ANCHOR = '<!-- RADICAL-DATA:END -->'
EX = re.compile(r'^\s*(.+?)\s*[（(]\s*(.+?)\s*[)）]\s*(.*?)\s*$', re.S)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xlsx', default=os.path.join(ROOT, 'data', '20-luong-tu-thong-dung-nhat.xlsx'))
    ap.add_argument('--file', default=INDEX)
    a = ap.parse_args()

    import openpyxl
    ws = openpyxl.load_workbook(a.xlsx, read_only=True).active
    items = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r or not r[0]:
            continue
        hz, py, vi, en, use, ex, exEn = [str(x or '').strip() for x in (list(r) + [''] * 7)[:7]]
        m = EX.match(ex)
        exCn, exPy, exVi = (m.group(1), m.group(2), m.group(3)) if m else (ex, '', '')
        items.append({'hz': hz, 'py': py, 'vi': vi, 'en': en, 'use': use,
                      'exCn': exCn, 'exPy': exPy, 'exVi': exVi, 'exEn': exEn})
    if not items:
        sys.exit('LỖI: file không có dòng dữ liệu nào.')

    s = open(a.file, encoding='utf-8').read()
    dumps = json.dumps(items, ensure_ascii=False, separators=(',', ':'))
    if '</script' in dumps:
        sys.exit('LỖI: dữ liệu chứa chuỗi </script — dừng để tránh hỏng trang.')
    block = (BEGIN + ' (tự động sinh bởi tools/build_measure_words.py — không sửa tay) -->\n'
             '<script id="measure-data">\nwindow.MEASURE_WORDS = ' + dumps + ';\n</script>\n' + END)
    if BEGIN in s:
        b0 = s.index(BEGIN)
        b1 = s.index(END, b0) + len(END)
        s = s[:b0] + block + s[b1:]
    else:
        i = s.index(ANCHOR) + len(ANCHOR)
        s = s[:i] + '\n' + block + s[i:]
    open(a.file, 'w', encoding='utf-8').write(s)
    print(f'{len(items)} lượng từ: ' + ' '.join(x['hz'] for x in items))
    bad = [x['hz'] for x in items if not x['exPy']]
    if bad:
        print('Không tách được câu ví dụ cho: ' + ', '.join(bad))


if __name__ == '__main__':
    main()
