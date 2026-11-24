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


def line_chart_html(points, title="", hint="", fmt=lambda v: f"{v:,.0f}"):
    """points: list of (label, value). A smooth-looking line with a soft area, a few labels and hover tips."""
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
    dots = "".join(
        f"<circle cx='{x_of(i):.1f}' cy='{y_of(v):.1f}' r='9' fill='transparent' class='hit'><title>{_esc(label)}: {_esc(fmt(v))}</title></circle>"
        + (f"<circle cx='{x_of(i):.1f}' cy='{y_of(v):.1f}' r='4' fill='#fff' stroke='#2f6feb' stroke-width='2.5' pointer-events='none'/>"
           if len(points) <= 40 else "")
        for i, (label, v) in enumerate(points))
    svg = (f"<svg viewBox='0 0 {W} {H}' width='100%' role='img' aria-label='{_esc(title)}'>"
           "<defs><linearGradient id='fill' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#2f6feb' stop-opacity='.22'/>"
           "<stop offset='1' stop-color='#2f6feb' stop-opacity='0'/></linearGradient></defs>"
           f"{''.join(grid)}<polygon points='{area}' fill='url(#fill)'/>"
           f"<polyline points='{path}' fill='none' stroke='#2f6feb' stroke-width='4' stroke-linejoin='round' stroke-linecap='round'/>"
           f"{dots}{labels}</svg>")
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
.hit:hover{fill:rgba(47,111,235,.18)}
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
  // While the visitor scrolls the page, the charts move on by themselves.
  try{
    var P=window.parent, F=window.frameElement;
    if(P&&F&&N>1&&!reduce){
      var ticking=false;
      P.addEventListener('scroll',function(){
        if(ticking)return; ticking=true;
        P.requestAnimationFrame(function(){ticking=false;
          if(Date.now()<pausedUntil)return;
          var r=F.getBoundingClientRect(), vh=P.innerHeight||800;
          if(r.bottom<0||r.top>vh)return;
          var p=(vh-r.top)/(vh+r.height);            // 0 = just entering from below, 1 = just leaving at the top
          p=Math.min(0.999,Math.max(0,(p-0.2)/0.6));  // use the middle of the trip
          var i=Math.floor(p*N); if(i!==cur)go(i,false);
        });
      },true);
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
        f"<div id='track' class='track'>{body}</div>{_SCRIPT}</body></html>"
    )


def render_carousel(slides):
    """slides: list of dicts {name, kind: 'bars'|'line', title, hint, items|points, fmt}."""
    built, tallest = [], 0
    for s in slides:
        if s["kind"] == "line":
            content = line_chart_html(s["points"], s.get("title", ""), s.get("hint", ""), s.get("fmt", lambda v: f"{v:,.0f}"))
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
