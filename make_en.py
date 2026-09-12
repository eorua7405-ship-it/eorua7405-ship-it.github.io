# -*- coding: utf-8 -*-
"""board-kr.html(국내판) -> board-en.html (영어판)

한국에서 지금 뭐가 유행하는지를 영어권 독자에게 보여주는 판본이다.
해외판을 영어로 옮기지 않는다 — 미국 독자에게 미국 유행을 알려줄 이유가 없다.

번역은 규칙 + 사전으로 한다. 항목 대부분이 같은 틀의 문장이라 규칙이 잘 듣는다.
끝내 남은 한글은 화면에 내보내지 않는다 — 영어 페이지에 한국어가 섞이면
번역이 덜 된 티만 나고 읽는 사람에게 쓸모가 없다. 대신 몇 개가 빠졌는지 보고한다.
"""
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = io.open(os.path.join(HERE, 'board-kr.html'), encoding='utf-8').read()

# ---------- 1) 틀이 정해진 문장 (정규식, 순서대로) ----------
RULES = [
 # 수치 표현
 (r'일간 스트리밍 ([\d,]+)회', r'\1 daily streams'),
 (r'일간 스트리밍 ([\d.]+)만회', r'\1K daily streams'),
 (r'24시간 ([\d,]+)회 · 좋아요 ([\d,]+)', r'\1 views in 24h · \2 likes'),
 (r'24시간 ([\d.]+)만회 · 아시아 전체 (\d+)위', r'\1M views in 24h · #\2 in Asia'),
 (r'일 관객 ([\d,]+)명 · 누적 ([\d,.]+)만', r'\1 admissions today · \2M cumulative'),
 (r'일 관객 ([\d,]+)명 · 누적 ([\d,]+)명', r'\1 admissions today · \2 cumulative'),
 (r'일 관객 ([\d,]+)명', r'\1 admissions today'),
 (r'게시물 ([\d.,]+)천개 · 조회 ([\d,]+)만회', r'\1K posts · \2M views'),
 (r'게시물 ([\d.,]+)만개 · 조회 ([\d,]+)억회', r'\1K posts · \2B views'),
 (r'게시물 ([\d.,]+)천개', r'\1K posts'),
 (r'게시물 ([\d.,]+)만개', r'\1K posts'),
 (r'릴스 ([\d.,]+)만개 사용', r'\1K reels'),
 (r'릴스 ([\d.,]+)천개 사용', r'\1K reels'),
 (r'릴스 ([\d,]+)개 사용', r'\1 reels'),
 (r'릴스 ([\d.,]+)만개', r'\1K reels'),
 (r'릴스 ([\d.,]+)천개', r'\1K reels'),
 (r'릴스 ([\d,]+)개', r'\1 reels'),
 # 그룹 이름
 (r'스포티파이 한국 TOP 50', 'Spotify Korea Top 50'),
 (r'24시간 조회수 TOP 30 \(롱폼\)', 'Top 30 by 24h views'),
 (r'인기 상승 오디오 TOP 37', 'Rising audio Top 37'),
 (r'게임메카 종합 TOP 20', 'GameMeca overall Top 20'),
 (r'일별 관객 순위', 'Daily box office'),
 (r'(\d+)일 급상승', r'Rising · \1-day'),
 # 순위·변동
 (r'순위 유지', 'no change'),
 (r'전일 대비 ([+-]\d+)', r'\1 vs yesterday'),
 (r'신규 진입', 'new entry'),
 (r'(\d+)위', r'#\1'),
 # 시점
 (r'(\d{4}\.\d{2}\.\d{2}) 집계 \(일간\)', r'\1 (daily)'),
 (r'(\d{4}\.\d{2}\.\d{2}) 집계 \(24시간\)', r'\1 (24h)'),
 (r'(\d{4}\.\d{2}\.\d{2}) 확인 \((\d+)일 집계\)', r'checked \1 (\2-day)'),
 (r'(\d{4}\.\d{2}\.\d{2}) 앱 확인', r'checked in app \1'),
 (r'(\d{4}\.\d{2}\.\d{2}) 집계', r'\1'),
 (r'(\d{4}\.\d{2}\.\d{2}) 개봉', r'released \1'),
 (r'(\d{4}\.\d{2}\.\d{2}) 확인', r'checked \1'),
 (r'(\d{4})\.(\d{2}) 급상승', r'rising \1.\2'),
 (r'(\d{4}) 상반기', r'H1 \1'),
 (r'(\d{4}) 하반기', r'H2 \1'),
 (r'(\d{4}) 확산', r'spreading \1'),
 (r'(\d{4}) 인기', r'popular \1'),
 (r'(\d{4}) 흐름', r'\1 trend'),
 (r'(\d{4}) 전반', r'through \1'),
 # 되풀이되는 설명문
 (r'스포티파이 한국 일간 차트 #(\d+)\.', r'#\1 on the Spotify Korea daily chart.'),
 (r'스포티파이 한국 일간 차트', 'Spotify Korea daily chart'),
 (r'인스타그램 오디오 인기 상승 #(\d+)\. 길이 ([\d:]+), 사용된 ([\d.,K]+) reels\.',
  r'#\1 on Instagram rising audio. \2 long, \3 reels.'),
 (r'([\d.,KMB]+) reels\. 순위 (up|down|flat|new entry|New|no change|Rising) 중이라 이번 주 안에 자리가 바뀔 수 있는 구간인 듯\.',
  r'\1 reels, and \2 — the kind of slot that can move again inside a week.'),
 (r'kworb 아시아 실시간 집계에서 추출한 한국 아티스트 영상 #(\d+)\. 아시아 전체로는 #(\d+)\.',
  r'#\1 among Korean-artist videos on kworb Asia realtime; #\2 across Asia overall.'),
 (r'영진위 발권데이터 기준 일별 관객 #(\d+)\.',
  r'#\1 by daily admissions, from KOFIC ticketing data.'),
 (r'([A-Za-z &.\'-]+)가 서비스하는 ([A-Za-z ]+)\. '
  r'포털 트렌드·PC방 접속·게임방송 시청자·유저 투표를 합산한 종합 #(\d+)\.',
  r'\2 operated by \1. #\3 overall — portal search, PC-cafe sessions, '
  r'stream viewers and user votes combined.'),
 (r'포털 트렌드·PC방 접속·게임방송 시청자·유저 투표를 합산한 종합 #(\d+)\.',
  r'#\1 overall — portal search, PC-cafe sessions, stream viewers and user votes combined.'),
 (r'PC방 접속과 방송 시청자 수가 함께 반영된 순위라 실제 체감과 가깝다\.',
  'The ranking folds in PC-cafe sessions and stream viewership, '
  'so it tracks what people actually play.'),
 (r'TikTok Creative Center 한국 (?:Rising · \d+-day|\d+일) 기준 #(\d+)\. '
  r'([\dK.,]+ posts), ([\dMB.,]+ views)\.',
  r'#\1 in Korea on TikTok Creative Center. \2, \3.'),
 (r'틱톡 크리에이티브 센터 한국 (?:Rising · \d+-day|\d+일) 기준 #(\d+)\.',
  r'#\1 in Korea on TikTok Creative Center.'),
 (r'틱톡 크리에이티브 센터', 'TikTok Creative Center'),
 (r'길이 ([\d:]+)', r'\1 long'),
 (r'Instagram 오디오 인기 (?:up|상승|down|flat) #(\d+)\. 길이 ([\d:—]+)(?: long)?, 사용된 ([\d.,K]+) reels\.',
  r'#\1 on Instagram rising audio. \2 long, \3 reels.'),
 (r'조회수 ([\d,]+)만회', r'\1M views'),
 (r'조회수 ([\d,]+)억회', r'\1B views'),
 (r'분류는 (.+?)\.', r'Category: \1.'),
 (r'뉴스·엔터', 'News & Entertainment'),
 (r'의류·액세서리', 'Apparel & Accessories'),
 (r'뷰티·퍼스널케어', 'Beauty & Personal Care'),
 (r'([\d,]+)만 개', r'\1M'),
 (r'([\d,]+)천 개', r'\1K'),
 (r'KOFIC ticketing data 기준 일별 #(\d+)\.', r'#\1 by daily admissions (KOFIC ticketing data).'),
(r'([A-Za-z ]+)가 서비스하는 ([A-Za-z ]+)\.', r'\2 operated by \1.'),
 (r'출처 ·', 'Sources ·'),
 (r'전체 보기', 'View all'),
]

# ---------- 2) 고정 낱말 (긴 것부터 치환) ----------
TERMS = {
 '인스타그램': 'Instagram', '유튜브': 'YouTube', '틱톡': 'TikTok',
 '음악 순위': 'Music', '영화 순위': 'Box Office', '게임 순위': 'Games',
 '음식': 'Food', '뷰티': 'Beauty', '패션': 'Fashion',
 '밈 · 신조어': 'Memes & Slang', '여행': 'Travel', '전자기기': 'Tech',
 '라이프스타일': 'Lifestyle',
 # 게임
 '리그 오브 레전드': 'League of Legends', 'FC 온라인': 'FC Online',
 '발로란트': 'Valorant', '메이플스토리 월드': 'MapleStory Worlds',
 '메이플스토리': 'MapleStory', '플레이어언노운스 배틀그라운드': 'PUBG: Battlegrounds',
 '리니지': 'Lineage', '서든어택': 'Sudden Attack', '오버워치 2': 'Overwatch 2',
 '로블록스': 'Roblox', '아이온2': 'Aion 2', '로스트아크': 'Lost Ark',
 '던전앤파이터': 'Dungeon & Fighter', '스타크래프트': 'StarCraft',
 '마인크래프트': 'Minecraft', '디아블로 2': 'Diablo II',
 '이터널 리턴': 'Eternal Return', '테일즈런너': 'TalesRunner',
 '월드 오브 워크래프트': 'World of Warcraft', '제우스: 오만의 신': 'Zeus',
 # 회사·매체
 '라이엇 게임즈': 'Riot Games', 'EA코리아': 'EA Korea', '위젯스튜디오': 'Widget Studio',
 '크래프톤': 'Krafton', '엔씨': 'NCSoft', '넥슨지티': 'Nexon GT', '넥슨': 'Nexon',
 '블리자드': 'Blizzard', '스마일게이트 RPG': 'Smilegate RPG', '네오플': 'Neople',
 '모장': 'Mojang', '님블뉴런': 'Nimble Neuron', '라온엔터': 'Raon',
 '올리브영': 'Olive Young', '무신사': 'Musinsa', '화해': 'Hwahae',
 '에이블리': 'Ably', '영화진흥위원회': 'KOFIC', '게임메카': 'GameMeca',
 '영진위 발권데이터': 'KOFIC ticketing data',
 # 장르·꼬리표
 '오리지널 오디오': 'Original audio', '뮤직비디오': 'Music video',
 '롤플레잉': 'RPG', '액션 RPG': 'Action RPG', '샌드박스': 'Sandbox',
 '어드벤처': 'Adventure', '스포츠': 'Sports', '전략': 'Strategy',
 '레이싱': 'Racing', '신규': 'New',
 '급상승 제품': 'Rising products', '카테고리': 'Category', '브랜드': 'Brands',
 '편의점': 'Convenience stores', '외식': 'Dining out', '플랫폼': 'Platforms',
 '스타일': 'Style', '신조어': 'Slang', '밈': 'Memes', '흐름': 'Signals',
 '여행 방식': 'How Koreans travel', '해시태그 규칙': 'Hashtag rules',
 '휴대폰 거래액': 'Phone sales', '가전': 'Home appliances', '노트북': 'Laptops',
 '메이크업': 'Makeup', '스킨케어': 'Skincare', '헤어 · 네일': 'Hair & Nails',
 '향': 'Fragrance', '맛 · 재료': 'Flavors', '메뉴': 'Menu', '스낵': 'Snacks',
 '음료': 'Drinks', '세트': 'Set', '품절': 'Sold out', '리뷰': 'Reviews',
 '장벽': 'Barrier', '제형 분화': 'New formats', '신개념': 'New format',
 '성분': 'Ingredients', '신흥': 'Emerging', '평판 1#': '#1 reputation',
 '상승': 'up', '하락': 'down', '유지': 'flat', '자료 없음': 'no public data',
 '디바이스': 'Device', '해당 없음': 'n/a', '계절': 'Seasonal', '교차': 'Cross-signal',
 '한정': 'Limited', '확산': 'Spreading', '집계': 'measured',
}

# ---------- 2-1) 화면 문구 (직역이 아니라 영어권 독자 기준으로 다시 씀) ----------
CHROME = [
 # 제목·헤더
 ('지금 이슈 있나요? — 국내', 'Trending in Korea'),
 ('<h1>지금<br><em>이슈</em> 있나요?</h1>',
  '<h1>Trending<br>in <em>Korea</em></h1>'),
 ('한국에서 <b>지금</b> 뜨는 것들. 매주 월요일 새로 뽑고, 항목마다 '
  '<b>언제 시작됐는지</b>와 <b>얼마나 큰지</b>를 붙였다.',
  'What Korea is actually into <b>right now</b>. Rebuilt every Monday, with '
  '<b>when each thing started</b> and <b>how big it is</b> attached to every entry.'),
 # 주간 스트립
 ('<span>집계 기간</span>', '<span>Period</span>'),
 ('<span>스냅샷</span>', '<span>Snapshot</span>'),
 ('<span>다음 갱신</span>', '<span>Next update</span>'),
 ('이번 주 New', 'New this week'),
 ('이번 주', 'This week'),
 ('분야 필터', 'Filter by part'),
 ('전체', 'All'),
 ('더 보기', 'More'),
 ('접기', 'Collapse'),
 ('자세히 보기', 'Details'),
 ('시작일 · 트래픽', 'Started · Traffic'),
 ('시작일', 'Started'),
 ('트래픽', 'Traffic'),
 ('개 전체', ' total'),
 # 상단 카드
 ('이번 주 #1', 'Top of the week'),
 ('국내 차트에서 숫자가 확인된 세 가지', 'Three numbers we could verify on Korean charts'),
 ('박스오피스 일별', 'Box office · daily'),
 ('스포티파이 한국', 'Spotify Korea'),
 ('일간 스트리밍 기준', 'by daily streams'),
 ('추석 해외 호텔 검색', 'Chuseok overseas hotel searches'),
 ('이번 주 요약!', 'This week in one read'),
 ('9월에 남은 날짜', 'Dates left in September'),
 ('국내 피드가 한 번씩 크게 출렁이는 날.',
  'Days when Korean feeds move all at once.'),
 ('이 보드는 매주 월요일에 다시 뽑는다.', 'This board is rebuilt every Monday.'),
 ('이 페이지는 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.',
  'Some product links are Coupang Partners affiliate links. '
  'We may earn a commission at no extra cost to you.'),
 ('<span>집계 기간</span>', '<span>Period</span>'),
 ('기간', 'Period'),
 ('스냅샷 ·', 'Snapshot ·'),
 ('스냅샷', 'Snapshot'),
 ('(금)', ' (Fri)'),
 ('(월)', ' (Mon)'),
 ('(토)', ' (Sat)'),
 ('(일)', ' (Sun)'),
 ('포함', 'included'),
 # 파트 소제목
 ('Instagram · 인기 up 오디오', 'Instagram · Rising audio'),
 ('TikTok · 급up 해시태그', 'TikTok · Rising hashtags'),
 ('YouTube · 롱폼 TOP 30', 'YouTube · Long-form Top 30'),
 ('Music · 스포티파이 한국', 'Music · Spotify Korea'),
 ('Box Office · 국내 일별 관객수', 'Box Office · Daily admissions'),
 ('Games · 국내 Games 순위', 'Games · Korea rankings'),
 ('Games · 국내 Games', 'Games · Korea'),
 ('Food · Convenience stores·Dining out 신상', 'Food · Convenience-store & dining launches'),
 ('Beauty · Olive Young 인기 제품', 'Beauty · Olive Young bestsellers'),
 ('Fashion · Musinsa·Fashion 트렌드', 'Fashion · Musinsa and the street'),
 ('Travel · 국내 Travel 트렌드', 'Travel · How Koreans travel now'),
 ('Tech · 갤럭시·Home appliances 신제품', 'Tech · Galaxy and home appliances'),
 ('Lifestyle · 소비 트렌드', 'Lifestyle · How Koreans spend'),
 ('Memes · Slang·유행어', 'Memes · Slang and catchphrases'),
 # 자료 출처
 ('앱 릴스 오디오 「인기 up」 (2026.09.06 04:05 직접 확인)',
  'Instagram app, Reels audio "Rising" list (checked 2026.09.06 04:05 KST)'),
 ('kworb 아시아 실시간 차트', 'kworb Asia realtime chart'),
 ('Spotify 한국 일간 (kworb)', 'Spotify Korea daily (kworb)'),
 ('한국 일간 (kworb)', 'Korea daily (kworb)'),
 ('KOFIC 발권데이터', 'KOFIC ticketing data'),
 ('발권데이터', 'ticketing data'),
 ('무비차트', 'MovieChart'),
 ('튜브보드 유튜버 랭킹', 'TubeBoard creator rankings'),
 ('콘텐츠파일럿', 'ContentsPilot'),
 ('트래블앤테이스트', 'Travel & Taste'),
 ('쿡앤셰프뉴스', 'Cook & Chef News'),
 ('서울관광재단', 'Seoul Tourism Organization'),
 ('하퍼스 바자 코리아', "Harper's Bazaar Korea"),
 ('일간투데이 Brands평판', 'Ilgan Today brand reputation'),
 ('쇼피 KBeauty 리포트', 'Shopee K-beauty report'),
 ('Olive Young 뉴스룸', 'Olive Young Newsroom'),
 ('Hwahae 랭킹', 'Hwahae rankings'),
 ('한국 Games 산업 협회', 'Korea Association of Game Industry'),
 ('(한국)', ' (Korea)'),
 ('인기 제품', 'bestsellers'),
 ('인기 up', 'Rising'),
 ('급up', 'Rising'),
 ('롱폼', 'Long-form'),
 ('신상', 'new launches'),
 ('랭킹', 'rankings'),
 ('뉴스룸', 'Newsroom'),
 ('트렌드', 'trends'),
 ('국내', 'Korea'),
 # 안내문
 ('지금 보고 있는 건 WEEK', 'You are looking at WEEK'),
 ('Snapshot이고, 기준 시각은', 'snapshot, measured'),
 ('St', 'St'),
 ('어느 매체가 어떤 지위로 지목했는지', 'which outlet named it and in what capacity'),
 ('를 적었다.', ' is recorded instead.'),
 ('TikTok 해시태그 조회수는 모두', 'TikTok hashtag view counts are all'),
 ('누적치', 'cumulative'),
 ('이며 단일 연도 수치가 아니다.', ', not single-year figures.'),
 ('지금 이슈 있나요?」', 'Trending in Korea」'),
 ('「', '"'), ('」', '"'),
 ('의 생각', "Why it's up"),
 ('인기 Games', 'Popular games'),
 ('조사', 'survey'),
 # 매체
 ('중앙이코노미뉴스', 'JoongAng Economy News'),
 ('한국섬유신문', 'Korea Fashion News'),
 ('고구마팜', 'Gogumafarm'),
 ('부킹닷컴', 'Booking.com'),
 ('트립닷컴', 'Trip.com'),
 ('텔트립', 'Teltrip'),
 ('다나와 DPG', 'Danawa DPG'),
 ('전자신문', 'Electronic Times'),
 ('삼성전자 Newsroom', 'Samsung Newsroom'),
 ('대학내일20대연구소', 'Univ. Tomorrow 20s Lab'),
 ('한국 Travel trends', 'Korea travel trends'),
 # 푸터
 ('운영 · 피유글로벌', 'Published by PUGlobal'),
 ('문의 · ', 'Contact · '),
]

# 고유명사가 영어로 바뀌어야 맞는 규칙이 있고(예: "Riot Games가 서비스하는"),
# 반대로 낱말 치환 전에 걸려야 하는 규칙도 있다. 그래서 규칙 -> 낱말 -> 규칙 순으로 돌린다.
# ---------- 스크립트는 치환에서 뺀다 ----------
# 본문 규칙이 자바스크립트 안까지 들어가면 정규식 리터럴이 깨진다.
# 실제로 '해당 없음' -> 'n/a' 가 /.../ 안의 슬래시를 건드려 스크립트가 통째로 죽었다.
# 화면에 보이는 문자열만 따로 옮긴다.
JS_STRINGS = [
 ("'인스타그램에서 보기'", "'View on Instagram'"),
 ("'유튜브에서 보기'", "'Watch on YouTube'"),
 ("'틱톡에서 보기'", "'View on TikTok'"),
 ("'스포티파이에서 듣기'", "'Listen on Spotify'"),
 ("'스팀에서 보기'", "'View on Steam'"),
 ("'유튜브 리뷰 보기'", "'Watch reviews'"),
 ("'예매 정보 보기'", "'Showtimes'"),
 ("'자세히 보기'", "'Details'"),
 ("'쿠팡에서 보기'", "'View on Coupang'"),
 ("'전체 보기'", "'View all'"),
 ("' 전체'", "' total'"),
 ("'개 전체'", "' total'"),
 ("'건'", "''"),
 ("'시작'", "'Started'"),
 ("'트래픽'", "'Traffic'"),
 ("'왜?'", "'Why'"),
 ("'재유행'", "'back again'"),
 ("'신규'", "'new'"),
]


def protect_scripts(t):
    keep = []

    def grab(m):
        keep.append(m.group(0))
        return '\x00SCRIPT%d\x00' % (len(keep) - 1)

    return re.sub(r'<script[^>]*>.*?</script>', grab, t, flags=re.S), keep


def restore_scripts(t, keep):
    for i, block in enumerate(keep):
        for a, b in JS_STRINGS:
            block = block.replace(a, b)
        t = t.replace('\x00SCRIPT%d\x00' % i, block)
    return t


# ---------- 0) 손으로 옮긴 문장 사전 ----------
# 규칙으로는 옮길 수 없는 서술형 문장을 여기서 먼저 바꾼다.
# 키는 board-kr.html 에 들어간 한국어 원문 그대로여야 한다 — 치환 전에 적용되기 때문이다.
# 주간 갱신 때 국내판 문장을 새로 쓰면 이 파일에 영어를 같이 넣는다.
DICT = {}
DP = os.path.join(HERE, '_en.json')
if os.path.exists(DP):
    import json
    DICT = json.load(io.open(DP, encoding='utf-8'))

s, _scripts = protect_scripts(SRC)
for k in sorted(DICT, key=len, reverse=True):
    if DICT[k]:
        s = s.replace(k, DICT[k])
for _ in range(2):
    for pat, rep in RULES:
        s = re.sub(pat, rep, s)
    for k in sorted(TERMS, key=len, reverse=True):
        s = s.replace(k, TERMS[k])
# 화면 문구는 맨 마지막에. 먼저 돌리면 '이번 주'·'트래픽' 같은 낱말이
# 항목 문장 안에서도 바뀌어 규칙이 안 걸린다.
for a, b in CHROME:
    s = s.replace(a, b)

s = restore_scripts(s, _scripts)

HAN = re.compile(r'[가-힣]')

# ---------- 3) 끝내 한글이 남은 조각은 화면에서 뺀다 ----------
dropped = {'take': 0, 'item': 0}


def clean_item(m):
    """항목 하나를 검사한다. 제목·설명이 한글이면 통째로 뺀다."""
    blk = m.group(0)
    tag = blk.split('>', 1)[0]
    h3 = re.search(r'<h3>(.*?)</h3>', blk, re.S)
    p = re.search(r'<p>(.*?)</p>', blk, re.S)
    # 제목이 한국어 고유명사인 건 괜찮다(곡·영상 제목). 설명문이 한글이면 못 쓴다.
    fields = [re.sub('<[^>]+>', '', p.group(1)) if p else '']
    for k in ('sum', 'traffic', 'group', 'since'):
        mk = re.search(r'data-%s="([^"]*)"' % k, tag)
        if mk:
            fields.append(mk.group(1))
    if any(HAN.search(f) for f in fields):
        dropped['item'] += 1
        return ''
    # 「왜?」만 한글이면 그 속성만 뗀다
    mt = re.search(r' data-take="([^"]*)"', tag)
    if mt and HAN.search(mt.group(1)):
        dropped['take'] += 1
        blk = blk.replace(mt.group(0), '', 1)
    return blk


s = re.sub(r'\s*<li class="item".*?</li>', lambda m: ('\n' + clean_item(m)) if clean_item(m) else '',
           s, flags=re.S)

# ---------- 2-2) 푸터 안내문은 문단 통째로 바꾼다 ----------
FOOT = [
 (r'<p><b>[^<]*</b>[^<]*WEEK.*?</p>',
  '<p><b>This board is rebuilt every Monday.</b> You are looking at the WEEK {w} snapshot '
  '(Sept 7-13), measured 2026-09-11. Start dates and traffic figures are copied only from the '
  'cited sources; where no public number exists, we record which outlet named the item and in '
  'what capacity. TikTok hashtag view counts are cumulative, not single-year figures.</p>'),
 (r'<p>개인정보처리방침 · .*?</p>',
  '<p>Privacy · This site uses Google Analytics to measure visits, which sets cookies. '
  'No personally identifying information is collected. See the '
  '<a href="/privacy/">privacy policy</a> for what is collected and how to opt out.</p>'),
 (r'<p>인용한 수치의 저작권은.*?</p>',
  '<p>Figures quoted here belong to their respective outlets. '
  'The <b>Why</b> notes and the weekly read are written by this board.</p>'),
]
for pat, rep in FOOT:
    s = re.sub(pat, rep.replace('{w}', re.search(r'<b>WEEK (\d+)</b>', s).group(1)), s, count=1, flags=re.S)

# 긴 서술형 블록(주간 요약·남은 날짜)은 아직 한국어다.
# 영어 페이지에 한국어 문단을 남기느니 통째로 뺀다. 번역되면 자동으로 남는다.
HAN_ANY = re.compile(r'[가-힣]')
for pat in (r'<details class="weekly-note">.*?</details>',
            r'<details class="board">.*?</details>',
            r'<section class="diary".*?</section>'):
    m = re.search(pat, s, re.S)
    if m and HAN_ANY.search(re.sub('<[^>]+>', '', m.group(0))):
        s = s.replace(m.group(0), '', 1)

io.open(os.path.join(HERE, 'board-en.html'), 'w', encoding='utf-8').write(s)

left = {}
for m in re.finditer(r'[가-힣][가-힣 ·,.()%~\d-]*', s):
    t = m.group(0).strip()
    if len(t) > 1:
        left[t] = left.get(t, 0) + 1
print('board-en.html 생성 · 항목 %d개 (설명문 미번역으로 뺀 항목 %d · 「왜?」만 뗀 항목 %d)'
      % (s.count('<li class="item"'), dropped['item'], dropped['take']))
print('남은 한글 조각 %d종 (상위 30)' % len(left))
for t, n in sorted(left.items(), key=lambda x: -x[1])[:30]:
    print('  %3d  %s' % (n, t[:70]))
