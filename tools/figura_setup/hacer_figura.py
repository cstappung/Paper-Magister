# Genera la figura del montaje experimental (fig:setup) como SVG con las
# fotos embebidas. Despues render.js la pasa a PNG y PDF con Chromium.
#
# Uso:  python3 tools/figura_setup/hacer_figura.py
#       node tools/figura_setup/render.js
#
# Formato vertical: esquema trifasico a la izquierda, con la potencia
# fluyendo de arriba (fuentes DC) hacia abajo (red), y los equipos a la
# derecha, recortados sin fondo y unidos a su bloque con lineas naranjas.
#
# El esquema se dibuja en coordenadas (u, v): u avanza en el sentido del
# flujo de potencia y v es transversal. Un grupo SVG lo transpone a (x, y)
# = (X0 + v, Y0 + u). Los textos se ubican aparte, ya transpuestos, para
# que queden derechos.

import base64
import io
import math
import os

from PIL import Image, ImageDraw, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
FOTOS = os.path.join(AQUI, "fotos")
SALIDA = os.path.join(AQUI, "..", "..", "figuras", "setup")

W, H = 1100, 1230
FUENTE = "'Times New Roman', 'Liberation Serif', serif"
TXT = 30
GRIS = "#efefef"
BORDE = "#333333"
NARANJO = "#f0a050"
AZUL = "#1f5fbf"
LW = 2.2

# --- equipos recortados: (archivo, poligono del contorno en px de la foto)
RECORTES = {
    "itech1": ("hioki_itech.jpg",
               [(165, 400), (633, 400), (633, 536), (165, 536)]),
    "itech2": ("hioki_itech.jpg",
               [(210, 637), (574, 637), (574, 746), (210, 746)]),
    "hioki":  ("hioki_itech.jpg",
               [(163, 236), (626, 236), (626, 403), (163, 403)]),
    "opal":   ("opalrt.jpg",
               [(138, 321), (791, 321), (794, 457), (135, 457)]),
    "nhr":    ("nhr9410.jpg",
               [(138, 508), (607, 504), (586, 811), (176, 813)]),
    "lcl":    ("lcl.jpg",
               [(22, 238), (758, 238), (768, 792), (26, 808)]),
}
# foto rectangular (sin quitar fondo): (archivo, caja)
RECT = {"proto": ("prototipo.jpg", (100, 250, 760, 662))}

partes, sobre, defs = [], [], []


def add(s):
    partes.append(s)


def png_b64(im):
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def jpg_b64(im):
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88)
    return base64.b64encode(buf.getvalue()).decode()


def recorte(clave, ancho):
    """Equipo recortado con fondo transparente, escalado a 'ancho' px de
    la figura (x2 para nitidez). Devuelve (b64, alto)."""
    archivo, poli = RECORTES[clave]
    im = Image.open(os.path.join(FOTOS, archivo)).convert("RGB")
    xs, ys = [p[0] for p in poli], [p[1] for p in poli]
    caja = (min(xs), min(ys), max(xs), max(ys))
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).polygon(poli, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0.8))
    im = im.crop(caja)
    mask = mask.crop(caja)
    im.putalpha(mask)
    esc = 2 * ancho / im.width
    im = im.resize((round(im.width * esc), round(im.height * esc)),
                   Image.LANCZOS)
    return png_b64(im), ancho * im.height / im.width


def foto_rect(clave, ancho):
    archivo, caja = RECT[clave]
    im = Image.open(os.path.join(FOTOS, archivo)).convert("RGB").crop(caja)
    esc = 2 * ancho / im.width
    im = im.resize((round(im.width * esc), round(im.height * esc)),
                   Image.LANCZOS)
    return jpg_b64(im), ancho * im.height / im.width


def imagen(b64, x, y, w, h, png=True, rx=0):
    tipo = "png" if png else "jpeg"
    clip = ""
    if rx:
        cid = f"clip{len(defs)}"
        defs.append(f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" '
                    f'height="{h}" rx="{rx}"/></clipPath>')
        clip = f' clip-path="url(#{cid})"'
    add(f'<image href="data:image/{tipo};base64,{b64}" x="{x}" y="{y}" '
        f'width="{w}" height="{h}" preserveAspectRatio="none"{clip}/>')


def panel(x, y, w, h, naranjo=False):
    est = (f'stroke="{NARANJO}" stroke-width="3" stroke-dasharray="10 6"'
           if naranjo else f'stroke="{BORDE}" stroke-width="1.6"')
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" '
        f'fill="{GRIS}" {est}/>')


def texto(x, y, s, size=TXT, anchor="middle", italic=False, color="#000",
          lista=None):
    st = ' font-style="italic"' if italic else ""
    (lista if lista is not None else partes).append(
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-size="{size}" fill="{color}"{st}>{s}</text>')


def sub_txt(x, y, base, sub, size=24, anchor="start", color="#000",
            lista=None):
    (lista if lista is not None else partes).append(
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-size="{size}" fill="{color}" font-style="italic">{base}'
        f'<tspan dy="6" font-size="{size*0.68:.0f}">{sub}</tspan></text>')


def linea_xy(pts, color="#000", w=LW, dash=None, flecha=False):
    d = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    if flecha:
        extra += ' marker-end="url(#flecha)"'
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" '
        f'stroke-linejoin="round"{extra}/>')


def recuadro_equipo(x, y, w, titulo, equipos, gap=10):
    """Recuadro gris con el titulo arriba y uno o mas equipos recortados
    apilados (cada uno al ancho del recuadro menos el margen)."""
    pad = 14
    ht = 40
    imgs = [recorte(c, w - 2 * pad) for c in equipos]
    h = ht + sum(a for _, a in imgs) + gap * (len(imgs) - 1) + pad
    panel(x, y, w, h)
    texto(x + w / 2, y + 31, titulo)
    yy = y + ht
    for b64, a in imgs:
        imagen(b64, x + pad, yy, w - 2 * pad, a)
        yy += a + gap
    return x, y, w, h


# ======================= esquema en (u, v) ==============================
# El grupo transpone: x = X0 + v, y = Y0 + u.
X0, Y0 = 40, 40
esq = []          # elementos del grupo (coordenadas u, v)
txt = []          # textos ya en (x, y)


def T(u, v):
    return X0 + v, Y0 + u


def L(pts, w=LW):
    d = "M " + " L ".join(f"{u:.1f} {v:.1f}" for u, v in pts)
    esq.append(f'<path d="{d}" fill="none" stroke="#000" stroke-width="{w}" '
               f'stroke-linejoin="round"/>')


def L_saltos(u0, u1, v, saltos, r=7):
    """Linea en u (v fija) con saltos en las u dadas."""
    a, b = min(u0, u1), max(u0, u1)
    d = f"M {a} {v} "
    for us in sorted(saltos):
        d += f"L {us-r} {v} A {r} {r} 0 0 1 {us+r} {v} "
    d += f"L {b} {v}"
    esq.append(f'<path d="{d}" fill="none" stroke="#000" '
               f'stroke-width="{LW}"/>')


def V_saltos(u, v0, v1, saltos, r=7):
    """Linea en v (u fija) con saltos en las v dadas."""
    a, b = min(v0, v1), max(v0, v1)
    d = f"M {u} {a} "
    for vs in sorted(saltos):
        d += f"L {u} {vs-r} A {r} {r} 0 0 0 {u} {vs+r} "
    d += f"L {u} {b}"
    esq.append(f'<path d="{d}" fill="none" stroke="#000" '
               f'stroke-width="{LW}"/>')


def P(u, v, r=4.5, color="#000"):
    esq.append(f'<circle cx="{u}" cy="{v}" r="{r}" fill="{color}"/>')


def mosfet(cu, cv, rot=0, Lm=56):
    """MOSFET con diodo de cuerpo, a lo largo de v (drenador en -v)."""
    h = Lm / 2
    g = (f'<g transform="translate({cu} {cv}) rotate({rot})" fill="none" '
         f'stroke="#000" stroke-width="{LW}">'
         f'<path d="M 0 {-h} L 0 -13 L -9 -13 M -9 13 L 0 13 L 0 {h}"/>'
         f'<path d="M -9 -18 L -9 18" stroke-width="3"/>'
         f'<path d="M -16 -13 L -16 13 M -16 0 L -26 0"/>'
         f'<path d="M 0 -20 L 13 -20 L 13 20 L 0 20"/>'
         f'<path d="M 7 5 L 19 5 L 13 -5 Z" fill="#000"/>'
         f'<path d="M 7 -5 L 19 -5"/></g>')
    esq.append(g)


def bobina(u0, u1, v, n=4, lado=1):
    paso = (u1 - u0) / n
    barr = 1 if lado > 0 else 0
    d = f"M {u0} {v} " + "".join(
        f"a {paso/2} {paso/2} 0 0 {barr} {paso} 0 " for _ in range(n))
    esq.append(f'<path d="{d}" fill="none" stroke="#000" '
               f'stroke-width="{LW}"/>')


def placas(u, vm, ancho=16, sep=6):
    """Placas de condensador perpendiculares a v, centradas en (u, vm)."""
    L([(u - ancho, vm - sep), (u + ancho, vm - sep)], w=3)
    L([(u - ancho, vm + sep), (u + ancho, vm + sep)], w=3)


def fuente_dc(u, v0, v1, r=20):
    vm = (v0 + v1) / 2
    L([(u, v0), (u, vm - r)])
    L([(u, vm + r), (u, v1)])
    esq.append(f'<circle cx="{u}" cy="{vm}" r="{r}" fill="#fff" '
               f'stroke="#000" stroke-width="{LW}"/>')
    x, y = T(u, vm)
    texto(x - 9, y + 7, "+", size=20, lista=txt)
    texto(x + 9, y + 7, "&#8722;", size=20, lista=txt)


def fuente_ac(u, v, r=21):
    esq.append(f'<circle cx="{u}" cy="{v}" r="{r}" fill="#fff" '
               f'stroke="#000" stroke-width="{LW}"/>')
    x, y = T(u, v)
    pts = " ".join(f"{x-12+24*k/20:.1f},{y-7*math.sin(2*math.pi*k/20):.1f}"
                   for k in range(21))
    txt.append(f'<polyline points="{pts}" fill="none" stroke="#000" '
               f'stroke-width="2"/>')


def caja_naranja(u0, v0, u1, v1):
    esq.append(f'<rect x="{u0}" y="{v0}" width="{u1-u0}" height="{v1-v0}" '
               f'rx="8" fill="none" stroke="{NARANJO}" stroke-width="3" '
               f'stroke-dasharray="10 6"/>')


# --- geometria (u en el sentido del flujo, v transversal) ---------------
vP, vX, vB, vN = 70, 150, 222, 330     # riel P, nodo, bus O, riel N
VT = [10, 26, 42]                        # salidas por el costado (a, b, c)
US = [330, 495, 660]                     # piernas a, b, c
UDC = [30, 90]                           # fuentes DC
UCAP = 195
UD = [800, 775, 750]                     # bajadas al LCL (a, b, c)
VR = [95, 195, 295]                      # columnas del LCL (a, b, c)
UL1, UC, UL2 = (835, 890), [915, 940, 965], (995, 1050)
UG, USTAR = 1105, 1150
VSTAR = 352

# fuentes DC en paralelo y enlace DC
for u in UDC:
    fuente_dc(u, vP, vN)
L_saltos(UDC[0], US[2], vP, [US[0] + 36, US[1] + 36])
L([(UDC[0], vN), (US[2], vN)])
L([(UCAP, vP), (UCAP, (vP + vB) / 2 - 6)])
placas(UCAP, (vP + vB) / 2)
L([(UCAP, (vP + vB) / 2 + 6), (UCAP, (vB + vN) / 2 - 6)])
placas(UCAP, (vB + vN) / 2)
L([(UCAP, (vB + vN) / 2 + 6), (UCAP, vN)])
for u in UDC + [UCAP]:
    P(u, vP)
    P(u, vN)
P(UCAP, vB)
x, y = T(UCAP, vB)
texto(x + 8, y - 12, "O", size=24, anchor="start", lista=txt)

# bus del punto medio, con saltos sobre los cables de S4 de a y b
L_saltos(UCAP, US[2] - 125, vB, [US[0], US[1]])

for k, u in enumerate(US):
    vs1 = (vP + vX) / 2
    L([(u, vP), (u, vs1 - 28)])
    mosfet(u, vs1)
    L([(u, vs1 + 28), (u, vX)])
    vs4 = (vB + vN) / 2 + 6
    L([(u, vX), (u, vs4 - 28)])
    mosfet(u, vs4)
    L([(u, vs4 + 28), (u, vN)])
    P(u, vP)
    P(u, vN)
    ua = u - 125
    L([(ua, vB), (ua, vX), (ua + 10, vX)])
    mosfet(ua + 37, vX, rot=-90)
    mosfet(u - 37, vX, rot=90)
    L([(u - 10, vX), (u, vX)])
    P(ua, vB)
    P(u, vX)
    uo = u + 36
    L([(u, vX), (uo, vX)])
    L([(uo, vX), (uo, VT[k]), (UD[k], VT[k]), (UD[k], VR[k])])

# rotulos de los interruptores (pierna a)
u = US[0]
for (uu, vv, s, dx, dy) in [(u, (vP + vX) / 2, "1", -12, 50),
                            (u, (vB + vN) / 2 + 6, "4", -12, 50),
                            (u - 88, vX, "2", 26, 8),
                            (u - 37, vX, "3", 26, 8)]:
    x, y = T(uu, vv)
    sub_txt(x + dx, y + dy, "S", s, size=22, lista=txt)

# LCL y red
for k in range(3):
    L([(UD[k], VR[k]), (UL1[0], VR[k])])
    bobina(UL1[0], UL1[1], VR[k])
    L([(UL1[1], VR[k]), (UL2[0], VR[k])])
    bobina(UL2[0], UL2[1], VR[k])
    L([(UL2[1], VR[k]), (UG - 21, VR[k])])
    fuente_ac(UG, VR[k])
    L([(UG + 21, VR[k]), (USTAR, VR[k])])
    P(USTAR, VR[k])
    x, y = T(UD[k], VR[k])
    texto(x - 10, y + 26, "abc"[k], size=24, italic=True, anchor="end",
          lista=txt)
for k in range(3):
    uc = UC[k]
    P(uc, VR[k])
    vpl = VR[k] + 30
    L([(uc, VR[k]), (uc, vpl - 6)])
    placas(uc, vpl, ancho=12)
    V_saltos(uc, vpl + 6, VSTAR, [VR[j] for j in range(k + 1, 3)])
L([(UC[0], VSTAR), (UC[2], VSTAR)])
L([(USTAR, VR[0]), (USTAR, VR[2])])
x, y = T((UL1[0] + UL1[1]) / 2, VR[0])
sub_txt(x - 14, y + 8, "L", "1", size=24, anchor="end", lista=txt)
x, y = T((UL2[0] + UL2[1]) / 2, VR[0])
sub_txt(x - 14, y + 8, "L", "2", size=24, anchor="end", lista=txt)
x, y = T(UC[2], VR[2] + 30)
sub_txt(x - 10, y + 44, "C", "f", size=24, lista=txt)

# medicion de potencia (antes del LCL)
P(140, vN, 6.5, AZUL)
x, y = T(140, vN)
sub_txt(x + 12, y + 8, "P", "in", size=24, color=AZUL, lista=txt)
P(UD[2], VR[2], 6.5, AZUL)
x, y = T(UD[2], VR[2])
sub_txt(x + 12, y - 4, "P", "out", size=24, color=AZUL, lista=txt)

# recuadros naranjos de cada bloque (en u, v)
CAJAS = {
    "dc":    (8, 48, 115, vN + 22),
    "conv":  (180, VT[0] - 12, 720, vN + 22),
    "lcl":   (815, VR[0] - 34, 1075, VSTAR + 16),
    "red":   (1075, VR[0] - 34, 1170, VR[2] + 34),
}
for c in CAJAS.values():
    caja_naranja(*c)


def caja_xy(nombre):
    u0, v0, u1, v1 = CAJAS[nombre]
    x0, y0 = T(u0, v0)
    x1, y1 = T(u1, v1)
    return x0, y0, x1, y1


# recuadro gris del esquema
SX0, SY0 = 20, 20
SX1, SY1 = X0 + 380, Y0 + 1185
panel(SX0, SY0, SX1 - SX0, SY1 - SY0)
add(f'<g transform="matrix(0 1 1 0 {X0} {Y0})">' + "".join(esq) + '</g>')
partes.extend(txt)

# ======================= equipos (columna derecha) =======================
XA, XB, WC = 440, 770, 315          # dos columnas de equipos
f_dc = recuadro_equipo(XA, 20, WC, "IT6006C-800-25 (&#215;2)",
                       ["itech1", "itech2"])
f_hi = recuadro_equipo(XB, 20, WC, "PW6001 (<tspan fill='#1f5fbf' "
                       "font-style='italic'>P<tspan dy='6' font-size='19'>"
                       "in</tspan><tspan dy='-6'>, P</tspan><tspan dy='6' "
                       "font-size='19'>out</tspan></tspan><tspan dy='-6'>)"
                       "</tspan>", ["hioki"])
f_op = recuadro_equipo(XB, f_hi[1] + f_hi[3] + 16, WC, "OP4510", ["opal"])

# prototipo (foto rectangular)
b64, a = foto_rect("proto", 600)
ypr = 350
panel(XA, ypr, 645, a + 60, naranjo=False)
texto(XA + 645 / 2, ypr + 31, "10 kW SiC T-Type")
imagen(b64, XA + 22, ypr + 40, 600, a, png=False, rx=8)
f_pr = (XA, ypr, 645, a + 60)

f_lc = recuadro_equipo(XA, 810, WC, "LCL filter", ["lcl"])
f_nh = recuadro_equipo(XB, 950, WC, "NHR9410", ["nhr"])


def zoom(caja, foto, esquinas=("tr", "br")):
    x0, y0, x1, y1 = caja_xy(caja)
    fx, fy, fw, fh = foto
    puntos = {"tr": (x1, y0), "br": (x1, y1)}
    destinos = [(fx, fy + 14), (fx, fy + fh - 14)]
    for e, d in zip(esquinas, destinos):
        linea_xy([puntos[e], d], color=NARANJO, w=2.4, dash="8 6")


zoom("dc", f_dc)
zoom("conv", f_pr)
# LCL y red: una sola linea, de la mitad del recuadro a la mitad de la foto
for caja, foto in [("lcl", f_lc), ("red", f_nh)]:
    x0, y0, x1, y1 = caja_xy(caja)
    linea_xy([(x1, (y0 + y1) / 2), (foto[0], foto[1] + foto[3] / 2)],
             color=NARANJO, w=2.4, dash="8 6")

# el controlador actua sobre el conversor
xo = f_op[0] + f_op[2] / 2
yo = f_op[1] + f_op[3]
cx0, cy0, cx1, cy1 = caja_xy("conv")
linea_xy([(xo, yo), (xo, yo + 22), (cx1 + 4, yo + 22)], w=2.6,
         flecha=True)
texto((cx1 + XB) / 2, yo + 14, "control", size=24, anchor="middle")
# el analizador mide P_in y P_out
texto(f_hi[0] + f_hi[2] - 16, f_hi[1] + 31, "", size=1)

# ======================= ensamblar SVG ==================================
defs.append('<marker id="flecha" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            '<path d="M 0 0 L 10 5 L 0 10 z" fill="#000"/></marker>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
       f'viewBox="0 0 {W} {H}" font-family="{FUENTE}">\n'
       f'<defs>{"".join(defs)}</defs>\n'
       f'<rect width="{W}" height="{H}" fill="#fff"/>\n'
       + "\n".join(partes) + "\n</svg>\n")
os.makedirs(SALIDA, exist_ok=True)
with open(os.path.join(SALIDA, "setup-export.svg"), "w") as f:
    f.write(svg)
print("ok", W, H)
for n, f_ in [("dc", f_dc), ("hi", f_hi), ("op", f_op), ("pr", f_pr),
              ("lc", f_lc), ("nh", f_nh)]:
    print(n, [round(v) for v in f_])
