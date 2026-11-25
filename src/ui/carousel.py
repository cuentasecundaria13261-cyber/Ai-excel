"""A chart carousel: charts side by side, arrows to move, and it slides by itself while the page scrolls.

The charts are drawn as plain HTML and SVG inside one small frame, so no chart library is needed.
Everything that comes from the visitor's file is escaped. If the frame cannot watch the page scroll
(some browsers block it), the arrows, the small tabs and swiping still work.
"""

import html
import json

import streamlit as st

from src.i18n import t
from src.ui.components import bar_chart_html, icon
from src.ui.style import _CSS

W, H = 860, 330
PAD_L, PAD_R, PAD_T, PAD_B = 78, 18, 14, 38


def _esc(value):
    return html.escape(str(value), quote=True)


def _nice_max(value):
    """Round the top of the chart up to a friendly number (1, 2, 2.5, 5 or 10 times a power of ten)."""
    if value <= 0:
        return 1.0
    power = 10 ** (len(str(int(value))) - 1) if value >= 1 else 1
    for step in (1, 2, 2.5, 5, 10):
        if value <= step * power:
            return step * power
    return 10 * power


def line_chart_html(points, title="", hint="", fmt=lambda v: f"{v:,.0f}", tips=None):
    """points: list of (label, value). A line with a soft area, a few labels and hover tips.
    tips: optional list (one per point) of extra lines shown when the visitor hovers over it."""
    points = [(str(label), float(value)) for label, value in points]
    if len(points) < 2:
        return ""
    top = _nice_max(max(max(v for _, v in points), 0))
    low = min(min(v for _, v in points), 0)
    span = (top - low) or 1
    inner_w, inner_h = W - PAD_L - PAD_R, H - PAD_T - PAD_B

    def x_of(i):
        return PAD_L + inner_w * i / (len(points) - 1)

    def y_of(v):
        return PAD_T + inner_h * (1 - (v - low) / span)

    grid = []
    for k in range(5):
        value = low + span * k / 4
        y = y_of(value)
        grid.append(f"<line x1='{PAD_L}' x2='{W - PAD_R}' y1='{y:.1f}' y2='{y:.1f}' stroke='#eef0f4'/>"
                    f"<text x='{PAD_L - 10}' y='{y + 5:.1f}' text-anchor='end' font-size='14' fill='#667085'>{_esc(fmt(value))}</text>")
    path = " ".join(f"{x_of(i):.1f},{y_of(v):.1f}" for i, (_, v) in enumerate(points))
    base = y_of(max(low, 0))
    area = f"{x_of(0):.1f},{base:.1f} {path} {x_of(len(points) - 1):.1f},{base:.1f}"
    ticks = sorted({0, len(points) // 4, len(points) // 2, (3 * len(points)) // 4, len(points) - 1})
    labels = "".join(
        f"<text x='{x_of(i):.1f}' y='{H - 10}' text-anchor='{'start' if i == 0 else 'end' if i == len(points) - 1 else 'middle'}'"
        f" font-size='14' fill='#667085'>{_esc(points[i][0])}</text>" for i in ticks)
    step = inner_w / (len(points) - 1)
    dots = "".join(
        (f"<circle cx='{x_of(i):.1f}' cy='{y_of(v):.1f}' r='4' fill='#fff' stroke='#2f6feb' stroke-width='2.5' pointer-events='none'/>"
         if len(points) <= 40 else "")
        + f"<rect class='pt' x='{x_of(i) - step / 2:.1f}' y='{PAD_T}' width='{step:.1f}' height='{inner_h}' fill='transparent'"
          f" data-x='{x_of(i):.1f}' data-y='{y_of(v):.1f}' data-tip='{_esc(json.dumps([label, fmt(v)] + list((tips[i] if tips else [])), ensure_ascii=False))}'/>"
        for i, (label, v) in enumerate(points))
    svg = (f"<svg viewBox='0 0 {W} {H}' width='100%' role='img' aria-label='{_esc(title)}'>"
           "<defs><linearGradient id='fill' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#2f6feb' stop-opacity='.22'/>"
           "<stop offset='1' stop-color='#2f6feb' stop-opacity='0'/></linearGradient></defs>"
           f"{''.join(grid)}<polygon points='{area}' fill='url(#fill)'/>"
           f"<line id='guide' x1='0' x2='0' y1='{PAD_T}' y2='{PAD_T + inner_h}' stroke='#9bb8f5' stroke-width='1.5' stroke-dasharray='4 4' visibility='hidden'/>"
           f"<polyline points='{path}' fill='none' stroke='#2f6feb' stroke-width='4' stroke-linejoin='round' stroke-linecap='round'/>"
           f"{dots}<circle id='hdot' r='7' fill='#2f6feb' stroke='#fff' stroke-width='3' visibility='hidden' pointer-events='none'/>{labels}</svg>")
    head = f"<div class='bar-title'>{_esc(title)}</div>" if title else ""
    foot = f"<div class='bar-hint'>{icon('info', 16)}<span>{_esc(hint)}</span></div>" if hint else ""
    return f"<div class='bars'>{head}{svg}{foot}</div>"


_CAROUSEL_CSS = """
<style>
html,body{margin:0;background:#fff;font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;color:#1f2430}
.top{display:flex;justify-content:space-between;align-items:center;gap:12px;margin:2px 2px 10px}
.pills{display:flex;gap:6px;flex-wrap:wrap}
.pill{border:1px solid var(--line);background:#fff;border-radius:999px;padding:6px 14px;font-size:.88rem;font-weight:600;color:#475467;cursor:pointer}
.pill.on{background:#eaf1fe;border-color:var(--accent);color:var(--accent)}
.nav{display:flex;align-items:center;gap:8px;flex:none}
.count{font-size:.85rem;color:var(--muted);min-width:3.2rem;text-align:center}
.arrow{width:40px;height:40px;border-radius:50%;border:1px solid var(--line);background:#fff;color:var(--accent);cursor:pointer;
  display:flex;align-items:center;justify-content:center;box-shadow:0 1px 3px rgba(16,24,40,.12);transition:border-color .15s,opacity .15s}
.arrow:hover{border-color:var(--accent)} .arrow[disabled]{opacity:.35;cursor:default}
.arrow svg{width:20px;height:20px}
.track{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;gap:0}
.track::-webkit-scrollbar{display:none}
.slide{flex:0 0 100%;scroll-snap-align:start;box-sizing:border-box;padding:0 2px}
.bars{margin:0 !important}
.bar-row{border-radius:8px;padding:2px 6px;margin-left:-6px;margin-right:-6px}.bar-row[data-tip]:hover{background:#f3f7ff}
#tip{position:fixed;pointer-events:none;display:none;z-index:20;background:#101828;color:#fff;border-radius:12px;padding:9px 13px;font-size:.85rem;line-height:1.5;box-shadow:0 8px 24px rgba(16,24,40,.28);max-width:260px}
#tip b{display:block;font-size:.92rem;margin-bottom:2px}#tip span{display:block;color:#d0d5dd}#tip span.k{color:#fff;font-weight:600}
</style>
"""

_ARROW_L = "<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'><path d='M15 18l-6-6 6-6'/></svg>"
_ARROW_R = "<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'><path d='M9 18l6-6-6-6'/></svg>"

_SCRIPT = """
<script>
(function(){
  var track=document.getElementById('track'), slides=[].slice.call(track.children), N=slides.length;
  var pills=[].slice.call(document.querySelectorAll('.pill')), prev=document.getElementById('prev'),
      next=document.getElementById('next'), count=document.getElementById('count');
  var cur=0, pausedUntil=0, reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  function show(i){cur=i;pills.forEach(function(p,k){p.classList.toggle('on',k===i)});
    prev.disabled=i<=0; next.disabled=i>=N-1; count.textContent=(i+1)+' / '+N;}
  function go(i,manual){i=Math.max(0,Math.min(N-1,i)); if(manual)pausedUntil=Date.now()+8000;
    track.scrollTo({left:i*track.clientWidth,behavior:reduce?'auto':'smooth'}); show(i);}
  prev.onclick=function(){go(cur-1,true)}; next.onclick=function(){go(cur+1,true)};
  pills.forEach(function(p,k){p.onclick=function(){go(k,true)}});
  track.addEventListener('scroll',function(){var i=Math.round(track.scrollLeft/Math.max(1,track.clientWidth)); if(i!==cur)show(i);});
  document.addEventListener('keydown',function(e){if(e.key==='ArrowLeft')go(cur-1,true); if(e.key==='ArrowRight')go(cur+1,true);});
  // Hover information
  var tip=document.getElementById('tip'), guide=document.getElementById('guide'), hdot=document.getElementById('hdot');
  function lines(el){try{return JSON.parse(el.getAttribute('data-tip'))}catch(e){return null}}
  document.addEventListener('mousemove',function(e){
    var el=e.target.closest?e.target.closest('[data-tip]'):null, l=el&&lines(el);
    if(!l){tip.style.display='none'; if(guide)guide.setAttribute('visibility','hidden'); if(hdot)hdot.setAttribute('visibility','hidden'); return;}
    var h='<b></b>'; tip.innerHTML=h; tip.firstChild.textContent=l[0];
    for(var i=1;i<l.length;i++){var s=document.createElement('span'); if(i===1)s.className='k'; s.textContent=l[i]; tip.appendChild(s);}
    tip.style.display='block';
    var x=e.clientX+14, y=e.clientY+14, w=tip.offsetWidth, hgt=tip.offsetHeight;
    if(x+w>window.innerWidth-6)x=e.clientX-w-14; if(y+hgt>window.innerHeight-6)y=e.clientY-hgt-14;
    tip.style.left=Math.max(4,x)+'px'; tip.style.top=Math.max(4,y)+'px';
    if(el.classList.contains('pt')&&guide&&hdot){var gx=el.getAttribute('data-x'), gy=el.getAttribute('data-y');
      guide.setAttribute('x1',gx); guide.setAttribute('x2',gx); guide.setAttribute('visibility','visible');
      hdot.setAttribute('cx',gx); hdot.setAttribute('cy',gy); hdot.setAttribute('visibility','visible');}
  });
  document.addEventListener('mouseleave',function(){tip.style.display='none'});

  // The page waits here while the visitor scrolls through the charts. After the last chart
  // (or before the first one, when going up) scrolling goes back to normal.
  try{
    var P=window.parent, F=window.frameElement;
    if(P&&F&&N>1&&!reduce){
      if(P.__aiCarouselOff){try{P.__aiCarouselOff()}catch(e){}}   // drop the listeners of an older copy of this frame
      var acc=0, holdUntil=0, centered=false, touchY=null;
      function inView(){var r=F.getBoundingClientRect(), vh=P.innerHeight||800;
        return r.height<vh*0.92 && r.top>=-4 && r.bottom<=vh+4;}
      function handle(dy,e){
        if(!dy)return;
        if(!inView()){centered=false;acc=0;return;}
        var dir=dy>0?1:-1, now=Date.now(), can=(dir>0&&cur<N-1)||(dir<0&&cur>0);
        if(!can){ if(now<holdUntil&&e.cancelable)e.preventDefault(); return; }   // short hold so momentum does not carry the page away
        if(e.cancelable)e.preventDefault();
        if(!centered){centered=true; F.scrollIntoView({block:'center',behavior:'smooth'});}
        if(now<holdUntil)return;
        acc+=dy; if(Math.abs(acc)<50)return;
        acc=0; holdUntil=now+650; go(cur+dir,false);
        if(cur===0||cur===N-1)holdUntil=now+500;
      }
      function onWheel(e){handle(e.deltaMode===1?e.deltaY*16:e.deltaY,e);}
      function onTouchStart(e){touchY=e.touches[0].clientY;}
      function onTouchMove(e){var y=e.touches[0].clientY; if(touchY===null){touchY=y;return;} var dy=touchY-y; touchY=y; handle(dy*2,e);}
      [document,P.document].forEach(function(d){
        d.addEventListener('wheel',onWheel,{passive:false,capture:true});
        d.addEventListener('touchstart',onTouchStart,{passive:true,capture:true});
        d.addEventListener('touchmove',onTouchMove,{passive:false,capture:true});
      });
      P.__aiCarouselOff=function(){[document,P.document].forEach(function(d){
        d.removeEventListener('wheel',onWheel,true);d.removeEventListener('touchstart',onTouchStart,true);d.removeEventListener('touchmove',onTouchMove,true);});};
    }
  }catch(e){}
  show(0);
})();
</script>
"""


def carousel_html(slides, labels=None):
    """slides: list of dicts {name, html}. Returns one full HTML document."""
    labels = labels or {}
    pills = "".join(f"<button class='pill{' on' if i == 0 else ''}' type='button'>{_esc(s['name'])}</button>" for i, s in enumerate(slides))
    body = "".join(f"<section class='slide'>{s['html']}</section>" for s in slides)
    return (
        "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"{_CSS}{_CAROUSEL_CSS}</head><body>"
        f"<div class='top'><div class='pills'>{pills}</div>"
        f"<div class='nav'><button id='prev' class='arrow' type='button' aria-label='{_esc(labels.get('prev', 'Previous'))}'>{_ARROW_L}</button>"
        f"<span id='count' class='count'>1 / {len(slides)}</span>"
        f"<button id='next' class='arrow' type='button' aria-label='{_esc(labels.get('next', 'Next'))}'>{_ARROW_R}</button></div></div>"
        f"<div id='track' class='track'>{body}</div><div id='tip'></div>{_SCRIPT}</body></html>"
    )


def render_carousel(slides):
    """slides: list of dicts {name, kind: 'bars'|'line', title, hint, items|points, fmt}."""
    built, tallest = [], 0
    for s in slides:
        if s["kind"] == "line":
            content = line_chart_html(s["points"], s.get("title", ""), s.get("hint", ""), s.get("fmt", lambda v: f"{v:,.0f}"), s.get("tips"))
            size = 480
        else:
            content = bar_chart_html(s["items"], s.get("title", ""), s.get("hint", ""))
            size = 120 + 38 * min(len(s["items"]), 12)
        if content:
            built.append({"name": s["name"], "html": content})
            tallest = max(tallest, size)
    if not built:
        return
    document = carousel_html(built, {"prev": t("Previous chart"), "next": t("Next chart")})
    try:
        from streamlit.components import v1 as components
    except (ImportError, TypeError):   # not a real Streamlit (for example in tests): fall back to plain markup
        st.markdown(document, unsafe_allow_html=True)
        return
    components.html(document, height=min(700, max(300, tallest + 70)), scrolling=False)
