# -*- coding: utf-8 -*-
"""board-kr.html 의 이미지 없는 항목에 자유 이용 이미지를 붙인다.

  · 인스타 오디오 / 음악  : iTunes Search API 앨범 아트워크
  · 게임                  : 스팀 공식 헤더 (스팀에 있는 것만)
  · 나머지                : Openverse CC0 / PDM / BY

키워드가 항목의 실체를 가리키지 못하는 것(신조어·밈 등)은 일부러 비워 둔다.
비어 있으면 카드가 타이포그래피 비주얼로 대체되므로 그쪽이 정확하다.
"""
import io, os, re, sys, json, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
# 기본은 국내판. 인자를 주면 그 파일을 처리한다 (글로벌판도 같은 규칙이 통한다)
P = os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else 'board-kr.html')
CACHE = os.path.join(HERE, '_kr_images.json')
UA = {'User-Agent': 'issue-now/1.0'}

# 스팀에 있는 국내 인기작만. 없는 건 붙이지 않는다.
STEAM = {
 '플레이어언노운스 배틀그라운드': 578080,
 '로스트아크': 1599340,
 '이터널 리턴': 1049590,
 '오버워치 2': 2357570,
 '메이플스토리': 216150,
 '배틀그라운드': 578080,
 '카운터 스트라이크 2': 730,
 '팰월드': 1623730,
 '발더스 게이트 3': 1086940,
 '엘든 링': 1245620,
 '몬스터 헌터 와일즈': 2246340,
 '데이브 더 다이버': 1868140,
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
 # 영화 — 포스터는 저작권이라 못 쓴다. 극장이라는 장소로 대신한다
 '오디세이': 'movie theater seats',
 # 밈·신조어는 타이포 비주얼이 정확해서 비워 둔다
 # 틱톡 태그
 '#불꽃축제': 'fireworks festival night',
 '#fireworks': 'fireworks sky',
 '#한강': 'han river seoul',
 '#광복절': 'korean flag',
 '#가을코디': 'autumn outfit fashion',
 '#올영세일': 'cosmetics shopping bag',
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
        # 확장자가 주소에 안 붙는 제공처가 많다. filetype 필드도 같이 본다.
        ok = (re.search(r'\.(jpe?g|png|webp)$', url.split('?')[0], re.I)
              or (it.get('filetype') or '').lower() in ('jpg', 'jpeg', 'png', 'webp'))
        if url.startswith('https://') and ok:
            by = (it.get('creator') or '').strip()[:40]
            lic = (it.get('license') or '').upper()
            return {'url': url, 'credit': (by + ' · ' + lic) if by else lic}
    return None


def itunes(term):
    # country=KR 을 붙이면 결과가 0으로 돌아온다. 붙이지 말 것.
    u = ('https://itunes.apple.com/search?term=' + urllib.parse.quote(term) +
         '&entity=song&limit=1')
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


STOP = {'trend', 'trends', 'trending', 'consumers', 'gen', 'z', 'the', 'of', 'and',
        'over', 'daily', 'year', 'challenge', 'content', 'design', 'style'}


def candidates(q):
    """전체 -> 앞 3단어 -> 앞 2단어 순으로 좁혀 본다. 중복은 걸러낸다."""
    if not q:
        return []
    words = [w for w in re.findall(r"[A-Za-z가-힣]+", q)
             if len(w) > 1 and w.lower() not in STOP]
    out = [q]
    for n in (3, 2):
        if len(words) >= n:
            out.append(' '.join(words[:n]))
    seen, uniq = set(), []
    for c in out:
        if c and c not in seen:
            seen.add(c)
            uniq.append(c)
    return uniq


CUR = ['']          # 지금 처리 중인 파트


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

    # 3) 그 외 -> Openverse. 손으로 적어둔 키워드가 우선이고,
    #    없으면 항목이 이미 들고 있는 영문 검색어(data-q)를 그대로 쓴다.
    q = ''
    for k, v in KW.items():
        if title.startswith(k):
            q = v
            break
    if not q:
        mq = re.search(r'data-q="([^"]*)"', tag)
        # 사진이 말이 되는 파트에서만 자동 검색을 쓴다.
        # 영화 포스터·밈·음원은 사진으로 대체하면 오히려 틀린 그림이 된다.
        if mq and CUR[0] in ('beauty', 'food', 'fashion', 'travel', 'tech', 'life'):
            q = mq.group(1)
    # data-q 는 문장에 가까워 그대로는 안 걸린다.
    # 연도·숫자·흔한 말을 걷어내고 앞 단어 몇 개로 줄여 가며 다시 찾는다.
    for cand in candidates(q):
        r = cached('ov:' + cand, openverse, cand)
        if r:
            filled['openverse'] += 1
            return add(tag, r['url'], r['credit']) + inner + '</li>'
    return m.group(0)


# 파트 단위로 돌려서 어느 파트의 항목인지 알 수 있게 한다
def run_section(m):
    CUR[0] = m.group(1)
    return re.sub(r'(<li class="item"[^>]*>)(.*?)</li>', fix, m.group(0), flags=re.S)


s = re.sub(r'<section class="cat" data-cat="(\w+)".*?</section>', run_section, s, flags=re.S)
json.dump(cache, io.open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
io.open(P, 'w', encoding='utf-8').write(s)
print('추가 · 아트워크 %(itunes)d · 스팀 %(steam)d · Openverse %(openverse)d' % filled,
      '| 전체 이미지', s.count('data-img='), '/ 항목', s.count('<li class="item"'))
