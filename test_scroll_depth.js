// node test_scroll_depth.js   (build.py 를 돌린 뒤)
// GA4 스크롤 깊이 스크립트를 index.html 에서 뽑아 가짜 DOM 으로 돌린다.
// scroll_depth 스크립트를 가짜 DOM 으로 돌린다
const fs = require('fs');
const html = fs.readFileSync(__dirname + '/index.html', 'utf8');
const m = html.match(/<script>\(function\(\)\{var hit=[\s\S]*?<\/script>/);
if (!m) { console.error('스크롤 스크립트를 index.html 에서 못 찾음'); process.exit(1); }
const src = m[0].slice(8, -9);
const fired = [], L = {};
let Y = 0;
const secs = [
  {cat:'beauty', top:  200, offsetParent:{}},
  {cat:'music',  top: 4000, offsetParent:{}},
  {cat:'hidden', top:    0, offsetParent:null},
];
const ctx = {
  innerHeight: 800, scrollY: 0,
  document: {documentElement:{scrollHeight: 5000},
    querySelectorAll: () => secs.map(s => ({
      offsetParent: s.offsetParent,
      getBoundingClientRect: () => ({top: s.top - Y}),
      getAttribute: () => s.cat}))},
  location: {pathname: '/kr/'},
  gtag: (ev, name, p) => fired.push([name, p.percent, p.part, p.edition]),
  addEventListener: (n, f) => { L[n] = f; },
  clearTimeout: () => {}, setTimeout: f => f(),
};
ctx.window = ctx; ctx.globalThis = ctx;
require('vm').createContext(ctx);
require('vm').runInContext(src, ctx);

function scrollTo(y) { Y = y; ctx.scrollY = y; L.scroll(); }
L.load();                       // 0%
scrollTo(4200 * 0.26);          // 26%
scrollTo(4200 * 0.80);          // 75% 까지 한 번에 -> 50,75 둘 다
scrollTo(4200 * 0.80);          // 중복 금지
scrollTo(4200);                 // 100%

const got = JSON.stringify(fired);
console.log(got);
const assert = require('assert');
assert.deepStrictEqual(fired.map(f => f[1]), [25, 50, 75, 100], '한 번씩 순서대로');
assert.strictEqual(fired[0][2], 'beauty', '26% 에선 beauty 가 보인다');
assert.strictEqual(fired[3][2], 'music', '바닥에선 music');
assert.ok(fired.every(f => f[3] === 'kr'), 'edition=kr');
assert.ok(!fired.some(f => f[2] === 'hidden'), '숨은 섹션은 세지 않는다');
console.log('통과');
