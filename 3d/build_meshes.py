# Test meshes for trying materials on the rubric icon (Cafés), built from the real Hugeicons icon.
# Run headless:  /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P 3d/build_meshes.py
# Writes 3d/lansy-3d-test.blend, check renders in 3d/check/, and a mesh report 3d/check/report.json.
#
# The icon: Hugeicons coffee-01, stroke rounded (core-free-icons 4.3.3, MIT): a 24-unit grid, strokes 1.5 wide, round caps.
# Three compositions, each its own collection, parts as separate objects with their own material slots:
#   disc        a coin with the icon in domed strokes (disc_icon_bevel)
#   disc_flat   the same coin with the icon as straight-walled strips, no chamfer (disc_icon_flat), next to it
#   icon_alone  the coin's relief icon standing free, the same mesh (flat back)
#   cup         a modelled cup with the icon's proportions: body, rim band, domed lid
# Every stroke shape is one closed surface: the strokes are swept with their own round caps, then joined by an exact boolean
# union, so glass refracts through one skin with no faces inside. Normals are recalculated outward and checked.
import bpy, bmesh, math, json, os, re
from mathutils import Vector, Matrix

ROOT = os.path.dirname(os.path.abspath(__file__))
HDRI = ROOT + '/hdri/studio_small_09_2k.hdr'
OUT_BLEND = ROOT + '/lansy-3d-test.blend'
CHECK = ROOT + '/check'
os.makedirs(CHECK, exist_ok=True)

# ---- the icon, verbatim from @hugeicons/core-free-icons/dist/esm/Coffee01Icon.js
ICON_PATHS = [
    "M5 7L6.7602 17.4048C7.06616 19.2134 7.21914 20.1177 7.76007 20.7417C9.21438 22.4194 14.7856 22.4194 16.2399 20.7417C16.7809 20.1177 16.9338 19.2134 17.2398 17.4048L19 7",
    "M5 7L5.74278 5.2876C6.35168 3.88385 6.65613 3.18197 7.29101 2.7856C8.88049 1.79324 14.9452 1.68444 16.709 2.7856C17.3439 3.18197 17.6483 3.88385 18.2572 5.2876L19 7",
    "M4 7H20",
]
ICON_ELLIPSE = (12, 14.5, 2, 2.5)
STROKE = 1.5

def parse_path(d):   # M, L, H, V, C (absolute) → a list of sampled points
    toks = re.findall(r'[MLHVCZ]|-?\d*\.?\d+(?:e-?\d+)?', d)
    pts, i, cmd, cur = [], 0, None, Vector((0, 0))
    def num():
        nonlocal i; v = float(toks[i]); i += 1; return v
    while i < len(toks):
        if toks[i] in 'MLHVCZ': cmd = toks[i]; i += 1; continue
        if cmd == 'M': cur = Vector((num(), num())); pts.append(cur.copy()); cmd = 'L'
        elif cmd == 'L':
            p = Vector((num(), num())); n = max(1, int((p - cur).length / .25))
            pts += [cur.lerp(p, k / n) for k in range(1, n + 1)]; cur = p
        elif cmd == 'H':
            p = Vector((num(), cur.y)); n = max(1, int((p - cur).length / .25))
            pts += [cur.lerp(p, k / n) for k in range(1, n + 1)]; cur = p
        elif cmd == 'V':
            p = Vector((cur.x, num())); n = max(1, int((p - cur).length / .25))
            pts += [cur.lerp(p, k / n) for k in range(1, n + 1)]; cur = p
        elif cmd == 'C':
            c1, c2, p = Vector((num(), num())), Vector((num(), num())), Vector((num(), num()))
            n = 32
            for k in range(1, n + 1):
                t = k / n; u = 1 - t
                pts.append(u**3 * cur + 3 * u * u * t * c1 + 3 * u * t * t * c2 + t**3 * p)
            cur = p
    out = [pts[0]]
    for p in pts[1:]:
        if (p - out[-1]).length > 1e-6: out.append(p)
    return out

def ellipse_pts(cx, cy, rx, ry, n=96):
    return [Vector((cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n))) for k in range(n)]

def to_world(p, s, z=0.0):   # icon units (svg, y down) → metres, centred on the icon's middle, y up
    return Vector(((p.x - 12) * s, -(p.y - 12) * s, z))

def trim_start(pts, d):   # move the first point d units along the path (so a round cap is not tangent to the rim it ends in)
    acc = 0
    for i in range(1, len(pts)):
        L = (pts[i] - pts[i - 1]).length
        if acc + L >= d: return [pts[i - 1].lerp(pts[i], (d - acc) / L)] + pts[i:]
        acc += L
    return pts

def tangents(P, closed):
    T = []
    for i in range(len(P)):
        a = P[i - 1] if (i > 0 or closed) else P[i]
        b = P[(i + 1) % len(P)] if (i < len(P) - 1 or closed) else P[i]
        if i == 0 and not closed: a = P[0]; b = P[1]
        if i == len(P) - 1 and not closed: a = P[-2]; b = P[-1]
        t = (b - a); t.z = 0; T.append(t.normalized())
    return T

def sweep_tube(bm, P, r, closed, seg=32, cap=10):   # a round tube with hemispherical caps; P in metres, in a plane z = const
    Z = Vector((0, 0, 1)); T = tangents(P, closed); rings = []
    def ring(c, t, rad):
        n = Z.cross(t).normalized()
        return [bm.verts.new(c + rad * (math.cos(2 * math.pi * k / seg) * n + math.sin(2 * math.pi * k / seg) * Z)) for k in range(seg)]
    def bridge(A, B):
        for k in range(seg): bm.faces.new((A[k], A[(k + 1) % seg], B[(k + 1) % seg], B[k]))
    def capend(c, t, sign):   # hemisphere: shrinking rings out along ±t, ending in a pole
        out = []
        for k in range(1, cap):
            ph = math.pi / 2 * k / cap
            out.append(ring(c + sign * t * r * math.sin(ph), t, r * math.cos(ph)))
        pole = bm.verts.new(c + sign * t * r)
        return out, pole
    for i, c in enumerate(P):
        rings.append(ring(c, T[i], r))
    for i in range(len(rings) - 1): bridge(rings[i], rings[i + 1])
    if closed: bridge(rings[-1], rings[0]); return
    # end caps
    for end, sign in ((0, -1), (len(P) - 1, 1)):
        rs, pole = capend(P[end], T[end], sign)
        chain = [rings[end]] + rs
        for a, b in zip(chain, chain[1:]):
            if sign > 0: bridge(a, b)
            else: bridge(b, a)
        last = chain[-1]
        for k in range(seg):
            f = (last[k], last[(k + 1) % seg], pole) if sign > 0 else (last[(k + 1) % seg], last[k], pole)
            bm.faces.new(f)

def sweep_strip(bm, P, w, z0, z1, closed, arc=24):   # a strip with straight walls and a flat top, round ends in plan, no chamfer
    Z = Vector((0, 0, 1)); T = tangents(P, closed); L, R = [], []
    for i, c in enumerate(P):
        n = Z.cross(T[i]).normalized()
        if 0 < i < len(P) - 1 or closed:   # keep the wall width through a bend (miter)
            t0 = (P[i] - P[i - 1]).normalized()
            m = 1 / max(.5, abs(T[i].dot(t0)))
        else: m = 1
        a, b = c + n * w / 2 * m, c - n * w / 2 * m
        L.append((bm.verts.new(Vector((a.x, a.y, z0))), bm.verts.new(Vector((a.x, a.y, z1)))))
        R.append((bm.verts.new(Vector((b.x, b.y, z0))), bm.verts.new(Vector((b.x, b.y, z1)))))
    N = len(P); rng = range(N) if closed else range(N - 1)
    for i in rng:
        j = (i + 1) % N
        bm.faces.new((L[i][0], L[j][0], L[j][1], L[i][1]))        # left wall
        bm.faces.new((R[j][0], R[i][0], R[i][1], R[j][1]))        # right wall
        bm.faces.new((L[i][1], L[j][1], R[j][1], R[i][1]))        # top
        bm.faces.new((R[i][0], R[j][0], L[j][0], L[i][0]))        # bottom
    if closed: return
    for end, sign in ((0, -1), (N - 1, 1)):   # a half-disc end: an arc from the left edge round the front to the right edge
        c = P[end]; t = T[end] * sign; n = Z.cross(T[end]).normalized()
        A = []
        for k in range(1, arc):
            th = math.pi * k / arc
            v = (math.cos(th) * n + math.sin(th) * t) if sign > 0 else (math.cos(th) * (-n) + math.sin(th) * t)
            q = c + w / 2 * v
            A.append((bm.verts.new(Vector((q.x, q.y, z0))), bm.verts.new(Vector((q.x, q.y, z1)))))
        first, last = (L[end], R[end]) if sign > 0 else (R[end], L[end])
        chain = [first] + A + [last]
        for a, b in zip(chain, chain[1:]):
            bm.faces.new((a[0], b[0], b[1], a[1]))
        top = [v[1] for v in chain]; bot = [v[0] for v in reversed(chain)]
        bm.faces.new(top); bm.faces.new(bot)

def sweep_profile(bm, P, Q, closed, capseg=24):
    # sweep a closed cross-section Q [(across, z)] along P; Q is symmetric with its top centre at Q[mid] (len = 2·mid + 1).
    # Open ends get a cap made by turning Q's half about the end point: round in plan, the same profile all round
    Z = Vector((0, 0, 1)); T = tangents(P, closed); nq = len(Q); mid = nq // 2; rings = []
    for i, c in enumerate(P):
        n = Z.cross(T[i]).normalized(); m = 1
        if 0 < i < len(P) - 1 or closed:   # keep the width through a bend (miter)
            m = 1 / max(.5, abs(T[i].dot((P[i] - P[i - 1]).normalized())))
        rings.append([bm.verts.new(Vector((c.x + n.x * x * m, c.y + n.y * x * m, z))) for (x, z) in Q])
    def bridge(A, B):
        for k in range(nq): bm.faces.new((A[k], A[(k + 1) % nq], B[(k + 1) % nq], B[k]))
    for i in range(len(P) - 1): bridge(rings[i], rings[i + 1])
    if closed: bridge(rings[-1], rings[0]); return
    for end, sign in ((0, -1), (len(P) - 1, 1)):
        c = P[end]; t = T[end] * sign; n = Z.cross(T[end]).normalized(); ring = rings[end]; half = Q[mid:]
        cols = [[ring[mid + j] for j in range(len(half))]]
        for k in range(1, capseg):
            th = math.pi * k / capseg; v = math.cos(th) * n + math.sin(th) * t
            cols.append([ring[mid]] + [bm.verts.new(Vector((c.x + v.x * x, c.y + v.y * x, z))) for (x, z) in half[1:]])
        cols.append([ring[mid - j] for j in range(len(half))])
        for A, B in zip(cols, cols[1:]):
            bm.faces.new((A[0], A[1], B[1]))
            for j in range(1, len(half) - 1): bm.faces.new((A[j], A[j + 1], B[j + 1], B[j]))
        bm.faces.new([col[-1] for col in cols])   # the bottom half-disc

def fillet_poly(pts, radii, n=10):   # round the corners of a 2D polyline: radii {corner index: radius}
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        r = radii.get(i, 0); b = Vector(pts[i])
        if not r: out.append(pts[i]); continue
        u = (Vector(pts[i - 1]) - b).normalized(); w = (Vector(pts[i + 1]) - b).normalized()
        ang = math.acos(max(-1, min(1, u.dot(w)))); d = r / math.tan(ang / 2)
        ctr = b + (u + w).normalized() * r / math.sin(ang / 2); p1, p2 = b + u * d, b + w * d
        a1 = math.atan2(p1.y - ctr.y, p1.x - ctr.x); a2 = math.atan2(p2.y - ctr.y, p2.x - ctr.x)
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        out += [(ctr.x + r * math.cos(a1 + da * k / n), ctr.y + r * math.sin(a1 + da * k / n)) for k in range(n + 1)]
    return out + [pts[-1]]

def support(pts, eps=.0001, minlen=.001):
    # supporting points 0.1 mm in from both ends of every long straight run of a profile, so smooth shading keeps flat and
    # straight surfaces flat (otherwise a fillet's tilted vertex normals bleed across the whole long face next to it)
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        A, B = Vector(a), Vector(b); L = (B - A).length
        if L > minlen: d = (B - A) / L; out += [tuple(A + d * eps), tuple(B - d * eps)]
        out.append(b)
    return out

def icon_outline(s, sw, g=.00004):
    # The icon's true outline at stroke width sw (icon units): the distance field to the icon's centre lines on a g-metre grid,
    # contoured at half the stroke (marching squares). Round caps and joins, tight corners offset correctly, strokes merged.
    # Returns the closed outline loops (2D, metres) and inside(q), a bilinear lookup of the field
    import numpy as np
    h = sw / 2 * s
    lines = [[to_world(p, s) for p in parse_path(d)] for d in ICON_PATHS]
    E = [to_world(p, s) for p in ellipse_pts(*ICON_ELLIPSE, n=256)]   # for the bounds only: the oval gets its own field below
    segs = [(L[k], L[k + 1]) for L in lines for k in range(len(L) - 1) if (L[k + 1] - L[k]).length > 1e-9]
    allp = [q for L in lines for q in L] + E
    x0 = min(q.x for q in allp) - h - 4 * g; y0 = min(q.y for q in allp) - h - 4 * g
    nx = int((max(q.x for q in allp) + h + 4 * g - x0) / g) + 1; ny = int((max(q.y for q in allp) + h + 4 * g - y0) / g) + 1
    xs = x0 + g * np.arange(nx); ys = y0 + g * np.arange(ny)
    D2 = np.full((nx, ny), (h + 8 * g) ** 2)
    for A, B in segs:   # only the box round each segment can be nearer than h
        i0 = max(0, int((min(A.x, B.x) - h - 8 * g - x0) / g)); i1 = min(nx, int((max(A.x, B.x) + h + 8 * g - x0) / g) + 2)
        j0 = max(0, int((min(A.y, B.y) - h - 8 * g - y0) / g)); j1 = min(ny, int((max(A.y, B.y) + h + 8 * g - y0) / g) + 2)
        X = xs[i0:i1, None]; Y = ys[None, j0:j1]; dx, dy = B.x - A.x, B.y - A.y
        t = np.clip(((X - A.x) * dx + (Y - A.y) * dy) / (dx * dx + dy * dy), 0, 1)
        np.minimum(D2[i0:i1, j0:j1], (X - A.x - t * dx) ** 2 + (Y - A.y - t * dy) ** 2, out=D2[i0:i1, j0:j1])
    F = h - np.sqrt(D2)   # > 0 inside
    # the oval is not in this field: icon_relief adds it as its own ring (oval_ring)
    def inside(q):
        fi = (q.x - x0) / g; fj = (q.y - y0) / g; i_, j_ = int(fi), int(fj)
        if not (0 <= i_ < nx - 1 and 0 <= j_ < ny - 1): return False
        u, v = fi - i_, fj - j_
        return (F[i_, j_] * (1 - u) * (1 - v) + F[i_ + 1, j_] * u * (1 - v) + F[i_, j_ + 1] * (1 - u) * v + F[i_ + 1, j_ + 1] * u * v) > 0
    In = F > 0
    mixed = np.argwhere((In[:-1, :-1] != In[1:, :-1]) | (In[:-1, :-1] != In[:-1, 1:]) | (In[:-1, :-1] != In[1:, 1:]))
    pt = {}
    def cross(key):   # the crossing on a grid edge: ('x', i, j) from (i, j) to (i+1, j); ('y', i, j) from (i, j) to (i, j+1)
        if key not in pt:
            k, i_, j_ = key; a_ = F[i_, j_]; b_ = F[i_ + 1, j_] if k == 'x' else F[i_, j_ + 1]; t_ = a_ / (a_ - b_)
            pt[key] = Vector((xs[i_] + g * t_, ys[j_])) if k == 'x' else Vector((xs[i_], ys[j_] + g * t_))
        return key
    adj = {}
    def link(a_, b_): adj.setdefault(a_, []).append(b_); adj.setdefault(b_, []).append(a_)
    for i_, j_ in mixed:
        c00, c10, c11, c01 = In[i_, j_], In[i_ + 1, j_], In[i_ + 1, j_ + 1], In[i_, j_ + 1]
        e = [('x', i_, j_), ('y', i_ + 1, j_), ('x', i_, j_ + 1), ('y', i_, j_)]
        hit = [k for k, (p_, q_) in enumerate(((c00, c10), (c10, c11), (c01, c11), (c00, c01))) if p_ != q_]
        if len(hit) == 2: link(cross(e[hit[0]]), cross(e[hit[1]])); continue
        centre = (F[i_, j_] + F[i_ + 1, j_] + F[i_ + 1, j_ + 1] + F[i_, j_ + 1]) > 0
        if (c00 and centre) or (not c00 and not centre): pairs = ((0, 1), (2, 3))   # a saddle: cut off c10 and c01
        else: pairs = ((3, 0), (1, 2))                                                # cut off c00 and c11
        for a_, b_ in pairs: link(cross(e[a_]), cross(e[b_]))
    loops, seen = [], set()
    for v0 in adj:
        if v0 in seen: continue
        loop, prev, cur = [v0], None, v0; seen.add(v0)
        while True:
            nxt = next((w for w in adj[cur] if w != prev and (w == v0 or w not in seen)), None)
            if nxt is None or nxt == v0: break
            loop.append(nxt); seen.add(nxt); prev, cur = cur, nxt
        if len(loop) > 8: loops.append([pt[k] for k in loop])
    return loops, inside, h

def icon_relief(loops, inside, h, z0, zw, a, coll, name, flat=False, ds=.00012, both=False):
    # both=True: rounded on both sides (the back the front mirrored about the wall's middle), for an icon seen from every side
    # The outline raised: straight walls from z0 to zw, then either a flat top (flat) or a rounded relief whose height at a point
    # depends on its distance d to the outline: zw + a·√(1 − (1 − d/h)²), flat past d = h. Joints become clean ridges, as an
    # extruded SVG with a round bevel. The top is a constrained Delaunay mesh, dense near the outline where the relief is steep
    from mathutils import kdtree, geometry
    def resample(L, step):
        out, carry = [], 0.0
        for i in range(len(L)):
            A, B = L[i], L[(i + 1) % len(L)]; seg = (B - A).length; t = carry
            while t < seg: out.append(A.lerp(B, t / seg)); t += step
            carry = t - seg
        return out
    kd_pts = [q for L in loops for q in resample(L, ds / 6)]
    kd = kdtree.KDTree(len(kd_pts))
    for i, q in enumerate(kd_pts): kd.insert((q.x, q.y, 0), i)
    kd.balance()
    def dist(q): return kd.find((q.x, q.y, 0))[2]
    B = [resample(L, ds) for L in loops]
    pts, cells, CELL = [], {}, ds * .2
    def add(q, force=False):
        key = (int(q.x // CELL), int(q.y // CELL))
        if not force:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for r in cells.get((key[0] + dx, key[1] + dy), ()):
                        if (pts[r] - q).length < CELL: return
        cells.setdefault(key, []).append(len(pts)); pts.append(q)
    edges = []
    for L in B:   # the outline itself, kept as constraint edges
        i0 = len(pts)
        for q in L: add(q, True)
        edges += [(i0 + k, i0 + (k + 1) % len(L)) for k in range(len(L))]
    nb = len(pts)
    if not flat:
        rings = [d * h / .0048 for d in (.00002, .00005, .0001, .00016, .00024, .00034, .00046, .0006, .00076, .00095, .00117, .00142, .0017, .002, .00235, .0027, .0031, .0035, .0039, .0043, .0047)]
        for L in B:   # offset rings inward, dense where the relief is steep; dropped past the middle of a stroke
            for k, q in enumerate(L):
                t = (L[(k + 1) % len(L)] - L[k - 1]).normalized(); n = Vector((-t.y, t.x))
                if not inside(q + n * 1e-5): n = -n
                for d in rings:
                    r = q + n * d
                    if abs(dist(r) - d) < .2 * d + 1e-6 and inside(r): add(r)
        lo = Vector((min(q.x for q in pts), min(q.y for q in pts))); hi = Vector((max(q.x for q in pts), max(q.y for q in pts)))
        gg = ds * 2; x = lo.x
        while x < hi.x:   # a coarse grid for the flat-ish middle
            y = lo.y
            while y < hi.y:
                q = Vector((x, y))
                if inside(q) and dist(q) > rings[8]: add(q)
                y += gg
            x += gg
    def zf(d): t = min(d / h, 1); return zw + a * math.sqrt(max(0, 1 - (1 - t) ** 2))
    out = bmesh.new()
    def tri(P, z_of):   # CDT with the outline as constraints; returns the vert of each input point
        V, Eo, Fc, OV, OE, _ = geometry.delaunay_2d_cdt(P, edges, [], 0, 1e-10, True)
        bv = [out.verts.new((V[j].x, V[j].y, z_of(OV[j], V[j]))) for j in range(len(V))]
        of = {}
        for j, o in enumerate(OV):
            for i in o: of[i] = bv[j]
        # which triangles are inside: a flood fill from the hull, flipping in/out at every outline edge crossed
        cons = {frozenset(Eo[k]) for k in range(len(Eo)) if OE[k]}
        ef = {}
        for fi, f in enumerate(Fc):
            for k in range(len(f)): ef.setdefault(frozenset((f[k], f[(k + 1) % len(f)])), []).append(fi)
        state = [None] * len(Fc); dq = []
        for key, fl in ef.items():
            if len(fl) == 1 and state[fl[0]] is None: state[fl[0]] = key in cons; dq.append(fl[0])
        while dq:
            fi = dq.pop(); f = Fc[fi]
            for k in range(len(f)):
                key = frozenset((f[k], f[(k + 1) % len(f)]))
                for g2 in ef[key]:
                    if state[g2] is None: state[g2] = state[fi] ^ (key in cons); dq.append(g2)
        for fi, f in enumerate(Fc):
            if state[fi]: out.faces.new([bv[j] for j in f])
        return of
    zt = (lambda o, q: zw) if flat else (lambda o, q: zw if any(i < nb for i in o) else zf(dist(q)))
    topv = tri(pts, zt)
    zc = (z0 + zw) / 2
    botv = tri(pts, lambda o, q: 2 * zc - zt(o, q)) if both else tri(pts[:nb], lambda o, q: z0)
    for (i, k) in edges: out.faces.new((botv[i], botv[k], topv[k], topv[i]))   # the walls
    oval_ring(out, h, z0, zw, a, flat, both=both)
    finish(out)
    return new_obj(name, out, coll)

def oval_ring(bm, h, z0, zw, a, flat, s=.004, nu=256, nq=12, both=False):
    # the icon's oval as one clean ring: the stroke's own cross-section (straight walls z0→zw, a half-ellipse dome of height a,
    # or a flat top) swept round the ellipse with quads. Across the band it runs radially between two ellipses, radii ± half
    # the stroke, so the hole stays an ellipse at any stroke (a true offset would pinch it into a lemon). A closed shell of its own
    ecx, ecy, erx, ery = ICON_ELLIPSE; c = to_world(Vector((ecx, ecy)), s); erx *= s; ery *= s
    Q = [(h, z0), (-h, z0)]                                                    # the bottom, outside to inside
    if flat: Q += [(-h, zw), (h, zw)]
    else:
        Q += [(-h, zw)] + [(-h * math.cos(math.pi * k / (2 * nq)) if k < nq else h * math.cos(math.pi * (2 * nq - k) / (2 * nq)),
                            zw + a * math.sin(math.pi * k / (2 * nq))) for k in range(1, 2 * nq)] + [(h, zw)]
    if both and not flat:   # the back: the top's profile mirrored about the wall's middle
        T = Q[2:]; zc = (z0 + zw) / 2; Q = [(x, 2 * zc - z) for (x, z) in reversed(T)] + T
    rings = []
    for u in range(nu):
        th = 2 * math.pi * u / nu; ct, st = math.cos(th), math.sin(th)
        rings.append([bm.verts.new((c.x + (erx + x) * ct, c.y + (ery + x) * st, z)) for (x, z) in Q])
    n = len(Q)
    for u in range(nu):
        A, B = rings[u], rings[(u + 1) % nu]
        for k in range(n): bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))

def icon_profile(s, Q, coll, name):   # the icon as strokes of cross-section Q (metres), strokes joined into one closed surface
    parts = []
    for k, d in enumerate(ICON_PATHS):
        P = parse_path(d)
        if k < 2: P = trim_start(P, .2); P = list(reversed(trim_start(list(reversed(P)), .2)))
        bm = bmesh.new(); sweep_profile(bm, [to_world(p, s) for p in P], Q, False); finish(bm)
        parts.append(new_obj(f'_{name}{k}', bm, coll))
    bm = bmesh.new(); sweep_profile(bm, [to_world(p, s) for p in ellipse_pts(*ICON_ELLIPSE)], Q, True); finish(bm)
    ring = new_obj(f'_{name}e', bm, coll)
    o = union(parts, name, coll)
    bm = bmesh.new(); bm.from_mesh(o.data); bm.from_mesh(ring.data); finish(bm); bm.to_mesh(o.data); bm.free()
    bpy.data.objects.remove(ring, do_unlink=True)
    return o

def finish(bm):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges)   # slivers under 1 µm left by the boolean
    for _ in range(3):   # zero-area slivers whose edges are long (collinear points): collapse each one's shortest edge
        bad = [f for f in bm.faces if f.is_valid and f.calc_area() < 1e-12]
        if not bad: break
        bmesh.ops.collapse(bm, edges=list({min(f.edges, key=lambda e: e.calc_length()) for f in bad}))
    bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context='EDGES')   # loose µm edges, ditto
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

def new_obj(name, bm, coll):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.validate()
    o = bpy.data.objects.new(name, me); coll.objects.link(o); return o

def union(objs, name, coll):   # exact boolean union of closed shells into one closed surface
    base = objs[0]; base.name = name
    for o in objs[1:]:
        m = base.modifiers.new('u', 'BOOLEAN'); m.operation = 'UNION'; m.solver = 'EXACT'; m.object = o
        with bpy.context.temp_override(object=base, active_object=base, selected_objects=[base]):
            bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.data.objects.remove(o, do_unlink=True)
    bm = bmesh.new(); bm.from_mesh(base.data); finish(bm); bm.to_mesh(base.data); bm.free()
    return base

def icon_tubes(s, zc, coll, name):
    r = STROKE / 2 * s; parts = []
    for k, d in enumerate(ICON_PATHS):
        P = parse_path(d)
        if k < 2:   # body and lid end inside the rim bar: pull their ends in a little so the caps cross the rim, not touch it
            P = trim_start(P, .2); P = list(reversed(trim_start(list(reversed(P)), .2)))
        bm = bmesh.new(); sweep_tube(bm, [to_world(p, s, zc) for p in P], r, False); finish(bm)
        parts.append(new_obj(f'_{name}{k}', bm, coll))
    bm = bmesh.new(); sweep_tube(bm, [to_world(p, s, zc) for p in ellipse_pts(*ICON_ELLIPSE)], r, True); finish(bm)
    ring = new_obj(f'_{name}e', bm, coll)
    o = union(parts, name, coll)
    # the oval is separate from the rest; join it as a second shell of the same object
    bm = bmesh.new(); bm.from_mesh(o.data); bm.from_mesh(ring.data); finish(bm); bm.to_mesh(o.data); bm.free()
    bpy.data.objects.remove(ring, do_unlink=True)
    return o

def icon_strips(s, z0, z1, coll, name):
    w = STROKE * s; parts = []
    for k, d in enumerate(ICON_PATHS):
        P = parse_path(d)
        if k < 2: P = trim_start(P, .2); P = list(reversed(trim_start(list(reversed(P)), .2)))
        bm = bmesh.new(); sweep_strip(bm, [to_world(p, s) for p in P], w, z0, z1, False); finish(bm)
        parts.append(new_obj(f'_{name}{k}', bm, coll))
    bm = bmesh.new(); sweep_strip(bm, [to_world(p, s) for p in ellipse_pts(*ICON_ELLIPSE)], w, z0, z1, True); finish(bm)
    ring = new_obj(f'_{name}e', bm, coll)
    o = union(parts, name, coll)
    bm = bmesh.new(); bm.from_mesh(o.data); bm.from_mesh(ring.data); finish(bm); bm.to_mesh(o.data); bm.free()
    bpy.data.objects.remove(ring, do_unlink=True)
    return o

def revolve(profile, seg, name, coll, closed_loop=False):
    # profile: [(r, z)], from the axis round to the axis (open) or a closed loop off the axis; points with r == 0 become poles
    bm = bmesh.new(); rings = []
    for (r, z) in profile:
        if r < 1e-9: rings.append([bm.verts.new((0, 0, z))])
        else: rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), z)) for k in range(seg)])
    pairs = list(zip(rings, rings[1:])) + ([(rings[-1], rings[0])] if closed_loop else [])
    for A, B in pairs:
        if len(A) == 1 and len(B) == 1: continue
        if len(A) == 1:
            for k in range(seg): bm.faces.new((A[0], B[(k + 1) % seg], B[k]))
        elif len(B) == 1:
            for k in range(seg): bm.faces.new((A[k], A[(k + 1) % seg], B[0]))
        else:
            for k in range(seg): bm.faces.new((A[k], A[(k + 1) % seg], B[(k + 1) % seg], B[k]))
    finish(bm); return new_obj(name, bm, coll)

def arc(cx, cz, rad, a0, a1, n=12):   # points on a fillet, angles in degrees, in the (r, z) plane
    return [(cx + rad * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cz + rad * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]

def check(o):   # the mesh report: closed, consistent, outward, no degenerate faces
    bm = bmesh.new(); bm.from_mesh(o.data)
    nonman = sum(1 for e in bm.edges if not e.is_manifold)
    boundary = sum(1 for e in bm.edges if e.is_boundary)
    loose = sum(1 for v in bm.verts if not v.link_faces)
    tiny = sum(1 for f in bm.faces if f.calc_area() < 1e-12)
    flipped = 0
    for e in bm.edges:   # two faces on an edge must walk it in opposite directions
        if len(e.link_loops) == 2:
            l1, l2 = e.link_loops
            if l1.vert == l2.vert: flipped += 1
    vol = bm.calc_volume(signed=True)
    r = dict(object=o.name, verts=len(bm.verts), faces=len(bm.faces), non_manifold_edges=nonman, boundary_edges=boundary,
             loose_verts=loose, degenerate_faces=tiny, inconsistent_edges=flipped, volume_cm3=round(vol * 1e6, 3),
             normals='outward' if vol > 0 else 'INWARD', dims_mm=[round(d * 1000, 1) for d in o.dimensions])
    r['ok'] = nonman == 0 and boundary == 0 and loose == 0 and tiny == 0 and flipped == 0 and vol > 0
    bm.free(); return r

def smooth(o, angle):
    for p in o.data.polygons: p.use_smooth = True
    try:
        with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o], selected_editable_objects=[o]):
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
    except Exception: pass

def mat(name, rgb, rough=.5):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough
    return m

def place(objs, M):   # apply a transform to mesh data, then set the lowest point on the ground (z = 0)
    for o in objs: o.data.transform(M)
    minz = min((o.matrix_world @ v.co).z for o in objs for v in o.data.vertices)   # by the vertices: bound_box is stale here
    for o in objs: o.data.transform(Matrix.Translation((0, 0, -minz)))

# ---- scene
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
def coll(name):
    c = bpy.data.collections.new(name); sc.collection.children.link(c); return c

M_BASE, M_ICON = mat('M_base', (.8, .8, .8), .45), mat('M_icon', (.35, .35, .35), .35)
M_BODY, M_RIM, M_LID = mat('M_cup_body', (.85, .85, .85), .6), mat('M_cup_rim', (.5, .5, .5), .4), mat('M_cup_lid', (.3, .3, .3), .25)

# 1) disc: Ø130 × 6.7 mm; the back edge rounded (3 mm), the front edge a 2 mm 45° chamfer with soft 0.6 mm edges.
#    The icon at 4 mm per unit, its strokes made bolder for the coin (2.4 units = 9.6 mm, as in the reference render), on two coins: flat = straight walls and a flat top, 3 mm up, sharp edges;
#    bevel = the flat icon's outline raised as a rounded relief (low walls, a near half-round top, clean ridges at joints), 4.9 mm up. Both sit 0.5 mm into the face
S = .004; R, Tk, CH = .065, .020 / 3, .002   # the coin 6.7 mm thick
cd = coll('disc')
disc = revolve(support(fillet_poly([(0, 0), (R, 0), (R, Tk - CH), (R - CH, Tk), (0, Tk)], {1: .003, 2: .0006, 3: .0006})), 192, 'disc_base', cd)
SW = 2.4   # the coin's stroke, icon units
h, z0 = SW / 2 * S, Tk - .0005
zw, a = Tk + .0006, .9 * h
cf = coll('disc_flat')
disc2 = bpy.data.objects.new('disc_base_flat', disc.data.copy()); cf.objects.link(disc2)
loops, inside, _ = icon_outline(S, SW)                                        # one outline for both coins
flat = icon_relief(loops, inside, h, z0, Tk + .003, 0, cf, 'disc_icon_flat', flat=True)
bevel = icon_relief(loops, inside, h, z0, zw, a, cd, 'disc_icon_bevel')        # the same outline, raised as a rounded relief
# a round-tube icon for compositions: stroke 2.0 units at 4 mm (a little bolder than drawn, as in the reference), a half-round top on a short wall,
# so it reads as tubes; joints clean as on the coin. Same frame as the coin's icon, hidden in the coin renders
SW_R = 2.0; loops_r, inside_r, h_r = icon_outline(S, SW_R)
iround = icon_relief(loops_r, inside_r, h_r, z0, z0 + .5 * h_r, h_r, cd, 'disc_icon_round')
ifull = icon_relief(loops, inside, h, z0, zw, a, cd, 'disc_icon_full', both=True)   # the coin's icon, rounded front and back
alone_me = bevel.data.copy()                                                   # the icon alone is this very mesh
place([disc, bevel, iround, ifull, disc2, flat], Matrix.Rotation(math.radians(78), 4, 'X'))   # standing, leaning back 12°, face to the camera (−Y)
for o in (disc2, flat): o.data.transform(Matrix.Translation((-.2, 0, 0)))      # the flat coin stands 20 cm to the left
disc.data.materials.append(M_BASE); bevel.data.materials.append(M_ICON); flat.data.materials.append(M_ICON)
smooth(disc, 50); smooth(disc2, 50); smooth(bevel, 50); smooth(flat, 30); smooth(iround, 50); iround.data.materials.append(M_ICON); smooth(ifull, 50); ifull.data.materials.append(M_ICON)

# 2) the icon alone: the coin's relief icon itself (same outline, stroke, scale and profile), standing up, its flat back behind
ca = coll('icon_alone')
alone = bpy.data.objects.new('icon_alone_relief', alone_me); ca.objects.link(alone)
place([alone], Matrix.Rotation(math.radians(90), 4, 'X'))
alone.data.materials.clear(); alone.data.materials.append(M_ICON); smooth(alone, 50)
for o in ca.objects: o.location.x += .25

# 3) the cup after the icon, 6 mm per unit: body (y 7→22), rim band at y 7 (x 4→20), domed lid (y 7→1.9)
u = .006; H = 15 * u
cc = coll('cup')
rb, rt, fb = 4.6 * u, 7.0 * u, 1.6 * u
body = revolve([(0, 0), (rb - fb, 0)] + arc(rb - fb, fb, fb, -90, -10)[1:] + [(rt, H)] + [(0, H)], 160, 'cup_body', cc)
rr0, rr1, rh, rf = 6.6 * u, 8.6 * u, .9 * u, .7 * u   # the rim band: a rounded rectangle in section, round the top of the body
rim = revolve(arc(rr1 - rf, H - rh + rf, rf, -90, 0) + arc(rr1 - rf, H + rh - rf, rf, 0, 90)[1:] + arc(rr0 + rf, H + rh - rf, rf, 90, 180)[1:]
              + arc(rr0 + rf, H - rh + rf, rf, 180, 270)[1:-1], 160, 'cup_rim', cc, closed_loop=True)
lt, lf = 4.7 * u, 1.6 * u   # the lid: from the rim's top up a sloping wall to a rounded flat top at y ≈ 2
lid = revolve([(0, H), (6.9 * u, H), (6.9 * u, H + rh), (6.26 * u, H + 1.71 * u)] + arc(lt - lf + .3 * u, H + 5.1 * u - lf, lf, -5, 90)[1:] + [(0, H + 5.1 * u)], 160, 'cup_lid', cc)
body.data.materials.append(M_BODY); rim.data.materials.append(M_RIM); lid.data.materials.append(M_LID)
for o in (body, rim, lid): smooth(o, 35); o.location.x += .5

# ---- report
report = [check(o) for o in (disc, bevel, iround, ifull, disc2, flat, alone, body, rim, lid)]
json.dump(report, open(CHECK + '/report.json', 'w'), indent=1)
print('REPORT', json.dumps(report))

# ---- studio: a seamless light backdrop, the HDRI and a soft key; cameras per composition (hero, front, turned, side, macro)
cs = coll('studio')
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=5)   # a floor; the background is a flat grey for the camera
finish(bm); floor = new_obj('floor', bm, cs); floor.data.materials.append(mat('M_floor', (.62, .62, .6), .75))
w = sc.world = bpy.data.worlds.new('studio'); w.use_nodes = True; nt = w.node_tree
env = nt.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(HDRI)
bgL = nt.nodes['Background']; bgL.inputs[1].default_value = .6; nt.links.new(env.outputs[0], bgL.inputs[0])
bgC = nt.nodes.new('ShaderNodeBackground'); bgC.inputs[0].default_value = (.5, .5, .49, 1); bgC.inputs[1].default_value = 1
lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0]); nt.links.new(bgL.outputs[0], mix.inputs[1]); nt.links.new(bgC.outputs[0], mix.inputs[2])
nt.links.new(mix.outputs[0], nt.nodes['World Output'].inputs[0])   # the HDRI lights and reflects; the camera sees flat grey
key = bpy.data.objects.new('key', bpy.data.lights.new('key', 'AREA')); cs.objects.link(key)
key.data.size = 1.2; key.data.energy = 18; key.location = (-.6, -.7, .9); key.rotation_euler = (math.radians(55), 0, math.radians(-40))

def cam(name, target, loc, lens, coll_):
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name)); coll_.objects.link(c)
    c.data.lens = lens; c.location = loc; c.data.clip_start = .005
    d = Vector(target) - Vector(loc); c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); return c

def rig(prefix, center, size, coll_):
    cx, cy, cz = center; dist = size * 4.2
    return {
        'hero':  cam(prefix + '_hero', center, (cx - dist * .45, cy - dist * .85, cz + dist * .25), 85, coll_),
        'front': cam(prefix + '_front', center, (cx, cy - dist, cz + dist * .05), 85, coll_),
        'turn':  cam(prefix + '_turn', center, (cx + dist * .6, cy - dist * .8, cz + dist * .3), 85, coll_),
        'side':  cam(prefix + '_side', center, (cx + dist, cy - dist * .05, cz), 85, coll_),
        'macro': cam(prefix + '_macro', (cx + size * .2, cy, cz + size * .25), (cx - size * .15, cy - size * 1.1, cz + size * .45), 100, coll_),
    }
def ctr(objs):
    pts = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return tuple((lo + hi) / 2), max(hi - lo)
bpy.context.view_layer.update()   # matrix_world is stale after moving objects until the depsgraph updates
cams = {}
for name, objs, cl in (('disc', [disc, bevel], cd), ('disc_flat', [disc2, flat], cf), ('icon_alone', [alone], ca), ('cup', [body, rim, lid], cc)):
    c, sz = ctr(objs); cams[name] = rig(name, c, sz, cl)

r = sc.render; r.engine = 'CYCLES'; sc.cycles.device = 'GPU'; sc.cycles.samples = 64; sc.cycles.use_denoising = True
try:
    p = bpy.context.preferences.addons['cycles'].preferences; p.compute_device_type = 'METAL'; p.get_devices()
    for dv in p.devices: dv.use = True
except Exception as e: print('gpu', e)
r.resolution_x = r.resolution_y = 900; sc.view_settings.view_transform = 'Khronos PBR Neutral'
r.image_settings.file_format = 'PNG'
sc.camera = cams['disc']['hero']
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)

# ---- check renders: each composition from its hero and side cameras (the coins also macro), the rest hidden
def shot(camobj, path):
    sc.camera = camobj; r.filepath = path; bpy.ops.render.render(write_still=True)
groups = {'icon_round': [iround], 'icon_full': [ifull], 'disc': [disc, bevel], 'disc_flat': [disc2, flat], 'icon_alone': [alone], 'cup': [body, rim, lid]}
for name in cams:
    for g, objs in groups.items():
        for o in objs: o.hide_render = g != name
    for v in (('hero', 'side', 'macro') if name.startswith('disc') else ('hero', 'side')): shot(cams[name][v], f'{CHECK}/{name}-{v}.png')
for objs in groups.values():
    for o in objs: o.hide_render = False
sc.camera = cams['disc']['hero']
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
print('DONE')
