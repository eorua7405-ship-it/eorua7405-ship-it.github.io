# -*- coding: utf-8 -*-
"""게임: 스팀 공식 최다 플레이 TOP 50 / 음악: 스포티파이 글로벌 TOP 50"""
import io, os, re, json, time, html, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'board.html')
s = io.open(p, encoding='utf-8').read()
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36'}


def get(url, timeout=30):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read().decode('utf-8', 'replace')


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def kor(n):
    if n >= 100000000:
        return '%.1f억' % (n / 100000000.0)
    if n >= 10000:
        return '%d만' % (n // 10000)
    return '{:,}'.format(n)


# ==================== 1. 스팀 최다 플레이 TOP 50 ====================
NAMES = os.path.join(HERE, '_steamnames.json')
names = json.load(io.open(NAMES, encoding='utf-8')) if os.path.exists(NAMES) else {}

ranks = json.loads(get('https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/'))['response']['ranks'][:50]
for r in ranks:
    a = str(r['appid'])
    if a in names:
        continue
    try:
        d = json.loads(get('https://store.steampowered.com/api/appdetails?appids=%s&l=korean' % a, 20))
        names[a] = d[a]['data']['name'] if d.get(a, {}).get('success') else ''
    except Exception as e:
        names[a] = ''
    time.sleep(0.35)
json.dump(names, io.open(NAMES, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('steam names:', sum(1 for r in ranks if names.get(str(r['appid']))), '/', len(ranks))


def game_li(r):
    a = str(r['appid'])
    nm = names.get(a) or ('앱 %s' % a)
    peak = r['peak_in_game']
    last = r.get('last_week_rank') or 0
    mv = '순위 유지' if last == r['rank'] else ('지난주 %d위' % last if last else '신규 진입')
    return ('        <li class="item" data-group="스팀 최다 플레이 TOP 50"'
            ' data-sum="최고 동시접속 %s명 · %s"'
            ' data-since="2026.09.05 집계 (주간)"'
            ' data-traffic="주간 최고 동시접속 %s명"'
            ' data-img="https://cdn.cloudflare.steamstatic.com/steam/apps/%s/header.jpg"'
            ' data-credit="Steam"'
            ' data-link="https://store.steampowered.com/app/%s/">\n'
            '          <h3>%s</h3>\n'
            '          <p>스팀 공식 집계 기준 주간 최다 플레이 %d위.</p>\n'
            '          <div class="meta"><span class="tag">%02d위</span><span class="tag">%s</span></div>\n'
            '        </li>' % (kor(peak), mv, '{:,}'.format(peak), a, a, esc(nm), r['rank'], r['rank'], mv))


m = re.search(r'(<section class="cat" data-cat="game" data-plat="steam">)(.*?)(</section>)', s, re.S)
body = m.group(2)
items = re.findall(r'\s*(<li class="item".*?</li>)', body, re.S)
keep = [it for it in items if 'data-group="스팀 동시접속"' not in it]
ul = re.search(r'(<ul class="items">)(.*?)(\n      </ul>)', body, re.S)
body = (body[:ul.start()] + ul.group(1) + '\n' + '\n'.join(game_li(r) for r in ranks) +
        '\n' + '\n        '.join([''] + keep) + ul.group(3) + body[ul.end():])
body = re.sub(r'<p class="src">출처 ·.*?</p>',
              '<p class="src">출처 · <a href="https://store.steampowered.com/charts/mostplayed">Steam 공식 차트</a> · '
              '<a href="https://alineaanalytics.substack.com/p/2026s-top-games-by-copies-sold-so">Alinea Analytics</a></p>',
              body, count=1, flags=re.S)
s = s[:m.start()] + m.group(1) + body + m.group(3) + s[m.end():]
print('game items:', len(ranks) + len(keep))


# ==================== 2. 스포티파이 글로벌 TOP 50 ====================
sp = get('https://kworb.net/spotify/country/global_daily.html')
tracks = []
for row in re.findall(r'<tr>(.*?)</tr>', sp, re.S):
    tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
    if len(tds) < 8:
        continue
    pos = re.sub('<[^>]+>', '', tds[0]).strip()
    if not pos.isdigit():
        continue
    cell = tds[2]
    txt = html.unescape(re.sub('<[^>]+>', '', cell)).strip()
    if ' - ' not in txt:
        continue
    artist, title = txt.split(' - ', 1)
    streams = re.sub('<[^>]+>', '', tds[6]).strip()
    tracks.append({'rank': int(pos), 'artist': artist.strip(), 'title': title.strip(),
                   'streams': streams, 'move': re.sub('<[^>]+>', '', tds[1]).strip()})
tracks = sorted(tracks, key=lambda x: x['rank'])[:50]
print('spotify rows:', len(tracks))

ART = os.path.join(HERE, '_artwork.json')
art = json.load(io.open(ART, encoding='utf-8')) if os.path.exists(ART) else {}
for t in tracks:
    k = '%s|%s' % (t['artist'], t['title'])
    if k in art:
        continue
    try:
        q = urllib.parse.quote('%s %s' % (t['artist'], re.sub(r'\(.*?\)', '', t['title'])))
        d = json.loads(get('https://itunes.apple.com/search?term=%s&entity=song&limit=1' % q, 20))
        r0 = d['results'][0] if d.get('resultCount') else None
        art[k] = r0['artworkUrl100'].replace('100x100bb', '600x600bb') if r0 else ''
    except Exception:
        art[k] = ''
    time.sleep(0.25)
json.dump(art, io.open(ART, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('artwork:', sum(1 for t in tracks if art.get('%s|%s' % (t['artist'], t['title']))), '/', len(tracks))


def song_li(t):
    k = '%s|%s' % (t['artist'], t['title'])
    img = art.get(k) or ''
    n = int(t['streams'].replace(',', '')) if t['streams'].replace(',', '').isdigit() else 0
    mv = '순위 유지' if t['move'] == '=' else ('전일 대비 ' + t['move'] if t['move'] else '')
    imgattr = (' data-img="%s" data-credit="Apple Music · %s"' % (img, esc(t['artist']))) if img else ''
    return ('        <li class="item" data-group="스포티파이 글로벌 TOP 50"'
            ' data-sum="일간 스트리밍 %s회 · %s"'
            ' data-since="2026.09.05 집계 (일간)"'
            ' data-traffic="일간 스트리밍 %s회"%s'
            ' data-term="%s %s">\n'
            '          <h3>%s — %s</h3>\n'
            '          <p>스포티파이 글로벌 일간 차트 %d위.</p>\n'
            '          <div class="meta"><span class="tag">%02d위</span><span class="tag">%s</span></div>\n'
            '        </li>' % (kor(n), esc(mv), t['streams'], imgattr,
                               esc(t['title']), esc(t['artist']),
                               esc(t['artist']), esc(t['title']), t['rank'], t['rank'], esc(mv)))


m = re.search(r'(<section class="cat" data-cat="music" data-plat="spotify">)(.*?)(</section>)', s, re.S)
body = m.group(2)
items = re.findall(r'\s*(<li class="item".*?</li>)', body, re.S)
keep = [it for it in items if 'data-group="빌보드 핫100"' not in it]
ul = re.search(r'(<ul class="items">)(.*?)(\n      </ul>)', body, re.S)
body = (body[:ul.start()] + ul.group(1) + '\n' + '\n'.join(song_li(t) for t in tracks) +
        '\n' + '\n        '.join([''] + keep) + ul.group(3) + body[ul.end():])
body = re.sub(r'<p class="src">출처 ·.*?</p>',
              '<p class="src">출처 · <a href="https://kworb.net/spotify/country/global_daily.html">Spotify 글로벌 일간 (kworb)</a> · '
              '<a href="https://www.billboard.com/charts/hot-100/">Billboard</a></p>',
              body, count=1, flags=re.S)
s = s[:m.start()] + m.group(1) + body + m.group(3) + s[m.end():]

io.open(p, 'w', encoding='utf-8').write(s)
print('items now:', s.count('<li class="item"'), '| imgs:', s.count('data-img='))
