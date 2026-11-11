# Genera la figura del montaje experimental (fig:setup) como SVG con las
# fotos embebidas. Despues render.js la pasa a PNG y PDF con Chromium.
#
# Uso:  python3 tools/figura_setup/hacer_figura.py
#       node tools/figura_setup/render.js
#
# Todas las posiciones estan en px de un lienzo W x H; la figura va a dos
# columnas (figure*), asi que W ~ 18 cm.

import base64
import io
import os

from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
FOTOS = os.path.join(AQUI, "fotos")
SALIDA = os.path.join(AQUI, "..", "..", "figuras", "setup")

W, H = 1700, 1000
FUENTE = "'Times New Roman', 'Liberation Serif', serif"
TXT = 26          # tamano del texto de las etiquetas
GRIS = "#efefef"  # fondo de los recuadros
BORDE = "#333333"
NARANJO = "#f0a050"
AZUL = "#1f5fbf"

# --- recortes de las fotos: (archivo, (x0, y0, x1, y1)) en px de la foto ---
RECORTES = {
    "hioki": ("hioki_itech.jpg", (168, 190, 628, 402)),
    "dc":    ("hioki_itech.jpg", (158, 398, 642, 752)),
    "nhr":   ("nhr9410.jpg", (132, 498, 612, 816)),
    "proto": ("prototipo.jpg", (100, 110, 760, 860)),
    "opal":  ("opalrt.jpg", (128, 312, 800, 466)),
}


def foto_b64(clave, ancho_px):
    """Recorta, escala al ancho pedido (x2 para nitidez) y devuelve base64."""
    archivo, caja = RECORTES[clave]
    im = Image.open(os.path.join(FOTOS, archivo)).convert("RGB").crop(caja)
    escala = 2 * ancho_px / im.width
    im = im.resize((round(im.width * escala), round(im.height * escala)),
                   Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88)
    alto_px = ancho_px * im.height / im.width
    return base64.b64encode(buf.getvalue()).decode(), alto_px


partes = []
defs = []


def add(s):
    partes.append(s)


def recuadro_foto(clave, x, y, ancho, titulo, sub=None, marco=None):
    """Recuadro gris redondeado con la foto y el texto debajo.
    Devuelve (x, y, ancho, alto) del recuadro."""
    pad = 10
    b64, alto_foto = foto_b64(clave, ancho - 2 * pad)
    alto_txt = 34 if sub is None else 62
    alto = pad + alto_foto + alto_txt
    cid = "clip_" + clave
    defs.append(
        f'<clipPath id="{cid}"><rect x="{x+pad}" y="{y+pad}" '
        f'width="{ancho-2*pad}" height="{alto_foto}" rx="6"/></clipPath>')
    estilo = (f'stroke="{NARANJO}" stroke-width="3" stroke-dasharray="10 6"'
              if marco == "naranjo" else
              f'stroke="{BORDE}" stroke-width="1.6"')
    add(f'<rect x="{x}" y="{y}" width="{ancho}" height="{alto}" rx="14" '
        f'fill="{GRIS}" {estilo}/>')
    add(f'<image href="data:image/jpeg;base64,{b64}" x="{x+pad}" y="{y+pad}" '
        f'width="{ancho-2*pad}" height="{alto_foto}" '
        f'clip-path="url(#{cid})" preserveAspectRatio="none"/>')
    ty = y + pad + alto_foto + 27
    add(f'<text x="{x+ancho/2}" y="{ty}" text-anchor="middle" '
        f'font-size="{TXT}">{titulo}</text>')
    if sub:
        add(f'<text x="{x+ancho/2}" y="{ty+27}" text-anchor="middle" '
            f'font-size="{TXT-4}" fill="#444">{sub}</text>')
    return x, y, ancho, alto


def linea(pts, color="#000", w=2.2, dash=None, flecha=False):
    d = "M " + " L ".join(f"{px} {py}" for px, py in pts)
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    if flecha:
        extra += ' marker-end="url(#flecha)"'
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}"'
        f'{extra}/>')


def punto(x, y, r=5, color="#000"):
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')


def texto(x, y, s, size=TXT, anchor="middle", italic=False, color="#000"):
    st = ' font-style="italic"' if italic else ""
    add(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}"'
        f' fill="{color}"{st}>{s}</text>')


def bobina(x0, x1, y, n=4):
    """Inductor horizontal de x0 a x1 (arcos hacia arriba)."""
    paso = (x1 - x0) / n
    d = f"M {x0} {y} "
    for k in range(n):
        d += f"a {paso/2} {paso/2} 0 0 1 {paso} 0 "
    add(f'<path d="{d}" fill="none" stroke="#000" stroke-width="2.2"/>')


def condensador_v(x, y0, y1):
    """Condensador vertical entre y0 (arriba) e y1 (abajo)."""
    ym = (y0 + y1) / 2
    linea([(x, y0), (x, ym - 6)])
    linea([(x, ym + 6), (x, y1)])
    linea([(x - 18, ym - 6), (x + 18, ym - 6)], w=3)
    linea([(x - 18, ym + 6), (x + 18, ym + 6)], w=3)


def tierra(x, y):
    linea([(x - 16, y), (x + 16, y)])
    linea([(x - 10, y + 6), (x + 10, y + 6)])
    linea([(x - 4, y + 12), (x + 4, y + 12)])


# ======================= recuadros con fotos ============================
hx, hy, hw, hh = recuadro_foto("hioki", 480, 20, 440, "Power analyzer",
                               "Hioki PW6001")
nx, ny, nw, nh = recuadro_foto("nhr", 1000, 20, 400, "Grid emulator",
                               "NHR 9410")
dx, dy, dw, dh = recuadro_foto("dc", 20, 300, 410, "DC sources",
                               "2 &#215; ITECH IT6006C-800-25")
px_, py_, pw_, ph_ = recuadro_foto("proto", 1220, 350, 460,
                                   "SiC T-Type prototype", "CHB011M12GM4T",
                                   marco="naranjo")
ox, oy, ow, oh = recuadro_foto("opal", 480, 830, 420, "Real-time platform",
                               "OPAL-RT OP4510")

# ======================= esquema central ================================
X0, X1, Y0, Y1 = 470, 1170, 360, 680
add(f'<rect x="{X0}" y="{Y0}" width="{X1-X0}" height="{Y1-Y0}" rx="16" '
    f'fill="{GRIS}" stroke="{BORDE}" stroke-width="1.6"/>')
yc = (Y0 + Y1) / 2           # punto medio (O)
yp, yn = yc - 80, yc + 80    # rieles P y N

# rieles DC desde el recuadro de las fuentes
linea([(dx + dw, yp), (700, yp)])
linea([(dx + dw, yn), (700, yn)])
texto(X0 + 18, yp - 10, "+", anchor="start")
texto(X0 + 18, yn + 30, "&#8722;", anchor="start")
texto(X0 + 50, yc + 9, "V", italic=True, anchor="start")
texto(X0 + 66, yc + 16, "dc", size=18, italic=True, anchor="start")

# condensadores del enlace DC y punto medio
xcap = 640
condensador_v(xcap, yp, yc)
condensador_v(xcap, yc, yn)
punto(xcap, yp, 4)
punto(xcap, yn, 4)
linea([(xcap, yc), (700, yc)])
punto(xcap, yc, 4)

# bloque T-Type
bx0, bx1 = 700, 880
add(f'<rect x="{bx0}" y="{yp-12}" width="{bx1-bx0}" height="{yn-yp+24}" '
    f'fill="#fff" stroke="#000" stroke-width="2.2"/>')
texto((bx0 + bx1) / 2, yc - 8, "3L T-Type")
texto((bx0 + bx1) / 2, yc + 24, "SiC")
add(f'<rect x="{bx0-12}" y="{yp-24}" width="{bx1-bx0+24}" '
    f'height="{yn-yp+48}" rx="8" fill="none" stroke="{NARANJO}" '
    f'stroke-width="3" stroke-dasharray="10 6"/>')

# salida trifasica (unilineal con marca de 3 fases)
xg = 1140
linea([(bx1, yc), (950, yc)])
linea([(905, yc + 12), (921, yc - 12)])
texto(913, yc - 18, "3", size=20)
bobina(950, 1010, yc)
linea([(1010, yc), (1040, yc)])
condensador_v(1025, yc, yc + 50)
tierra(1025, yc + 50)
bobina(1040, 1100, yc)
linea([(1100, yc), (xg, yc), (xg, ny + nh)])
texto(980, yc - 40, "L", italic=True, size=24)
texto(990, yc - 34, "1", italic=True, size=16)
texto(1070, yc - 40, "L", italic=True, size=24)
texto(1080, yc - 34, "2", italic=True, size=16)
texto(1052, yc + 40, "C", italic=True, size=24, anchor="start")
texto(1025, yn + 40, "LCL filter", size=22)

# puntos de medicion de potencia (antes del LCL)
xin, xout = 570, 930
punto(xin, yp, 7, AZUL)
punto(xout, yc, 7, AZUL)
texto(xin, yp + 32, "P", italic=True, color=AZUL)
texto(xin + 13, yp + 39, "in", size=18, italic=True, color=AZUL)
texto(xout + 4, yc + 34, "P", italic=True, color=AZUL)
texto(xout + 17, yc + 41, "out", size=18, italic=True, color=AZUL)
linea([(xin, yp), (xin, hy + hh)], color=AZUL, dash="8 6")
linea([(xout, yc), (xout, 320), (880, 320), (880, hy + hh)], color=AZUL,
      dash="8 6")

# senales de control: OPAL-RT -> compuertas, mediciones -> OPAL-RT
xs = 760
linea([(xs, oy), (xs, yn + 24)], flecha=True, w=2.2)
linea([(xs + 50, yn + 24), (xs + 50, oy)], flecha=True, w=2.2)
texto(xs - 10, 760, "gate", size=22, anchor="end")
texto(xs - 10, 786, "signals", size=22, anchor="end")
texto(xs + 60, 760, "v, i", size=22, anchor="start", italic=True)

# referencia al prototipo
linea([(bx1 + 12, yn + 10), (px_, yn + 10)], color=NARANJO, w=3,
      dash="10 6")

# ======================= ensamblar SVG ==================================
defs.append('<marker id="flecha" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
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
