#!/usr/bin/env python3
"""
Generates chair.svg: an empty wooden chair in a spare room, as seen by a
slightly elevated fixed camera.

The chair is modeled as a handful of 3D boxes, projected through a pinhole
camera, shaded by a single window light, and given a cast shadow by projecting
each part onto the floor along the light direction. No dependencies.

    python3 tools/make_chair.py > chair.svg
"""
import math
import random

W, H = 1280, 720
random.seed(7)

# ---------------------------------------------------------------- camera ----
CAM = (-34.0, 150.0, -215.0)      # cm; x right, y up, z into the room
TARGET = (10.0, 44.0, 18.0)
FOCAL = 1120.0                    # px


def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def norm(a):
    l = math.sqrt(dot(a, a)); return (a[0] / l, a[1] / l, a[2] / l)


FWD = norm(sub(TARGET, CAM))
RIGHT = norm(cross((0, 1, 0), FWD))
UP = cross(FWD, RIGHT)


def project(p):
    d = sub(p, CAM)
    x, y, z = dot(d, RIGHT), dot(d, UP), dot(d, FWD)
    return (W / 2 + FOCAL * x / z, H / 2 - FOCAL * y / z)


def depth(p):
    return dot(sub(p, CAM), FWD)


# ----------------------------------------------------------------- light ----
LIGHT = norm((-0.62, 0.70, -0.36))   # toward the window: left, up, front

# ----------------------------------------------------------------- chair ----
YAW = math.radians(-32)
CHAIR_AT = (18.0, 0.0, 10.0)


def place(p):
    x, y, z = p
    c, s = math.cos(YAW), math.sin(YAW)
    return (x * c + z * s + CHAIR_AT[0], y + CHAIR_AT[1], -x * s + z * c + CHAIR_AT[2])


def box(cx0, cz0, y0, cx1, cz1, y1, hw, hd):
    """A (possibly slanted) square-section post from (cx0,y0,cz0) up to (cx1,y1,cz1)."""
    bot = [(cx0 - hw, y0, cz0 - hd), (cx0 + hw, y0, cz0 - hd), (cx0 + hw, y0, cz0 + hd), (cx0 - hw, y0, cz0 + hd)]
    top = [(cx1 - hw, y1, cz1 - hd), (cx1 + hw, y1, cz1 - hd), (cx1 + hw, y1, cz1 + hd), (cx1 - hw, y1, cz1 + hd)]
    return [place(v) for v in bot + top]


def slab(x0, x1, y0, y1, z0, z1):
    return [place(v) for v in [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1),
                               (x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]]


LEAN = 6.0          # how far the back posts lean back at the top (cm)
TOP = 92.0


def lean(y):        # z offset of the back at height y
    return max(0.0, (y - 44.0) / (TOP - 44.0)) * LEAN


parts = []          # (verts, tone)  tone tweaks the wood a little per part
L = 1.8             # half leg thickness
# legs
for sx in (-1, 1):
    parts.append((box(sx * 18.5, -17.0, 0, sx * 18.0, -16.5, 43, L, L), 1.0))
    parts.append((box(sx * 18.5, 17.5, 0, sx * 18.5, 17.5 + LEAN, TOP, L, L), 1.0))
# seat (slightly overhanging, a touch lighter from wear)
parts.append((slab(-21.5, 21.5, 43.0, 46.0, -20.5, 20.0), 1.07))
# aprons under the seat
parts.append((slab(-17, 17, 36, 43, -17.6, -16.4), 0.95))
parts.append((slab(-17, 17, 36, 43, 16.9, 18.1), 0.95))
for sx in (-1, 1):
    parts.append((slab(sx * 18.9 - 0.6, sx * 18.9 + 0.6, 36, 43, -15.5, 15.5), 0.95))
# stretchers
for sx in (-1, 1):
    parts.append((slab(sx * 18.4 - 0.9, sx * 18.4 + 0.9, 13, 15.5, -15, 15.5), 0.97))
parts.append((slab(-17, 17, 19, 21, -17.0, -15.6), 0.97))
# back: top rail, lower rail, three spindles
parts.append((slab(-17.5, 17.5, 80, 90, 17.5 + lean(80) - 1.3, 17.5 + lean(90) + 1.3), 1.03))
parts.append((slab(-17.5, 17.5, 58, 62, 17.5 + lean(58) - 1.0, 17.5 + lean(62) + 1.0), 1.0))
for x in (-8.5, 0, 8.5):
    parts.append((box(x, 17.5 + lean(46), 46, x, 17.5 + lean(80), 80, 1.0, 0.9), 1.0))

FACES = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
WOOD = (178, 142, 102)


def face_normal(pts):
    n = cross(sub(pts[1], pts[0]), sub(pts[2], pts[0]))
    return norm(n)


def shade(rgb, k):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c * k))) for c in rgb)


def poly(pts):
    return " ".join("%.1f,%.1f" % project(p) for p in pts)


def hull(points):
    pts = sorted(set(points))
    if len(pts) < 3: return pts
    def cr(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


# ---------------------------------------------------------------- room ------
WALL_Z = 120.0
def hline(y, z):
    a, b = project((-900, y, z)), project((900, y, z))
    # extend to the image edges
    m = (b[1] - a[1]) / (b[0] - a[0])
    return (0.0, a[1] - m * a[0]), (float(W), a[1] + m * (W - a[0]))

FL0, FL1 = hline(0, WALL_Z)
BT0, BT1 = hline(11, WALL_Z - 1.5)
floor_y_img = max(FL0[1], FL1[1])

out = []
o = out.append
o(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
o('<title>An empty chair</title>')
o('''<defs>
  <linearGradient id="wall" x1="0" y1="0" x2="1" y2="0.25">
    <stop offset="0" stop-color="#d9d2c4"/><stop offset="0.45" stop-color="#cbc3b4"/><stop offset="1" stop-color="#a9a193"/>
  </linearGradient>
  <linearGradient id="wallv" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#000" stop-opacity="0.16"/><stop offset="0.5" stop-color="#000" stop-opacity="0"/>
    <stop offset="1" stop-color="#000" stop-opacity="0.10"/>
  </linearGradient>
  <linearGradient id="floor" x1="0" y1="0" x2="0.35" y2="1">
    <stop offset="0" stop-color="#5e4b3b"/><stop offset="1" stop-color="#3c2e23"/>
  </linearGradient>
  <linearGradient id="floorao" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#000" stop-opacity="0.35"/><stop offset="1" stop-color="#000" stop-opacity="0"/>
  </linearGradient>
  <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3.2"/></filter>
  <filter id="soft6" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="softer" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>
  <filter id="sensor" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="n"/>
    <feColorMatrix type="saturate" values="0"/>
  </filter>
</defs>''')

# wall + baseboard
o(f'<rect width="{W}" height="{H}" fill="url(#wall)"/>')
o(f'<rect width="{W}" height="{H}" fill="url(#wallv)"/>')
# window light on the wall (four panes, soft edges)
wl = [(-215, 165, WALL_Z), (-95, 185, WALL_Z), (-95, 70, WALL_Z), (-215, 50, WALL_Z)]
o(f'<g filter="url(#soft6)" opacity="0.34"><polygon points="{poly(wl)}" fill="#fff4dc"/></g>')
mx = [(-157, 176, WALL_Z), (-153, 176, WALL_Z), (-153, 60, WALL_Z), (-157, 60, WALL_Z)]
my = [(-215, 108, WALL_Z), (-95, 128, WALL_Z), (-95, 124, WALL_Z), (-215, 104, WALL_Z)]
o(f'<g filter="url(#soft)" opacity="0.30"><polygon points="{poly(mx)}" fill="#3a3027"/><polygon points="{poly(my)}" fill="#3a3027"/></g>')
def band(a0, a1, b0, b1):
    return f"{a0[0]:.1f},{a0[1]:.1f} {a1[0]:.1f},{a1[1]:.1f} {b1[0]:.1f},{b1[1]:.1f} {b0[0]:.1f},{b0[1]:.1f}"

o(f'<polygon points="{band(BT0, BT1, FL0, FL1)}" fill="#ddd6c9"/>')
o(f'<line x1="{BT0[0]}" y1="{BT0[1]:.1f}" x2="{BT1[0]}" y2="{BT1[1]:.1f}" stroke="#f1ece3" stroke-width="1.5" opacity="0.8"/>')

# floor + boards, clipped to the floor plane
floor_pts = f"{FL0[0]},{FL0[1]:.1f} {FL1[0]},{FL1[1]:.1f} {W},{H} 0,{H}"
o(f'<clipPath id="floorclip"><polygon points="{floor_pts}"/></clipPath>')
o('<g clip-path="url(#floorclip)">')
o(f'<polygon points="{floor_pts}" fill="url(#floor)"/>')
boards = []
BW = 14.0
for i in range(-40, 40):
    x = i * BW
    a, b = project((x, 0, WALL_Z)), project((x, 0, -175))
    boards.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
    # staggered butt joints
    z = WALL_Z - random.uniform(20, 140)
    while z > -175:
        p, q = project((x, 0, z)), project((x + BW, 0, z))
        boards.append(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}"/>')
        z -= random.uniform(90, 180)
o(f'<g stroke="#2a1f17" stroke-width="1" opacity="0.30">{"".join(boards)}</g>')
# per-board tone variation
tones = []
for i in range(-40, 40):
    x = i * BW
    q = [(x, 0, WALL_Z), (x + BW, 0, WALL_Z), (x + BW, 0, -175), (x, 0, -175)]
    tones.append(f'<polygon points="{poly(q)}" fill="{"#fff" if random.random() < .5 else "#000"}" opacity="{random.uniform(0.01, 0.035):.3f}"/>')
o("".join(tones))
o(f'<rect y="{floor_y_img - 30:.1f}" width="{W}" height="90" fill="url(#floorao)"/>')
o('</g>')
o(f'<line x1="{FL0[0]}" y1="{FL0[1]:.1f}" x2="{FL1[0]}" y2="{FL1[1]:.1f}" stroke="#000" stroke-width="2" opacity="0.25"/>')

# window light on the floor
fl = [(-230, 0, 60), (-110, 0, 70), (-40, 0, -70), (-170, 0, -95)]
o(f'<g filter="url(#soft6)" opacity="0.16"><polygon points="{poly(fl)}" fill="#ffe9c4"/></g>')

# ------------------------------------------------------------- shadows ------
def on_floor(p):
    t = p[1] / LIGHT[1]
    return (p[0] - LIGHT[0] * t, 0.0, p[2] - LIGHT[2] * t)


shadow_polys = []
for verts, _ in parts:
    pts2d = [project(on_floor(v)) for v in verts]
    shadow_polys.append(" ".join("%.1f,%.1f" % p for p in hull(pts2d)))
o('<g filter="url(#soft)" opacity="0.55" fill="#140d08">' +
  "".join(f'<polygon points="{s}"/>' for s in shadow_polys) + '</g>')
# contact occlusion under the seat
cx, cy = project(place((0, 0, 0)))
o(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="120" ry="30" fill="#140e09" opacity="0.35" filter="url(#softer)"/>')
for sx, sz in ((-18.5, -17), (18.5, -17), (-18.5, 17.5), (18.5, 17.5)):
    fx, fy = project(place((sx, 0, sz)))
    o(f'<ellipse cx="{fx:.1f}" cy="{fy:.1f}" rx="9" ry="3" fill="#000" opacity="0.5" filter="url(#soft)"/>')

# --------------------------------------------------------------- chair ------
def centroid(vs):
    return tuple(sum(v[i] for v in vs) / len(vs) for i in range(3))


faces = []
for verts, tone in parts:
    for f in FACES:
        pts = [verts[i] for i in f]
        n = face_normal(pts)
        c = centroid(pts)
        if dot(n, sub(CAM, c)) <= 0:
            continue
        lit = max(0.0, dot(n, LIGHT))
        k = (0.52 + 0.62 * lit) * tone
        faces.append((depth(centroid(verts)), depth(c), pts, shade(WOOD, k)))

faces.sort(key=lambda f: (-f[0], -f[1]))
o('<g stroke-linejoin="round">')
for _, _, pts, col in faces:
    o(f'<polygon points="{poly(pts)}" fill="{col}" stroke="{col}" stroke-width="0.7"/>')
o('</g>')

# faint grain along the seat top
seat_top = [place(v) for v in [(-21.5, 46, -20.5), (21.5, 46, -20.5), (21.5, 46, 20), (-21.5, 46, 20)]]
grain = []
for i in range(1, 14):
    t = i / 14 + random.uniform(-0.015, 0.015)
    a = tuple(seat_top[0][j] + (seat_top[1][j] - seat_top[0][j]) * t for j in range(3))
    b = tuple(seat_top[3][j] + (seat_top[2][j] - seat_top[3][j]) * t for j in range(3))
    pa, pb = project(a), project(b)
    grain.append(f'<line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}"/>')
o(f'<g stroke="#5a3d24" stroke-width="0.6" opacity="0.09">{"".join(grain)}</g>')

# ---------------------------------------------------------- camera feel -----
o(f'<rect width="{W}" height="{H}" filter="url(#sensor)" opacity="0.07"/>')
o('</svg>')
print("\n".join(out))
