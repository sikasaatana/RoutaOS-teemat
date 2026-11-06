#!/usr/bin/env python3
"""0.99.55: teemaluettelo (teemat.txt) palvelimelle.

Lukee kansion *.teema-tiedostot ja kirjoittaa luettelon, jossa jokainen
teema on oma osionsa [tunnus] kaikkine vareineen (esikatselu ennen
latausta). Kuvien SHA-256 lasketaan (kuva_sha256=, taustakuva_sha256=), jos kuva on kansiossa.
Palvelimelle kopioidaan teemat.txt ja kuvat samaan kansioon.

Kaytto: python3 tools/teemat/tee_luettelo.py [kansio] [ulos]
        (oletus tools/teemat ja <kansio>/teemat.txt)
"""
import sys, os, hashlib
d = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(d, 'teemat.txt')
rows = ['# RoutaOS-teemat (tools/teemat/tee_luettelo.py)', '']
n = 0
for f in sorted(os.listdir(d)):
    if not f.endswith('.teema'): continue
    tid = f[:-6].lower()
    rows.append('[%s]' % tid)
    kuva = None; tausta = None
    for line in open(os.path.join(d, f), encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line: continue
        k, v = [x.strip() for x in line.split('=', 1)]
        if k == 'kuva': kuva = v
        if k == 'taustakuva': tausta = v
        rows.append('%s=%s' % (k, v))
    if kuva and os.path.exists(os.path.join(d, kuva)):
        rows.append('kuva_sha256=' + hashlib.sha256(open(os.path.join(d, kuva), 'rb').read()).hexdigest())
    if tausta and os.path.exists(os.path.join(d, tausta)):
        rows.append('taustakuva_sha256=' + hashlib.sha256(open(os.path.join(d, tausta), 'rb').read()).hexdigest())
    rows.append('')
    n += 1
open(out, 'w', encoding='utf-8').write('\n'.join(rows))
print(out, n, 'teemaa')
