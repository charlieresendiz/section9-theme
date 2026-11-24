import random, math, json, sys
random.seed(1995)
W, H = 1600, 1000
o = []
a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">')
a('''<style>
.rain{animation:fall linear infinite}
@keyframes fall{from{transform:translateY(-1100px)}to{transform:translateY(1100px)}}
.drop{animation:drop 3.6s linear infinite}
@keyframes drop{from{transform:translate(0,-200px)}to{transform:translate(-60px,1000px)}}
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
.haze{animation:haze 30s ease-in-out infinite alternate}
@keyframes haze{from{opacity:.55}to{opacity:.9}}
</style>''')
a('''<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#020507"/><stop offset=".55" stop-color="#041013"/><stop offset=".8" stop-color="#08242a"/><stop offset="1" stop-color="#03090b"/>
</linearGradient>
<radialGradient id="glow" cx=".5" cy=".78" r=".6"><stop offset="0" stop-color="#1fd6a8" stop-opacity=".18"/><stop offset="1" stop-color="#1fd6a8" stop-opacity="0"/></radialGradient>
<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".75"/></radialGradient>
<linearGradient id="scanband" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5fffd0" stop-opacity="0"/><stop offset=".5" stop-color="#5fffd0" stop-opacity=".05"/><stop offset="1" stop-color="#5fffd0" stop-opacity="0"/></linearGradient>
<linearGradient id="sweepg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3cffc0" stop-opacity="0"/><stop offset="1" stop-color="#3cffc0" stop-opacity=".22"/></linearGradient>
<pattern id="lines" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".35"/></pattern>
</defs>''')
a(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
a(f'<rect class="haze" width="{W}" height="{H}" fill="url(#glow)"/>')

# code rain: glyph strokes per column
def glyph(x, y):
    segs = []
    for _ in range(random.randint(2, 4)):
        kind = random.random()
        if kind < .35:
            yy = y + random.choice([2, 6, 10]); segs.append(f'M{x+1} {yy}h{random.choice([6,8])}')
        elif kind < .7:
            xx = x + random.choice([2, 5, 8]); segs.append(f'M{xx} {y+1}v{random.choice([6,9,12])}')
        else:
            segs.append(f'M{x+8} {y+2}l-{random.choice([5,7])} {random.choice([8,10])}')
    return ''.join(segs)

a('<g fill="none" stroke="#3cffb0" stroke-width="1.4" stroke-linecap="square">')
cols = 34
for i in range(cols):
    x = int(i * W / cols + random.uniform(-10, 10))
    n = random.randint(14, 30)
    d = ''.join(glyph(x, j * 18) for j in range(n))
    dur = random.uniform(26, 52)
    delay = -random.uniform(0, dur)
    op = random.uniform(.10, .28)
    head = f'<path d="{glyph(x, n*18)}" stroke="#c8ffee" opacity=".9"/>'
    a(f'<g class="rain" style="animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s"><path d="{d}" opacity="{op:.2f}"/>{head}</g>')
a('</g>')

# skyline far + near
def skyline(base, hmin, hmax, wmin, wmax, color, wins, winop):
    x = -20; bld = []; wl = []
    while x < W + 20:
        w = random.randint(wmin, wmax); h = random.randint(hmin, hmax)
        bld.append(f'M{x} {H}V{base-h}h{w}V{H}Z')
        if random.random() < .25:
            bld.append(f'M{x+w//2-1} {base-h}v-{random.randint(15,50)}h2v{0}Z'.replace('v0Z','V'+str(base-h)+'Z'))
        if wins:
            for wy in range(base - h + 10, base - 10, 14):
                for wx in range(x + 5, x + w - 6, 10):
                    if random.random() < .16:
                        wl.append((wx, wy))
        x += w + random.randint(0, 6)
    a(f'<path d="{"".join(bld)}" fill="{color}"/>')
    return wl
skyline(830, 120, 340, 40, 90, '#071a1e', False, 0)
wl = skyline(880, 60, 230, 50, 120, '#030a0c', True, .6)
random.shuffle(wl)
groups = [wl[k::5] for k in range(5)]
for gi, g in enumerate(groups):
    d = ''.join(f'M{x} {y}h4v6h-4Z' for x, y in g[:70])
    col = random.choice(['#ffcf7a', '#7affe0', '#9fd8ff', '#ffcf7a', '#7affe0'])
    a(f'<path class="win" style="animation-duration:{8+gi*3}s;animation-delay:-{gi*2}s" d="{d}" fill="{col}" opacity=".6"/>')
# water reflection band
a(f'<rect y="880" width="{W}" height="{H-880}" fill="#02080a"/>')
a('<g stroke="#2fd6ac" stroke-opacity=".12" stroke-width="1">' + ''.join(
    f'<path d="M{random.randint(0,W)} {y}h{random.randint(40,200)}"/>' for y in range(892, H, 9)) + '</g>')

# rain drops
a('<g stroke="#9feee0" stroke-opacity=".10" stroke-width="1">')
for i in range(70):
    x = random.randint(0, W + 200); y = random.randint(0, H)
    a(f'<path class="drop" style="animation-delay:-{random.uniform(0,3.6):.2f}s" d="M{x} {y}l-4 26"/>')
a('</g>')

# net nodes: bottom-left corner pinned
a('<svg x="0" y="0" width="100%" height="100%" viewBox="0 0 1000 660" preserveAspectRatio="xMinYMax meet"><g transform="translate(0 260)">')
pts = [(40,330),(110,270),(190,310),(150,200),(260,240),(80,160),(320,330),(230,150),(30,240),(360,270)]
edges = [(0,1),(1,2),(1,3),(3,4),(2,4),(3,5),(4,6),(4,7),(5,8),(0,8),(6,9),(7,3),(2,6),(9,4)]
a('<g stroke="#2ee6b6" stroke-width="1" fill="none">')
for (p, q) in edges:
    (x1,y1),(x2,y2) = pts[p], pts[q]
    a(f'<path d="M{x1} {y1}L{x2} {y2}" stroke-opacity=".18"/>')
    a(f'<path class="pkt" style="animation-duration:{random.uniform(5,11):.1f}s" d="M{x1} {y1}L{x2} {y2}" stroke="#bfffee" stroke-width="2" pathLength="200" stroke-opacity=".7"/>')
a('</g><g fill="#2ee6b6">')
for k,(x,y) in enumerate(pts):
    a(f'<g class="node" style="animation-delay:-{k*0.7:.1f}s"><circle cx="{x}" cy="{y}" r="3"/><circle cx="{x}" cy="{y}" r="8" fill="none" stroke="#2ee6b6" stroke-opacity=".35"/></g>')
a('</g></g></svg>')

# HUD reticle top-right pinned
a('<svg x="0" y="0" width="100%" height="100%" viewBox="0 0 1000 620" preserveAspectRatio="xMaxYMin meet"><g transform="translate(770 30)" fill="none" stroke="#3cffc0">')
a('<circle cx="100" cy="100" r="96" stroke-opacity=".18"/>')
ticks = ''.join(f'M{100+88*math.cos(t):.1f} {100+88*math.sin(t):.1f}L{100+96*math.cos(t):.1f} {100+96*math.sin(t):.1f}' for t in [k*math.pi/36 for k in range(72)])
a(f'<path class="spin" d="{ticks}" stroke-opacity=".35"/>')
a('<circle class="spinr" cx="100" cy="100" r="70" stroke-opacity=".4" stroke-dasharray="30 8 4 8" stroke-width="2"/>')
a('<circle cx="100" cy="100" r="44" stroke-opacity=".25"/>')
hexd = 'M' + 'L'.join(f'{100+26*math.cos(math.pi/3*k+math.pi/6):.1f} {100+26*math.sin(math.pi/3*k+math.pi/6):.1f}' for k in range(6)) + 'Z'
a(f'<path class="spin" d="{hexd}" stroke-opacity=".6"/>')
a('<path d="M100 0v30M100 170v30M0 100h30M170 100h30" stroke-opacity=".5"/>')
a('<g transform="scale(.5)"><path class="sweep" d="M200 200L392 200A192 192 0 0 0 366 104Z" fill="url(#sweepg)" stroke="none"/></g>')
# readout bars
for k in range(5):
    w = random.randint(20, 70)
    a(f'<path d="M-10 {230+k*9}h{w}" stroke-opacity=".35" stroke-width="3"/>')
a('</g></svg>')

# scan band, scanlines, vignette
a(f'<rect class="scan" y="0" width="{W}" height="180" fill="url(#scanband)"/>')
a(f'<rect width="{W}" height="{H}" fill="url(#lines)" opacity=".5"/>')
a(f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')
a('</svg>')
svg = ''.join(o)
sys.stderr.write(f'{len(svg)} chars\n')
print('// Generated scene: night net-city, code rain, HUD reticle, data nodes.\nexport const SCENE = ' + json.dumps(svg) + '\n')
