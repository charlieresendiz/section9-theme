"""Generates the Section 9 // Net Dive backdrop: an idle scene and an active one
(shown while Claude works). Light build: few separately animated elements, so
the app keeps it moving even when it renders without a GPU."""
import json, math, random, re, sys

W, H = 1600, 1000

CSS = """
.lane{animation:fall linear infinite}
@keyframes fall{from{transform:translateY(-1100px)}to{transform:translateY(1100px)}}
.sheet{animation:sheet linear infinite}
@keyframes sheet{from{transform:translateY(-1000px)}to{transform:translateY(0)}}
.win{animation:win ease-in-out infinite alternate}
@keyframes win{from{opacity:.9}to{opacity:.15}}
.spin{transform-box:fill-box;transform-origin:center;animation:spin 80s linear infinite}
.spinr{transform-box:fill-box;transform-origin:center;animation:spin 120s linear infinite reverse}
.sweep{transform-origin:200px 200px;animation:spin 14s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.pkt{stroke-dasharray:6 194;animation:pkt linear infinite}
@keyframes pkt{to{stroke-dashoffset:-200}}
.node{animation:node 7s ease-in-out infinite alternate}
@keyframes node{from{opacity:.35}to{opacity:.95}}
.scan{animation:scan 16s linear infinite}
@keyframes scan{from{transform:translateY(-200px)}to{transform:translateY(1100px)}}
"""

ACTIVE_CSS = """
.storm{animation:fadein 1.6s ease-out both}
@keyframes fadein{from{opacity:0}to{opacity:1}}
.shim{animation:shim 2.4s ease-in-out infinite alternate}
@keyframes shim{from{opacity:1}to{opacity:.55}}
.sweep{animation-duration:5s}
.pkt{animation-duration:2.2s}
"""

DEFS = """<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#020507"/><stop offset=".55" stop-color="#041013"/><stop offset=".8" stop-color="#08242a"/><stop offset="1" stop-color="#03090b"/>
</linearGradient>
<radialGradient id="glow" cx=".5" cy=".78" r=".6"><stop offset="0" stop-color="#1fd6a8" stop-opacity=".18"/><stop offset="1" stop-color="#1fd6a8" stop-opacity="0"/></radialGradient>
<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".75"/></radialGradient>
<linearGradient id="scanband" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5fffd0" stop-opacity="0"/><stop offset=".5" stop-color="#5fffd0" stop-opacity=".05"/><stop offset="1" stop-color="#5fffd0" stop-opacity="0"/></linearGradient>
<linearGradient id="sweepg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3cffc0" stop-opacity="0"/><stop offset="1" stop-color="#3cffc0" stop-opacity=".22"/></linearGradient>
<pattern id="lines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".35"/></pattern>
</defs>"""


def glyph(rng, x, y):
    """A katakana-like glyph: two to four short strokes in a 10 by 14 cell."""
    segs = []
    for _ in range(rng.randint(2, 4)):
        kind = rng.random()
        if kind < .35:
            segs.append(f'M{x+1} {y + rng.choice([2, 6, 10])}h{rng.choice([6, 8])}')
        elif kind < .7:
            segs.append(f'M{x + rng.choice([2, 5, 8])} {y+1}v{rng.choice([6, 9, 12])}')
        else:
            segs.append(f'M{x+8} {y+2}l-{rng.choice([5, 7])} {rng.choice([8, 10])}')
    return ''.join(segs)


def lanes(rng, columns, lane_count, step, lens, spread):
    """Columns merged into a few lanes; each lane is one body path and one head path."""
    out = [{'body': [], 'head': []} for _ in range(lane_count)]
    for i, x in enumerate(columns):
        n = rng.randint(*lens)
        y0 = -rng.randint(0, spread)
        lane = out[i % lane_count]
        lane['body'].append(''.join(glyph(rng, x, y0 + j * step) for j in range(n)))
        lane['head'].append(glyph(rng, x, y0 + n * step))
    return [{'body': ''.join(l['body']), 'head': ''.join(l['head'])} for l in out]


def build(active):
    a = []
    a.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">')
    a.append('<style>' + CSS + (ACTIVE_CSS if active else '') + '</style>')
    a.append(DEFS)
    a.append(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
    a.append(f'<rect width="{W}" height="{H}" fill="url(#glow)" opacity=".75"/>')

    # code rain: 34 columns in 6 lanes
    rng = random.Random(1995)
    cols = [int(i * W / 34 + rng.uniform(-10, 10)) for i in range(34)]
    rain = lanes(rng, cols, 6, 18, (14, 30), 500)
    speeds = [30, 36, 42, 48, 26, 54]
    a.append('<g fill="none" stroke="#3cffb0" stroke-width="1.4" stroke-linecap="square">')
    for k, lane in enumerate(rain):
        dur = speeds[k] * (.42 if active else 1)
        delay = -dur * k / 6
        if active:
            a.append(f'<g class="lane" style="animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s">'
                     f'<path d="{lane["body"]}" stroke-width="4.5" opacity=".07"/>'
                     f'<g class="shim" style="animation-delay:-{k * .4:.1f}s"><path d="{lane["body"]}" stroke="#7dffd4" opacity=".5"/></g>'
                     f'<path d="{lane["head"]}" stroke="#c8ffee" opacity=".9"/></g>')
        else:
            a.append(f'<g class="lane" style="animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s">'
                     f'<path d="{lane["body"]}" opacity=".2"/>'
                     f'<path d="{lane["head"]}" stroke="#c8ffee" opacity=".9"/></g>')
    a.append('</g>')

    if active:
        # the downpour: 52 more columns in 6 faster lanes, fading in
        srng = random.Random(2077)
        scols = [int(srng.uniform(0, W)) for _ in range(52)]
        storm = lanes(srng, scols, 6, 16, (10, 22), 700)
        a.append('<g class="storm" fill="none" stroke="#9fffe0" stroke-width="1.2" stroke-linecap="square">')
        for k, lane in enumerate(storm):
            dur = [7, 9, 11, 8, 10, 12][k]
            a.append(f'<g class="lane" style="animation-duration:{dur}s;animation-delay:-{dur * k / 6:.1f}s">'
                     f'<path d="{lane["body"]}" opacity=".45"/>'
                     f'<path d="{lane["head"]}" stroke="#ffffff" opacity=".85"/></g>')
        a.append('</g>')

    # skyline far + near, with lit windows in 5 groups
    rng = random.Random(880)

    def skyline(base, hmin, hmax, wmin, wmax, color, wins):
        x = -20
        bld, wl = [], []
        while x < W + 20:
            w = rng.randint(wmin, wmax)
            h = rng.randint(hmin, hmax)
            bld.append(f'M{x} {H}V{base-h}h{w}V{H}Z')
            if rng.random() < .25:
                bld.append(f'M{x + w // 2 - 1} {base-h}v-{rng.randint(15, 50)}h2V{base-h}Z')
            if wins:
                for wy in range(base - h + 10, base - 10, 14):
                    for wx in range(x + 5, x + w - 6, 10):
                        if rng.random() < .16:
                            wl.append((wx, wy))
            x += w + rng.randint(0, 6)
        a.append(f'<path d="{"".join(bld)}" fill="{color}"/>')
        return wl

    skyline(830, 120, 340, 40, 90, '#071a1e', False)
    wl = skyline(880, 60, 230, 50, 120, '#030a0c', True)
    rng.shuffle(wl)
    for gi in range(5):
        d = ''.join(f'M{x} {y}h4v6h-4Z' for x, y in wl[gi::5][:70])
        col = ['#ffcf7a', '#7affe0', '#9fd8ff', '#ffcf7a', '#7affe0'][gi]
        a.append(f'<path class="win" style="animation-duration:{8 + gi * 3}s;animation-delay:-{gi * 2}s" d="{d}" fill="{col}" opacity=".6"/>')

    # water
    a.append(f'<rect y="880" width="{W}" height="{H - 880}" fill="#02080a"/>')
    a.append('<path d="' + ''.join(f'M{rng.randint(0, W)} {y}h{rng.randint(40, 200)}' for y in range(892, H, 9))
             + '" stroke="#2fd6ac" stroke-opacity=".12"/>')

    # rain drops: two looping sheets, each covering two screen heights
    for k, (count, dur, op) in enumerate([(40, 3.6, .10), (30, 5.2, .07)]):
        pts = [(rng.randint(0, W + 40), rng.randint(0, H)) for _ in range(count)]
        d = ''.join(f'M{x} {y + dy}l-4 26' for x, y in pts for dy in (0, H))
        a.append(f'<path class="sheet" style="animation-duration:{dur * (.7 if active else 1):.1f}s" d="{d}" stroke="#9feee0" stroke-opacity="{op}"/>')

    # net nodes: bottom-left corner, packets and pulses in 3 groups each
    a.append('<svg x="0" y="0" width="100%" height="100%" viewBox="0 0 1000 660" preserveAspectRatio="xMinYMax meet"><g transform="translate(0 260)">')
    pts = [(40, 330), (110, 270), (190, 310), (150, 200), (260, 240), (80, 160), (320, 330), (230, 150), (30, 240), (360, 270)]
    edges = [(0, 1), (1, 2), (1, 3), (3, 4), (2, 4), (3, 5), (4, 6), (4, 7), (5, 8), (0, 8), (6, 9), (7, 3), (2, 6), (9, 4)]
    line = lambda p, q: f'M{pts[p][0]} {pts[p][1]}L{pts[q][0]} {pts[q][1]}'
    a.append(f'<path d="{"".join(line(p, q) for p, q in edges)}" stroke="#2ee6b6" stroke-opacity=".18" fill="none"/>')
    a.append('<g fill="none" stroke="#bfffee" stroke-width="2" stroke-opacity=".7">')
    for k in range(3):
        segs = ''.join(f'<path d="{line(p, q)}" pathLength="200"/>' for p, q in edges[k::3])
        a.append(f'<g class="pkt" style="animation-duration:{[6, 8, 10][k]}s">{segs}</g>')
    a.append('</g>')
    for k in range(3):
        dots = ''.join(f'<circle cx="{x}" cy="{y}" r="3"/><circle cx="{x}" cy="{y}" r="8" fill="none" stroke="#2ee6b6" stroke-opacity=".35"/>' for x, y in pts[k::3])
        a.append(f'<g class="node" fill="#2ee6b6" style="animation-delay:-{k * 2.3:.1f}s">{dots}</g>')
    a.append('</g></svg>')

    # HUD reticle: top-right corner
    a.append('<svg x="0" y="0" width="100%" height="100%" viewBox="0 0 1000 620" preserveAspectRatio="xMaxYMin meet"><g transform="translate(770 30)" fill="none" stroke="#3cffc0">')
    a.append('<circle cx="100" cy="100" r="96" stroke-opacity=".18"/>')
    ticks = ''.join(f'M{100 + 88 * math.cos(t):.1f} {100 + 88 * math.sin(t):.1f}L{100 + 96 * math.cos(t):.1f} {100 + 96 * math.sin(t):.1f}'
                    for t in [k * math.pi / 36 for k in range(72)])
    a.append(f'<path class="spin" d="{ticks}" stroke-opacity=".35"/>')
    a.append('<circle class="spinr" cx="100" cy="100" r="70" stroke-opacity=".4" stroke-dasharray="30 8 4 8" stroke-width="2"/>')
    a.append('<circle cx="100" cy="100" r="44" stroke-opacity=".25"/>')
    hexd = 'M' + 'L'.join(f'{100 + 26 * math.cos(math.pi / 3 * k + math.pi / 6):.1f} {100 + 26 * math.sin(math.pi / 3 * k + math.pi / 6):.1f}' for k in range(6)) + 'Z'
    a.append(f'<path class="spin" d="{hexd}" stroke-opacity=".6"/>')
    a.append('<path d="M100 0v30M100 170v30M0 100h30M170 100h30" stroke-opacity=".5"/>')
    a.append('<g transform="scale(.5)"><path class="sweep" d="M200 200L392 200A192 192 0 0 0 366 104Z" fill="url(#sweepg)" stroke="none"/></g>')
    a.append('<path d="' + ''.join(f'M-10 {230 + k * 9}h{rng.randint(20, 70)}' for k in range(5)) + '" stroke-opacity=".35" stroke-width="3"/>')
    a.append('</g></svg>')

    # scan band, scanlines, vignette
    a.append(f'<rect class="scan" width="{W}" height="180" fill="url(#scanband)"/>')
    a.append(f'<rect width="{W}" height="{H}" fill="url(#lines)" opacity=".5"/>')
    a.append(f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')
    a.append('</svg>')
    return re.sub(r'\n\s*', '', ''.join(a))


idle, active = build(False), build(True)
for name, svg in (('idle', idle), ('active', active)):
    moving = len(re.findall(r'class="(?:lane|sheet|win|spin|spinr|sweep|pkt|node|scan|storm|shim)"', svg))
    sys.stderr.write(f'{name}: {len(svg)} chars, {moving} animated elements\n')
print('// Generated by tools/gen_scene.py: night net-city, code rain, HUD reticle, data nodes.')
print('// SCENE is the idle backdrop; SCENE_ACTIVE plays while Claude works.')
print('export const SCENE = ' + json.dumps(idle))
print('export const SCENE_ACTIVE = ' + json.dumps(active))
