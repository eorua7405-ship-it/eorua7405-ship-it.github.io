# -*- coding: utf-8 -*-
"""board.html(아티팩트 원본) -> index.html(배포용 정적 페이지)"""
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(HERE, 'board.html'), encoding='utf-8').read()

title = re.search(r'<title>(.*?)</title>', src).group(1)
head = []
for pat in (r'<title>.*?</title>', r'<link rel="preconnect"[^>]*>',
            r'<link rel="stylesheet"[^>]*>', r'<style>.*?</style>'):
    head += [m.group(0) for m in re.finditer(pat, src, re.S)]

body = src
for part in head:
    body = body.replace(part, '', 1)
body = body.strip()

desc = ('매주 월요일 갱신되는 해외 유행 보드. 인스타 릴스·유튜브·음악·영화·게임·패션·음식·뷰티·밈·여행 '
        '트렌드를 시작일과 트래픽 수치, 그리고 왜 지금 뜨는지에 대한 해석과 함께 정리합니다.')

reset = """  :root{color-scheme:light dark}
  html{-webkit-text-size-adjust:100%}
  body{margin:0;font:14px/1.5 system-ui,-apple-system,sans-serif}
  img{max-width:100%}
  [hidden]{display:none!important}"""

icon = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'"
        "%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%94%A5%3C/text%3E%3C/svg%3E")

doc = ('<!doctype html>\n<html lang="ko">\n<head>\n'
       '<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
       '<meta name="description" content="' + desc + '">\n'
       '<meta name="author" content="피유글로벌">\n'
       '<meta property="og:type" content="website">\n'
       '<meta property="og:title" content="' + title + '">\n'
       '<meta property="og:description" content="' + desc + '">\n'
       '<meta property="og:locale" content="ko_KR">\n'
       '<meta name="twitter:card" content="summary_large_image">\n'
       '<link rel="icon" href="' + icon + '">\n'
       + head[0] + '\n'
       + '\n'.join(head[1:-1]) + '\n'
       + '<style>\n' + reset + '\n</style>\n'
       + head[-1] + '\n'
       '</head>\n<body>\n' + body + '\n</body>\n</html>\n')

io.open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8').write(doc)
print('index.html rebuilt:', len(doc), 'bytes')
