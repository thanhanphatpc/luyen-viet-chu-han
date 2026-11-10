#!/usr/bin/env python3
"""
Sinh tab "Top 50 từ theo từ loại" từ file Excel, ghi vào index.html (khối TOP50-DATA).

Cách dùng:
    python3 tools/build_top50.py [--xlsx data/top50-tu-loai-hsk.xlsx]

File Excel: mỗi sheet là một từ loại (vd "Động từ (动词)"), cột:
    STT | Hán tự | Pinyin | Từ loại | Chủ đề / Nghĩa | Ví dụ (Hán) | Pinyin ví dụ | Nghĩa ví dụ
data/top50-tu-loai-bo-sung.json (khoá = "Hán tự|câu ví dụ") chứa phần Claude bổ sung:
    py (pinyin từ chuẩn), en (nghĩa Anh), exPy (pinyin câu viết lại), exEn (câu tiếng Anh).
Từ mới chưa có trong file bổ sung thì giữ pinyin gốc, chưa có tiếng Anh (script báo ra). Chạy lại an toàn.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'index.html')
BEGIN = '<!-- TOP50-DATA:BEGIN'
END = '<!-- TOP50-DATA:END -->'
ANCHOR = '<!-- MEASURE-DATA:END -->'


def clean(x):
    return re.sub(r'\s+', ' ', str(x or '')).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xlsx', default=os.path.join(ROOT, 'data', 'top50-tu-loai-hsk.xlsx'))
    ap.add_argument('--extra', default=os.path.join(ROOT, 'data', 'top50-tu-loai-bo-sung.json'))
    a = ap.parse_args()

    import openpyxl
    extra = json.load(open(a.extra, encoding='utf-8')).get('items', {}) if os.path.exists(a.extra) else {}
    wb = openpyxl.load_workbook(a.xlsx, read_only=True, data_only=True)
    cats, missing = [], []
    for ws in wb.worksheets:
        items = []
        for r in list(ws.iter_rows(values_only=True))[1:]:
            r = (list(r) + [None] * 8)[:8]
            stt, hz, py, pos, vi, exCn, exPy, exVi = [clean(x) for x in r]
            if not hz:
                continue
            x = extra.get(hz + '|' + exCn, {})
            auto = [k for k in ('py', 'en', 'exPy', 'exEn') if x.get(k)]
            if not x:
                missing.append(hz)
                exPy = re.sub(r'\s+([，。！？,.!?])', r'\1', exPy)
            items.append({'no': int(float(stt)) if stt else len(items) + 1, 'hz': hz, 'py': x.get('py') or py, 'pos': pos,
                          'vi': vi, 'en': x.get('en', ''), 'exCn': exCn, 'exPy': x.get('exPy') or exPy, 'exVi': exVi,
                          'exEn': x.get('exEn', ''), 'auto': ','.join(auto)})
        if items:
            cats.append({'name': ws.title.strip(), 'items': items})
    if not cats:
        sys.exit('LỖI: file không có dữ liệu.')

    s = open(INDEX, encoding='utf-8').read()
    dumps = json.dumps(cats, ensure_ascii=False, separators=(',', ':'))
    if '</script' in dumps:
        sys.exit('LỖI: dữ liệu chứa chuỗi </script — dừng để tránh hỏng trang.')
    block = (BEGIN + ' (tự động sinh bởi tools/build_top50.py — không sửa tay) -->\n'
             '<script id="top50-data">\nwindow.TOP50 = ' + dumps + ';\n</script>\n' + END)
    if BEGIN in s:
        b0 = s.index(BEGIN)
        b1 = s.index(END, b0) + len(END)
        s = s[:b0] + block + s[b1:]
    else:
        i = s.index(ANCHOR) + len(ANCHOR)
        s = s[:i] + '\n' + block + s[i:]
    open(INDEX, 'w', encoding='utf-8').write(s)
    print(', '.join(f'{c["name"]}: {len(c["items"])}' for c in cats))
    if missing:
        print(f'{len(missing)} từ chưa có phần bổ sung (pinyin chuẩn/tiếng Anh): ' + ' '.join(missing))


if __name__ == '__main__':
    main()
