# -*- coding: utf-8 -*-
"""영화·게임 항목에 공식 예고편 썸네일을 붙인다.

포스터는 저작권이라 못 쓰지만, 유튜브 썸네일은 이 사이트가 이미 쓰고 있는 자료다
(유튜브 파트 전체가 i.ytimg.com 이다). 예고편은 배급사가 공개용으로 올린 것이라
같은 성격으로 본다.

첫 검색 결과를 그냥 쓰지 않는다 — 제목이 겹치는지 확인하고, 안 겹치면 건너뛴다.
엉뚱한 영화의 썸네일을 붙이는 건 이미지가 없는 것보다 나쁘다.

    python fetch_trailers.py            # board-kr.html
    python fetch_trailers.py board.html
"""
import io, os, re, sys, json, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else 'board-kr.html')
CACHE = os.path.join(HERE, '_trailers.json')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0',
      'Accept-Language': 'ko-KR,ko;q=0.9'}

cache = json.load(io.open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}


def norm(t):
    """비교용으로 기호·공백을 털어낸다."""
    return re.sub(r'[^0-9A-Za-z가-힣]', '', t).lower()


def search(q, want):
    """첫 결과를 쓰되 제목이 겹칠 때만. 안 겹치면 None."""
    u = 'https://www.youtube.com/results?search_query=' + urllib.parse.quote(q)
    h = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25)
    h = h.read().decode('utf-8', 'replace')
    ids = re.findall(r'"videoId":"([\w-]{11})"', h)
    titles = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}', h)
    key = norm(want)
    for vid, title in zip(ids, titles[:8]):
        try:                      # 유튜브 JSON 은 한글을 유니코드 이스케이프로 준다
            title = json.loads('"' + title + '"')
        except Exception:
            pass
        if key and key[:8] in norm(title):
            return {'id': vid, 'title': title}
    return None


def cached(k, q, want):
    if k in cache:
        return cache[k]
    try:
        cache[k] = search(q, want)
    except Exception as e:
        print('ERR ', k, e)
        return None
    print(('OK   ' if cache[k] else 'MISS '), k)
    time.sleep(0.6)
    return cache[k]


s = io.open(P, encoding='utf-8').read()
n = [0]
CUR = ['']

SUFFIX = {'movie': '예고편', 'game': '공식 트레일러'}


def fix(m):
    tag, inner = m.group(1), m.group(2)
    if 'data-img=' in tag:
        return m.group(0)
    if CUR[0] not in SUFFIX:
        return m.group(0)
    h3 = re.search(r'<h3>(.*?)</h3>', inner, re.S)
    if not h3:
        return m.group(0)
    title = re.sub('<[^>]+>', '', h3.group(1)).strip()
    if len(norm(title)) < 4:
        return m.group(0)
    r = cached('%s:%s' % (CUR[0], title), '%s %s' % (title, SUFFIX[CUR[0]]), title)
    if not r:
        return m.group(0)
    n[0] += 1
    add = (' data-img="https://i.ytimg.com/vi/%s/hqdefault.jpg" data-credit="YouTube"' % r['id'])
    if 'data-link=' not in tag:
        add += ' data-link="https://www.youtube.com/watch?v=%s"' % r['id']
    return tag[:-1] + add + '>' + inner + '</li>'


def run_section(m):
    CUR[0] = m.group(1)
    return re.sub(r'(<li class="item"[^>]*>)(.*?)</li>', fix, m.group(0), flags=re.S)


s = re.sub(r'<section class="cat" data-cat="(\w+)".*?</section>', run_section, s, flags=re.S)
json.dump(cache, io.open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
io.open(P, 'w', encoding='utf-8').write(s)
print('예고편 썸네일 %d개 추가 | 전체 이미지 %d / 항목 %d'
      % (n[0], s.count('data-img='), s.count('<li class="item"')))
