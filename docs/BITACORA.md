# Bitacora

## 2026-10-25

### Aplicado en `main_conf_EN.tex` (comentarios azules del autor)

- Intro: estado del arte de correccion en linea (MP3C); el modelo off-line se
  describe como completo, no simplificado. Vacio de tiempo real en una frase.
  Se quito la frase de factor de potencia unitario (LUT indexada por (M,phi)).
- Contribuciones: nuevo punto de validacion experimental en conversor de
  10 kW / 750 V (depende de resultados que aun faltan).
- `eq:tdd`: suma sobre `n in N, n >= 5`, con N = {1,5,7,11,...,49}.
- Perdidas de conduccion: Simpson reemplazado por la primitiva exacta
  G(theta) = theta/2 - sin(2 theta)/4. Nuevos labels `eq:t_i`,
  `eq:pcond_final`. Eliminados `eq:pcond_s2s3`, `eq:simpson`,
  `eq:pcond_total`.
- Problema off-line por par (M,phi) y contraste con el objetivo del RT.
- Control: continuidad por warm start y re-siembra en phi dentro del parrafo
  existente; frase duplicada eliminada.
- Resultados: LUT 9 x 25, OPAL-RT OP4510 con Ts = 200 us. Parrafo de
  cumplimiento armonico en RT sin la cifra del 9 %.

### Seccion RT (`sec_rtopp.tex`) integrada en `main_conf_EN.tex`

- Pegada tal cual en lugar de `\input{sec_rtopp}` (commit propio).
- Coherencia: N se toma de `eq:tdd`; Loss Terms ya no dice que reemplaza a
  Simpson; `eq:rt_T` es t_i con signo (G de `eq:t_i`) y `eq:rt_pcond` usa
  |t_i|; el residuo cuadratico agranda |t_i| sin valor absoluto.

### Opcion A en Loss Terms (comentario azul del autor)

- Se mantiene la FO cuadratica. Parrafo nuevo al final de "Local Quadratic
  Problem": el residuo cuadratico tiene gradiente proporcional al residuo,
  asi que conduccion entra con c*t_i^0 (no c/pi) y conmutacion con e_i^0 ~
  E_on (no 2 f1 I_nom). Con R_G = 22: E_on = 8.6e-5 J/A; gradiente real
  conmutacion <= 0.17 W/rad vs conduccion <= 1.40 W/rad (cociente 0.12); en
  la FO el cociente es 6e-9..8e-8. El modelo de perdidas esta bien; lo que
  no es fiel es como entra al paso GN. lambda_l fija el nivel de TDD.

### Codigo `RTOPP_D19_simple_rip.m` vs. paper (seccion RT)

1. Restricciones IEEE y TDD como pesos adaptativos (integrador log por
   restriccion, una vez por superciclo, con espectro exacto):
   theta_k <- theta_k*|xh_k|/eps_k, theta_T <- theta_T*TDD/(0.95*5 %),
   factor en [0.9, 4], theta en [0.05, 1e3]. Q_k = (W_TDD+theta_T+theta_k)w_k.
   Interpretacion KKT: theta*w_k ~ multiplicador de Lagrange.
2. Fundamental: igualdad exacta en el paso GN (KKT 2x2, complemento de
   Schur) + trim de Newton exacto en cada muestra (FT_TOL 1e-5).
3. Poliedro de angulos (orden con eps_sep, cruce por pi, niveles, caja
   +-0.6 rad alrededor de la semilla): barrera log MU_B = 1e-6, recorte
   fraction-to-boundary TAU_B = 0.9, clamp_angles de salvaguarda.
4. Region de confianza: DG_MAX por resto de Taylor (LIN_FRAC 0.7) en norma,
   DG_OUT = 0.05 rad fuera de norma.
5. Estancamiento: N_STK = 100 superciclos sin mejorar 5 % -> rota la semilla
   (+0, +1, +2 en phi) y reinicia multiplicadores.
6. M_CYC = 5 (fases 0..4).
7. Rizado lado convertidor: armonicos 53..97 (16) en la FO con peso fijo
   LAMBDA_RIP*(g_c/I_L)^2, objetivo 0; J pasa a 66 filas, W cuesta ~2x.
8. P_loss: PLp = (P_CD0 - C_CD*sum T0) + (P_SW0 + C_SW*sum S0) con T0 con
   signo. Cada par (g_i, g_{i+D}) es un pulso (las restricciones de nivel
   lo garantizan) y T0 < 0 <=> pulso negativo, donde S4 reemplaza a S2+S3:
   la conduccion baja en |T0|, pero el codigo la sube. Solo afecta el valor
   reportado, no la optimizacion.
9. Detalle: clamp_angles detecta el cruce por pi con pi (eps_sep*0), pero
   la barrera usa pi - eps_sep/2; entre ambos la barrera trabaja con piso
   S_FLR. P_SW0 = 3.84 W es constante (casi 40 % de P_sw nominal).

### Intro y bibliografia (2026-10-25)

- Intro reescrita con la misma estructura (contexto, T-Type/SiC, modulacion
  programada, multipolar + perdidas, tiempo real) y las referencias del zip.
  Parrafo T-Type sin cambios. Se resolvio `[REF MP3C]` con `geyer_mp3c`.
- Diferencia clave con Tsekouras TPEL 2026: usa secuencia alternada
  Delta u_i = (-1)^(i+1) (no multipolar), NPC, sin perdidas.
- Bibliografia: 38 entradas, reordenadas por primera cita. Detalle y
  candidatas en `docs/REFERENCIAS.md`.

### Intro, segunda iteracion (2026-10-26)

- Parrafo 1 vuelve a la version anterior; IEEE 519 y la red distorsionada
  pasan al parrafo de tiempo real.
- T-Type: 10-15 kHz atribuido a `alemi_ttype` (confirmado en el paper; Yang
  no compara con NPC). Sin mencion de modulacion alta/baja.
- Angulo virtual: `perez_basante_hws` + `koukoula_junction`.
- Menos citas en parrafos 3 y 5: 38 -> 28 referencias.
- Notas `\old` y comentarios azules de la intro eliminados.

### Esquema de control v4 (2026-10-26)

- Nuevos bloques: RT-OPP (entre LUT y generador), observador de armonicos
  (entrada v_abc, salida x*_h al RT-OPP) y angulo de carga phi(P*,Q*) sin
  mediciones (a la LUT y al RT-OPP). M tambien entra al RT-OPP.
- El angulo del bloque polar ahora se llama delta (antes phi, que chocaba
  con el angulo de carga del modelo de perdidas). Texto, caption y la
  definicion de phi en eq:p_con actualizados; x*_h se cita en el termino TDD.
- Fuentes y scripts en `tools/figura_control/`.
- P*,Q* entra una sola vez y se bifurca (punto) hacia la referencia de
  corriente y el bloque phi(P*,Q*); la etiqueta queda bajo el cable.
- Reordenado (pedido del autor, se veia enredado): fila superior = angulo de
  carga | LUT | observador; fila principal = polar -> RT-OPP -> generador.
  La LUT queda sobre el RT-OPP (gamma^0 baja vertical), M y phi llegan a ambos
  con un solo cruce (salto). Ancho 437 mm (antes 456).

## 2026-11-07

### Seccion RT alineada con `RTOPP_D19_simple_rip.m` (vista general)

Pedido del autor: que se entiendan las estrategias del codigo sin entrar en
detalles.
- Parrafo inicial: sin "projected onto the constraints"; las restricciones
  armonicas entran como pesos adaptativos; la LUT da semilla y re-siembras.
- Algorithm 1 reescrito: re-siembra, actualizacion de pesos con espectro
  exacto, W y r con barrera, paso con igualdad de fundamental, region de
  confianza y fraction-to-boundary, trim de Newton por muestra.
- TDD Term: q_n = (w_TDD + theta_T + theta_n)(...)^2; parrafo del termino de
  rizado (armonicos 53..97, peso fijo lambda_r, ganancia lado convertidor).
- Nueva `subsec:rt_con` (Constraint Handling): pesos adaptativos
  (`eq:rt_theta`, lectura KKT), fundamental como igualdad (Schur 2x2 + trim),
  barrera del poliedro de angulos + caja + region de confianza, re-siembras.
- Nueva `subsec:rt_sched` (Execution Schedule): 5 fases, costo fijo por
  muestra, 1 ms por iteracion GN.
- `tab:rt_param`: Ts = 200 us, M_cyc = 5; agregados lambda_r, rho, rho_T,
  [theta_min, theta_max], mu_B, tau_B. Nota \upd de resultados sin lo de Ts.
- No se describen (detalle): histeresis de celdas, DG_OUT, N_STK, N_FBAD,
  clamp_angles, recurrencia de Chebyshev.

### Cambios del autor incorporados (2026-11-07)

El autor pego su `.tex` local: era la version previa a la figura v4
(`bff7560`) mas cambios propios de figuras, que se portaron a la version
actual (no se subio tal cual porque habria revertido PR #9 y #12):
- Fig. del patron: `figuras/Vis_lut/G_raster_sw.png`.
- Fig. de perdidas: `figure*` con `figuras/resumen_3x4/resumen_3x4.png`.
- Figura experimental nueva antes de la bibliografia
  (`figuras/experimental_1x4/experimental_1x4.png`, caption por escribir,
  label `fig:resumen_3x4`).

### Sin reparto en M_cyc fases (2026-11-07)

Pedido del autor: el reparto de cada iteracion en M_cyc fases es detalle de
implementacion; el paper se enfoca en la estructura funcional. Se quito la
frase del parrafo inicial RT, la subseccion Execution Schedule
(`subsec:rt_sched`), la fila M_cyc de `tab:rt_param` y "every 800 us / eight
control periods" de los \sug del abstract y conclusiones. En el codigo sigue
M_CYC = 5 (no mencionarlo salvo que el autor lo pida).

## 2026-11-09

### Repo alineado con el Overleaf

El autor subio el zip del Overleaf. El paper que compila es `MAIN_FINAL.tex`:
igual al del repo salvo la Tabla III (d = 19, 950 Hz; se quitaron la nota
\upd, la \sug y el comentario azul). Se subio tal cual en commit propio,
renombrando `main_conf_EN.tex` -> `MAIN_FINAL.tex`.
- Agregados `IEEEtran.cls`, `Figures/Topologia_T_Type.{pdf,svg}` y en
  `figuras/` las 6 figuras usadas con su `-export.svg`.
- El esquema de control v4 lo rediseno el autor (phi entra arriba al
  RT-OPP, M a la LUT por la izquierda): se reemplazo el PNG y se borraron mi
  SVG generado, el v3 original y `tools/figura_control/` (en el historial).
- d = 19 / 950 Hz aplicado tambien en "Optimized Angles" y conclusiones
  ("three to seven times", 2850/950 = 3.0 y 6450/950 = 6.8). Quedan con
  d = 17 solo las notas \upd del abstract y de resultados, que avisan que
  las cifras (56/40 %, 9.7 W, LUT de 1000 puntos en 8 min) se calcularon con
  d = 17 y hay que verificarlas.

### Resultados de perdidas con las figuras nuevas (2026-11-09)

El autor subio `resumen_3x4_gdpwm` (mapas de perdidas del modelo en el plano
(I_d, I_q), |I| = 10..20 A: OPP d = 19, PD-PWM 2850 Hz, SV-GDPWM 4050 Hz) y
`comparacion_opp_{gdpwm,pwm}_sinplecs` (modelo vs. medicion en 8 puntos).
`.tex` del autor subido tal cual primero (traia la figura gdpwm dos veces y
ya no usaba `experimental_1x4`).
- Seccion renombrada "Simulation and Experimental Results".
- Loss Comparison reescrita: benchmarks PD-PWM (m_f = 57) y SV-GDPWM
  (m_f = 81, cita nueva `hava_gdpwm`); medias del modelo OPP 6.8 W, PD-PWM
  10.1 W, SV-GDPWM 10.3 W; reduccion modelo 33.9 % / 36.0 %, medida 8.4 % /
  33.4 %.
- `tab:comparacion` nueva: perdidas totales en el punto nominal (I_d = 20 A,
  I_q = 0), modelo y medicion (12.7/19.6, 17.4/21.7, 17.6/28.8 W).
- Figuras `fig:comp_gdpwm` y `fig:comp_pwm` con caption, dentro de Loss
  Comparison; se quitaron las dos copias con "Descripcion de la figura".
- Abstract (texto y \sug) y conclusiones con las cifras nuevas; se quito
  "Experimental validation ... future work". Seccion RT: la frase "comparable
  at the rated point (Table)" ahora cita Fig. perdidas.
- Pendiente del autor (\upd): por que la reduccion medida vs. PD-PWM (8.4 %)
  es mucho menor que la del modelo; describir montaje y medicion; confirmar
  marcadores segmentados (espejo en I_d), mu y triangulo/circulo; Fig. 5 de
  armonicos aun con DPWM1 6450 Hz y d = 17; frase de PLECS ("sinplecs").
- Se borraron del repo `figuras/resumen_3x4` y `figuras/experimental_1x4`.

### Argumento de la brecha modelo-medicion (2026-11-09)

Analisis punto a punto (8 puntos, valores de las figuras):
- Offset medicion - modelo: PD-PWM 4.3..6.5 W (media 5.5), OPP 6.4..9.4
  (7.4), SV-GDPWM 9.9..12.8 (11.0).
- Con el offset de PD-PWM sumado a ambos, la reduccion del modelo baja de
  ~34 % a ~20 %; el resto (20 -> 8.4 %) es el offset extra del OPP (+1.9 W),
  atribuido al rizado (modelo con corriente sinusoidal).
- Carga ligera: en (0,-10) y (7,-7) el offset supera a la perdida modelada
  (162 % y 108 %); reduccion 40.0 -> 4.8 % y 37.6 -> 4.1 %, diferencia
  medida 0.4-0.5 W.
- Texto: tres efectos (offset comun, carga ligera, rizado) + cierre "up to
  14.4 % vs PD-PWM, 37.7 % vs SV-GDPWM". Abstract y conclusiones con "up to
  14 %".
- Abierto (\upd): explicar el offset mayor de SV-GDPWM; listar efectos no
  modelados; confirmar que se midio con el RT-OPP activo.

- Captions de las tres figuras de perdidas acortados a lo esencial (pedido
  del autor, 2026-11-09).

### Esqueleto y revision del hilo (2026-11-09)

- Nuevo `main_plan.tex` (esqueleto de la version de revista, IDs S1..S7,
  F1..F8, T1..T5, A1).
- Revision del hilo conductor por un agente revisor: `docs/REVISION_HILO.md`;
  resumen y esqueleto propuesto en la seccion 6 de `main_plan.tex`. No
  aplicado al paper: el autor decide.

### Decisiones del autor sobre la revision del hilo (2026-11-09)

Nueva regla del autor: en `MAIN_FINAL.tex` no se edita texto directo; solo
comentarios `\upd` (rojo) y sugerencias `\sug` (verde). El autor aplica o
responde. (Agregada a CLAUDE.md.)
1. El RT si minimiza perdidas: se mantiene titulo y contribuciones; `\sug` en
   S5.4 para no decir "regularizer rather than a loss minimizer".
2. TDD 1.7 % RT vs 5 % off-line: off-line con restricciones duras, RT con
   pesos en la FO. `\sug` en S4.1, S6.2 y conclusiones ("The off-line
   optimizer drives ...").
3. El RT si se valido experimentalmente: quitadas las notas de trabajo futuro
   en conclusiones y el punto (3) de la nota de S6.3.
4. Observador de armonicos: `\sug` con corchetes en S4.2.
- `main_plan.tex`: cada bloque lleva los hallazgos de la revision como
  comentario rojo + sugerencia verde; bloque propuesto S2* "System
  Description"; seccion 6.1 con estas decisiones.

- `main_plan.tex` (2026-11-11): tabla del mapa de secciones con columnas de
  ancho fijo (se veia aplastada); bloque nuevo S6.0 "Experimental Setup" con
  F9 (foto + diagrama de conexiones) y T6 (equipos), pedido del autor.

- `main_plan.tex` (2026-11-11): aplicados los comentarios azules del autor
  (primero se subio su version tal cual). Cada bloque tiene ahora el campo
  "Cambios" con lo acordado que falta llevar al paper (solo como \upd/\sug).
  Decisiones: contribuciones en el orden del cuerpo; la (b) de S1 se descarta
  (el aporte es que ya no hay enteros); Hessiano DP se mantiene; S2* y el
  esqueleto de 8 secciones quedan a futuro; LCL sale de Loss Estimation
  (propuesto S2.4, por confirmar); phi = desfase de la corriente del
  conversor respecto de la fundamental (no "load angle"); un solo simbolo
  I_cond; ajustar el modelo de conmutacion de S3 para que calce con el RT;
  S4.1 pasa a "Off-Line Pattern Design" con multi-start y LUT, y
  delta -> Delta gamma_max; re-siembra solo en S5.5; plataforma y Ts al
  inicio de S5; barrido de lambda_l a S6.4 (a futuro); S6.0 breve con una
  sola foto (la arma el autor) y T6 (pedir datos al autor); M = 0.87 si es
  punto de tabla (paso 0.001 + punto extra 0.835); el OPP equivale a
  1900 Hz y 2850/4050 Hz son portadoras, cada una la minima que cumple
  IEEE 519; el off-line no restringe el rizado, solo el RT (53-97).
  Confirmado despues: LCL en S2.4 (al final de S2); punto nominal 9.8 kW
  sin redondear en resultados, 10 kW en contribuciones y resumen (el paper
  ya lo cumple).

- `MAIN_FINAL.tex` (2026-11-11): el autor pego su version de Overleaf (commit
  propio). Diferencias con la del repo: no tenia las 5 notas del PR #22
  (restricciones duras, observador, regularizador, RT bajo el limite,
  "off-line optimizer"), volvia la nota de trabajo futuro del RT y la Fig. de
  perdidas va a 0.8\linewidth. Sobre esa version se agregaron las notas del
  plan, solo como \upd/\sug (sin tocar texto): orden de contribuciones,
  apertura de S2, epsilon_sep, LCL a S2.4, phi ("current displacement
  angle" en vez de "load angle", 5 lugares), I_cond, modelo de conmutacion
  igual al RT, titulo y metodo de S4.1, Delta gamma_max, observador, S4.2
  sin RT, plataforma/OF/"now" en S5, S5.3 con un solo cambio, S5.4,
  transitorio de re-siembra, parrafo inicial de S6, S6.0 Experimental Setup,
  phi en S6.1, S6.2, frecuencias y rizado en S6.3, nota de S6.4 y S7. Se
  borraron dos notas resueltas (verificar Fig. 4 y trabajo futuro del RT).
- Diferencia que cambia el resultado (reportada en S3.2): eq:p_sw usa f_1 y
  corriente con signo; el codigo RT usa 2 f_1, magnitud, E = E_0 + E' i y
  correccion por R_G. Si Julia uso eq:p_sw tal cual, el off-line peso la
  conmutacion a la mitad frente a la conduccion. Falta confirmar con el autor.

- `MAIN_FINAL.tex` (2026-11-11, segunda ronda): el autor respondio cada nota
  con un comentario azul (commit propio, tal cual). Aplicado en el texto, con
  el texto anterior en `\old{}`: orden de contribuciones; LCL al final de la
  Seccion II (sin la referencia a sec:rt); epsilon_sep; phi = "current
  displacement angle"; I_cond en perdidas e I_nom solo para TDD (tambien en
  T4 y en la Seccion RT); eq:p_sw igual al RT (2 f_1, magnitud, E_0 + E' i,
  R_G); S4.1 "Off-Line Optimization Problem", Delta gamma_max sin valor y sin
  citar IV-B; frase de restricciones duras (el RT sigue minimizando perdidas);
  metodo de Julia en S4.1 (mismos tiempos, total ~45 min, M de 0.83 a 0.9);
  observador = filtro de Kalman hasta el 13, 5 kHz, compensando el LCL (cita
  nueva `kalman_filter`, 30 refs); S4.2 sin RT; S5 con OPAL-RT y Ts (sin peor
  caso de ejecucion), OF definida, sin "now"; S5.3 con un solo cambio; S5.4
  sin "regularizer" ni barrido; transitorio de re-siembra; intro de
  resultados sin PLECS; subseccion Experimental Setup + Tabla de equipos
  (ITECH IT6006C-800-25 x2, NHR 9410, OPAL-RT OP4510, Hioki PW6001);
  PD-PWM/SV-GDPWM en Harmonic Compliance con TDD en [XX]; RT bajo el limite;
  frecuencias y rizado en Loss Comparison; offset explicado (rizado +
  datasheet sin DPT; hipotesis de SV-GDPWM a baja corriente, a revisar);
  OPP -> RT-OPP en la Tabla de perdidas; conclusiones con 45 min y parrafo
  RT (5 % de ahorro por compensar armonicos).
- Decisiones del autor: "The optimizer drives" se deja; la sugerencia de
  convergencia se quita hasta tener datos (comentada al final de resultados,
  junto con el barrido de lambda_l); solo queda pendiente una subseccion RT
  de compensacion de armonicos.
- Pendientes nuevos: foto del montaje; TDD de PD-PWM/SV-GDPWM al rehacer la
  Fig. 5; cifra unica de cambio de perdidas en RT.
- Respuestas del autor: las perdidas se miden antes del LCL (no incluyen el
  filtro); el off-line se describe con el mismo modelo de conmutacion del RT
  (no hay que revisar Julia); el 5 % de ahorro es al compensar un 8 % de
  quinto armonico a 5 kW.

### Pendientes


- [x] Unificar Ts (200 us; M_cyc ya no se menciona en el paper).
- [x] Seccion RT alineada con `RTOPP_D19_simple_rip.m` (2026-11-07). Falta
      que el autor la revise; el costo O(N_h d^2) no cuenta el rizado.
- [ ] Regenerar Fig. D y Fig. E con `RTOPP_D19_simple_rip.m` (se hicieron con
      `RTOPP_D19.m`); el parrafo de lambda_l usa cifras de la Fig. E.
- [ ] Julia calculo los patrones con Simpson; el texto ahora describe la
      integral exacta (diferencia < 1.9 % de P_cond). Decidir si se menciona.
- [ ] P_loss reportada sobreestima la conduccion con pulsos negativos
      (confirmado en el codigo, ver abajo). Decidir si se corrige con
      abs(T0i) en `PLp` antes de generar figuras de perdidas.
- [ ] Como se impuso la continuidad en phi en Julia (comentario % en el
      problema off-line).
- [ ] Cifra del 9 % de tolerancia a fondo armonico: definir el ensayo.
- [ ] Decidir candidatas de `docs/REFERENCIAS.md` (seccion 3), en especial
      Rahmanpour TIA 2025 (multipolar + limites de red) y Perez-Basante 2019
      (origen del angulo virtual).
- Pendientes del autor (no tocar sin que lo pida): abstract, figura de
  control y su caption, Fig. 5 de armonicos con GDPWM y d = 19, Fig. 4, conclusiones,
  bibliografia, resultados experimentales.

- Figura del montaje (2026-11-11, borrador 1): generador en
  `tools/figura_setup/` (`hacer_figura.py` arma el SVG con las fotos
  embebidas y `render.js` lo pasa a PNG/PDF con Chromium). Fotos del autor en
  `tools/figura_setup/fotos/` (y el ejemplo de referencia). Salida en
  `figuras/setup/`. Aun no se incluye en `MAIN_FINAL.tex`: se itera con el
  autor.
- Figura del montaje, borrador 2 (2026-11-11): esquema trifasico (dos
  fuentes DC en paralelo, enlace DC con punto medio O, tres piernas T-Type
  con MOSFET y diodo de cuerpo, LCL trifasico con C_f en estrella, tres
  fuentes AC de red en estrella) y seis fotos (fuentes DC, prototipo, LCL
  arriba; Hioki, OPAL-RT, NHR abajo) unidas con lineas naranjas punteadas.
  Respuestas del autor: emulador conectado directo; no detallar las senales
  del OPAL-RT (solo "control"); dejar por ahora las etiquetas del lab y las
  IP; cuidar el espacio.

### 2026-11-11 - Figura del montaje, borrador 3 (vertical)

- Pedido del autor: recortes que muestren el equipo completo, sin fondo,
  figura vertical, rotulos cortos como en el ejemplo.
- `tools/figura_setup/hacer_figura.py`: esquema trifasico a la izquierda
  (fuentes DC arriba, T-Type, LCL y red abajo), fotos a la derecha.
  Fotos recortadas con poligono a mano y fondo transparente (sin rembg).
  Lineas naranjas punteadas unen cada bloque del esquema con su foto.
- Rotulos: IT6006C-800-25 (x2), PW6001 (P_in, P_out), OP4510,
  10 kW SiC T-Type, LCL filter, NHR9410. Flecha "control" de OP4510 al
  conversor.
- Pendiente: visto bueno del autor e insertar como Fig. [F9] en
  Experimental Setup.

### 2026-11-11 - Figura del montaje, borrador 4

- Pedido del autor: esquema al centro, foto del prototipo mas chica,
  agregar el modulo SiC (CHB011M12GM4T, imagen del fabricante en
  `fotos/modulo_sic.png`), colores mas intensos, lineas mas gruesas y mejores
  simbolos. No insertar aun en `MAIN_FINAL.tex`.
- Izquierda: ITECH (x2), prototipo (prueba sin fondo, recorte a mano),
  LCL. Derecha: PW6001, OP4510 (flecha de control), modulo SiC, NHR9410.
- MOSFET con canal en tres tramos, flecha y diodo; trazo 3 px; naranjo y
  azul mas saturados; fotos con +25 % de saturacion.
- Pendiente: el autor confirma si el prototipo queda sin fondo.

### 2026-11-11 - Figura del montaje, borrador 5

- Prototipo de vuelta como foto rectangular (sin recorte), mas completa.
- Fuentes DC: circulo con simbolo de continua y polaridad en los bornes.
- Zonas resaltadas como en el ejemplo: recuadros naranjos con relleno
  claro, fotos asociadas con el mismo estilo y un cono translucido entre la
  zona y la foto. PW6001 y OP4510 quedan en gris (no son zona del esquema).
- CHB011M12GM4T es un modulo T-Type (una pierna, segun Wolfspeed): se
  resalta la pierna c y el cono va a la foto del modulo.
