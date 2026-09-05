# -*- coding: utf-8 -*-
"""스포티파이 한국 일간 TOP 50 -> board-kr.html 음악 파트"""
import io, os, re, json, time, html, urllib.parse, urllib.request
HERE=os.path.dirname(os.path.abspath(__file__)); p=os.path.join(HERE,'board-kr.html')
s=io.open(p,encoding='utf-8').read()
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0'}
def get(u,t=30):
    with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t) as r:
        return r.read().decode('utf-8','replace')
def esc(t): return t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')
def kor(n):
    if n>=100000000: return '%.1f억'%(n/1e8)
    if n>=10000: return '%d만'%(n//10000)
    return '{:,}'.format(n)
page=get('https://kworb.net/spotify/country/kr_daily.html')
tr=[]
for row in re.findall(r'<tr>(.*?)</tr>',page,re.S):
    td=re.findall(r'<td[^>]*>(.*?)</td>',row,re.S)
    if len(td)<8: continue
    pos=re.sub('<[^>]+>','',td[0]).strip()
    if not pos.isdigit(): continue
    txt=html.unescape(re.sub('<[^>]+>','',td[2])).strip()
    if ' - ' not in txt: continue
    a,t=txt.split(' - ',1)
    tr.append({'r':int(pos),'a':a.strip(),'t':t.strip(),
               'st':re.sub('<[^>]+>','',td[6]).strip(),
               'mv':re.sub('<[^>]+>','',td[1]).strip()})
tr=sorted(tr,key=lambda x:x['r'])[:50]
C=os.path.join(HERE,'_artwork_kr.json'); art=json.load(io.open(C,encoding='utf-8')) if os.path.exists(C) else {}
for x in tr:
    k='%s|%s'%(x['a'],x['t'])
    if k in art: continue
    try:
        q=urllib.parse.quote('%s %s'%(x['a'],re.sub(r'\(.*?\)','',x['t'])))
        d=json.loads(get('https://itunes.apple.com/search?term=%s&entity=song&limit=1'%q,20))
        art[k]=d['results'][0]['artworkUrl100'].replace('100x100bb','600x600bb') if d.get('resultCount') else ''
    except Exception: art[k]=''
    time.sleep(0.25)
json.dump(art,io.open(C,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
def li(x):
    k='%s|%s'%(x['a'],x['t']); img=art.get(k) or ''
    n=int(x['st'].replace(',','')) if x['st'].replace(',','').isdigit() else 0
    mv='순위 유지' if x['mv']=='=' else ('전일 대비 '+x['mv'] if x['mv'] else '')
    ia=(' data-img="%s" data-credit="Apple Music · %s"'%(img,esc(x['a']))) if img else ''
    return ('        <li class="item" data-group="스포티파이 한국 TOP 50"'
      ' data-sum="일간 스트리밍 %s회 · %s" data-since="%s 집계 (일간)"'
      ' data-traffic="일간 스트리밍 %s회"%s data-term="%s %s">\n'
      '          <span class="rank">%02d</span>\n'
      '          <h3>%s — %s</h3>\n          <p>스포티파이 한국 일간 차트 %d위.</p>\n'
      '          <div class="meta"><span class="tag">%02d위</span><span class="tag">%s</span></div>\n        </li>'
      %(kor(n),esc(mv),'2026.09.06',x['st'],ia,esc(x['t']),esc(x['a']),x['r'],esc(x['a']),esc(x['t']),x['r'],x['r'],esc(mv)))
m=re.search(r'(<section class="cat" data-cat="music" data-plat="spotify">)(.*?)(</section>)',s,re.S)
body=m.group(2)
ul=re.search(r'(<ul class="items">)(.*?)(\n      </ul>)',body,re.S)
body=body[:ul.start()]+ul.group(1)+'\n'+'\n'.join(li(x) for x in tr)+ul.group(3)+body[ul.end():]
s=s[:m.start()]+m.group(1)+body+m.group(3)+s[m.end():]
io.open(p,'w',encoding='utf-8').write(s)
print('KR 음악:',len(tr),'| 아트워크:',sum(1 for x in tr if art.get('%s|%s'%(x['a'],x['t']))),'| 총 항목:',s.count('<li class="item"'))
