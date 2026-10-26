import json, re, sys
# uso: python3 build_svg.py orig.svg labels_out.json salida.svg
s = open(sys.argv[1]).read()
L = json.load(open(sys.argv[2]))
DX = 188.9766

def shift_id(eid):
    global s
    m = re.search(r'<(\w+)\s[^>]*?id="%s"[^>]*>' % re.escape(eid), s)
    assert m, eid
    tag = m.group(0)
    if ' transform="' in tag:
        new = tag.replace(' transform="', ' transform="translate(%.4f,0) ' % DX, 1)
    else:
        new = tag.replace(' id="%s"' % eid, ' id="%s" transform="translate(%.4f,0)"' % (eid, DX), 1)
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

# --- lado derecho: corre un bloque a la derecha ---
right = ['et52epo1d', 'fx43hzp9i', 'eicd6nuv', 'ee9s0vdw', 'ey2aueux', 'e7nh910y',
         'en42ks8z', 'eba4kt910', 'fxgycuu611', 'ecngpsd1b', 'fx8iy5bf1i',
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
xR = 816.379                    # RT-OPP (posicion vieja del generador)
xE = 627.4024                   # estimador de phi (sobre la LUT)
xO = 816.379 + DX               # observador (sobre el generador corrido)
xPCC = 1388.9782 + DX           # nodo de medicion de v_abc
n = ''
n += blk(xR, YB) + lab('rtopp', xR + W/2, YM)
n += blk(xE, YT - H/2) + lab('est', xE + W/2, YT)
n += blk(xO, YT - H/2) + lab('obs', xO + W/2, YT)
n += lab('lut', 627.4024 + W/2, YM)
# RT-OPP -> generador
n += wire('M %.4f %.4f L %.4f %.4f' % (xR + W, YM, xR + W + 52.9135 - GAP + 7.5591 - 0.0, YM))
# etiqueta gamma^0 en el cable LUT -> RT-OPP
n += lab('g0', 779.6609, 103.5245, center=False)
# phi: estimador -> LUT y -> RT-OPP
xEc = xE + W/2; yEb = YT + H/2; yBr = 49.0
n += wire('M %.4f %.4f L %.4f %.4f' % (xEc, yEb, xEc, YB - GAP))
n += dot(xEc, yBr)
n += wire('M %.4f %.4f L %.4f %.4f L %.4f %.4f' % (xEc, yBr, 860.0, yBr, 860.0, YB - GAP))
n += lab('phi', 670.5, 44.0, center=False)
# P*,Q* entra una vez y se divide: referencia de corriente y estimador de phi
xPQ = 34.0
n += dot(xPQ, YM)
n += wire('M %.4f %.4f L %.4f %.4f L %.4f %.4f' % (xPQ, YM, xPQ, YT, xE - GAP, YT))
# observador: v_abc desde el PCC, salida x*_h al RT-OPP
n += wire('M %.4f %.4f L %.4f %.4f L %.4f %.4f' % (xPCC, YM, xPCC, YT, xO + W + GAP, YT))
n += lab('vabc2', 1528.0, YT - 6.0, center=False)
n += wire('M %.4f %.4f L 920.0 %.4f L 920.0 %.4f' % (xO, YT, YT, YB - GAP))
n += lab('xh', 926.5, 52.0, center=False)
# M al RT-OPP (fundamental de referencia)
xMb = 597.0; yM2 = 176.0
n += dot(xMb, YM)
n += wire('M %.4f %.4f L %.4f %.4f L 880.0 %.4f L 880.0 %.4f' % (xMb, YM, xMb, yM2, yM2, 151.1812 + GAP))
n += lab('M2', 760.0, yM2 - 4.5, center=False)
# delta en el cable del bloque polar al generador
n += lab('delta', 835.6735 + DX, 190.753, center=False)

s = s.replace('</svg>', '<g id="nuevos_rtopp" transform="scale(0.264583)">\n' + n + '</g>\n</svg>')
# lienzo: mas ancho y mas alto
s = s.replace('width="405mm" height="85mm" viewBox="1 -1 405 85"',
              'width="456mm" height="104mm" viewBox="1 -20 456 104"')
open(sys.argv[3], 'w').write(s)
print('ok', len(s))
