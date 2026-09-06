# -*- coding: utf-8 -*-
"""board-kr.html 의 이미지 없는 항목에 자유 이용 이미지를 붙인다.

  · 인스타 오디오 / 음악  : iTunes Search API 앨범 아트워크
  · 게임                  : 스팀 공식 헤더 (스팀에 있는 것만)
  · 나머지                : Openverse CC0 / PDM / BY

키워드가 항목의 실체를 가리키지 못하는 것(신조어·밈 등)은 일부러 비워 둔다.
비어 있으면 카드가 타이포그래피 비주얼로 대체되므로 그쪽이 정확하다.
"""
import io, os, re, json, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 'board-kr.html')
CACHE = os.path.join(HERE, '_kr_images.json')
UA = {'User-Agent': 'issue-now/1.0'}

# 스팀에 있는 국내 인기작만. 없는 건 붙이지 않는다.
STEAM = {
 '플레이어언노운스 배틀그라운드': 578080,
 '로스트아크': 1599340,
 '이터널 리턴': 1049590,
 '오버워치 2': 2357570,
 '메이플스토리': 216150,
}

# h3 앞부분 -> Openverse 검색어
KW = {
 # 음식
 '두바이 모찌': 'chocolate mochi dessert',
 '흑백요리사 콜라보': 'korean convenience store food',
 '와사비 명란볼': 'korean snack packages',
 '스몰 럭셔리': 'premium dessert cafe',
 '2026 외식 4대': 'restaurant table dining',
 '건강식의 확장': 'healthy salad bowl',
 '일상형 파인다이닝': 'fine dining plate',
 '수산물의 재발견': 'sashimi seafood platter',
 # 뷰티
 '달바 워터풀': 'sunscreen bottle',
 'VT 리들샷': 'sheet mask skincare',
 '메디큐브 에이지': 'beauty device face',
 '클리오 × 국가유산청': 'eyeshadow palette',
 '다이브인 저분자': 'serum dropper bottle',
 '세라마이드 모찌': 'moisturizer cream jar',
 '선케어가 제형별로': 'sunscreen skincare products',
 '팩클렌저': 'facial cleanser foam',
 '노크 아카이브': 'body toner glass bottle',
 '브랜드 평판 1위': 'cosmetics store shelf',
 # 패션
 '무신사 매출': 'online fashion shopping',
 '앱 이용자 순위': 'smartphone shopping app',
 '외국인이 오프라인': 'clothing store interior',
 '2026 is the new 2016': 'streetwear outfit',
 # 여행
 '짧고 자주': 'weekend trip suitcase',
 '여름휴가는 국내가': 'korea beach summer',
 '감성 소도시': 'korean small town street',
 '워케이션': 'laptop cafe remote work',
 '캠핑 · 글램핑': 'camping tent night',
 '일본 945만': 'tokyo street japan',
 '중앙아시아': 'samarkand uzbekistan',
 '해외여행 계획': 'airport departure board',
 '반려동물 동반': 'dog travel car',
 # 전자기기
 '갤럭시 S25 FE': 'samsung galaxy smartphone',
 '갤럭시 S26 울트라': 'smartphone camera closeup',
 '신규 플래그십': 'smartphones lineup',
 '갤럭시 S26 출시': 'smartphone in hand',
 '비스포크 AI 콤보': 'washing machine laundry',
 '녹색상품': 'energy efficient appliance',
 '갤럭시 북6': 'laptop computer desk',
 # 라이프스타일
 '제철코어': 'seasonal vegetables market',
 '나노 커뮤니티': 'small group meeting',
 '쇼퍼테인먼트': 'live streaming shopping',
 'AI와 상의하며': 'person using chatbot phone',
}

cache = json.load(io.open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}


def get(url, timeout=30):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def openverse(q):
    u = ('https://api.openverse.org/v1/images/?q=' + urllib.parse.quote(q) +
         '&license=cc0,pdm,by&page_size=5&mature=false')
    for it in json.loads(get(u, 40)).get('results', []):
        url = it.get('url') or ''
        if url.startswith('https://') and re.search(r'\.(jpe?g|png|webp)$', url.split('?')[0], re.I):
            by = (it.get('creator') or '').strip()[:40]
            lic = (it.get('license') or '').upper()
            return {'url': url, 'credit': (by + ' · ' + lic) if by else lic}
    return None


def itunes(term):
    u = ('https://itunes.apple.com/search?term=' + urllib.parse.quote(term) +
         '&entity=song&limit=1&country=KR')
    for it in json.loads(get(u, 25)).get('results', []):
        a = it.get('artworkUrl100')
        if a:
            return {'url': a.replace('100x100bb', '600x600bb'), 'credit': 'iTunes'}
    return None


def cached(key, fn, *a):
    if key in cache:
        return cache[key]
    try:
        cache[key] = fn(*a)
    except Exception as e:
        print('ERR ', key, e)
        return None
    print(('OK   ' if cache[key] else 'MISS '), key)
    time.sleep(0.3)
    return cache[key]


s = io.open(P, encoding='utf-8').read()
filled = {'itunes': 0, 'steam': 0, 'openverse': 0}


def add(tag, img, credit):
    return tag[:-1] + ' data-img="%s" data-credit="%s">' % (img, credit.replace('"', ''))


def fix(m):
    tag, inner = m.group(1), m.group(2)
    if 'data-img=' in tag:
        return m.group(0)
    h3 = re.search(r'<h3>(.*?)</h3>', inner, re.S)
    if not h3:
        return m.group(0)
    title = re.sub('<[^>]+>', '', h3.group(1)).strip()

    # 1) 오디오 · 음악 -> 아트워크. '오리지널 오디오'는 음원이 아니라 건너뛴다.
    if ' — ' in title and not title.startswith('오리지널 오디오'):
        r = cached('itunes:' + title, itunes, title.replace(' — ', ' '))
        if r:
            filled['itunes'] += 1
            return add(tag, r['url'], r['credit']) + inner + '</li>'
        return m.group(0)

    # 2) 게임 -> 스팀 헤더
    if title in STEAM:
        filled['steam'] += 1
        return (add(tag, 'https://cdn.cloudflare.steamstatic.com/steam/apps/%d/header.jpg'
                    % STEAM[title], 'Steam') + inner + '</li>')

    # 3) 그 외 -> Openverse
    for k, q in KW.items():
        if title.startswith(k):
            r = cached('ov:' + q, openverse, q)
            if r:
                filled['openverse'] += 1
                return add(tag, r['url'], r['credit']) + inner + '</li>'
            break
    return m.group(0)


s = re.sub(r'(<li class="item"[^>]*>)(.*?)</li>', fix, s, flags=re.S)
json.dump(cache, io.open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
io.open(P, 'w', encoding='utf-8').write(s)
print('추가 · 아트워크 %(itunes)d · 스팀 %(steam)d · Openverse %(openverse)d' % filled,
      '| 전체 이미지', s.count('data-img='), '/ 항목', s.count('<li class="item"'))
