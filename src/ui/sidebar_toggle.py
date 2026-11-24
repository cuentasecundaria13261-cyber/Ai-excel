"""A round button, always visible at the top left, that slides the side panel in and out.

Streamlit has its own small arrow for this, but it is easy to miss (it can show only on hover).
This button is drawn on the page by a few lines of script. It uses Streamlit's own open/close arrow
when it can find it, and otherwise hides or shows the panel itself. If the browser blocks the script,
nothing breaks: the page simply keeps Streamlit's own arrow.
"""

import streamlit as st

from src.i18n import t

_SCRIPT = """
<script>
(function(){
  try{
    var P=window.parent, D=P.document, ID='ai-excel-sidebar-toggle';
    var old=D.getElementById(ID); if(old) old.remove();
    var oldStyle=D.getElementById(ID+'-style'); if(oldStyle) oldStyle.remove();
    var css=D.createElement('style'); css.id=ID+'-style';
    css.textContent='#'+ID+'{position:fixed;top:12px;left:12px;z-index:1000002;width:44px;height:44px;border-radius:14px;'+
      'border:1px solid #d6e3fd;background:#fff;color:#2f6feb;box-shadow:0 2px 10px rgba(16,24,40,.18);cursor:pointer;'+
      'display:flex;align-items:center;justify-content:center;padding:0;transition:transform .15s,border-color .15s}'+
      '#'+ID+':hover{border-color:#2f6feb;transform:scale(1.06)}#'+ID+' svg{width:24px;height:24px}'+
      '.ai-excel-hide-sidebar [data-testid="stSidebar"]{display:none !important}';
    D.head.appendChild(css);
    var b=D.createElement('button'); b.id=ID; b.type='button';
    b.setAttribute('aria-label',%(label)s); b.title=%(label)s;
    b.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'+
      '<rect x="3" y="4" width="18" height="16" rx="3"/><path d="M9 4v16"/></svg>';
    function sidebar(){return D.querySelector('[data-testid="stSidebar"]');}
    function isOpen(){
      var s=sidebar(); if(!s||D.body.classList.contains('ai-excel-hide-sidebar')) return false;
      var a=s.getAttribute('aria-expanded'); if(a!==null) return a==='true';
      return s.getBoundingClientRect().right>20;
    }
    function nativeButton(open){
      var sel=open?['[data-testid="stSidebarCollapseButton"] button','[data-testid="stSidebarCollapseButton"]']
                  :['[data-testid="stExpandSidebarButton"]','[data-testid="stSidebarCollapsedControl"] button','[data-testid="collapsedControl"] button'];
      for(var i=0;i<sel.length;i++){var e=D.querySelector(sel[i]); if(e) return e;}
      return null;
    }
    b.onclick=function(){
      var open=isOpen();
      if(D.body.classList.contains('ai-excel-hide-sidebar')){D.body.classList.remove('ai-excel-hide-sidebar'); return;}
      var n=nativeButton(open);
      if(n){n.click(); return;}
      if(open) D.body.classList.add('ai-excel-hide-sidebar');
    };
    D.body.appendChild(b);
  }catch(e){}
})();
</script>
"""


def render_sidebar_toggle():
    label = t("Show or hide the side panel").replace("\\", "").replace('"', "").replace("<", "").replace(">", "")
    document = "<!doctype html><html><body>" + (_SCRIPT % {"label": '"' + label + '"'}) + "</body></html>"
    try:
        from streamlit.components import v1 as components
    except (ImportError, TypeError):   # not a real Streamlit (for example in tests): nothing to draw
        return
    components.html(document, height=0)
