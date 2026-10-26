import json, re, sys
# uso: python3 build_svg.py orig.svg labels_out.json salida.svg
s = open(sys.argv[1]).read()
L = json.load(open(sys.argv[2]))
DX = 120.0     # corrimiento del generador en adelante
D1 = 60.0      # corrimiento de la columna RT-OPP / LUT

def shift_id(eid, dx=None):
    global s
    if dx is None: dx = DX
    m = re.search(r'<(\w+)\s[^>]*?id="%s"[^>]*>' % re.escape(eid), s)
    assert m, eid
    tag = m.group(0)
    if ' transform="' in tag:
        new = tag.replace(' transform="', ' transform="translate(%.4f,0) ' % dx, 1)
    else:
        new = tag.replace(' id="%s"' % eid, ' id="%s" transform="translate(%.4f,0)"' % (eid, dx), 1)
    s = s.replace(tag, new, 1)

def remove_id(eid):
    global s
    m = re.search(r'<(\w+)\s[^>]*?id="%s"' % re.escape(eid), s)
    i = m.start(); tagname = m.group(1)
    # elemento con hijos: buscar cierre balanceado
    depth = 0; j = i
    pat = re.compile(r'<(/?)%s\b[^>]*?(/?)>' % tagname)
    for mm in pat.finditer(s, i):
        if mm.group(1) == '/': depth -= 1
        elif mm.group(2) == '/': pass
        else: depth += 1
        if depth == 0:
            j = mm.end(); break
    s = s[:i] + s[j:]

def set_attr(eid, attr, fn):
    global s
    m = re.search(r'<(\w+)\s[^>]*?id="%s"[^>]*>' % re.escape(eid), s)
    tag = m.group(0)
    v = float(re.search(r' %s="([^"]*)"' % attr, tag).group(1))
    new = re.sub(r' %s="[^"]*"' % attr, ' %s="%.4f"' % (attr, fn(v)), tag, count=1)
    s = s.replace(tag, new, 1)

# --- lado derecho: generador en adelante corre DX ---
right = ['et52epo1d', 'fx43hzp9i', 'eicd6nuv', 'ee9s0vdw', 'ey2aueux', 'e7nh910y',
         'en42ks8z', 'eba4kt910', 'ecngpsd1b', 'fx8iy5bf1i',
         'e3na4ky3l', 'e6pitvn3m', 'e0ojw0u3n', 'e9q2bwo3p', 'egygjb63q',
         'e2qvhco3r', 'ej5kq0j3s', 'eu0ctu73t',
         # capa del convertidor y LCL
         'ez3nyiy25', 'eu8n0kv3e', 'eloijxp23', 'egbc57n3', 'e9topjz3o', 'eh860so2x',
         'et8swy93c', 'e79sf0m7v', 'e4htg5o7w', 'es89dar7x', 'e63tvy97y', 'e40twnh7z',
         'eaklkb380', 'ev7j8bz13', 'eq1fwtc81', 'e0rklyu2', 'ed6nqvs3', 'g4yav4xd',
         'en22vgah', 'ezz6mipi', 'eulptcjj', 'ezfnye8k', 'ez0quy4l', 'ewm1oqxp',
         'e15qimfq', 'em881vhr', 'ex5h7pls', 'eo24sqow', 'eoa5is1x', 'ecsdz8ky',
         'e0oss1411', 'eu6ly7i3g', 'fxftw2l70', 'e5pim36e', 'elcggdff', 'e1xml4mg',
         'fx9qlqyeh', 'fx2bg65dv1', 'e2izqf7vt']
for e in right:
    shift_id(e)
g = '<g filter="url(#somv5q63r3i)" transform="translate(9.4488,-13.0795)">'
assert s.count(g) == 1
s = s.replace(g, g.replace('translate(9.4488', 'translate(%.4f' % (9.4488 + DX)))
set_attr('ejqy1y63u', 'x1', lambda v: v + DX)   # i_abc horizontal
set_attr('en1h9yzb', 'x2', lambda v: v + DX)    # delta horizontal
# la caja de la LUT original pasa a ser el RT-OPP (corre D1)
shift_id('ecr6qwb8', D1)
set_attr('e14yxjwr', 'x2', lambda v: v + D1)    # M: polar -> RT-OPP
shift_id('e0po8ozt', D1)                        # gamma: RT-OPP -> generador
set_attr('e0po8ozt', 'x2', lambda v: v + DX - D1)
shift_id('fxgycuu611', (DX + D1) / 2)           # etiqueta gamma al centro del cable
shift_id('fx3e1rzq12', 67.0)                    # etiqueta M a la derecha de la rama
remove_id('fx8slo5pj')   # etiqueta vieja de la LUT
remove_id('fxbctl76j')   # phi viejo -> delta
# etiqueta P*,Q* bajo el cable de entrada (arriba sube la rama al estimador)
s = s.replace('transform="matrix(0.017,0,0,0.017,6.9981,103.571)"',
              'transform="matrix(0.017,0,0,0.017,6.9981,134.0)"', 1)

# --- elementos nuevos ---
SC = 0.018898
def lab(key, x, y, center=True):
    vb = [float(t) for t in L[key]['viewBox'].split()]
    if center:
        tx = x - SC * (vb[0] + vb[2] / 2); ty = y - SC * (vb[1] + vb[3] / 2)
    else:
        tx, ty = x, y
    return ('<g fill="#000000" filter="url(#somanlaw85m)" '
            'transform="matrix(%g,0,0,%g,%.4f,%.4f)">%s</g>\n' % (SC, SC, tx, ty, L[key]['inner']))

W, H = 128.5041, 75.5906
def blk(x, y):
    return ('<rect fill="url(#grad8qjlx55l)" filter="url(#edlrc5t6)" height="%.4f" '
            'stroke="#000000" stroke-width="1.63698" width="%.4f" x="%.4f" y="%.4f"/>\n' % (H, W, x, y))
def wire(d, arrow=True):
    return ('<path d="%s" fill="none" stroke="#000000" stroke-linecap="round" '
            'stroke-linejoin="round" stroke-width="1.51181"%s/>\n'
            % (d, ' marker-end="url(#fle412ng7k)"' if arrow else ''))
def dot(x, y):
    return ('<ellipse cx="%.4f" cy="%.4f" fill="#000000" rx="1.189" ry="1.189" '
            'stroke="#000000" stroke-width="2.2677"/>\n' % (x, y))

YM = 113.386; YT = -15.0; YB = 75.5906; GAP = 7.5591
xP = 438.4258                   # columna del bloque polar
xC = 627.4024 + D1              # columna RT-OPP (abajo) / LUT (arriba)
xG = 816.379 + DX               # columna del generador / observador
xPCC = 1388.9782 + DX           # nodo de medicion de v_abc
n = ''
n += lab('rtopp', xC + W/2, YM)
n += blk(xP, YT - H/2) + lab('est', xP + W/2, YT)
n += blk(xC, YT - H/2) + lab('lut', xC + W/2, YT)
n += blk(xG, YT - H/2) + lab('obs', xG + W/2, YT)
# P*,Q* entra una vez y se divide: referencia de corriente y angulo de carga
xPQ = 34.0
n += dot(xPQ, YM)
n += wire('M %.4f %.4f L %.4f %.4f L %.4f %.4f' % (xPQ, YM, xPQ, YT, xP - GAP, YT))
# phi: angulo de carga -> LUT, con rama al RT-OPP (salto sobre el cable de M)
yF = YT - 18.0; xFd = 600.0; yFr = YM - 24.0
xMd = 645.0; yMu = YT + 18.0; R = 5.0
n += wire('M %.4f %.4f L %.4f %.4f' % (xP + W, yF, xC - GAP, yF))
n += dot(xFd, yF)
n += wire('M %.4f %.4f L %.4f %.4f L %.4f %.4f A %.1f %.1f 0 0 1 %.4f %.4f L %.4f %.4f'
          % (xFd, yF, xFd, yFr, xMd - R, yFr, R, R, xMd + R, yFr, xC - GAP, yFr))
n += lab('phi', 608.0, yF - 6.0, center=False)
# M: rama del cable polar -> RT-OPP hacia la LUT
n += dot(xMd, YM)
n += wire('M %.4f %.4f L %.4f %.4f L %.4f %.4f' % (xMd, YM, xMd, yMu, xC - GAP, yMu))
# gamma^0: LUT -> RT-OPP
xCc = xC + W/2
n += wire('M %.4f %.4f L %.4f %.4f' % (xCc, YT + H/2, xCc, YB - GAP))
n += lab('g0', xCc + 6.0, 56.0, center=False)
# observador: v_abc desde el PCC, salida x*_h al RT-OPP
n += wire('M %.4f %.4f L %.4f %.4f L %.4f %.4f' % (xPCC, YM, xPCC, YT, xG + W + GAP, YT))
n += lab('vabc2', 1339.02 + DX, YT - 6.0, center=False)
xHo = xG + 20.0; yH = 45.0; xHi = xC + W - 22.0
n += wire('M %.4f %.4f L %.4f %.4f L %.4f %.4f L %.4f %.4f'
          % (xHo, YT + H/2, xHo, yH, xHi, yH, xHi, YB - GAP))
n += lab('xh', xHi + 22.0, yH - 6.0, center=False)
# delta en el cable del bloque polar al generador
n += lab('delta', 835.6735 + DX, 190.753, center=False)

s = s.replace('</svg>', '<g id="nuevos_rtopp" transform="scale(0.264583)">\n' + n + '</g>\n</svg>')
# lienzo: mas ancho y mas alto
wmm = 405 + DX * 0.264583
s = s.replace('width="405mm" height="85mm" viewBox="1 -1 405 85"',
              'width="%.0fmm" height="104mm" viewBox="1 -20 %.0f 104"' % (wmm, wmm))
open(sys.argv[3], 'w').write(s)
print('ok', len(s), 'ancho mm', round(wmm))
