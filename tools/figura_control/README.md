# Figura del esquema de control (fig:control)

Genera `figuras/esquema_control_OPP_v4/` a partir del SVG original del autor
(`figuras/esquema_control_OPP_v3/esquema_control_OPP_v3.svg`): corre un bloque
a la derecha la parte del generador de patrones en adelante y agrega RT-OPP,
el observador de armonicos y el bloque del angulo de carga phi(P*,Q*).
Las etiquetas nuevas se generan con MathJax para que calcen con las originales.

```
npm install mathjax-full@3.2.2           # en esta carpeta
node mj.js labels.json > labels_out.json
python3 build_svg.py ../../figuras/esquema_control_OPP_v3/esquema_control_OPP_v3.svg \
    labels_out.json ../../figuras/esquema_control_OPP_v4/esquema_control_OPP_v4.svg
# PNG a 3x (Chromium de Playwright)
NODE_PATH=$(npm root -g) node render.js ../../figuras/esquema_control_OPP_v4/esquema_control_OPP_v4.svg \
    ../../figuras/esquema_control_OPP_v4/esquema_control_OPP_v4.png 1800 411 3
```
