# Genera la figura del montaje experimental (fig:setup) como SVG con las
# fotos embebidas. Despues render.js la pasa a PNG y PDF con Chromium.
#
# Uso:  python3 tools/figura_setup/hacer_figura.py
#       node tools/figura_setup/render.js
#
# Esquema trifasico al centro (fuentes DC, enlace DC, T-Type, LCL, red) y
# fotos arriba y abajo, unidas a su bloque con lineas naranjas punteadas.
# Todas las posiciones estan en px de un lienzo W x H; la figura va a dos
# columnas (figure*), asi que W ~ 18 cm.

import base64
import io
import math
import os

from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
FOTOS = os.path.join(AQUI, "fotos")
SALIDA = os.path.join(AQUI, "..", "..", "figuras", "setup")

W, H = 1600, 1000
FUENTE = "'Times New Roman', 'Liberation Serif', serif"
TXT = 26
GRIS = "#efefef"
BORDE = "#333333"
NARANJO = "#f0a050"
AZUL = "#1f5fbf"
LW = 2.2          # grosor de las lineas del esquema

# --- recortes de las fotos: (archivo, (x0, y0, x1, y1)) en px de la foto ---
RECORTES = {
    "dc":    ("hioki_itech.jpg", (160, 398, 640, 700)),
    "proto": ("prototipo.jpg", (100, 335, 760, 590)),
    "lcl":   ("lcl.jpg", (0, 290, 768, 674)),
    "hioki": ("hioki_itech.jpg", (168, 190, 628, 402)),
    "opal":  ("opalrt.jpg", (128, 312, 800, 466)),
    "nhr":   ("nhr9410.jpg", (135, 540, 610, 722)),
}

partes, defs = [], []


def add(s):
    partes.append(s)


def foto_b64(clave, ancho_px):
    archivo, caja = RECORTES[clave]
    im = Image.open(os.path.join(FOTOS, archivo)).convert("RGB").crop(caja)
    escala = 2 * ancho_px / im.width
    im = im.resize((round(im.width * escala), round(im.height * escala)),
                   Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88)
    return base64.b64encode(buf.getvalue()).decode(), ancho_px * im.height / im.width


def recuadro_foto(clave, x, y, ancho, titulo, sub=None, marco=False,
                  arriba=False):
    """Recuadro gris con la foto y el texto. Si arriba=True el texto va
    sobre la foto. Devuelve (x, y, ancho, alto)."""
    pad = 10
    b64, hf = foto_b64(clave, ancho - 2 * pad)
    ht = 32 if sub is None else 58
    alto = pad + hf + ht
    yf = y + (ht if arriba else pad)
    cid = "clip_" + clave
    defs.append(f'<clipPath id="{cid}"><rect x="{x+pad}" y="{yf}" '
                f'width="{ancho-2*pad}" height="{hf}" rx="6"/></clipPath>')
    estilo = (f'stroke="{NARANJO}" stroke-width="3" stroke-dasharray="10 6"'
              if marco else f'stroke="{BORDE}" stroke-width="1.6"')
    add(f'<rect x="{x}" y="{y}" width="{ancho}" height="{alto}" rx="14" '
        f'fill="{GRIS}" {estilo}/>')
    add(f'<image href="data:image/jpeg;base64,{b64}" x="{x+pad}" y="{yf}" '
        f'width="{ancho-2*pad}" height="{hf}" clip-path="url(#{cid})" '
        f'preserveAspectRatio="none"/>')
    ty = (y + 26) if arriba else (yf + hf + 26)
    texto(x + ancho / 2, ty, titulo)
    if sub:
        texto(x + ancho / 2, ty + 26, sub, size=TXT - 4, color="#444")
    return x, y, ancho, alto


def linea(pts, color="#000", w=LW, dash=None, flecha=False):
    d = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    if flecha:
        extra += ' marker-end="url(#flecha)"'
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" '
        f'stroke-linejoin="round"{extra}/>')


def vlinea_saltos(x, y0, y1, saltos, r=7):
    """Linea vertical de y0 a y1 con saltos (semicirculo) en las y dadas."""
    a, b = min(y0, y1), max(y0, y1)
    d = f"M {x} {a} "
    for ys in sorted(saltos):
        d += f"L {x} {ys-r} A {r} {r} 0 0 1 {x} {ys+r} "
    d += f"L {x} {b}"
    add(f'<path d="{d}" fill="none" stroke="#000" stroke-width="{LW}"/>')


def hlinea_saltos(y, x0, x1, saltos, r=7):
    a, b = min(x0, x1), max(x0, x1)
    d = f"M {a} {y} "
    for xs in sorted(saltos):
        d += f"L {xs-r} {y} A {r} {r} 0 0 1 {xs+r} {y} "
    d += f"L {b} {y}"
    add(f'<path d="{d}" fill="none" stroke="#000" stroke-width="{LW}"/>')


def punto(x, y, r=4.5, color="#000"):
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')


def texto(x, y, s, size=TXT, anchor="middle", italic=False, color="#000"):
    st = ' font-style="italic"' if italic else ""
    add(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
        f'fill="{color}"{st}>{s}</text>')


def sub_txt(x, y, base, sub, size=24, anchor="start", color="#000"):
    """Texto en italica con subindice (p.ej. L_1)."""
    add(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
        f'fill="{color}" font-style="italic">{base}<tspan dy="6" '
        f'font-size="{size*0.68:.0f}">{sub}</tspan></text>')


def mosfet(cx, cy, rot=0, L=56):
    """MOSFET con diodo de cuerpo, vertical (drenador arriba) de largo L,
    centrado en (cx, cy) y rotado rot grados."""
    h = L / 2
    g = (f'<g transform="translate({cx} {cy}) rotate({rot})" fill="none" '
         f'stroke="#000" stroke-width="{LW}">')
    g += (f'<path d="M 0 {-h} L 0 -13 L -9 -13 M -9 13 L 0 13 L 0 {h}"/>'
          f'<path d="M -9 -18 L -9 18" stroke-width="3"/>'
          f'<path d="M -16 -13 L -16 13 M -16 0 L -26 0"/>'
          f'<path d="M 0 -20 L 13 -20 L 13 20 L 0 20"/>'
          f'<path d="M 7 5 L 19 5 L 13 -5 Z" fill="#000"/>'
          f'<path d="M 7 -5 L 19 -5"/>')
    g += '</g>'
    add(g)


def bobina(x0, x1, y, n=4):
    paso = (x1 - x0) / n
    d = f"M {x0} {y} " + "".join(
        f"a {paso/2} {paso/2} 0 0 1 {paso} 0 " for _ in range(n))
    add(f'<path d="{d}" fill="none" stroke="#000" stroke-width="{LW}"/>')


def placas_v(x, ym, ancho=16, sep=6):
    """Placas de un condensador vertical centrado en (x, ym)."""
    linea([(x - ancho, ym - sep), (x + ancho, ym - sep)], w=3)
    linea([(x - ancho, ym + sep), (x + ancho, ym + sep)], w=3)


def fuente_dc(x, yp, yn, r=20):
    ym = (yp + yn) / 2
    linea([(x, yp), (x, ym - r)])
    linea([(x, ym + r), (x, yn)])
    add(f'<circle cx="{x}" cy="{ym}" r="{r}" fill="#fff" stroke="#000" '
        f'stroke-width="{LW}"/>')
    texto(x, ym - 3, "+", size=20)
    texto(x, ym + 16, "&#8722;", size=20)


def fuente_ac(cx, cy, r=20):
    add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" stroke="#000" '
        f'stroke-width="{LW}"/>')
    pts = " ".join(f"{cx-12+24*k/20:.1f},{cy-7*math.sin(2*math.pi*k/20):.1f}"
                   for k in range(21))
    add(f'<polyline points="{pts}" fill="none" stroke="#000" '
        f'stroke-width="2"/>')


def caja_naranja(x0, y0, x1, y1):
    add(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="8" '
        f'fill="none" stroke="{NARANJO}" stroke-width="3" '
        f'stroke-dasharray="10 6"/>')


def zoom(p0, p1):
    linea([p0, p1], color=NARANJO, w=2.4, dash="8 6")


# ======================= geometria del esquema ==========================
DY = 14                                         # desplazamiento vertical
PX0, PX1, PY0, PY1 = 20, 1580, 318 + DY, 708 + DY   # recuadro del esquema
yP, yN = 400 + DY, 672 + DY                     # rieles P y N
yX = 482 + DY                                   # nodo de salida de cada pierna
yB = 556 + DY                                   # bus del punto medio O
XS = [520, 700, 880]                            # piernas a, b, c
YT = [338 + DY, 354 + DY, 370 + DY]                            # salidas por arriba (a, b, c)
XD = [1060, 1030, 1000]                         # bajadas al LCL (a, b, c)
YR = [430 + DY, 530 + DY, 630 + DY]                            # filas del LCL (a, b, c)
XL1, XC, XL2, XG = (1110, 1170), [1205, 1235, 1265], (1300, 1360), 1440
XSTAR = 1490

# ======================= fotos ==========================================
fdc = recuadro_foto("dc", 20, 10, 370, "DC sources",
                    "2 &#215; ITECH IT6006C-800-25")
fpr = recuadro_foto("proto", 410, 10, 640, "SiC T-Type prototype",
                    "CHB011M12GM4T")
flc = recuadro_foto("lcl", 1090, 10, 490, "LCL filter")
fhi = recuadro_foto("hioki", 20, 744, 400, "Power analyzer",
                    "Hioki PW6001: <tspan fill='#1f5fbf' font-style='italic'>"
                    "P<tspan dy='5' font-size='15'>in</tspan><tspan dy='-5'>,"
                    " P</tspan><tspan dy='5' font-size='15'>out</tspan>"
                    "</tspan>", arriba=True)
fop = recuadro_foto("opal", 450, 744, 560, "Real-time controller",
                    "OPAL-RT OP4510", arriba=True)
fnh = recuadro_foto("nhr", 1100, 744, 480, "Grid emulator", "NHR 9410",
                    arriba=True)

# ======================= esquema ========================================
add(f'<rect x="{PX0}" y="{PY0}" width="{PX1-PX0}" height="{PY1-PY0}" '
    f'rx="16" fill="{GRIS}" stroke="{BORDE}" stroke-width="1.6"/>')

# fuentes DC en paralelo y enlace DC
xdc = [70, 140]
for x in xdc:
    fuente_dc(x, yP, yN)
xcap = 270
hlinea_saltos(yP, xdc[0], XS[2], [XS[0] + 40, XS[1] + 40])
linea([(xdc[0], yN), (XS[2], yN)])
linea([(xcap, yP), (xcap, yB - 6 - 30)])
placas_v(xcap, (yP + yB) / 2 + 10)
linea([(xcap, (yP + yB) / 2 + 16), (xcap, yB)])
linea([(xcap, yB), (xcap, (yB + yN) / 2 - 6)])
placas_v(xcap, (yB + yN) / 2)
linea([(xcap, (yB + yN) / 2 + 6), (xcap, yN)])
# arreglo del tramo superior del condensador (de yP a sus placas)
for x in xdc + [xcap]:
    punto(x, yP)
    punto(x, yN)
punto(xcap, yB)
texto(xcap - 22, yB + 8, "O", size=22, anchor="end")

# bus del punto medio con saltos sobre los cables de S4 de las piernas a, b
hlinea_saltos(yB, xcap, XS[2] - 130, [XS[0], XS[1]])

# piernas T-Type
for k, x in enumerate(XS):
    # S1: de P al nodo
    linea([(x, yP), (x, (yP + yX) / 2 - 28)])
    mosfet(x, (yP + yX) / 2)
    linea([(x, (yP + yX) / 2 + 28), (x, yX)])
    # S4: del nodo a N (el cable cruza el bus en yB)
    ys4 = (yB + yN) / 2 + 8
    linea([(x, yX), (x, ys4 - 28)])
    mosfet(x, ys4)
    linea([(x, ys4 + 28), (x, yN)])
    punto(x, yP)
    punto(x, yN)
    # S2/S3: bidireccional del punto medio al nodo
    xa, xb = x - 130, x
    linea([(xa, yB), (xa, yX), (xa + 10, yX)])
    mosfet(xa + 38, yX, rot=-90)
    mosfet(xb - 38, yX, rot=90)
    linea([(xb - 10, yX), (xb, yX)])
    punto(xa, yB)
    punto(x, yX)
    # salida: a la derecha y hacia arriba, sobre el riel P
    xo = x + 40
    linea([(x, yX), (xo, yX)])
    linea([(xo, yX), (xo, YT[k])])
    # tramo superior hasta la bajada al LCL
    linea([(xo, YT[k]), (XD[k], YT[k]), (XD[k], YR[k])])

# etiquetas de los interruptores en la pierna a
x = XS[0]
sub_txt(x - 62, (yP + yX) / 2 + 8, "S", "1", size=22)
sub_txt(x + 26, (yB + yN) / 2 + 16, "S", "4", size=22)
sub_txt(x - 104, yX + 52, "S", "2", size=22)
sub_txt(x - 48, yX + 52, "S", "3", size=22)

# filas del LCL con saltos donde bajan los condensadores
for k in range(3):
    saltos_fila = [XC[j] for j in range(k)]   # condensadores de filas de arriba
    hlinea_saltos(YR[k], XD[k], XL1[0], [])
    bobina(XL1[0], XL1[1], YR[k])
    linea([(XL1[1], YR[k]), (XL2[0], YR[k])])
    texto(XD[k] + 14, YR[k] - 10, "abc"[k], size=22, italic=True,
          anchor="start")
    bobina(XL2[0], XL2[1], YR[k])
    linea([(XL2[1], YR[k]), (XG - 22, YR[k])])
    fuente_ac(XG, YR[k])
    linea([(XG + 22, YR[k]), (XSTAR, YR[k])])
    punto(XSTAR, YR[k])
# condensadores en estrella
ystar = 690 + DY
for k in range(3):
    xc = XC[k]
    punto(xc, YR[k])
    yplac = YR[k] + 34
    linea([(xc, YR[k]), (xc, yplac - 6)])
    placas_v(xc, yplac, ancho=12)
    vlinea_saltos(xc, yplac + 6, ystar, [YR[j] for j in range(k + 1, 3)])
linea([(XC[0], ystar), (XC[2], ystar)])
linea([(XSTAR, YR[0]), (XSTAR, YR[2])])
sub_txt((XL1[0] + XL1[1]) / 2 - 8, YR[0] - 16, "L", "1", size=24)
sub_txt((XL2[0] + XL2[1]) / 2 - 8, YR[0] - 16, "L", "2", size=24)
sub_txt(XC[2] + 18, YR[2] + 44, "C", "f", size=24)

# puntos de medicion de potencia (antes del LCL)
punto(330, yN, 6.5, AZUL)
sub_txt(318, yN - 14, "P", "in", size=24, anchor="end", color=AZUL)
punto(XD[2], YR[2], 6.5, AZUL)
sub_txt(XD[2] - 8, YR[2] + 34, "P", "out", size=24, anchor="middle",
        color=AZUL)

# recuadros naranjos y lineas de zoom hacia las fotos
caja_naranja(40, yP - 26, 170, yN + 22)
caja_naranja(375, yP - 22, 935, yN + 22)
caja_naranja(1095, YR[0] - 46, 1380, ystar + 12)
caja_naranja(XG - 34, YR[0] - 34, XSTAR + 22, YR[2] + 34)
for (bx0, bx1, by), (fx, fy, fw, fh) in [((40, 170, yP - 26), fdc),
                                          ((375, 935, yP - 22), fpr),
                                          ((1095, 1380, YR[0] - 46), flc)]:
    zoom((bx0, by), (fx + 14, fy + fh))
    zoom((bx1, by), (fx + fw - 14, fy + fh))
zoom((XG - 34, YR[2] + 34), (fnh[0] + fnh[2] - 120, fnh[1]))
zoom((XSTAR + 22, YR[2] + 34), (fnh[0] + fnh[2] - 14, fnh[1]))

# el controlador actua sobre el conversor
linea([(700, fop[1]), (700, yN + 24)], flecha=True, w=2.6)
texto(712, fop[1] - 6, "control", size=22, anchor="start")
# el analizador mide P_in y P_out


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
print("ok", W, H, "fotos:", [round(v) for v in fdc + fpr + flc],
      [round(v) for v in fhi + fop + fnh])
