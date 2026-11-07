#!/usr/bin/env python3
"""
Thêm bài học hằng ngày (từ khối DATA-LUYEN-VIET trong bài Gemini) vào index.html.

Cách dùng:
    python3 tools/add_lesson.py --input bai_hoc.txt [--topic "kinh-doanh-ban-hang"] [--hwd /duong/dan/hanzi-writer-data]

- --input : file text chứa nội dung bài (chỉ cần có các dòng dạng
            Day3|发展|fāzhǎn|ĐT|phát triển|to develop|公司发展得很快。|Gōngsī fāzhǎn de hěn kuài.|Công ty phát triển rất nhanh.|The company is developing fast.)
            Trường cuối (câu ví dụ tiếng Anh) không bắt buộc: thiếu thì script tự tìm trong thân bài.
            Có thể dán nguyên cả bài, script tự lọc các dòng DATA. Dùng "-" để đọc từ stdin.
- --topic : tên chủ đề (lấy từ tên file Docs "Day3-kinh-doanh-ban-hang"). Có thể truyền cả tên file.
- --readme: cập nhật thêm bảng "Thống kê từ mới theo tuần" trong README.md.
- --hwd   : thư mục gói npm hanzi-writer-data (chứa <chữ>.json). Bỏ trống → tự tải bằng `npm pack`.

Chạy lại cùng một Day sẽ ghi đè Day đó (an toàn khi chạy lại).
Chữ chưa có dữ liệu nét trong bản offline sẽ được bổ sung từ hanzi-writer-data.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile

DAY1 = dt.date(2026, 11, 7)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'index.html')
BEGIN = '<!-- LESSON-DATA:BEGIN'
END = '<!-- LESSON-DATA:END -->'
HAN = re.compile(r'[㐀-鿿]')
LINE = re.compile(r'^\s*[`>*\-\s]*Day\s*(\d+)\s*\|(.+)$', re.I)
MERGE_JS = ("(function(){var b=window.HANZI_DATA_BUNDLE||(window.HANZI_DATA_BUNDLE={}),"
            "m=window.CHAR_META||(window.CHAR_META={}),k;for(k in window.EXTRA_HANZI)if(!b[k])"
            "b[k]=window.EXTRA_HANZI[k];for(k in window.EXTRA_META)if(!m[k])m[k]=window.EXTRA_META[k];})();")


def parse_lines(text):
    days = {}
    for raw in text.splitlines():
        m = LINE.match(raw.strip().strip('`'))
        if not m:
            continue
        day = int(m.group(1))
        f = [x.strip() for x in m.group(2).split('|')]
        f += [''] * (9 - len(f))
        hz = ''.join(HAN.findall(f[0]))
        if not hz:
            continue
        word = {'hz': hz, 'py': f[1], 'pos': f[2], 'vi': f[3], 'en': f[4],
                'exCn': f[5], 'exPy': f[6], 'exVi': f[7], 'exEn': f[8]}
        lst = days.setdefault(day, [])
        if all(w['hz'] != hz for w in lst):
            lst.append(word)
    return days


def find_example_en(text, ex_cn, ex_vi, ex_py=''):
    """Bài thiếu trường câu tiếng Anh: tìm trong thân bài dòng tiếng Anh ngay sau câu ví dụ (sau pinyin + nghĩa Việt)."""
    if not ex_cn:
        return ''
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ex_cn not in ln or ln.lstrip().startswith(('Day', '`Day')):
            continue
        for nxt in lines[i + 1:i + 6]:
            t = re.sub(r'^[^A-Za-z]*', '', nxt).strip()
            if HAN.search(nxt) or not t:
                continue
            if (ex_vi and ex_vi in nxt) or (ex_py and ex_py in nxt):
                continue
            if re.search(r'[À-ỹđĐ]', t):  # còn dấu tiếng Việt / pinyin → bỏ qua
                continue
            if re.match(r'^[A-Za-z][A-Za-z0-9 ,.;:!?\'"()/-]+$', t) and len(t.split()) >= 2:
                return t
    return ''


def topic_from(arg):
    if not arg:
        return ''
    t = re.sub(r'^\s*Day\s*\d+\s*[-_ ]*', '', arg.strip(), flags=re.I)
    return t.replace('-', ' ').strip()


def load_json_after(s, marker, start=0):
    i = s.index(marker, start) + len(marker)
    obj, end = json.JSONDecoder().raw_decode(s, i)
    return obj, end


def ensure_hwd(path):
    if path:
        return path
    tmp = tempfile.mkdtemp(prefix='hwd-')
    subprocess.run(['npm', 'pack', 'hanzi-writer-data@2.0.1', '--silent'], cwd=tmp, check=True,
                   stdout=subprocess.DEVNULL)
    tgz = [f for f in os.listdir(tmp) if f.endswith('.tgz')][0]
    with tarfile.open(os.path.join(tmp, tgz)) as t:
        t.extractall(tmp, filter='data') if hasattr(tarfile, 'data_filter') else t.extractall(tmp)
    return os.path.join(tmp, 'package')


def char_pinyin(c):
    try:
        from pypinyin import pinyin, Style
        return pinyin(c, style=Style.TONE)[0][0]
    except Exception:
        return ''


README = os.path.join(ROOT, 'README.md')
STATS_BEGIN = '<!-- WEEK-STATS:BEGIN (tự động sinh bởi tools/add_lesson.py) -->'
STATS_END = '<!-- WEEK-STATS:END -->'


def week_stats(lessons):
    """Đếm từ mới / chữ Hán mới theo tuần (thứ Hai → Chủ nhật). Từ đã gặp ở ngày trước không tính lại."""
    seen_w, seen_c, weeks = set(), set(), {}
    for d in sorted(lessons, key=lambda x: x['day']):
        try:
            date = dt.datetime.strptime(d.get('date', ''), '%d/%m/%Y').date()
        except ValueError:
            continue
        mon = date - dt.timedelta(days=date.weekday())
        wk = weeks.setdefault(mon, {'days': 0, 'words': 0, 'chars': 0})
        wk['days'] += 1
        for w in d.get('words', []):
            if not w.get('hz') or w['hz'] in seen_w:
                continue
            seen_w.add(w['hz'])
            wk['words'] += 1
            for c in HAN.findall(w['hz']):
                if c not in seen_c:
                    seen_c.add(c)
                    wk['chars'] += 1
    return weeks, len(seen_w), len(seen_c)


def update_readme(lessons):
    if not os.path.exists(README):
        return
    weeks, tw, tc = week_stats(lessons)
    rows = ['| Tuần | Số bài | Từ mới | Chữ Hán mới |', '|---|---:|---:|---:|']
    for mon in sorted(weeks, reverse=True):
        sun = mon + dt.timedelta(days=6)
        w = weeks[mon]
        rows.append(f"| {mon:%d/%m} – {sun:%d/%m/%Y} | {w['days']} | {w['words']} | {w['chars']} |")
    rows.append(f"| **Tổng cộng** | **{len(lessons)}** | **{tw}** | **{tc}** |")
    block = STATS_BEGIN + '\n' + '\n'.join(rows) + '\n' + STATS_END
    r = open(README, encoding='utf-8').read()
    if STATS_BEGIN in r and STATS_END in r:
        i = r.index(STATS_BEGIN); j = r.index(STATS_END) + len(STATS_END)
        r = r[:i] + block + r[j:]
    else:
        r = r.rstrip('\n') + '\n\n## Thống kê từ mới theo tuần\n\nTự cập nhật mỗi lần chạy `tools/add_lesson.py` (tuần tính từ thứ Hai đến Chủ nhật; từ đã học ở ngày trước không tính lại).\n\n' + block + '\n'
    open(README, 'w', encoding='utf-8').write(r)
    print('Đã cập nhật bảng thống kê tuần trong README.md')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--topic', default='')
    ap.add_argument('--hwd', default='')
    ap.add_argument('--file', default=INDEX)
    ap.add_argument('--readme', action='store_true', help='cập nhật bảng thống kê tuần trong README.md')
    a = ap.parse_args()

    text = sys.stdin.read() if a.input == '-' else open(a.input, encoding='utf-8').read()
    new_days = parse_lines(text)
    for words in new_days.values():
        for w in words:
            if not w['exEn']:
                w['exEn'] = find_example_en(text, w['exCn'], w['exVi'], w['exPy'])
    if not new_days:
        print('LỖI: không tìm thấy dòng DATA-LUYEN-VIET nào (dạng DayN|Hán tự|...).', file=sys.stderr)
        sys.exit(2)

    s = open(a.file, encoding='utf-8').read()
    bundle_keys = set(load_json_after(s, 'window.HANZI_DATA_BUNDLE = ')[0].keys())
    meta = load_json_after(s, 'window.CHAR_META = ')[0]

    b0 = s.index(BEGIN)
    b1 = s.index(END, b0) + len(END)
    block = s[b0:b1]
    lessons = load_json_after(block, 'window.DAILY_LESSONS = ')[0]
    extra_hz = load_json_after(block, 'window.EXTRA_HANZI = ')[0]
    extra_meta = load_json_after(block, 'window.EXTRA_META = ')[0]

    # Ưu tiên tên chủ đề có dấu trong dòng "📅 ... – Chủ đề: ..." của bài Gemini
    mt = re.search(r'Chủ đề\s*[:：]\s*(.+)', text)
    topic = mt.group(1).strip().strip('*').strip() if mt else topic_from(a.topic)
    for day, words in new_days.items():
        old = next((d for d in lessons if d['day'] == day), None)
        entry = {'day': day,
                 'date': (DAY1 + dt.timedelta(days=day - 1)).strftime('%d/%m/%Y'),
                 'topic': topic or (old or {}).get('topic', ''),
                 'words': words}
        lessons = [d for d in lessons if d['day'] != day] + [entry]
    lessons.sort(key=lambda d: d['day'])

    hwd = None
    added, missing = [], []
    for day in sorted(new_days):
        for w in new_days[day]:
            for c in dict.fromkeys(HAN.findall(w['hz'])):
                if c not in bundle_keys and c not in extra_hz:
                    hwd = hwd or ensure_hwd(a.hwd)
                    p = os.path.join(hwd, c + '.json')
                    if os.path.exists(p):
                        d = json.load(open(p, encoding='utf-8'))
                        extra_hz[c] = {k: d[k] for k in ('strokes', 'medians', 'radStrokes') if k in d}
                        added.append(c)
                    else:
                        missing.append(c)
                if c not in meta and c not in extra_meta:
                    single = w['hz'] == c
                    extra_meta[c] = {
                        'py': w['py'] if single else char_pinyin(c),
                        'rad': '', 'radName': '',
                        'vi': w['vi'] if single else f"(trong từ {w['hz']}: {w['vi']})",
                        'viSrc': 'lesson', 'en': w['en'] if single else '',
                        'exCn': w['exCn'], 'exPy': w['exPy'], 'exVi': w['exVi'], 'exEn': w.get('exEn', '')}

    dumps = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    new_block = (BEGIN + ' (tự động sinh bởi tools/add_lesson.py — không sửa tay) -->\n'
                 '<script id="lesson-data">\n'
                 f'window.DAILY_LESSONS = {dumps(lessons)};\n'
                 f'window.EXTRA_HANZI = {dumps(extra_hz)};\n'
                 f'window.EXTRA_META = {dumps(extra_meta)};\n'
                 f'{MERGE_JS}\n'
                 '</script>\n' + END)
    if '</script' in new_block.split('<script id="lesson-data">', 1)[1].rsplit('</script>', 1)[0]:
        sys.exit('LỖI: dữ liệu chứa chuỗi </script — dừng để tránh hỏng trang.')
    open(a.file, 'w', encoding='utf-8').write(s[:b0] + new_block + s[b1:])

    for day in sorted(new_days):
        print(f"Day{day}: " + ', '.join(w['hz'] for w in new_days[day]))
    print('Bổ sung dữ liệu nét: ' + (', '.join(added) if added else 'không cần'))
    if missing:
        print('KHÔNG tìm thấy dữ liệu nét cho: ' + ', '.join(missing))
    print(f'Tổng số ngày đã học: {len(lessons)}')
    weeks, _, _ = week_stats(lessons)
    if weeks:
        mon = max(weeks)
        print(f"Tuần {mon:%d/%m}: {weeks[mon]['words']} từ mới, {weeks[mon]['chars']} chữ Hán mới")
    if a.readme:
        update_readme(lessons)


if __name__ == '__main__':
    main()
