# -*- coding: utf-8 -*-
"""board.html(원본) -> index.html + 주차 아카이브 + 사이트맵 + OG 이미지"""
import io, os, re, glob, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://issueitnow.com'
src = io.open(os.path.join(HERE, 'board.html'), encoding='utf-8').read()

TITLE = re.search(r'<title>(.*?)</title>', src).group(1)
WEEK = int(re.search(r'<b>WEEK (\d+)</b>', src).group(1))
PERIOD = re.search(r'<span>집계 기간</span><b>(.*?)</b>', src).group(1).strip()
DESC = ('매주 월요일 갱신되는 해외 유행 보드. 인스타 릴스·유튜브·음악·영화·게임·패션·음식·뷰티·밈·여행 '
        '트렌드를 시작일과 트래픽 수치, 그리고 왜 지금 뜨는지에 대한 해석과 함께 정리합니다.')

head = []
for pat in (r'<title>.*?</title>', r'<link rel="preconnect"[^>]*>',
            r'<link rel="stylesheet"[^>]*>', r'<style>.*?</style>'):
    head += [m.group(0) for m in re.finditer(pat, src, re.S)]
body = src
for part in head:
    body = body.replace(part, '', 1)
body = body.strip()

RESET = """  :root{color-scheme:light dark}
  html{-webkit-text-size-adjust:100%}
  body{margin:0;font:14px/1.5 system-ui,-apple-system,sans-serif}
  img{max-width:100%}
  [hidden]{display:none!important}"""

ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'"
        "%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%94%A5%3C/text%3E%3C/svg%3E")

NAV = ('<div style="background:#2A211B;color:#F0EDE7;padding:7px 16px;font:600 12px/1.4 '
       '\'Noto Sans KR\',sans-serif;text-align:center">'
       '<a href="/" style="color:#F0EDE7;text-decoration:none">이번 주</a>'
       '<span style="opacity:.4;margin:0 10px">·</span>'
       '<a href="/archive/" style="color:#F0EDE7;text-decoration:none">지난 주 보관함</a>'
       '<span style="opacity:.4;margin:0 10px">·</span>'
       '<a href="/privacy/" style="color:#F0EDE7;text-decoration:none">개인정보처리방침</a></div>\n')


def page(canonical, title, desc, top=''):
    ld = ('{"@context":"https://schema.org","@type":"CollectionPage","name":"%s",'
          '"description":"%s","url":"%s","inLanguage":"ko",'
          '"isPartOf":{"@type":"WebSite","name":"지금 이슈 있나요?","url":"%s"},'
          '"publisher":{"@type":"Organization","name":"피유글로벌"}}'
          % (title, desc, canonical, SITE))
    return ('<!doctype html>\n<html lang="ko">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta name="description" content="' + desc + '">\n'
            '<meta name="author" content="피유글로벌">\n'
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
            + head[0] + '\n' + '\n'.join(head[1:-1]) + '\n'
            + '<style>\n' + RESET + '\n</style>\n' + head[-1] + '\n'
            '</head>\n<body>\n' + NAV + top + body + '\n</body>\n</html>\n')


# ---------- 1) 이번 주 ----------
io.open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8').write(page(SITE + '/', TITLE, DESC))

# ---------- 2) 주차 스냅샷 ----------
wdir = os.path.join(HERE, 'week', str(WEEK))
if not os.path.isdir(wdir):
    os.makedirs(wdir)
banner = ('<div style="background:#C8102E;color:#fff;padding:9px 16px;font:600 13px/1.4 '
          '\'Noto Sans KR\',sans-serif;text-align:center">WEEK %d(%s) 보관본입니다. '
          '<a href="/" style="color:#fff">이번 주 보기 →</a></div>\n' % (WEEK, PERIOD))
io.open(os.path.join(wdir, 'index.html'), 'w', encoding='utf-8').write(
    page('%s/week/%d/' % (SITE, WEEK), '%s — WEEK %d' % (TITLE, WEEK),
         'WEEK %d(%s) 해외 유행 스냅샷. %s' % (WEEK, PERIOD, DESC), banner))

# ---------- 3) 아카이브 ----------
weeks = sorted((int(os.path.basename(d)) for d in glob.glob(os.path.join(HERE, 'week', '*'))
                if os.path.basename(d).isdigit()), reverse=True)
rows = '\n'.join('<li><a href="/week/%d/">WEEK %d</a><span>%s</span></li>'
                 % (w, w, '이번 주' if w == WEEK else '보관본') for w in weeks)
arch = ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>지난 주 보관함 — 지금 이슈 있나요?</title>\n'
        '<meta name="description" content="주차별 해외 유행 스냅샷 보관함. 매주 월요일에 새로 뽑고 지난 주는 그대로 남깁니다.">\n'
        '<link rel="canonical" href="' + SITE + '/archive/">\n'
        '<meta property="og:title" content="지난 주 보관함 — 지금 이슈 있나요?">\n'
        '<meta property="og:image" content="' + SITE + '/og.png">\n'
        '<link rel="icon" href="' + ICON + '">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;800;900&display=swap">\n'
        '<style>body{margin:0;background:#F0EDE7;color:#2A211B;font-family:"Noto Sans KR",system-ui,sans-serif}'
        '.w{max-width:720px;margin:0 auto;padding:48px 20px}'
        'h1{font-size:34px;font-weight:900;letter-spacing:-.03em;margin:0 0 8px}'
        'p.sub{color:#5C4F47;margin:0 0 28px;font-size:14.5px}'
        'ul{list-style:none;padding:0;margin:0}'
        'li{display:flex;align-items:baseline;gap:12px;padding:15px 4px;border-bottom:1px solid #DBD2C7}'
        'li a{font-size:19px;font-weight:800;color:#2A211B;text-decoration:none;letter-spacing:-.02em}'
        'li a:hover{color:#C8102E}li span{margin-left:auto;font-size:12px;color:#7E6F64}'
        'a.home{display:inline-block;margin-top:26px;font-size:13px;font-weight:700;color:#C8102E;text-decoration:none}'
        '@media(prefers-color-scheme:dark){body{background:#17120F;color:#F2EBE3}'
        'li{border-color:#382E27}li a{color:#F2EBE3}p.sub,li span{color:#B7A89C}}</style>\n'
        '</head>\n<body><div class="w">\n<h1>지난 주 보관함</h1>\n'
        '<p class="sub">매주 월요일에 새로 뽑고, 지난 주는 여기 그대로 남습니다.</p>\n'
        '<ul>\n' + rows + '\n</ul>\n<a class="home" href="/">← 이번 주 보드로</a>\n'
        '</div></body>\n</html>\n')
adir = os.path.join(HERE, 'archive')
if not os.path.isdir(adir):
    os.makedirs(adir)
io.open(os.path.join(adir, 'index.html'), 'w', encoding='utf-8').write(arch)

# ---------- 3-1) 개인정보처리방침 ----------
DOC_CSS = ('<style>body{margin:0;background:#F0EDE7;color:#2A211B;'
           'font-family:"Noto Sans KR",system-ui,sans-serif;line-height:1.75}'
           '.w{max-width:720px;margin:0 auto;padding:44px 20px 72px}'
           'h1{font-size:30px;font-weight:900;letter-spacing:-.03em;margin:0 0 6px}'
           'p.meta{color:#7E6F64;font-size:12.5px;margin:0 0 30px}'
           'h2{font-size:16.5px;font-weight:800;letter-spacing:-.02em;margin:32px 0 8px;'
           'padding-top:20px;border-top:1px solid #DBD2C7}'
           'p,li{font-size:14.5px;color:#372E28;margin:0 0 10px}'
           'ul{padding-left:18px;margin:0 0 10px}'
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
           '<meta name="robots" content="index,follow">\n'
           '<link rel="icon" href="' + ICON + '">\n'
           '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;800;900&display=swap">\n'
           + DOC_CSS + '\n</head>\n<body>' + NAV + '<div class="w">\n'
           '<h1>개인정보처리방침</h1>\n'
           '<p class="meta">사이트 · 지금 이슈 있나요? &nbsp;|&nbsp; 운영 · 피유글로벌 &nbsp;|&nbsp; 시행일 · 2026년 9월 5일</p>\n'

           '<h2>1. 수집하는 개인정보</h2>\n'
           '<p>이 사이트는 <b>어떠한 개인정보도 직접 수집하지 않습니다.</b> 회원가입, 로그인, 댓글, 문의 양식 등 '
           '이용자가 정보를 입력하는 기능 자체가 없습니다. 이름, 이메일, 전화번호, 결제정보를 요구하지 않습니다.</p>\n'

           '<h2>2. 쿠키</h2>\n'
           '<p>이 사이트는 자체적으로 쿠키를 설치하거나 이용자의 브라우저에 정보를 저장하지 않습니다. '
           '접속 기록을 별도로 보관하지도 않습니다.</p>\n'
           '<p>다만 이 사이트는 GitHub Pages를 통해 제공되며, 웹폰트는 Google Fonts에서 불러옵니다. '
           '이 과정에서 해당 사업자의 서버에 접속 기록(IP 주소 등)이 남을 수 있으며, 이는 각 사업자의 정책을 따릅니다.</p>\n'

           '<h2>3. 광고</h2>\n'
           '<p><b>현재 이 사이트에는 광고가 게재되어 있지 않습니다.</b></p>\n'
           '<p>향후 Google 애드센스 등 광고를 도입할 경우, Google을 포함한 제3자 광고 공급업체가 쿠키를 사용하여 '
           '이용자의 이전 방문 기록을 바탕으로 광고를 게재할 수 있습니다. 이용자는 '
           '<a href="https://adssettings.google.com/">Google 광고 설정</a>에서 맞춤 광고를 해제할 수 있고, '
           '<a href="https://www.aboutads.info/choices/">aboutads.info</a>에서 제3자 공급업체의 쿠키를 일괄 거부할 수 있습니다. '
           '광고를 실제로 도입하는 시점에 본 방침을 갱신합니다.</p>\n'

           '<h2>4. 제휴 링크</h2>\n'
           '<p>이 사이트의 일부 항목에는 쿠팡 파트너스 링크가 포함되어 있으며, 이를 통해 구매가 발생하면 '
           '운영자가 일정액의 수수료를 받습니다. <b>구매자가 추가로 부담하는 금액은 없습니다.</b></p>\n'
           '<p>해당 링크를 누르면 쿠팡으로 이동하며, 이후의 개인정보 처리는 쿠팡의 방침을 따릅니다. '
           '제휴 여부는 페이지 상단에 상시 고지하고 있습니다.</p>\n'

           '<h2>5. 외부 링크</h2>\n'
           '<p>이 사이트는 인스타그램, 유튜브, 스팀, 스포티파이, 트립어드바이저 등 외부 서비스로 이동하는 링크를 제공합니다. '
           '이동한 사이트에서의 개인정보 처리에 대해서는 이 방침이 적용되지 않으며, 각 서비스의 정책을 확인하시기 바랍니다.</p>\n'

           '<h2>6. 콘텐츠와 저작권</h2>\n'
           '<p>본문에 인용한 수치와 순위의 저작권은 각 매체에 있으며, 항목마다 출처를 표기하고 원문으로 연결합니다. '
           '이미지는 상업적 이용이 허용된 라이선스(CC0·퍼블릭도메인·CC BY) 또는 각 플랫폼이 제공하는 공식 이미지만 사용하며, '
           '저작자 표기가 필요한 경우 이미지에 함께 표시합니다. '
           '각 항목의 <b>「왜?」 해설과 주간 요약은 이 사이트가 직접 작성한 것</b>입니다.</p>\n'

           '<h2>7. 만 14세 미만 아동</h2>\n'
           '<p>이 사이트는 아동을 대상으로 하지 않으며, 개인정보를 수집하지 않으므로 아동의 정보 역시 수집하지 않습니다.</p>\n'

           '<h2>8. 문의</h2>\n'
           '<p>본 방침에 대한 문의, 저작권 관련 요청, 정정 요구는 운영자에게 연락하실 수 있습니다.<br>'
           '운영 · <b>피유글로벌</b> &nbsp;|&nbsp; 문의 · <b>contact@issueitnow.com</b></p>\n'

           '<h2>9. 방침 변경</h2>\n'
           '<p>본 방침이 변경되는 경우 이 페이지에 갱신하여 게시하며, 시행일을 함께 표기합니다.</p>\n'

           '<a class="home" href="/">← 이번 주 보드로</a>\n'
           '</div></body>\n</html>\n')
pdir = os.path.join(HERE, 'privacy')
if not os.path.isdir(pdir):
    os.makedirs(pdir)
io.open(os.path.join(pdir, 'index.html'), 'w', encoding='utf-8').write(privacy)

# ---------- 4) sitemap · robots ----------
today = datetime.date.today().isoformat()
urls = [(SITE + '/', '1.0', 'weekly'), (SITE + '/archive/', '0.6', 'weekly'),
        (SITE + '/privacy/', '0.3', 'yearly')]
urls += [('%s/week/%d/' % (SITE, w), '0.5', 'never') for w in weeks]
io.open(os.path.join(HERE, 'sitemap.xml'), 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + '\n'.join('  <url><loc>%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq>'
                '<priority>%s</priority></url>' % (u, today, c, pr) for u, pr, c in urls)
    + '\n</urlset>\n')
io.open(os.path.join(HERE, 'robots.txt'), 'w', encoding='utf-8').write(
    'User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % SITE)

# ---------- 5) OG 이미지 ----------
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
    d.text((84, 400), '매주 월요일, 해외에서 지금 뜨는 것들', font=F(34, False), fill='#5C4F47')
    d.text((84, 458), 'WEEK %d  ·  %s' % (WEEK, PERIOD), font=F(30), fill='#C8102E')
    d.text((84, 542), '인스타 · 유튜브 · 음악 · 영화 · 게임 · 패션 · 음식 · 뷰티 · 밈 · 여행',
           font=F(23, False), fill='#7E6F64')
    im.save(os.path.join(HERE, 'og.png'))
    og = 'og.png'
except Exception as e:
    og = 'og 생략(%s)' % e

print('index + week/%d/ + archive/ + privacy/ + sitemap(%d URL) + robots + %s' % (WEEK, len(urls), og))
