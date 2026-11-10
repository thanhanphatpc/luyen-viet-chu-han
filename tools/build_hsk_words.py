#!/usr/bin/env python3
"""
Nhúng từ vựng HSK 1–6 kèm câu ví dụ (data/hsk-tu-vung.json) vào index.html (khối HSK-WORDS).

Cách dùng:
    python3 tools/build_hsk_words.py

- window.HSK_WORDS : mảng các từ, mỗi từ = [hz, py, pos, vi, en, exCn, exPy, exVi, exEn, lvl, auto]
                     lvl 1–6 = cấp HSK theo file của anh Thành, 0 = Claude bổ sung;
                     auto = chuỗi các trường Claude bổ sung (vd "en,exEn,exPy" hoặc "all").
- window.HSK_CHAR_WORDS : { chữ: [chỉ số từ, ...] } tối đa 3 từ cho mỗi chữ trong bộ 2663 chữ,
                     ưu tiên: chính chữ đó (nếu là một từ) → từ thường (không phải thành ngữ) cấp thấp, ngắn → thành ngữ.
Chạy lại an toàn (ghi đè khối cũ).
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'index.html')
DATA = os.path.join(ROOT, 'data', 'hsk-tu-vung.json')
BEGIN = '<!-- HSK-WORDS:BEGIN'
END = '<!-- HSK-WORDS:END -->'
ANCHOR = '<!-- MEASURE-DATA:END -->'
HAN = re.compile(r'[㐀-鿿]')
PER_CHAR = 3


def load_char_meta(s):
    i = s.index('window.CHAR_META =') + len('window.CHAR_META =')
    return json.JSONDecoder().raw_decode(s[i:].lstrip())[0]


def main():
    s = open(INDEX, encoding='utf-8').read()
    meta = load_char_meta(s)
    words = json.load(open(DATA, encoding='utf-8'))['words']

    rows, seen = [], {}
    for w in words:
        rows.append([w['hz'], w['py'], w.get('pos', ''), w['vi'], w.get('en', ''), w['exCn'], w.get('exPy', ''),
                     w.get('exVi', ''), w.get('exEn', ''), w.get('lvl', 0), ','.join(w.get('auto', []))])

    def rank(i):
        w = words[i]
        key = ''.join(HAN.findall(w['hz']))
        idiom = w.get('pos', '').upper() == 'TN' or len(key) >= 4
        lvl = w.get('lvl', 0) or 7
        return (idiom, lvl, len(key))

    by_char = {}
    for i, w in enumerate(words):
        key = ''.join(HAN.findall(w['hz']))
        for c in set(key):
            by_char.setdefault(c, []).append(i)
    char_words, missing = {}, []
    for c in meta:
        lst = by_char.get(c, [])
        if not lst:
            missing.append(c)
            continue
        own = [i for i in lst if ''.join(HAN.findall(words[i]['hz'])) == c]
        forc = [i for i in lst if words[i].get('forChar') == c]
        rest = sorted((i for i in lst if i not in own and i not in forc), key=rank)
        picked, hzs = [], set()
        for i in own + forc + rest:
            k = ''.join(HAN.findall(words[i]['hz']))
            if k in hzs:
                continue
            hzs.add(k)
            picked.append(i)
            if len(picked) == PER_CHAR:
                break
        char_words[c] = picked

    d1 = json.dumps(rows, ensure_ascii=False, separators=(',', ':'))
    d2 = json.dumps(char_words, ensure_ascii=False, separators=(',', ':'))
    if '</script' in d1 + d2:
        sys.exit('LỖI: dữ liệu chứa chuỗi </script — dừng để tránh hỏng trang.')
    block = (BEGIN + ' (tự động sinh bởi tools/build_hsk_words.py — không sửa tay) -->\n'
             '<script id="hsk-words">\nwindow.HSK_WORDS = ' + d1 + ';\nwindow.HSK_CHAR_WORDS = ' + d2 +
             ';\n</script>\n' + END)
    if BEGIN in s:
        b0 = s.index(BEGIN)
        b1 = s.index(END, b0) + len(END)
        s = s[:b0] + block + s[b1:]
    else:
        i = s.index(ANCHOR) + len(ANCHOR)
        s = s[:i] + '\n' + block + s[i:]
    open(INDEX, 'w', encoding='utf-8').write(s)
    no_ex = [w['hz'] for w in words if not w.get('exCn')]
    print(f'{len(rows)} từ; {len(char_words)}/{len(meta)} chữ có từ + câu ví dụ.')
    if missing:
        print('Chữ chưa có từ/câu ví dụ: ' + ''.join(missing))
    if no_ex:
        print('Từ thiếu câu ví dụ: ' + ' '.join(no_ex))


if __name__ == '__main__':
    main()
