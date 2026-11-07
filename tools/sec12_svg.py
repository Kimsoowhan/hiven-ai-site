# -*- coding: utf-8 -*-
"""12번 폴더 구조도·연계도용 SVG 그리기 도구 (한글 글자 폭 추정으로 줄바꿈·글자 크기 맞춤)."""
import html
FONT = 'Noto Sans CJK KR,Noto Sans KR,Pretendard,sans-serif'

def E(s): return html.escape(str(s), quote=False)

def tw(s, fs):
    return sum(fs * (1.0 if ord(c) > 0x2E7F else (0.35 if c in ' .,:;|·()[]\'"' else 0.6)) for c in s)

def wrap(s, maxw, fs):
    out = []
    for para in str(s).split('\n'):
        cur = ''
        for ch in para:
            if tw(cur + ch, fs) > maxw and cur:
                out.append(cur); cur = ch
            else:
                cur += ch
        out.append(cur)
    return out

class Canvas:
    def __init__(self, w, h, title, sub='', foot=''):
        self.w, self.h = w, h
        self.o = []
        a = self.o.append
        a('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="%s">' % (w, h, w, h, FONT))
        a('<defs><marker id="ah" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto-start-reverse"><path d="M0,0 L9,4.5 L0,9 z" fill="#3b4a8c"/></marker>'
          '<marker id="ar" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto-start-reverse"><path d="M0,0 L9,4.5 L0,9 z" fill="#c62828"/></marker>'
          '<marker id="ag" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto-start-reverse"><path d="M0,0 L9,4.5 L0,9 z" fill="#2e7d32"/></marker></defs>')
        a('<rect width="%d" height="%d" fill="#fff"/>' % (w, h))
        self.text(36, 46, title, 25, '#0b1640', 700, 'start')
        if sub:
            for i, ln in enumerate(wrap(sub, w - 72, 13)):
                self.text(36, 72 + i * 18, ln, 13, '#444', 400, 'start')
        self.foot = foot

    def text(self, x, y, s, fs=13, fill='#222', w=400, anchor='middle'):
        self.o.append('<text x="%s" y="%s" text-anchor="%s" font-size="%s" font-weight="%s" fill="%s">%s</text>' % (x, y, anchor, fs, w, fill, E(s)))

    def rect(self, x, y, w, h, fill='#fff', stroke='#0b1640', sw=1.2, rx=8, dash=None):
        self.o.append('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="%s" stroke-width="%s"%s/>' % (
            x, y, w, h, rx, fill, stroke, sw, (' stroke-dasharray="%s"' % dash) if dash else ''))

    def box(self, x, y, w, h, txt, fs=13, fill='#fff', stroke='#0b1640', col='#222', bold=False, rx=8, align='middle', sw=1.2, dash=None, pad=8, head=None, headcol=None):
        """글자는 상자 안에 맞춘다: 글자 크기를 줄여 보고(최소 8.5), 그래도 넘치면 줄임표."""
        self.rect(x, y, w, h, fill, stroke, sw, rx, dash)
        yy = y
        if head:
            hs = min(fs + 1, 15)
            self.o.append('<text x="%s" y="%s" text-anchor="%s" font-size="%s" font-weight="700" fill="%s">%s</text>' % (
                x + (w / 2 if align == 'middle' else pad), y + hs + 5, align, hs, headcol or stroke, E(head)))
            yy = y + hs + 8
            h2 = h - (hs + 8)
        else:
            h2 = h
        f = fs
        while True:
            lines = wrap(txt, w - 2 * pad, f)
            need = len(lines) * f * 1.32 + 6
            if need <= h2 or f <= 8.5:
                break
            f -= 0.5
        mx = max(1, int((h2 - 6) // (f * 1.32)))
        if len(lines) > mx:
            lines = lines[:mx]
            lines[-1] = lines[-1][:max(0, len(lines[-1]) - 1)] + '…'
        total = len(lines) * f * 1.32
        y0 = yy + (h2 - total) / 2 + f * 1.0 if align == 'middle' and not head else yy + f * 1.15 + 3
        tx = x + (w / 2 if align == 'middle' else pad)
        for i, ln in enumerate(lines):
            self.o.append('<text x="%s" y="%s" text-anchor="%s" font-size="%s" font-weight="%s" fill="%s">%s</text>' % (
                tx, round(y0 + i * f * 1.32, 1), align, f, 700 if bold else 400, col, E(ln)))

    def line(self, x1, y1, x2, y2, col='#3b4a8c', sw=1.6, dash=None, mk='ah', both=False):
        self.o.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s"%s%s%s/>' % (
            x1, y1, x2, y2, col, sw, (' stroke-dasharray="%s"' % dash) if dash else '',
            (' marker-end="url(#%s)"' % mk) if mk else '', (' marker-start="url(#%s)"' % mk) if both else ''))

    def path(self, d, col='#3b4a8c', sw=1.6, dash=None, mk='ah'):
        self.o.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s"%s%s/>' % (d, col, sw, (' stroke-dasharray="%s"' % dash) if dash else '', (' marker-end="url(#%s)"' % mk) if mk else ''))

    def svg(self):
        if self.foot:
            self.text(36, self.h - 14, self.foot, 11, '#666', 400, 'start')
        return '\n'.join(self.o) + '\n</svg>\n'
