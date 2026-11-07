#!/usr/bin/env python3
"""
Sinh bảng 214 bộ thủ (Khang Hy) xếp theo mức dùng, rồi ghi vào index.html + data/bo-thu-214.csv.

Cách dùng:
    python3 tools/build_radicals.py [--xlsx data/Danh_sach_214_Bo_Thu.xlsx]

- Nguồn danh sách: file Excel của anh Thành (cột STT, Bộ Thủ, Số Nét, Pinyin, Âm Hán Việt, Ý Nghĩa).
- "Mức dùng" = số chữ trong bộ 2663 chữ HSK 1–6 của trang (window.CHAR_META, trường rad) thuộc bộ đó.
  Dạng giản thể / biến thể (氵, 讠, 钅, ⺼…) được quy về bộ gốc; 阝 bên trái = 阜 (170), bên phải = 邑 (163)
  (xác định bằng vị trí nét bộ thủ trong dữ liệu nét).
- Kết quả nằm giữa <!-- RADICAL-DATA:BEGIN --> … <!-- RADICAL-DATA:END --> (không sửa tay khối này).
Chạy lại an toàn (ghi đè khối cũ).
"""
import argparse
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'index.html')
BEGIN = '<!-- RADICAL-DATA:BEGIN'
END = '<!-- RADICAL-DATA:END -->'
ANCHOR = '<!-- LESSON-DATA:END -->'

# Dạng giản thể / biến thể → dạng gốc trong danh sách 214 bộ
VARIANTS = {
    '讠': '言', '钅': '金', '贝': '貝', '页': '頁', '车': '車', '饣': '食', '门': '門', '马': '馬',
    '⺮': '竹', '⺼': '肉', '王': '玉', '户': '戶', '罒': '网', '⺳': '网', '见': '見', '丷': '八',
    '鸟': '鳥', '⺌': '小', '乚': '乙', '乛': '乙', '母': '毋', '鱼': '魚', '龙': '龍', '爫': '爪',
    '耂': '老', '覀': '襾', '西': '襾', '氺': '水', '青': '靑', '风': '風', '㔾': '卩', '⺗': '心',
    '民': '氏', '齿': '齒', '巳': '己', '飞': '飛', '长': '長', '⺀': '冫', '黄': '黃', '⺊': '卜',
    '丬': '爿', '旡': '无', '虎': '虍', '肀': '聿', '麦': '麥', '齐': '齊', '韦': '韋',
    '龟': '龜', '黾': '黽', '卤': '鹵', '斗': '斗', '鬥': '鬥',
}


def load_json_after(s, marker):
    i = s.index(marker) + len(marker)
    return json.JSONDecoder().raw_decode(s, i)[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xlsx', default=os.path.join(ROOT, 'data', 'Danh_sach_214_Bo_Thu.xlsx'))
    ap.add_argument('--file', default=INDEX)
    a = ap.parse_args()

    import openpyxl
    ws = openpyxl.load_workbook(a.xlsx, read_only=True).active
    rads = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r or r[0] is None:
            continue
        kx, form, strokes, py, hv, mean = (list(r) + [''] * 6)[:6]
        rads.append({'kx': int(kx), 'form': str(form).strip(), 'strokes': int(strokes or 0),
                     'py': str(py or '').strip(), 'hv': str(hv or '').strip(), 'vi': str(mean or '').strip()})
    if len(rads) != 214:
        sys.exit(f'LỖI: file có {len(rads)} bộ, cần đúng 214.')

    form2kx = {}
    for r in rads:
        for f in r['form'].split('/'):
            form2kx.setdefault(f.strip(), r['kx'])
    for v, base in VARIANTS.items():
        if base in form2kx:
            form2kx.setdefault(v, form2kx[base])

    s = open(a.file, encoding='utf-8').read()
    meta = load_json_after(s, 'window.CHAR_META = ')
    bundle = load_json_after(s, 'window.HANZI_DATA_BUNDLE = ')

    by_kx = {r['kx']: r for r in rads}
    for r in rads:
        r['chars'], r['seen'] = [], {}
    unmapped = {}
    for c, m in meta.items():
        f = (m.get('rad') or '').strip()
        if not f:
            continue
        if f == '阝':
            rs = (bundle.get(c) or {}).get('radStrokes') or [0]
            kx = 170 if min(rs) == 0 else 163
        else:
            kx = form2kx.get(f)
        if not kx:
            unmapped[f] = unmapped.get(f, 0) + 1
            continue
        r = by_kx[kx]
        r['chars'].append(c)
        r['seen'][f] = r['seen'].get(f, 0) + 1

    out = []
    for r in rads:
        forms = sorted(r['seen'].items(), key=lambda x: -x[1])
        out.append({'kx': r['kx'], 'form': r['form'], 'strokes': r['strokes'], 'py': r['py'], 'hv': r['hv'],
                    'vi': r['vi'], 'n': len(r['chars']), 'forms': [[f, n] for f, n in forms],
                    'chars': ''.join(r['chars'])})
    out.sort(key=lambda r: (-r['n'], r['kx']))
    for i, r in enumerate(out, 1):
        r['rank'] = i

    dumps = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
    block = (BEGIN + ' (tự động sinh bởi tools/build_radicals.py — không sửa tay) -->\n'
             '<script id="radical-data">\nwindow.RADICALS_214 = ' + dumps + ';\n</script>\n' + END)
    if BEGIN in s:
        b0 = s.index(BEGIN)
        b1 = s.index(END, b0) + len(END)
        s = s[:b0] + block + s[b1:]
    else:
        i = s.index(ANCHOR) + len(ANCHOR)
        s = s[:i] + '\n' + block + s[i:]
    open(a.file, 'w', encoding='utf-8').write(s)

    os.makedirs(os.path.join(ROOT, 'data'), exist_ok=True)
    with open(os.path.join(ROOT, 'data', 'bo-thu-214.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Hạng dùng', 'STT Khang Hy', 'Bộ thủ', 'Dạng gặp trong HSK (số chữ)', 'Số nét', 'Pinyin',
                    'Âm Hán Việt', 'Ý nghĩa', 'Số chữ HSK 1–6', 'Các chữ HSK thuộc bộ'])
        for r in out:
            w.writerow([r['rank'], r['kx'], r['form'], ' '.join(f'{x}({n})' for x, n in r['forms']), r['strokes'],
                        r['py'], r['hv'], r['vi'], r['n'], r['chars']])

    used = sum(1 for r in out if r['n'])
    print(f'214 bộ; {used} bộ có chữ trong HSK 1–6; tổng {sum(r["n"] for r in out)} chữ đã xếp bộ.')
    print('Top 10: ' + ', '.join(f"{r['form']} {r['hv']} ({r['n']})" for r in out[:10]))
    if unmapped:
        print('CHƯA quy được về bộ gốc: ' + ', '.join(f'{k}({v})' for k, v in unmapped.items()))


if __name__ == '__main__':
    main()
