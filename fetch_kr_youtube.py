# -*- coding: utf-8 -*-
"""한국 아티스트 롱폼 영상 24시간 조회수 순위 -> board-kr.html 유튜브 파트"""
import io, os, re, html, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'board-kr.html')
s = io.open(p, encoding='utf-8').read()
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0'}

with urllib.request.urlopen(urllib.request.Request('https://kworb.net/youtube/realtime_asian.html',
                                                   headers=UA), timeout=30) as r:
    page = r.read().decode('utf-8', 'replace')

HANGUL = re.compile(r'[가-힣]')
rows = []
for row in re.findall(r'<tr>(.*?)</tr>', page, re.S):
    vid = re.search(r'video/([\w-]{11})\.html">(.*?)</a>', row, re.S)
    if not vid:
        continue
    td = [re.sub('<[^>]+>', '', c).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)]
    if len(td) < 5 or not td[0].isdigit():
        continue
    title = html.unescape(re.sub('<[^>]+>', '', vid.group(2))).strip()
    if not HANGUL.search(title):          # 한글이 들어간 = 한국 아티스트 영상
        continue
    rows.append({'aid': int(td[0]), 'id': vid.group(1), 't': title,
                 'views': td[3], 'likes': td[4]})
rows = rows[:30]
print('한국 아티스트 영상:', len(rows))


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def kor(n):
    if n >= 100000000:
        return '%.1f억' % (n / 1e8)
    if n >= 10000:
        return '%d만' % (n // 10000)
    return '{:,}'.format(n)


def li(x, r):
    n = int(x['views'].replace(',', '')) if x['views'].replace(',', '').isdigit() else 0
    return ('        <li class="item" data-group="24시간 조회수 TOP 30 (롱폼)"'
            ' data-sum="24시간 %s회 · 아시아 전체 %d위"'
            ' data-since="2026.09.06 집계 (24시간)"'
            ' data-traffic="24시간 %s회 · 좋아요 %s"'
            ' data-img="https://i.ytimg.com/vi/%s/hqdefault.jpg" data-credit="YouTube"'
            ' data-link="https://www.youtube.com/watch?v=%s">\n'
            '          <span class="rank">%02d</span>\n'
            '          <h3>%s</h3>\n'
            '          <p>kworb 아시아 실시간 집계에서 추출한 한국 아티스트 영상 %d위. 아시아 전체로는 %d위.</p>\n'
            '          <div class="meta"><span class="tag">%02d위</span><span class="tag">뮤직비디오</span></div>\n'
            '        </li>'
            % (kor(n), x['aid'], x['views'], x['likes'], x['id'], x['id'], r, esc(x['t']), r, x['aid'], r))


new_items = [li(x, i + 1) for i, x in enumerate(rows)]

m = re.search(r'(<section class="cat" data-cat="youtube" data-plat="youtube">)(.*?)(</section>)', s, re.S)
body = m.group(2)
ul = re.search(r'(<ul class="items">)(.*?)(\n      </ul>)', body, re.S)
old = re.findall(r'\s*(<li class="item".*?</li>)', ul.group(2), re.S)
keep = [it for it in old if 'data-group="24시간 조회수 TOP 30 (롱폼)"' not in it]
body = (body[:ul.start()] + ul.group(1) + '\n' + '\n'.join(new_items) +
        '\n' + '\n        '.join([''] + keep) + ul.group(3) + body[ul.end():])
body = body.replace('<span class="en">YouTube · 구독자 TOP 25</span>',
                    '<span class="en">YouTube · 롱폼 TOP 30 + 채널</span>')
body = re.sub(r'<p class="src">출처 ·.*?</p>',
              '<p class="src">출처 · <a href="https://kworb.net/youtube/realtime_asian.html">kworb 아시아 실시간 차트</a> · '
              '<a href="https://tubeboard.kr/ranking">튜브보드 유튜버 랭킹</a></p>', body, count=1, flags=re.S)
s = s[:m.start()] + m.group(1) + body + m.group(3) + s[m.end():]

io.open(p, 'w', encoding='utf-8').write(s)
print('유튜브 파트 항목:', body.count('<li class="item"'), '| 전체:', s.count('<li class="item"'))
