# -*- coding: utf-8 -*-
"""board.html(글로벌) · board-kr.html(국내) -> 사이트 전체 생성

만들어지는 것: /, /kr/, /week/<주차>/, /kr/week/<주차>/, /archive/, /privacy/,
sitemap.xml, robots.txt, og.png
"""
import io, os, re, glob, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://issueitnow.com'
BRAND = '지금 이슈 있나요?'
GA = 'G-YSVK0BXCWE'
GA_TAG = ('<script async src="https://www.googletagmanager.com/gtag/js?id=' + GA + '"></script>'
          '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag(' + repr('js') + ',new Date());gtag(' + repr('config') + ',' + repr(GA) + ')</script>')

DESC_G = ('매주 월요일 갱신되는 해외 유행 보드. '
          '릴스·유튜브·음악·영화·게임·패션·음식·뷰티·밈·여행을 수치와 해석으로 정리합니다.')
DESC_E = ('What Korea is into right now, rebuilt every Monday. Music, reels audio, box office, games, beauty and slang, with the numbers behind each.')
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


NAV_EN = ('<div style="background:#2A211B;color:#F0EDE7;padding:7px 16px;font:600 12px/1.4 '
          "'Noto Sans KR',sans-serif;text-align:center\">"
          '<a href="/en/" style="color:#F0EDE7;text-decoration:none">This week</a>'
          '<span style="opacity:.4;margin:0 10px">·</span>'
          '<a href="/archive/" style="color:#F0EDE7;text-decoration:none">Past weeks</a>'
          '<span style="opacity:.4;margin:0 10px">·</span>'
          '<a href="/privacy/" style="color:#F0EDE7;text-decoration:none">Privacy</a></div>')


def toggle(edition):
    def btn(label, href, on):
        st = 'background:#C8102E;color:#fff' if on else 'background:transparent;color:#7E6F64'
        return ('<a href="%s" style="%s;display:inline-block;padding:7px 20px;border-radius:999px;'
                "font:700 12.5px/1 'Noto Sans KR',sans-serif;text-decoration:none\">%s</a>"
                % (href, st, label))
    return ('<div style="background:#F0EDE7;border-bottom:1px solid #DBD2C7;padding:10px 16px;text-align:center">'
            '<span style="display:inline-flex;gap:4px;background:#fff;border:1px solid #DBD2C7;'
            'border-radius:999px;padding:3px">' + btn('Global' if edition == 'en' else '글로벌', '/', edition == 'global')
            + btn('Korea' if edition == 'en' else '국내', '/kr/', edition == 'kr')
            + btn('EN', '/en/', edition == 'en') + '</span></div>')


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

HAS_EN = os.path.exists(os.path.join(HERE, 'board-en.html'))
if HAS_EN:
    SRC_E, HEAD_E, BODY_E = load('board-en.html')


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


def page(canonical, title, desc, head, body, edition, top='', pub=None, alt_path=''):
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
            '<meta name="author" content="' + ('PUGlobal' if edition == 'en' else '피유글로벌') + '">\n'
            '<meta name="naver-site-verification" content="87fd336dbe76ffba397115874449d9c49ffa1bc2">\n'
            '<link rel="canonical" href="' + canonical + '">\n'
            + (('<link rel="alternate" hreflang="ko" href="%s/kr/%s">' + chr(10) +
                '<link rel="alternate" hreflang="en" href="%s/en/%s">' + chr(10) +
                '<link rel="alternate" hreflang="x-default" href="%s/kr/%s">' + chr(10))
               % (SITE, alt_path, SITE, alt_path, SITE, alt_path)
               if edition in ('kr', 'en') and HAS_EN else '') +
            '<meta property="og:type" content="website">\n'
            '<meta property="og:site_name" content="' + ('Trending in Korea' if edition == 'en' else '지금 이슈 있나요?') + '">\n'
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
            '<link rel="alternate" type="application/rss+xml" title="지금 이슈 있나요?" href="' + SITE + '/rss.xml">\n'
            + GA_TAG + '\n'
            '<script type="application/ld+json">' + ld + '</script>\n'
            '<script type="application/ld+json">' + lists + '</script>\n'
            + '<title>' + title + '</title>' + '\n' + '\n'.join(head[1:-1]) + '\n'
            + '<style>\n' + RESET + '\n</style>\n' + head[-1] + '\n'
            '</head>\n<body>\n' + (NAV_EN if edition == 'en' else NAV) + '\n' + toggle(edition) + '\n' + top + body + '\n</body>\n</html>\n')


AFF_NOTE_KO = ('<p style="max-width:820px;margin:26px auto 0;padding:10px 13px;'
               'border:1px dashed #DBD2C7;border-radius:8px;font:500 12px/1.6 '
               "'Noto Sans KR',sans-serif;color:#7E6F64\">"
               '이 페이지는 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</p>')
AFF_NOTE_EN = ('<p style="max-width:820px;margin:26px auto 0;padding:10px 13px;'
               'border:1px dashed #DBD2C7;border-radius:8px;font:500 12px/1.6 '
               "'Noto Sans KR',sans-serif;color:#7E6F64\">"
               'Some product links are Coupang Partners affiliate links. '
               'We may earn a commission at no extra cost to you.</p>')

SECTION_URLS = []

SEC_CSS = """
  :root{--bg:#F0EDE7;--card:#fff;--ink:#2A211B;--dim:#7E6F64;--line:#DBD2C7;--red:#C8102E}
  :root:not([data-theme="light"]){}
  @media (prefers-color-scheme:dark){
    :root{--bg:#1A1512;--card:#241D18;--ink:#F0EDE7;--dim:#A9998C;--line:#3A2F27}}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
       font:15px/1.65 'Noto Sans KR',system-ui,sans-serif}
  .wrap{max-width:820px;margin:0 auto;padding:0 18px 64px}
  .top{background:#2A211B;color:#F0EDE7;padding:9px 16px;font:600 12px/1.4 inherit;text-align:center}
  .top a{color:#F0EDE7;text-decoration:none}
  h1{font-size:26px;line-height:1.3;margin:26px 0 6px}
  .sub{color:var(--dim);font-size:13px;margin:0 0 26px}
  h2.grp{font-size:14px;letter-spacing:.04em;color:var(--red);
         margin:34px 0 12px;padding-bottom:7px;border-bottom:1px solid var(--line)}
  ol{list-style:none;margin:0;padding:0}
  li{display:grid;grid-template-columns:38px minmax(0,1fr);gap:12px;
     background:var(--card);border:1px solid var(--line);border-radius:10px;
     padding:13px 15px;margin-bottom:9px}
  li.noimg{grid-template-columns:minmax(0,1fr)}
  .num{font:800 14px/1.4 inherit;color:var(--red)}
  .thumb{width:38px;height:38px;border-radius:7px;object-fit:cover;background:var(--line)}
  h3{font-size:15.5px;margin:0 0 4px}
  h3 a{color:inherit;text-decoration:none;border-bottom:1px solid var(--line)}
  p{margin:0 0 7px;font-size:13.5px;color:var(--ink)}
  .facts{font-size:12px;color:var(--dim)}
  .facts b{color:var(--ink);font-weight:600}
  .src{font-size:12px;color:var(--dim);margin-top:30px}
  .src a{color:var(--dim)}
  .more{margin-top:34px;font-size:13px;line-height:2}
  .more a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line);margin-right:4px}
  .back{display:inline-block;margin:24px 0 0;font-weight:700;color:var(--red);text-decoration:none}
"""


def esc(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


def parse_section(sec):
    """섹션 HTML -> (그룹명, 항목들). 항목은 화면에 보이던 값 그대로 쓴다."""
    groups, order = {}, []
    for blk in re.findall(r'<li class="item"[^>]*>.*?</li>', sec, re.S):
        tag = blk.split('>', 1)[0]

        def at(k):
            m = re.search(r'data-%s="([^"]*)"' % k, tag)
            return m.group(1) if m else ''
        h3 = re.search(r'<h3>(.*?)</h3>', blk, re.S)
        p = re.search(r'<p>(.*?)</p>', blk, re.S)
        g = at('group') or '항목'
        if g not in groups:
            groups[g] = []
            order.append(g)
        groups[g].append({
            'name': re.sub('<[^>]+>', '', h3.group(1)).strip() if h3 else '',
            'desc': re.sub('<[^>]+>', '', p.group(1)).strip() if p else at('sum'),
            'since': at('since'), 'traffic': at('traffic'),
            'link': at('link'), 'img': at('img'), 'credit': at('credit')})
    return [(g, groups[g]) for g in order]


def section_pages(body, sub, lab, head, siblings=None):
    """파트마다 검색엔진이 읽을 수 있는 실제 주소의 페이지를 뽑는다."""
    made = []
    for m in re.finditer(r'<section class="cat" data-cat="(\w+)".*?</section>', body, re.S):
        cat, sec = m.group(1), m.group(0)
        h2 = re.search(r'<h2>(.*?)</h2>', sec)
        en = re.search(r'<span class="en">(.*?)</span>', sec)
        if not h2:
            continue
        part = h2.group(1)
        ko = ''
        if en and ' · ' in en.group(1):
            ko = en.group(1).split(' · ', 1)[1]
        topic = part if (not ko or ko in part or part in ko) else '%s %s' % (part, ko)
        groups = parse_section(sec)
        total = sum(len(v) for _, v in groups)
        if total < 3:
            continue

        url = '%s/%s%s/' % (SITE, sub, cat)
        if sub == 'en/':
            title = '%s in Korea — %d week %d' % (topic, YEAR, WEEK)
            desc = ('%s in Korea this week: %d entries with start dates and traffic figures.'
                    % (topic, total))
        else:
            title = '%s %s %d년 %d주차 — %s' % (lab, topic, YEAR, WEEK, BRAND)
            desc = '%s %s. %d개를 시작일과 트래픽 수치로 정리했습니다.' % (lab, topic, total)

        rows = []
        for g, items in groups:
            rows.append('<h2 class="grp">%s</h2>' % esc(g))
            rows.append('<ol>')
            for i, it in enumerate(items):
                nm = esc(it['name'])
                nm = ('<a href="%s" rel="nofollow noopener" target="_blank">%s</a>'
                      % (esc(it['link']), nm)) if it['link'] else nm
                facts = ' · '.join(
                    filter(None, [(('Started <b>%s</b>' if sub == 'en/' else '시작 <b>%s</b>') % esc(it['since'])) if it['since'] else '',
                                  (('Traffic <b>%s</b>' if sub == 'en/' else '트래픽 <b>%s</b>') % esc(it['traffic'])) if it['traffic'] else '']))
                thumb = ('<img class="thumb" src="%s" alt="%s" loading="lazy">'
                         % (esc(it['img']), esc(it['name']))) if it['img'] else ''
                rows.append('<li class="%s">%s<div><h3>%s</h3><p>%s</p>'
                            '<div class="facts">%s</div></div></li>'
                            % ('' if thumb else 'noimg', thumb or '<span class="num">%02d</span>' % (i + 1),
                               nm, esc(it['desc']), facts))
            rows.append('</ol>')

        sib = ''
        if siblings:
            sib = ('<div class="more">' + ('Other parts · ' if sub == 'en/' else '다른 파트 · ') +
                   ' · '.join('<a href="/%s%s/">%s</a>' % (sub, c, t)
                              for c, t in siblings if c != cat) + '</div>')
        src = re.search(r'<p class="src">(.*?)</p>', sec, re.S)
        ld = json.dumps({'@context': 'https://schema.org', '@type': 'ItemList',
                         'name': topic, 'numberOfItems': total, 'url': url,
                         'itemListElement': [
                             {'@type': 'ListItem', 'position': i + 1, 'name': it['name']}
                             for i, it in enumerate(
                                 [x for _, v in groups for x in v][:30])]},
                        ensure_ascii=False, separators=(',', ':'))

        html = ('<!doctype html>\n<html lang="ko">\n<head>\n'
                '<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                '<title>' + esc(title) + '</title>\n'
                '<meta name="description" content="' + esc(desc) + '">\n'
                '<link rel="canonical" href="' + url + '">\n'
                '<meta property="og:type" content="article">\n'
                '<meta property="og:title" content="' + esc(title) + '">\n'
                '<meta property="og:description" content="' + esc(desc) + '">\n'
                '<meta property="og:url" content="' + url + '">\n'
                '<meta property="og:image" content="' + SITE + '/og.png">\n'
                '<meta property="og:locale" content="ko_KR">\n'
                '<link rel="icon" href="' + ICON + '">\n'
                + GA_TAG + '\n'
                '<script type="application/ld+json">' + ld + '</script>\n'
                '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
                '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
                'family=Noto+Sans+KR:wght@400;600;700;800&display=swap">\n'
                '<style>' + SEC_CSS + '</style>\n</head>\n<body>\n'
                '<div class="top"><a href="/' + sub + '">←' + (' Back to this week' if sub == 'en/' else lab + ' 이번 주 전체 보기') + '</a></div>\n'
                '<div class="wrap">\n'
                '<h1>' + esc(topic) + '</h1>\n'
                '<p class="sub">' + lab + ' · ' + (('%d week %d (' % (YEAR, WEEK)) if sub == 'en/'
                   else str(YEAR) + '년 ' + str(WEEK) + '주차 (')
                + PERIOD + ') · ' + (str(total) + ' entries' if sub == 'en/' else '총 ' + str(total) + '개') + '</p>\n'
                + '\n'.join(rows) +
                '\n<p class="src">' + (src.group(1) if src else '') + '</p>\n'
                + sib + '\n'
                + (AFF_NOTE_EN if sub == 'en/' else AFF_NOTE_KO) + '\n'
                '<a class="back" href="/' + sub + '">←' + (' Back to this week' if sub == 'en/' else lab + ' 이번 주 전체 보기') + '</a>\n'
                '</div>\n</body>\n</html>\n').replace('\n', chr(10))

        write(os.path.join(HERE, sub, cat, 'index.html'), html)
        SECTION_URLS.append(url)
        made.append((cat, topic))
    return made



def inject_part_links(body, sub, made):
    """각 파트 끝의 출처 줄 위에 그 파트 전용 페이지로 가는 실제 링크를 넣는다."""
    for cat, topic in made:
        pat = '<section class="cat" data-cat="%s"' % cat
        i = body.find(pat)
        if i < 0:
            continue
        j = body.find('<p class="src">', i)
        if j < 0:
            continue
        a = ('<p style="margin:14px 0 0;font-size:12.5px"><a href="/%s%s/" '
             'style="color:#C8102E;font-weight:700;text-decoration:none">'
             '%s</a></p>' % (sub, cat,
                             (topic + ' &mdash; see all &rarr;') if sub == 'en/'
                             else topic + ' 전체 목록 보기 &rarr;'))
        body = body[:j] + a + body[j:]
    return body



def order_by_affiliate(body):
    """파트너스 링크가 든 그룹을 파트 앞쪽으로. 그룹 안 차례는 그대로 둔다."""
    def one(m):
        head, items_html, tail = m.group(1), m.group(2), m.group(3)
        blocks = re.findall(r'\s*<li class="item".*?</li>', items_html, re.S)
        if not blocks:
            return m.group(0)
        order, groups = [], {}
        for b in blocks:
            g = re.search(r'data-group="([^"]*)"', b)
            g = g.group(1) if g else ''
            if g not in groups:
                groups[g] = []
                order.append(g)
            groups[g].append(b)
        # 링크가 많이 달린 그룹부터. 같으면 원래 차례를 지킨다.
        def score(g):
            return -sum('data-aff=' in b for b in groups[g])
        ranked = sorted(order, key=lambda g: (score(g), order.index(g)))
        # 순서가 그대로여도 다시 조립한다 — 원본에서 같은 그룹이 흩어져 있으면
        # 여기서 한데 모여야 "관련된 것끼리" 읽힌다.
        out = ''.join(''.join(groups[g]) for g in ranked)
        return head + out + tail

    return re.sub(r'(<section class="cat"[^>]*>.*?<ul class="items">)(.*?)(</ul>)',
                  one, body, flags=re.S)



# 파트 묶음 — 위에서부터 이 차례로 놓는다. 묶음 안은 제휴 항목이 많은 순.
SECTION_CLUSTERS = [
    ('beauty', 'fashion', 'food', 'tech', 'life', 'travel'),   # 사는 것
    ('instagram', 'tiktok', 'youtube'),                        # 숏폼
    ('music', 'movie', 'game'),                                # 차트
    ('meme',),                                                 # 말
]


def order_sections(body):
    """상품이 걸린 파트를 위로. 성격이 같은 파트는 붙여 둔다."""
    secs = {}
    for m in re.finditer(r'    <section class="cat" data-cat="(\w+)".*?</section>\n?', body, re.S):
        secs[m.group(1)] = m.group(0)
    if not secs:
        return body

    ordered = []
    for cluster in SECTION_CLUSTERS:
        have = [c for c in cluster if c in secs]
        have.sort(key=lambda c: -secs[c].count('data-aff='))
        ordered += have
    ordered += [c for c in secs if c not in ordered]     # 묶음에 없는 새 파트는 뒤로

    first = min(body.index(secs[c]) for c in secs)
    rest = body
    for c in secs:
        rest = rest.replace(secs[c], '', 1)
    return rest[:first] + ''.join(secs[c] for c in ordered) + rest[first:]



def rebuild_chips(body, edition):
    """분야 필터를 파트 차례에 맞춰 다시 만든다. 파트가 늘면 칩도 자동으로 는다."""
    m = re.search(r'(<div class="filters-inner" id="chips">)(.*?)(</div>)', body, re.S)
    if not m:
        return body
    cats = re.findall(r'<section class="cat" data-cat="(\w+)"', body)
    names = dict(re.findall(r'<section class="cat" data-cat="(\w+)".*?<h2>(.*?)</h2>', body, re.S))
    btn = ('<button class="chip" aria-pressed="%s" data-cat="%s">%s</button>')
    out = [btn % ('true', 'all', 'All' if edition == 'en' else '전체')]
    for c in cats:
        out.append(btn % ('false', c, names.get(c, c)))
    return body[:m.start()] + m.group(1) + '\n    ' + '\n    '.join(out) + '\n  ' + m.group(3) + body[m.end():]



def annotate_prev_week(body, sub):
    """지난주 보관본의 순위와 대조해 변화 배지를 붙인다. 보관본이 없으면 그냥 둔다."""
    past = [w for w in weeks_of(sub) if w < WEEK]
    if not past:
        return body
    src = os.path.join(HERE, sub, 'week', str(max(past)), 'index.html')
    if not os.path.exists(src):
        return body
    old = io.open(src, encoding='utf-8').read()

    def rank_map(t):
        out = {}
        for blk in re.findall(r'<li class="item".*?</li>', t, re.S):
            r = re.search(r'<span class="rank">(\d+)</span>', blk)
            h = re.search(r'<h3>(.*?)</h3>', blk, re.S)
            if r and h:
                key = re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', h.group(1))).strip()
                out.setdefault(key, int(r.group(1)))
        return out

    prev = rank_map(old)
    if not prev:
        return body
    hit = [0]

    def mark(m):
        blk = m.group(0)
        r = re.search(r'<span class="rank">(\d+)</span>', blk)
        h = re.search(r'<h3>(.*?)</h3>', blk, re.S)
        if not (r and h):
            return blk
        if '지난주' in blk:          # kworb 발 태그가 이미 있으면 건드리지 않는다
            return blk
        key = re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', h.group(1))).strip()
        if key not in prev:
            return blk
        d = prev[key] - int(r.group(1))       # 양수면 순위가 올라갔다
        if d > 0:
            txt = '지난주 %d위 ▲%d' % (prev[key], d)
        elif d < 0:
            txt = '지난주 %d위 ▼%d' % (prev[key], -d)
        else:
            return blk               # 그대로면 배지를 붙이지 않는다 — 변화만 보여준다
        hit[0] += 1
        return blk.replace('<div class="meta">',
                           '<div class="meta"><span class="tag">%s</span>' % txt, 1)

    body = re.sub(r'<li class="item".*?</li>', mark, body, flags=re.S)
    if hit[0]:
        print('   %s지난주 대비 %d개' % (sub or './', hit[0]))
    return body


def weeks_of(sub):
    return sorted((int(os.path.basename(d)) for d in glob.glob(os.path.join(HERE, sub, 'week', '*'))
                   if os.path.basename(d).isdigit()), reverse=True)


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
if HAS_EN:
    EDITIONS.append(('en', 'en/', 'Trending in Korea', DESC_E, HEAD_E, BODY_E))

for ed, sub, title, desc, head, body in EDITIONS:
    base = SITE + '/' + sub

    # 제목은 브랜드명만 두면 아무도 검색하지 않는 말이 된다. 무엇을 다루는지 앞에 쓴다.
    lab = {'global': '해외', 'kr': '국내', 'en': 'Korea'}[ed]
    # kworb 는 지난주 차트에 없던 곡을 -1 · 99 · 161 로 적어 보낸다. 숫자로 두면 거짓말이 된다.
    body = re.sub(r'<span class="tag">지난주 (?:-?\d{3,}|-\d+|9[5-9])위</span>',
                  '<span class="tag">지난주 차트 밖</span>', body)
    body = annotate_prev_week(body, sub)   # 지난주 순위와 대조
    body = order_by_affiliate(body)   # 제휴 링크가 붙은 그룹을 앞으로
    body = order_sections(body)      # 상품이 걸린 파트를 위로
    body = rebuild_chips(body, ed)   # 필터 칩을 파트 차례에 맞춘다
    made = section_pages(body, sub, lab, head)          # 1차 — 파트 목록 수집
    SECTION_URLS[:] = SECTION_URLS[:len(SECTION_URLS) - len(made)]
    made = section_pages(body, sub, lab, head, made)    # 2차 — 서로 링크해서 다시 쓴다
    links = ('<div style="max-width:1180px;margin:0 auto;padding:26px 18px 40px;'
             "font:13px/2 'Noto Sans KR',sans-serif;color:#7E6F64\">" + ('All parts · ' if sub == 'en/' else '파트별 전체 목록 · ')
             + ' · '.join('<a href="/%s%s/" style="color:#7E6F64">%s</a>' % (sub, c, t)
                          for c, t in made) + '</div>')
    body = inject_part_links(body, sub, made)
    write(os.path.join(HERE, sub, 'index.html'),
          page(base,
               ('Trending in Korea — this week' if ed == 'en'
                else '이번 주 %s 유행 총정리 — %s' % (lab, BRAND)),
               desc, head, body + links, ed, alt_path=''))
    wdir = os.path.join(HERE, sub, 'week', str(WEEK))
    write(os.path.join(wdir, 'index.html'),
          page('%sweek/%d/' % (base, WEEK),
               ('Trending in Korea — %d week %d (%s)' % (YEAR, WEEK, PERIOD) if ed == 'en'
                else '%d년 %d주차 %s 유행 총정리 (%s) — %s' % (YEAR, WEEK, lab, PERIOD, BRAND)),
               '%d년 %d주차(%s) 보관본. %s에서 그 주에 뜨던 것을 그대로 남긴 기록입니다.'
               % (YEAR, WEEK, PERIOD, '해외' if ed == 'global' else '국내'), head, body, ed,
               banner('/' + sub), TODAY, 'week/%d/' % WEEK))

# ---------- 아카이브 ----------

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
        + GA_TAG + '\n'
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
        '\n<a class="home" href="/">← 이번 주 보드로</a>\n' + AFF_NOTE_KO + '\n</div></body>\n</html>\n')
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
        + GA_TAG + '\n'
           '<link rel="icon" href="' + ICON + '">\n'
           '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;800;900&display=swap">\n'
           + DOC_CSS + '\n</head>\n<body>' + NAV + '<div class="w">\n'
           '<h1>개인정보처리방침</h1>\n'
           '<p class="meta">사이트 · 지금 이슈 있나요? &nbsp;|&nbsp; 운영 · 피유글로벌 &nbsp;|&nbsp; 시행일 · 2026년 9월 5일 &nbsp;|&nbsp; 최종 갱신 · 2026년 9월 8일</p>\n'
           '<h2>1. 수집하는 개인정보</h2>\n'
           '<p>이 사이트는 <b>어떠한 개인정보도 직접 수집하지 않습니다.</b> 회원가입, 로그인, 댓글, 문의 양식 등 '
           '이용자가 정보를 입력하는 기능 자체가 없습니다. 방문 통계는 2항에 따라 익명으로만 수집합니다.</p>\n'
           '<h2>2. 쿠키</h2>\n'
           '<p>이 사이트는 방문 통계를 파악하기 위해 <b>Google 애널리틱스(GA4)</b>를 사용하며, '
           '이 과정에서 쿠키가 사용됩니다. 수집되는 것은 방문한 페이지, 머문 시간, 유입 경로, '
           '기기·브라우저 종류, 대략적인 지역(도시 단위) 같은 <b>익명 통계</b>이며 이름·연락처 등 '
           '개인을 식별할 수 있는 정보는 수집하지 않습니다. IP 주소는 Google에 의해 익명 처리됩니다.</p>\n'
           '<p>수집을 원하지 않으면 브라우저에서 쿠키를 차단하거나 '
           '<a href="https://tools.google.com/dlpage/gaoptout">Google 애널리틱스 차단 부가기능</a>을 '
           '설치하면 됩니다. 차단해도 사이트 이용에는 아무런 제한이 없습니다.</p>\n'
           '<p>이와 별개로 GitHub Pages로 제공되고 웹폰트를 Google Fonts에서 불러오므로, '
           '그 과정에서 해당 사업자의 서버에 접속 기록이 남을 수 있으며 이는 각 사업자의 정책을 따릅니다.</p>\n'
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
           '<a class="home" href="/">← 이번 주 보드로</a>\n' + AFF_NOTE_KO + '\n</div></body>\n</html>\n')
write(os.path.join(HERE, 'privacy', 'index.html'), privacy)

# ---------- sitemap · robots ----------
today = TODAY
urls = [(SITE + '/', '1.0', 'weekly'), (SITE + '/archive/', '0.6', 'weekly'),
        (SITE + '/privacy/', '0.3', 'yearly')]
if HAS_KR:
    urls.insert(1, (SITE + '/kr/', '1.0', 'weekly'))
for ed, sub, *_ in EDITIONS:
    urls += [('%s/%sweek/%d/' % (SITE, sub, w), '0.5', 'never') for w in weeks_of(sub)]
urls += [(u, '0.8', 'weekly') for u in SECTION_URLS]
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
# ---------- RSS ----------
# 주차 보관본이 이 사이트의 발행 단위다. 보드는 계속 덮어써지므로 피드에 넣지 않는다.
def rss():
    import email.utils
    items = []
    for ed, sub, *_ in EDITIONS:
        lab = {'global': '해외', 'kr': '국내', 'en': 'Korea'}[ed]
        for w in weeks_of(sub):
            url = '%s/%sweek/%d/' % (SITE, sub, w)
            if ed == 'en':
                title = 'Trending in Korea — %d week %d' % (YEAR, w)
                desc = 'What Korea is into in week %d of %d.' % (w, YEAR)
            else:
                title = '%d년 %d주차 %s 유행 총정리' % (YEAR, w, lab)
                desc = '%d년 %d주차 %s에서 유행한 것들. 항목마다 시작일과 트래픽 수치.' % (YEAR, w, lab)
            items.append((w, ed, url, title, desc))
    items.sort(key=lambda x: (-x[0], x[1]))
    now = email.utils.formatdate(usegmt=True)

    def esc(t):
        return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))

    body = '\n'.join(
        '  <item>\n'
        '    <title>%s</title>\n'
        '    <link>%s</link>\n'
        '    <guid isPermaLink="true">%s</guid>\n'
        '    <description>%s</description>\n'
        '    <pubDate>%s</pubDate>\n'
        '  </item>' % (esc(t), u, u, esc(d), now)
        for _, _, u, t, d in items)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
            '<channel>\n'
            '  <title>지금 이슈 있나요?</title>\n'
            '  <link>%s/</link>\n'
            '  <atom:link href="%s/rss.xml" rel="self" type="application/rss+xml"/>\n'
            '  <description>매주 월요일 갱신되는 해외·국내 유행 보드.</description>\n'
            '  <language>ko</language>\n'
            '  <lastBuildDate>%s</lastBuildDate>\n'
            '%s\n'
            '</channel>\n</rss>\n' % (SITE, SITE, now, body))


write(os.path.join(HERE, 'rss.xml'), rss())

write(os.path.join(HERE, 'robots.txt'),
      'User-agent: *\nAllow: /\n\n'
      + ''.join('User-agent: %s\nAllow: /\n\n' % b for b in AI_BOTS)
      + 'Sitemap: %s/sitemap.xml\n' % SITE)

# ---------- IndexNow ----------
# 바뀐 주소를 검색엔진에 즉시 통보한다. 빙·네이버·얀덱스가 같은 규약을 받는다.
INDEXNOW_KEY = 'c26981028fc3472ea6f3db0401e26506'   # 빙 웹마스터 도구가 발급한 키
write(os.path.join(HERE, INDEXNOW_KEY + '.txt'), INDEXNOW_KEY)
_stamp = os.path.join(HERE, '.indexnow-last')
_last = 0.0
if os.path.exists(_stamp):
    try:
        _last = float(io.open(_stamp, encoding='utf-8').read().strip())
    except ValueError:
        _last = 0.0
_now = __import__('time').time()

if _now - _last < 1800:
    print('IndexNow 건너뜀 · 마지막 통보 %d분 전' % ((_now - _last) / 60))
else:
  try:
      import urllib.request
      payload = json.dumps({'host': 'issueitnow.com', 'key': INDEXNOW_KEY,
                            'keyLocation': '%s/%s.txt' % (SITE, INDEXNOW_KEY),
                            'urlList': [u for u, _, _ in urls]}).encode()
      req = urllib.request.Request('https://api.indexnow.org/indexnow', data=payload,
                                   headers={'Content-Type': 'application/json; charset=utf-8'})
      with urllib.request.urlopen(req, timeout=20) as r:
          print('IndexNow 통보 · %d URL · 응답 %d' % (len(urls), r.status))
          io.open(_stamp, 'w', encoding='utf-8').write(str(_now))
  except Exception as e:
      print('IndexNow 통보 실패(무시하고 진행):', e)

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
