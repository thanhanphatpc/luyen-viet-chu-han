#!/usr/bin/env python3
"""
Sinh tab "Ngữ pháp HSK 2.0" từ file Excel, ghi vào index.html (khối GRAMMAR-DATA).

Cách dùng:
    python3 tools/build_grammar.py [--xlsx data/ngu-phap-hsk-1-6.xlsx]

File Excel: mỗi sheet là một cấp (HSK1 … HSK6), cột:
    STT | Điểm ngữ pháp | Cấu trúc | Giải nghĩa (Tiếng Việt) | Câu ví dụ (Hán tự) | Pinyin câu ví dụ | Dịch nghĩa | Ghi chú / Lưu ý
Mỗi dòng là một câu ví dụ; các dòng cùng STT + tên điểm được gộp thành một điểm ngữ pháp.
data/ngu-phap-bo-sung.json (khoá = câu tiếng Trung) chứa phần Claude bổ sung:
    exPy = pinyin câu viết lại chuẩn, exEn = dịch tiếng Anh. Câu mới chưa có trong file này thì giữ pinyin gốc, chưa có tiếng Anh.
Ghi chú chỉ lặp lại tên điểm ("Lưu ý: <tên>") thì bỏ. Chạy lại an toàn (ghi đè khối cũ).
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'index.html')
BEGIN = '<!-- GRAMMAR-DATA:BEGIN'
END = '<!-- GRAMMAR-DATA:END -->'
ANCHOR = '<!-- MEASURE-DATA:END -->'


def clean(x):
    return re.sub(r'[ \t]+', ' ', str(x or '')).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xlsx', default=os.path.join(ROOT, 'data', 'ngu-phap-hsk-1-6.xlsx'))
    ap.add_argument('--extra', default=os.path.join(ROOT, 'data', 'ngu-phap-bo-sung.json'))
    a = ap.parse_args()

    import openpyxl
    extra = {}
    if os.path.exists(a.extra):
        extra = json.load(open(a.extra, encoding='utf-8')).get('sentences', {})
    wb = openpyxl.load_workbook(a.xlsx, read_only=True, data_only=True)
    points, no_en = [], []
    for ws in wb.worksheets:
        m = re.search(r'(\d)', ws.title)
        if not m:
            continue
        lvl = int(m.group(1))
        cur = None
        for r in list(ws.iter_rows(values_only=True))[1:]:
            r = (list(r) + [None] * 8)[:8]
            stt, name, struct, expl, cn, py, vi, note = r
            cn = clean(cn)
            if not cn:
                continue
            name = clean(name)
            key = (stt, name)
            if not cur or cur['_key'] != key:
                note = clean(note)
                if note.startswith('Lưu ý:') and note[6:].strip() in name:
                    note = ''
                cur = {'_key': key, 'lvl': lvl, 'no': int(stt) if isinstance(stt, (int, float)) else len(points) + 1,
                       'name': name, 'struct': str(struct or '').strip(), 'expl': clean(expl), 'note': note, 'ex': []}
                points.append(cur)
            x = extra.get(cn, {})
            auto = []
            if x.get('exPy'):
                py = x['exPy']
                auto.append('exPy')
            else:
                py = re.sub(r'\s+([，。！？,.!?])', r'\1', clean(py))
            en = x.get('exEn', '')
            if en:
                auto.append('exEn')
            else:
                no_en.append(cn)
            cur['ex'].append({'cn': cn, 'py': py, 'vi': clean(vi), 'en': en, 'auto': ','.join(auto)})
    for p in points:
        p.pop('_key')
    if not points:
        sys.exit('LỖI: file không có điểm ngữ pháp nào.')

    s = open(INDEX, encoding='utf-8').read()
    dumps = json.dumps(points, ensure_ascii=False, separators=(',', ':'))
    if '</script' in dumps:
        sys.exit('LỖI: dữ liệu chứa chuỗi </script — dừng để tránh hỏng trang.')
    block = (BEGIN + ' (tự động sinh bởi tools/build_grammar.py — không sửa tay) -->\n'
             '<script id="grammar-data">\nwindow.GRAMMAR = ' + dumps + ';\n</script>\n' + END)
    if BEGIN in s:
        b0 = s.index(BEGIN)
        b1 = s.index(END, b0) + len(END)
        s = s[:b0] + block + s[b1:]
    else:
        i = s.index(ANCHOR) + len(ANCHOR)
        s = s[:i] + '\n' + block + s[i:]
    open(INDEX, 'w', encoding='utf-8').write(s)
    from collections import Counter
    c = Counter(p['lvl'] for p in points)
    print(f'{len(points)} điểm ngữ pháp, {sum(len(p["ex"]) for p in points)} câu ví dụ: ' +
          ', '.join(f'HSK{k}: {c[k]}' for k in sorted(c)))
    if no_en:
        print(f'{len(no_en)} câu chưa có tiếng Anh/pinyin bổ sung (thêm vào {os.path.relpath(a.extra, ROOT)}): ' + ' | '.join(no_en[:20]))


if __name__ == '__main__':
    main()
