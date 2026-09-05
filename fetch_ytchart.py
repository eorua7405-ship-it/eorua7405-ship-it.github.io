# -*- coding: utf-8 -*-
"""kworb 24시간 최다 조회 영상 TOP 50으로 유튜브 파트의 롱폼 그룹을 교체한다."""
import io, os, re, html, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'board.html')
s = io.open(p, encoding='utf-8').read()

req = urllib.request.Request('https://kworb.net/youtube/', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=30) as r:
    page = r.read().decode('utf-8', 'replace')

rows = re.findall(r'<tr>(.*?)</tr>', page, re.S)
chart = []
for r_ in rows:
    vid = re.search(r'video/([\w-]{11})\.html">(.*?)</a>', r_, re.S)
    if not vid:
        continue
    tds = [re.sub('<[^>]+>', '', c).strip() for c in re.findall(r'<td[^>]*>(.*?)</td>', r_, re.S)]
    if len(tds) < 5 or not tds[0].isdigit():
        continue
    chart.append({'rank': int(tds[0]), 'move': tds[1], 'id': vid.group(1),
                  'title': html.unescape(re.sub('<[^>]+>', '', vid.group(2))).strip(),
                  'views': tds[3], 'likes': tds[4]})
chart = sorted(chart, key=lambda x: x['rank'])[:50]
print('chart rows:', len(chart))


def kor(nstr):
    n = int(nstr.replace(',', ''))
    if n >= 100000000:
        return '%.1f억 회' % (n / 100000000.0)
    if n >= 10000:
        return '%d만 회' % (n // 10000)
    return '%s회' % nstr


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


MOVE = {'=': '순위 유지', 'NEW': '신규 진입'}


def li(c):
    mv = MOVE.get(c['move'], ('전일 대비 ' + c['move']) if c['move'] else '')
    return ('        <li class="item" data-group="24시간 조회수 TOP 50"'
            ' data-sum="%s · %s"'
            ' data-since="2026.09.05 집계 (24시간)"'
            ' data-traffic="24시간 %s회 · 좋아요 %s"'
            ' data-img="https://i.ytimg.com/vi/%s/hqdefault.jpg"'
            ' data-credit="YouTube"'
            ' data-link="https://www.youtube.com/watch?v=%s">\n'
            '          <h3>%s</h3>\n'
            '          <p>kworb 실시간 집계 기준 24시간 최다 조회 %d위.</p>\n'
            '          <div class="meta"><span class="tag">%02d위</span><span class="tag">%s</span></div>\n'
            '        </li>' % (kor(c['views']), esc(mv), c['views'], c['likes'],
                               c['id'], c['id'], esc(c['title']), c['rank'],
                               c['rank'], esc(mv)))


m = re.search(r'(<section class="cat" data-cat="youtube" data-plat="youtube">)(.*?)(</section>)', s, re.S)
assert m
body = m.group(2)
items = re.findall(r'\s*(<li class="item".*?</li>)', body, re.S)
DROP = ('data-group="24시간 조회수 TOP 50"', 'data-group="롱폼"')   # 자기가 만든 그룹 + 옛 그룹
keep = [it for it in items if not any(d in it for d in DROP)]
print('기존', len(items), '-> 유지', len(keep))

ul = re.search(r'(<ul class="items">)(.*?)(\n      </ul>)', body, re.S)
new_ul = ul.group(1) + '\n' + '\n'.join(li(c) for c in chart) + '\n' + '\n        '.join([''] + keep) + ul.group(3)
body = body[:ul.start()] + new_ul + body[ul.end():]
body = body.replace('<span class="en">YouTube · 롱폼 + 숏폼</span>',
                    '<span class="en">YouTube · 24시간 TOP 50 + 숏폼</span>')
body = re.sub(r'<p class="src">출처 ·.*?</p>',
              '<p class="src">출처 · <a href="https://kworb.net/youtube/">kworb 실시간 차트</a> · '
              '<a href="https://sendshort.ai/guides/shorts-creators/">SendShort</a> · '
              '<a href="https://www.zebracat.ai/post/what-is-the-most-viewed-youtube-shorts">Zebracat</a></p>',
              body, count=1, flags=re.S)
s = s[:m.start()] + m.group(1) + body + m.group(3) + s[m.end():]

s = s.replace('var MAX = 50; // 한 파트당 표시 상한', 'var MAX = 80; // 한 파트당 표시 상한')

io.open(p, 'w', encoding='utf-8').write(s)
print('items now:', s.count('<li class="item"'), '| imgs:', s.count('data-img='))
