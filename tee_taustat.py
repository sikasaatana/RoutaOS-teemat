#!/usr/bin/env python3
"""0.99.57: teemojen taustakuvat (1600x900 JPEG, ASUS X75A:n ruutu).

Maisemat piirretaan ohjelmallisesti (liukuvarit, tunturit, metsa,
revontulet, hehku, tahdet, lumi), joten kuvilla ei ole lisenssirajoituksia.
Tulos: tools/teemat/<tunnus>-tausta.jpg (baseline JPEG, RoutaOS purkaa).
Kaytto: python3 tools/teemat/tee_taustat.py [tunnus ...]
"""
import os, sys, math
import numpy as np
from PIL import Image

W, H = 1600, 900
D = os.path.dirname(os.path.abspath(__file__))

def hexc(h): h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)

def vgrad(stops):
    """stops: [(0..1, '#rrggbb'), ...] ylhaalta alas."""
    y = np.linspace(0, 1, H, dtype=np.float32)
    out = np.zeros((H, 3), np.float32)
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        m = (y >= a) & (y <= b)
        t = ((y[m] - a) / max(b - a, 1e-6))[:, None]
        t = t * t * (3 - 2 * t)
        out[m] = hexc(ca) * (1 - t) + hexc(cb) * t
    return np.repeat(out[:, None, :], W, axis=1)

def ridge(base, amp, freqs, seed):
    rng = np.random.default_rng(seed)
    x = np.arange(W, dtype=np.float32) / W
    y = np.zeros(W, np.float32)
    for f in freqs:
        y += np.sin(x * f * 2 * math.pi + rng.uniform(0, 6.28)) / f ** 0.6
    y = (y - y.min()) / (np.ptp(y) + 1e-6)
    return (base - y * amp) * H

def fill_below(img, ys, col, alpha=1.0):
    c = hexc(col)
    yy = np.arange(H)[:, None]
    m = yy >= ys[None, :]
    img[m] = img[m] * (1 - alpha) + c * alpha

def forest(img, ys, col, seed, size=(18, 46), dens=0.9):
    rng = np.random.default_rng(seed)
    c = hexc(col)
    x = 0
    while x < W:
        h = rng.uniform(*size); w = h * rng.uniform(0.32, 0.42)
        base = ys[min(int(x), W - 1)] + 2
        top = base - h
        x0, x1 = int(x - w), int(x + w)
        for yy in range(max(int(top), 0), min(int(base), H)):
            t = (yy - top) / h
            half = w * t * (0.8 + 0.2 * math.sin(t * 40))
            a, b = max(int(x - half), 0), min(int(x + half) + 1, W)
            if a < b: img[yy, a:b] = c
        x += w * rng.uniform(0.7, 1.6) / dens

def stars(img, n, seed, ymax=0.6, bright=255):
    rng = np.random.default_rng(seed)
    xs = rng.integers(0, W, n); ys = rng.integers(0, int(H * ymax), n)
    v = rng.uniform(0.3, 1.0, n)
    for x, y, a in zip(xs, ys, v):
        img[y, x] = img[y, x] * (1 - a) + bright * a
        if a > 0.85 and 0 < x < W - 1 and 0 < y < H - 1:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                img[y + dy, x + dx] = img[y + dy, x + dx] * 0.6 + bright * 0.4

def glow(img, cx, cy, r, col, a=0.8):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx - cx * W) ** 2 + (yy - cy * H) ** 2) / (r * H)
    k = np.clip(np.exp(-d * d * 2.2) * a, 0, 1)[..., None]
    img[:] = img * (1 - k) + hexc(col) * k

def disc(img, cx, cy, r, col):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx - cx * W) ** 2 + (yy - cy * H) ** 2)
    k = np.clip(r * H - d + 1, 0, 1)[..., None]
    img[:] = img * (1 - k) + hexc(col) * k

def aurora(img, seed, cols, y0=0.18, amp=0.10, height=0.32, strength=0.9):
    rng = np.random.default_rng(seed)
    x = np.arange(W, dtype=np.float32) / W
    yy = np.arange(H, dtype=np.float32)[:, None] / H
    for i, col in enumerate(cols):
        c = y0 + i * 0.05 + amp * np.sin(x * rng.uniform(2, 4) * math.pi + rng.uniform(0, 6)) \
            + 0.03 * np.sin(x * rng.uniform(9, 14) * math.pi + rng.uniform(0, 6))
        rays = 0.78 + 0.22 * np.sin(x * rng.uniform(30, 55) + rng.uniform(0, 6)) ** 2
        d = yy - c[None, :]
        k = np.where(d < 0, np.exp(-(d / (height * 0.9)) ** 2), np.exp(-(d / 0.025) ** 2))
        k = k * rays[None, :] * strength / (1 + i * 0.6)
        k = np.clip(k, 0, 1)[..., None]
        img[:] = img + (hexc(col) - img) * k * 0.85

def snow(img, n, seed, size=2, a=0.8):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x, y = rng.integers(0, W - size), rng.integers(0, H - size)
        s = rng.integers(1, size + 1)
        img[y:y + s, x:x + s] = img[y:y + s, x:x + s] * (1 - a) + 255 * a

def reflect(img, y_water, tint, dark=0.55):
    yw = int(y_water * H)
    n = H - yw
    src = img[max(yw - n, 0):yw][::-1].copy()
    if src.shape[0] < n: src = np.concatenate([src, np.repeat(src[-1:], n - src.shape[0], 0)])
    wave = (np.sin(np.arange(n)[:, None] * 0.9 + np.arange(W)[None, :] * 0.02) * 0.08 + 1)[..., None]
    img[yw:] = (src * wave) * dark + hexc(tint) * (1 - dark)

def save(img, name):
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGB')
    p = os.path.join(D, name + '-tausta.jpg')
    im.save(p, quality=88, optimize=True, progressive=False)
    print(p, os.path.getsize(p) // 1024, 'kt')

def revontuli():
    img = vgrad([(0, '#03070F'), (0.55, '#0B1A2A'), (1, '#10263A')])
    stars(img, 900, 1)
    aurora(img, 2, ['#3DDC97', '#29B6A0', '#7B5CD6'], y0=0.12, amp=0.08, height=0.26)
    fill_below(img, ridge(0.80, 0.16, [1.5, 3, 7, 15], 3), '#0E1D2B')
    r = ridge(0.90, 0.06, [2, 5, 11], 4); fill_below(img, r, '#08121C'); forest(img, r, '#050B12', 5)
    return img

def kaamos():
    img = vgrad([(0, '#070A22'), (0.6, '#151A48'), (1, '#262B5E')])
    stars(img, 500, 6, 0.5)
    glow(img, 0.72, 0.70, 0.55, '#F2A65A', 0.55)
    r = ridge(0.82, 0.08, [1.2, 3, 6], 7); fill_below(img, r, '#DCE2F5'); forest(img, r - 2, '#0C1030', 8, (30, 70), 0.6)
    fill_below(img, ridge(0.92, 0.03, [2, 4], 9), '#EEF1FB')
    glow(img, 0.72, 0.70, 0.12, '#FFD9A0', 0.9); disc(img, 0.72, 0.70, 0.008, '#FFF3D6')
    snow(img, 2500, 10, 2, 0.7)
    return img

def ruska():
    img = vgrad([(0, '#2B1A3A'), (0.45, '#B4573A'), (0.62, '#F0A030'), (1, '#3A2418')])
    glow(img, 0.3, 0.58, 0.35, '#FFD27A', 0.7); disc(img, 0.3, 0.58, 0.04, '#FFE7B0')
    fill_below(img, ridge(0.66, 0.14, [1.3, 3, 7], 11), '#8A3E22')
    fill_below(img, ridge(0.76, 0.10, [2, 4, 9], 12), '#B5501F')
    r = ridge(0.86, 0.07, [2.5, 6, 13], 13); fill_below(img, r, '#5E2A14'); forest(img, r, '#2A1309', 14, (16, 40))
    fill_below(img, ridge(0.96, 0.03, [3, 8], 15), '#1E110B')
    return img

def tunturi():
    img = vgrad([(0, '#8DB8E3'), (0.6, '#D8E8F6'), (1, '#F4F8FC')])
    glow(img, 0.78, 0.22, 0.30, '#FFFFFF', 0.6)
    fill_below(img, ridge(0.60, 0.25, [1.1, 2.5, 6], 21), '#C6D7EA')
    fill_below(img, ridge(0.72, 0.18, [1.5, 3.5, 8], 22), '#E3ECF6')
    r = ridge(0.86, 0.08, [2, 5, 12], 23); fill_below(img, r, '#F7FAFD'); forest(img, r, '#4B6A86', 24, (10, 24), 0.5)
    return img

def saaristo():
    img = vgrad([(0, '#0E2A3A'), (0.35, '#2E6D7E'), (0.6, '#E39A6B'), (0.62, '#E39A6B')])
    glow(img, 0.5, 0.60, 0.4, '#FFC48A', 0.8); disc(img, 0.5, 0.605, 0.035, '#FFE2B8')
    reflect(img, 0.62, '#0F3A4A', 0.6)
    for x0, w, h in ((0.08, 0.18, 0.035), (0.62, 0.12, 0.025), (0.82, 0.22, 0.045), (0.36, 0.06, 0.015)):
        a, b = int(x0 * W), min(int((x0 + w) * W), W)
        xs = np.arange(a, b)
        top = 0.62 * H - h * H * np.sin((xs - a) / (b - a) * math.pi) ** 0.6
        for x, t in zip(xs, top): img[int(t):int(0.62 * H) + 2, x] = hexc('#0A1E28')
    return img

def juhannus():
    img = vgrad([(0, '#F6D7C3'), (0.45, '#FBE7C8'), (0.6, '#FFE9B8'), (0.62, '#FFE9B8')])
    glow(img, 0.62, 0.56, 0.4, '#FFD08A', 0.7); disc(img, 0.62, 0.565, 0.045, '#FFF4D8')
    reflect(img, 0.62, '#E8C9B0', 0.65)
    yw = int(0.62 * H)
    rr = ridge(0.62, 0.05, [2, 5, 11], 41)
    land = np.full(W, 1e9, np.float32)
    edge = int(W * 0.35)
    land[:edge] = rr[:edge] - np.linspace(0, 1, edge) ** 3 * 0      # niemi vasemmalla
    for x in range(edge):
        img[int(land[x]):yw + 2, x] = hexc('#3E5A3A')
    forest(img, land, '#2E4430', 42, (20, 55))
    return img

def hamara():
    img = vgrad([(0, '#1A1030'), (0.5, '#4A2C6E'), (0.75, '#C0688A'), (1, '#2A1A40')])
    stars(img, 400, 51, 0.45)
    disc(img, 0.8, 0.18, 0.05, '#F3E9FF'); disc(img, 0.815, 0.17, 0.047, '#2F1D4C')
    fill_below(img, ridge(0.70, 0.22, [1.2, 2.6, 6], 52), '#3A2556')
    fill_below(img, ridge(0.80, 0.14, [1.8, 4, 9], 53), '#2A1A40')
    fill_below(img, ridge(0.92, 0.06, [2.5, 6], 54), '#1A1028')
    return img

def metsa():
    img = vgrad([(0, '#C9DCCB'), (0.5, '#8FB59A'), (1, '#1E3A2A')])
    cols = ['#9DBFA6', '#7AA287', '#55806A', '#2F5A44', '#16301F']
    for i, c in enumerate(cols):
        r = ridge(0.45 + i * 0.11, 0.06, [2, 5, 11], 60 + i)
        fill_below(img, r + 30, c)
        forest(img, r + 30, c, 70 + i, (30 + i * 18, 70 + i * 30), 1.1)
    return img

def lumi():
    img = vgrad([(0, '#E9F0F8'), (0.6, '#F6F9FC'), (1, '#FFFFFF')])
    fill_below(img, ridge(0.66, 0.12, [1.2, 2.5], 81), '#E2EAF4')
    fill_below(img, ridge(0.78, 0.10, [1.5, 3], 82), '#EEF3F9')
    fill_below(img, ridge(0.90, 0.06, [2, 4], 83), '#FAFCFE')
    snow(img, 900, 84, 3, 0.5)
    return img

def sauna():
    img = vgrad([(0, '#1A0F0A'), (0.6, '#3A2014'), (1, '#140A06')])
    rng = np.random.default_rng(91)
    for _ in range(26):
        glow(img, rng.uniform(0, 1), rng.uniform(0.2, 0.95), rng.uniform(0.04, 0.12), rng.choice(['#E8742C', '#F0A030', '#D9483B']), rng.uniform(0.25, 0.6))
    # puupaneelit
    for x in range(0, W, 80):
        img[:, x:x + 2] = img[:, x:x + 2] * 0.6
    return img

ALL = dict(revontuli=revontuli, kaamos=kaamos, ruska=ruska, tunturi=tunturi, saaristo=saaristo,
           juhannus=juhannus, hamara=hamara, metsa=metsa, lumi=lumi, sauna=sauna)

if __name__ == '__main__':
    for n in (sys.argv[1:] or ALL):
        save(ALL[n](), n)
