# -*- coding: utf-8 -*-
"""board.html(원본) -> index.html + 주차 아카이브 + 사이트맵 + OG 이미지"""
import io, os, re, glob, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://eorua7405-ship-it.github.io'
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
       '<a href="/archive/" style="color:#F0EDE7;text-decoration:none">지난 주 보관함</a></div>\n')


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

# ---------- 4) sitemap · robots ----------
today = datetime.date.today().isoformat()
urls = [(SITE + '/', '1.0', 'weekly'), (SITE + '/archive/', '0.6', 'weekly')]
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

print('index + week/%d/ + archive/ + sitemap(%d URL) + robots + %s' % (WEEK, len(urls), og))
