# -*- coding: utf-8 -*-
"""board.html(글로벌) · board-kr.html(국내) -> 사이트 전체 생성

만들어지는 것: /, /kr/, /week/<주차>/, /kr/week/<주차>/, /archive/, /privacy/,
sitemap.xml, robots.txt, og.png
"""
import io, os, re, glob, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://issueitnow.com'
BRAND = '지금 이슈 있나요?'

DESC_G = ('매주 월요일 갱신되는 해외 유행 보드. '
          '릴스·유튜브·음악·영화·게임·패션·음식·뷰티·밈·여행을 수치와 해석으로 정리합니다.')
DESC_K = ('매주 월요일 갱신되는 국내 유행 보드. '
          '릴스·유튜브·음악·영화·게임·패션·음식·뷰티·밈·여행을 수치와 해석으로 정리합니다.')

RESET = """  :root{color-scheme:light dark}
  html{-webkit-text-size-adjust:100%}
  body{margin:0;font:14px/1.5 system-ui,-apple-system,sans-serif}
  img{max-width:100%}
  [hidden]{display:none!important}"""

ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'"
        "%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%94%A5%3C/text%3E%3C/svg%3E")

NAV = ('<div style="background:#2A211B;color:#F0EDE7;padding:7px 16px;font:600 12px/1.4 '
       "'Noto Sans KR',sans-serif;text-align:center\">"
       '<a href="/" style="color:#F0EDE7;text-decoration:none">이번 주</a>'
       '<span style="opacity:.4;margin:0 10px">·</span>'
       '<a href="/archive/" style="color:#F0EDE7;text-decoration:none">지난 주 보관함</a>'
       '<span style="opacity:.4;margin:0 10px">·</span>'
       '<a href="/privacy/" style="color:#F0EDE7;text-decoration:none">개인정보처리방침</a></div>')


def toggle(edition):
    def btn(label, href, on):
        st = 'background:#C8102E;color:#fff' if on else 'background:transparent;color:#7E6F64'
        return ('<a href="%s" style="%s;display:inline-block;padding:7px 20px;border-radius:999px;'
                "font:700 12.5px/1 'Noto Sans KR',sans-serif;text-decoration:none\">%s</a>"
                % (href, st, label))
    return ('<div style="background:#F0EDE7;border-bottom:1px solid #DBD2C7;padding:10px 16px;text-align:center">'
            '<span style="display:inline-flex;gap:4px;background:#fff;border:1px solid #DBD2C7;'
            'border-radius:999px;padding:3px">' + btn('글로벌', '/', edition == 'global')
            + btn('국내', '/kr/', edition == 'kr') + '</span></div>')


def load(fn):
    t = io.open(os.path.join(HERE, fn), encoding='utf-8').read()
    head = []
    for pat in (r'<title>.*?</title>', r'<link rel="preconnect"[^>]*>',
                r'<link rel="stylesheet"[^>]*>', r'<style>.*?</style>'):
        head += [m.group(0) for m in re.finditer(pat, t, re.S)]
    body = t
    for part in head:
        body = body.replace(part, '', 1)
    return t, head, body.strip()


SRC_G, HEAD_G, BODY_G = load('board.html')
TITLE_G = re.search(r'<title>(.*?)</title>', SRC_G).group(1)
WEEK = int(re.search(r'<b>WEEK (\d+)</b>', SRC_G).group(1))
YEAR = datetime.date.today().year
PERIOD = re.search(r'<span>집계 기간</span><b>(.*?)</b>', SRC_G).group(1).strip()

HAS_KR = os.path.exists(os.path.join(HERE, 'board-kr.html'))
if HAS_KR:
    SRC_K, HEAD_K, BODY_K = load('board-kr.html')
    TITLE_K = re.search(r'<title>(.*?)</title>', SRC_K).group(1)


TODAY = datetime.date.today().isoformat()


def itemlists(body, canonical):
    """각 파트를 순위 목록으로 선언한다. 답변형 AI가 인용할 때 필요한 최소 단위."""
    out = []
    for m in re.finditer(r'<section class="cat" data-cat="(\w+)".*?</section>', body, re.S):
        sec = m.group(0)
        h2 = re.search(r'<h2>(.*?)</h2>', sec)
        en = re.search(r'<span class="en">(.*?)</span>', sec)
        if not h2:
            continue
        names = [re.sub('<[^>]+>', '', t).strip()
                 for t in re.findall(r'<h3>(.*?)</h3>', sec, re.S)]
        if len(names) < 3:
            continue
        out.append({'@type': 'ItemList',
                    'name': '%s - %s' % (h2.group(1), en.group(1) if en else ''),
                    'numberOfItems': len(names),
                    'itemListOrder': 'https://schema.org/ItemListOrderDescending',
                    'url': canonical + '#/' + m.group(1),
                    'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n}
                                        for i, n in enumerate(names[:20])]})
    return out


def page(canonical, title, desc, head, body, edition, top='', pub=None):
    ld = ('{"@context":"https://schema.org","@type":"CollectionPage","name":"%s",'
          '"description":"%s","url":"%s","inLanguage":"ko",'
          '%s'
          '"isPartOf":{"@type":"WebSite","name":"지금 이슈 있나요?","url":"%s"},'
          '"publisher":{"@type":"Organization","name":"피유글로벌"}}'
          % (title, desc, canonical,
             ('"datePublished":"%s","dateModified":"%s",' % (pub, pub)) if pub else '',
             SITE))
    lists = json.dumps({'@context': 'https://schema.org',
                        '@graph': itemlists(body, canonical)},
                       ensure_ascii=False, separators=(',', ':'))
    # 글로벌 · 국내는 같은 내용의 다른 판본이라 서로 대체 버전임을 알린다
    return ('<!doctype html>\n<html lang="ko">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta name="description" content="' + desc + '">\n'
            '<meta name="author" content="피유글로벌">\n'
            '<meta name="naver-site-verification" content="87fd336dbe76ffba397115874449d9c49ffa1bc2">\n'
            '<link rel="canonical" href="' + canonical + '">\n'
            '<meta property="og:type" content="website">\n'
            '<meta property="og:site_name" content="지금 이슈 있나요?">\n'
            '<meta property="og:title" content="' + title + '">\n'
            '<meta property="og:description" content="' + desc + '">\n'
            '<meta property="og:url" content="' + canonical + '">\n'
            '<meta property="og:image" content="' + SITE + '/og.png">\n'
            '<meta property="og:image:width" content="1200">\n'
            '<meta property="og:image:height" content="630">\n'
            '<meta property="og:locale" content="ko_KR">\n'
            '<meta name="twitter:card" content="summary_large_image">\n'
            '<meta name="twitter:title" content="' + title + '">\n'
            '<meta name="twitter:description" content="' + desc + '">\n'
            '<meta name="twitter:image" content="' + SITE + '/og.png">\n'
            '<link rel="icon" href="' + ICON + '">\n'
            '<script type="application/ld+json">' + ld + '</script>\n'
            '<script type="application/ld+json">' + lists + '</script>\n'
            + '<title>' + title + '</title>' + '\n' + '\n'.join(head[1:-1]) + '\n'
            + '<style>\n' + RESET + '\n</style>\n' + head[-1] + '\n'
            '</head>\n<body>\n' + NAV + '\n' + toggle(edition) + '\n' + top + body + '\n</body>\n</html>\n')


def banner(prefix):
    return ('<div style="background:#C8102E;color:#fff;padding:9px 16px;font:600 13px/1.4 '
            "'Noto Sans KR',sans-serif;text-align:center\">WEEK %d(%s) 보관본입니다. "
            '<a href="%s" style="color:#fff">이번 주 보기 →</a></div>\n' % (WEEK, PERIOD, prefix or '/'))


def write(path, text):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    io.open(path, 'w', encoding='utf-8').write(text)


EDITIONS = [('global', '', TITLE_G, DESC_G, HEAD_G, BODY_G)]
if HAS_KR:
    EDITIONS.append(('kr', 'kr/', TITLE_K, DESC_K, HEAD_K, BODY_K))

for ed, sub, title, desc, head, body in EDITIONS:
    base = SITE + '/' + sub

    # 제목은 브랜드명만 두면 아무도 검색하지 않는 말이 된다. 무엇을 다루는지 앞에 쓴다.
    lab = '해외' if ed == 'global' else '국내'
    write(os.path.join(HERE, sub, 'index.html'),
          page(base, '이번 주 %s 유행 총정리 — %s' % (lab, BRAND), desc, head, body, ed))
    wdir = os.path.join(HERE, sub, 'week', str(WEEK))
    write(os.path.join(wdir, 'index.html'),
          page('%sweek/%d/' % (base, WEEK),
               '%d년 %d주차 %s 유행 총정리 (%s) — %s' % (YEAR, WEEK, lab, PERIOD, BRAND),
               '%d년 %d주차(%s) 보관본. %s에서 그 주에 뜨던 것을 그대로 남긴 기록입니다.'
               % (YEAR, WEEK, PERIOD, '해외' if ed == 'global' else '국내'), head, body, ed,
               banner('/' + sub), TODAY))

# ---------- 아카이브 ----------
def weeks_of(sub):
    return sorted((int(os.path.basename(d)) for d in glob.glob(os.path.join(HERE, sub, 'week', '*'))
                   if os.path.basename(d).isdigit()), reverse=True)


blocks = []
for ed, sub, title, desc, head, body in EDITIONS:
    ws = weeks_of(sub)
    label = '글로벌' if ed == 'global' else '국내'
    rows = '\n'.join('<li><a href="/%sweek/%d/">WEEK %d</a><span>%s</span></li>'
                     % (sub, w, w, '이번 주' if w == WEEK else '보관본') for w in ws)
    blocks.append('<h2>%s</h2>\n<ul>\n%s\n</ul>' % (label, rows))

arch = ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>지난 주 보관함 — 지금 이슈 있나요?</title>\n'
        '<meta name="description" content="주차별 유행 스냅샷 보관함. 글로벌과 국내를 매주 월요일에 새로 뽑고 지난 주는 그대로 남깁니다.">\n'
        '<link rel="canonical" href="' + SITE + '/archive/">\n'
        '<meta property="og:title" content="지난 주 보관함 — 지금 이슈 있나요?">\n'
        '<meta property="og:image" content="' + SITE + '/og.png">\n'
        '<link rel="icon" href="' + ICON + '">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;800;900&display=swap">\n'
        '<style>body{margin:0;background:#F0EDE7;color:#2A211B;font-family:"Noto Sans KR",system-ui,sans-serif}'
        '.w{max-width:720px;margin:0 auto;padding:44px 20px}'
        'h1{font-size:34px;font-weight:900;letter-spacing:-.03em;margin:0 0 8px}'
        'h2{font-size:13px;font-weight:800;letter-spacing:.1em;color:#C8102E;margin:34px 0 4px}'
        'p.sub{color:#5C4F47;margin:0 0 10px;font-size:14.5px}'
        'ul{list-style:none;padding:0;margin:0}'
        'li{display:flex;align-items:baseline;gap:12px;padding:14px 4px;border-bottom:1px solid #DBD2C7}'
        'li a{font-size:18px;font-weight:800;color:#2A211B;text-decoration:none;letter-spacing:-.02em}'
        'li a:hover{color:#C8102E}li span{margin-left:auto;font-size:12px;color:#7E6F64}'
        'a.home{display:inline-block;margin-top:26px;font-size:13px;font-weight:700;color:#C8102E;text-decoration:none}'
        '@media(prefers-color-scheme:dark){body{background:#17120F;color:#F2EBE3}'
        'li{border-color:#382E27}li a{color:#F2EBE3}p.sub,li span{color:#B7A89C}}</style>\n'
        '</head>\n<body>' + NAV + '<div class="w">\n<h1>지난 주 보관함</h1>\n'
        '<p class="sub">매주 월요일에 새로 뽑고, 지난 주는 여기 그대로 남습니다.</p>\n'
        + '\n'.join(blocks) +
        '\n<a class="home" href="/">← 이번 주 보드로</a>\n</div></body>\n</html>\n')
write(os.path.join(HERE, 'archive', 'index.html'), arch)

# ---------- 개인정보처리방침 ----------
DOC_CSS = ('<style>body{margin:0;background:#F0EDE7;color:#2A211B;'
           'font-family:"Noto Sans KR",system-ui,sans-serif;line-height:1.75}'
           '.w{max-width:720px;margin:0 auto;padding:44px 20px 72px}'
           'h1{font-size:30px;font-weight:900;letter-spacing:-.03em;margin:0 0 6px}'
           'p.meta{color:#7E6F64;font-size:12.5px;margin:0 0 30px}'
           'h2{font-size:16.5px;font-weight:800;letter-spacing:-.02em;margin:32px 0 8px;'
           'padding-top:20px;border-top:1px solid #DBD2C7}'
           'p,li{font-size:14.5px;color:#372E28;margin:0 0 10px}'
           'b{font-weight:700}a{color:#1B3FD6}'
           'a.home{display:inline-block;margin-top:34px;font-size:13px;font-weight:700;'
           'color:#C8102E;text-decoration:none}'
           '@media(prefers-color-scheme:dark){body{background:#17120F;color:#F2EBE3}'
           'p,li{color:#E6DDD4}h2{border-color:#382E27}p.meta{color:#B7A89C}a{color:#8AA3FF}}'
           '</style>')

privacy = ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
           '<title>개인정보처리방침 — 지금 이슈 있나요?</title>\n'
           '<meta name="description" content="지금 이슈 있나요?의 개인정보처리방침. 수집 항목, 쿠키, 제휴 링크, 외부 서비스 안내.">\n'
           '<link rel="canonical" href="' + SITE + '/privacy/">\n'
           '<link rel="icon" href="' + ICON + '">\n'
           '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;800;900&display=swap">\n'
           + DOC_CSS + '\n</head>\n<body>' + NAV + '<div class="w">\n'
           '<h1>개인정보처리방침</h1>\n'
           '<p class="meta">사이트 · 지금 이슈 있나요? &nbsp;|&nbsp; 운영 · 피유글로벌 &nbsp;|&nbsp; 시행일 · 2026년 9월 5일</p>\n'
           '<h2>1. 수집하는 개인정보</h2>\n'
           '<p>이 사이트는 <b>어떠한 개인정보도 직접 수집하지 않습니다.</b> 회원가입, 로그인, 댓글, 문의 양식 등 '
           '이용자가 정보를 입력하는 기능 자체가 없습니다.</p>\n'
           '<h2>2. 쿠키</h2>\n'
           '<p>이 사이트는 자체적으로 쿠키를 설치하거나 이용자의 브라우저에 정보를 저장하지 않습니다. '
           '다만 GitHub Pages로 제공되고 웹폰트를 Google Fonts에서 불러오므로, 그 과정에서 해당 사업자의 서버에 '
           '접속 기록이 남을 수 있으며 이는 각 사업자의 정책을 따릅니다.</p>\n'
           '<h2>3. 광고</h2>\n'
           '<p><b>현재 이 사이트에는 광고가 게재되어 있지 않습니다.</b> 향후 Google 애드센스 등을 도입할 경우 '
           '제3자 광고 공급업체가 쿠키를 사용할 수 있으며, '
           '<a href="https://adssettings.google.com/">Google 광고 설정</a>과 '
           '<a href="https://www.aboutads.info/choices/">aboutads.info</a>에서 해제할 수 있습니다. '
           '도입 시점에 본 방침을 갱신합니다.</p>\n'
           '<h2>4. 제휴 링크</h2>\n'
           '<p>일부 항목에는 쿠팡 파트너스 링크가 포함되어 있으며, 이를 통해 구매가 발생하면 운영자가 일정액의 '
           '수수료를 받습니다. <b>구매자가 추가로 부담하는 금액은 없습니다.</b> 제휴 여부는 페이지 상단에 상시 고지합니다.</p>\n'
           '<h2>5. 외부 링크</h2>\n'
           '<p>인스타그램, 유튜브, 스팀, 스포티파이 등 외부 서비스로 이동하는 링크를 제공합니다. '
           '이동한 사이트의 개인정보 처리에는 이 방침이 적용되지 않습니다.</p>\n'
           '<h2>6. 콘텐츠와 저작권</h2>\n'
           '<p>인용한 수치와 순위의 저작권은 각 매체에 있으며 항목마다 출처를 표기합니다. 이미지는 상업적 이용이 '
           '허용된 라이선스 또는 각 플랫폼이 제공하는 공식 이미지만 사용합니다. '
           '각 항목의 <b>「왜?」 해설과 주간 요약은 이 사이트가 직접 작성한 것</b>입니다.</p>\n'
           '<h2>7. 만 14세 미만 아동</h2>\n'
           '<p>아동을 대상으로 하지 않으며, 개인정보를 수집하지 않으므로 아동의 정보 역시 수집하지 않습니다.</p>\n'
           '<h2>8. 문의</h2>\n'
           '<p>운영 · <b>피유글로벌</b> &nbsp;|&nbsp; 문의 · <b>contact@issueitnow.com</b></p>\n'
           '<h2>9. 방침 변경</h2>\n'
           '<p>변경 시 이 페이지에 갱신하여 게시하며 시행일을 함께 표기합니다.</p>\n'
           '<a class="home" href="/">← 이번 주 보드로</a>\n</div></body>\n</html>\n')
write(os.path.join(HERE, 'privacy', 'index.html'), privacy)

# ---------- sitemap · robots ----------
today = TODAY
urls = [(SITE + '/', '1.0', 'weekly'), (SITE + '/archive/', '0.6', 'weekly'),
        (SITE + '/privacy/', '0.3', 'yearly')]
if HAS_KR:
    urls.insert(1, (SITE + '/kr/', '1.0', 'weekly'))
for ed, sub, *_ in EDITIONS:
    urls += [('%s/%sweek/%d/' % (SITE, sub, w), '0.5', 'never') for w in weeks_of(sub)]
write(os.path.join(HERE, 'sitemap.xml'),
      '<?xml version="1.0" encoding="UTF-8"?>\n'
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + '\n'.join('  <url><loc>%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq>'
                  '<priority>%s</priority></url>' % (u, today, c, pr) for u, pr, c in urls)
      + '\n</urlset>\n')
# 답변형 AI는 대부분 검색 인덱스를 거쳐 출처를 고른다. 막을 이유가 없으니 이름으로 허용해 둔다.
AI_BOTS = ('GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-User',
           'Claude-SearchBot', 'PerplexityBot', 'Perplexity-User', 'Google-Extended',
           'Applebot-Extended', 'CCBot', 'Bingbot', 'Amazonbot', 'meta-externalagent')
write(os.path.join(HERE, 'robots.txt'),
      'User-agent: *\nAllow: /\n\n'
      + ''.join('User-agent: %s\nAllow: /\n\n' % b for b in AI_BOTS)
      + 'Sitemap: %s/sitemap.xml\n' % SITE)

# ---------- OG 이미지 ----------
try:
    from PIL import Image, ImageDraw, ImageFont

    def F(sz, bold=True):
        f = r'C:\Windows\Fonts\malgunbd.ttf' if bold else r'C:\Windows\Fonts\malgun.ttf'
        return ImageFont.truetype(f, sz) if os.path.exists(f) else ImageFont.load_default()

    im = Image.new('RGB', (1200, 630), '#F0EDE7')
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1200, 10], fill='#C8102E')
    big = F(104)
    d.text((80, 110), '지금', font=big, fill='#2A211B')
    d.text((80, 240), '이슈', font=big, fill='#C8102E')
    d.text((80 + d.textlength('이슈', font=big) + 24, 240), '있나요?', font=big, fill='#2A211B')
    d.text((84, 400), '매주 월요일, 해외와 국내에서 지금 뜨는 것들', font=F(34, False), fill='#5C4F47')
    d.text((84, 458), 'WEEK %d  ·  %s' % (WEEK, PERIOD), font=F(30), fill='#C8102E')
    d.text((84, 542), '글로벌 · 국내  |  음악 · 영화 · 게임 · 패션 · 음식 · 뷰티 · 밈 · 여행',
           font=F(23, False), fill='#7E6F64')
    im.save(os.path.join(HERE, 'og.png'))
    og = 'og.png'
except Exception as e:
    og = 'og 생략(%s)' % e

print('완료 · 판본 %d개(%s) · week %d · sitemap %d URL · %s'
      % (len(EDITIONS), ', '.join(e[0] for e in EDITIONS), WEEK, len(urls), og))
