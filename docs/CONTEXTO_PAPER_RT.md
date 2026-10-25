# Contexto: paper de revista RT-OPP (T-Type multipolar) — traspaso de chat

Documento de traspaso para seguir escribiendo el paper en otro chat. Resume
todo lo decidido y medido hasta el 25-10-2026. Respuestas al usuario en
**espanol**; el paper en **ingles**.

---

## 1. Que se esta haciendo

El usuario (Carlos Stappung, con Javier Pereda, PUC Chile) tiene un paper de
conferencia ya enviado: *"Loss-Minimizing Multipolar Optimal Pulse Patterns for
Grid-Connected T-Type Converters With TDD Compliance"* (IEEEtran conference,
archivo `main_conf_EN.tex`). Lo esta convirtiendo en **paper de revista**
agregando la **implementacion en tiempo real (RT-OPP)**.

- La seccion nueva vive en `sec_rtopp.tex` y se incluye con `\input{sec_rtopp}`.
- Hasta ahora solo esta escrita la **funcion objetivo (FO)**: modelo armonico
  linealizado, termino TDD, perdidas, QP local y ecuaciones normales.
- **Falta**: la subseccion de **restricciones** del RT y los resultados RT.

## 2. Archivos (llevar al repo)

| Archivo | Que es |
|---|---|
| `main_conf_EN.tex` | Paper completo con notas **rojas** `\upd{}` (que actualizar) y **verdes** `\sug{}` (texto sugerido). `\input{sec_rtopp}` ya movido. |
| `sec_rtopp.tex` | Seccion "Real-Time Implementation" (FO + Algorithm 1 + tabla de parametros RT). |
| `figuras_rt/rt_convergencia.pdf/.png` | Figura D: convergencia (aceptada por el usuario). |
| `figuras_rt/rt_lambda.pdf/.png` | Figura E: barrido de lambda_l (pendiente de que el usuario la apruebe). |
| `figuras_rt/*.m, *.mat` | Scripts y datos para regenerar D y E. |
| `figuras_rt/instrumentadas/` | `RTOPP_D19L.m` (lambda y KSW via `getappdata`) y `RTOPP_D19N.m` (gradiente lineal de perdidas): copias del bloque usadas solo para la figura E. |
| `RTOPP_D19.m` | Codigo del bloque RT (referencia, **no modificar**). |
| `gamma_phi.mat` | LUT: `mod_index` (1x9, 0.835..0.9), `phi_index` (1x25, -180..180 deg cada 15), `optimized_gamma_list3` (25x9x38). |
| `Conversor_T-Type_05-06-26_limpio.pptx` | Diapos antiguas del usuario con la derivacion de la FO (referencia). |

No hay LaTeX instalado en el PC local: nada se ha compilado aqui. El usuario
compila en su equipo y compartio un PDF (`Latex Paper Revista.pdf`).

## 3. Estructura del paper (labels existentes)

1. Introduction (contribuciones en itemize)
2. Multipolar Harmonic Formulation — `eq:fourier_gamma` (a_n, b_n con 2d angulos
   virtuales), `eq:tdd` (I_TDD con `\hat v_n g_n`, normalizado a I_nom),
   `eq:niveles` (restricciones lineales de nivel)
3. Loss Estimation `sec:perdidas` — `eq:p_con`, `eq:pcond_s2s3`, `eq:simpson`,
   `eq:pcond_total`, `eq:pcond_final`, `eq:p_sw`; LCL `sec:filtro`, `eq:fres`;
   tablas `tab:estados_cond`, `tab:transiciones_zvs`; figs `fig:ttype`,
   `fig:patron_opp`, `fig:control`
4. OPP Implementation Scheme — `eq:opp_propuesto` (problema off-line),
   `tab:parametros`, subseccion Control and Pattern Generation `sec:implementacion`
5. **Real-Time Implementation** `sec:rt` (`\input{sec_rtopp}`, DESPUES de
   `sec:implementacion` y ANTES de Simulation Results; si va antes, la subseccion
   de control queda numerada V-E dentro de la seccion RT)
6. Simulation Results — `fig:patron_pulsos`, `fig:fft_comparacion`,
   `fig:perdidas`, `tab:comparacion`
7. Conclusions; bibliografia manual (11 refs)

Macros: `\gv` (gamma negrita), `\av`, `\pct` (% en texto y matematica),
`\definecolor{Gray}{gray}{0.9}` + `\rowcolor{Gray}` en tablas booktabs,
`\upd{}` rojo, `\sug{}` verde (cada una con un `\renewcommand` comentado para
ocultarlas). Paquetes ya cargados: amsmath, algorithmic, booktabs, xcolor[table],
stfloats, subcaption, tikz, comment.

Datos del paper off-line: d = 17 (850 Hz), Vdc = 750 V, L1 = L2 = 1 mH,
C = 46 uF, f_res = 1050 Hz (armonico 21), I_nom = 20 A, f1 = 50 Hz, 10 kW,
modulo CHB011M12GM4T. Resultados: perdidas -56 % vs DPWM1 6450 Hz, -40 % vs
PWM 2850 Hz; tabla nominal OPP 9.9/9.7/19.6 W, TDD 5.00 %. Resuelto en Julia
con Ipopt (archivos Julia: solo lectura).

## 4. Seccion RT escrita (`sec_rtopp.tex`)

Notacion elegida (alineada con el paper):
- Armonicos n en N = {1,5,7,11,...,49} (impares no triples < 50), N_h = 17.
- x = [x_1; x_5; ...], x_n = [a_n; b_n]. Linealizacion x(g+dg) ~ x + J dg,
  dJ: da_n/dg_i = -(2/pi)cos(n g_i), db_n/dg_i = -(2/pi) sin(n g_i).
- x* : fundamental [0, M]; armonicos n>=5 = fondo de la red (0 con red limpia).
  x_e = x* - x.
- TDD RT: I_TDD = 100%/I_nom * sqrt(sum (Vdc/2 g_n)^2 ||x_n - x*_n||^2).
- Q = diag(q_1 I2, q_5 I2, ...), q_1 = 1, q_n = w_TDD (Vdc g_n /(2 I_nom))^2.
- Conduccion: t_i = int_{g_i-phi}^{g_{i+d}-pi-phi} sin^2 = G(g_{i+d}-pi-phi) - G(g_i-phi),
  G(th) = th/2 - sin(2th)/4. P_cond = r_ds,on I_nom^2 (1 - (1/pi) sum t_i).
  t ~ t0 - B_t dg, B_t = [diag(p), -diag(p')], p_i = sin^2(g_i-phi), p'_i = sin^2(g_{i+d}-phi).
- Conmutacion: e_i = E_on|sin(g_i-phi)| + E_off|sin(g_{i+d}-phi)|.
  P_sw = P_sw0 + 2 f1 I_nom sum e_i, P_sw0 = 2 f1 d (E_on0 + E_off0).
  e ~ e0 - B_e dg, B_e = [diag(s), diag(s')], s_i = -E_on cos(g_i-phi) sgn(sin(g_i-phi)),
  s'_i = -E_off cos(g_{i+d}-phi) sgn(sin(g_{i+d}-phi)).
  (Se renombro S_i -> e_i, B_P -> B_t, B_S -> B_e para no chocar con los
  interruptores S1..S4.)
- FO: min 1/2||x_e - J dg||_Q^2 - (lam_l c/2)||t0 - B_t dg||^2
  + (lam_l/2)||e0 - B_e dg||^2 + (lam_u/2)||dg||^2, con c = r_ds,on I_nom^2 = 4.4 W.
- Ecuaciones normales W dg = r:
  W = J'QJ - lam_l c B_t'B_t + lam_l B_e'B_e + lam_u I;
  r = J'Q x_e - lam_l c B_t' t0 + lam_l B_e' e0.
- Resultado propio: B_t'B_t son bloques 2x2 con autovalores 0 y p^2+p'^2 <= 2
  => W >= (lam_u - 2 lam_l c) I; con lam_u = 1, lam_l = 0.01, margen 0.91 (W siempre DP).
- Costo: Q diagonal, B_t/B_e bloques diagonales -> bandas en diagonal y +-d;
  dominante J'QJ, O(N_h d^2).
- Algorithm 1 (pseudocodigo con `algorithmic` dentro de un figure, contador
  propio `algcount`): sembrar desde LUT(M,phi) en primer llamado o flanco de
  enable; loop: evaluar x, J, t0, B_t, e0, B_e; x_e; armar W, r; dg = W^-1 r con
  region de confianza; proyectar gamma+dg sobre las restricciones; aplicar.
- Texto aclara que **cada iteracion GN se reparte en M_cyc = 8 fases (una por
  muestra)**, o sea una iteracion cada 800 us; entre medio se aplica el ultimo
  patron valido.
- Tabla `tab:rt_param`: Ts 100 us, M_cyc 8, d 19, N_h 17, lam_l 0.01, lam_u 1,
  w_TDD 1, I_nom 20 A, R_G 22 ohm.

## 5. Hechos del codigo `RTOPP_D19.m` (1689 lineas, no tocar)

- Firma: `[angle_f, delta_u, TDD, P_loss, x_final, seed, ieee_vio] =
  RTOPP_D19(x_star, PHI, enable, mod_index, phi_index, gammas, fg)`;
  `mod_index/phi_index/gammas` son **Parameters** (no senales); PHI en radianes.
- D = 19, N = 38, HARM = [1 5 7 11 13 17 19 23 25 29 31 35 37 41 43 47 49].
- g_h (corriente de red por unidad de espectro, ya incluye Vdc/2):
  597.9, 126.5, 95.9, 74.8, 74.5, 102.0, **174.1 (19)**, **128.9 (23)**, 56.9,
  22.6, 16.3, 9.58, 7.65, 5.17, 4.34, 3.17, 2.74.
- Limites IEEE 519 (Isc/IL < 20): 4 % (<11), 2 % (11-15), 1.5 % (17-21),
  0.6 % (23-33), 0.3 % (>=35).
- Sintonia: LAMBDA_U 1, LAMBDA_LOSS 0.01, W_TDD 1, FUND_TOL 1e-4, N_PASS 21,
  OMEGA 1.90 (sobre-relajacion de proyecciones), RHO 0.90 (margen IEEE),
  LIN_FRAC 0.70 (region de confianza por error de Taylor), TDD_MAX 5,
  TDD_FRAC 0.95, EPS_SEP 0.2 deg, histeresis de semilla HYST_P/HYST_M,
  trim de fundamental FT_TOL 1e-5, modo reparacion (QP con presupuesto,
  N_REP, re-siembra por estancamiento), M_CYC 8.
- Restricciones (para la subseccion que falta): R1 discos IEEE por armonico,
  R4 bola de TDD, R2 fundamental, R3 angulos fisicos (orden con eps_sep, cruce
  por pi, nivel, caja), proyecciones ciclicas sobre-relajadas; luego "3b" trim
  de fundamental cada muestra. Re-siembra: el eje **phi** re-siembra al cruzar
  celda (con histeresis); el eje **M no** re-siembra.
- Perdidas en el codigo: R_ON 0.011, I_CON 20 fijo, R_GATE 22.
  kon = (-0.0048149 R^2 + 0.31277 R + 0.25531)/0.25531,
  koff = (-0.00088891 R^2 + 0.14795 R + 0.16746)/0.16746,
  E_ON = 4.570969372e-6 kon, E_OFF = 2.369616108e-7 koff (J/A),
  E_ON0 = 1.025851298e-4 kon, E_OFF0 = 5.127701211e-6 koff (J),
  P_loss reportada = (I^2 R_on - I^2R_on/pi sum T0) + (P_SW0 + 2 f I sum S0).
- qobj(1:2) = 1; qobj armonicos = W_TDD (g_h/20)^2. TDD medido sobre x - x*.

## 6. Diferencias matematicas detectadas

**Paper off-line vs RT:**
1. Simpson -> integral exacta G(theta). Medido sobre toda la LUT: diferencia
   max 1.9 % de P_cond (0.06 W), media 0.7 %.
2. Perdidas en la FO RT como residuos **cuadraticos** (-c||t||^2 + ||e||^2), no
   lineales como en el paper -> otro minimizador.
3. |sin| en conmutacion (paper: seno con signo). En M = 0.87, phi = -15 deg,
   8 de 38 eventos caen en el semiciclo contrario; en toda la LUT ~52 %.
4. phi explicito; LUT indexada por (M, phi).
5. I fijo 20 A en RT (paper: I_cond(M)).
6. RT minimiza TDD con perdidas como regularizador; el off-line minimiza
   perdidas s.a. TDD <= 5 %.
7. x* incluye fondo armonico de red.
8. d = 19 en RT vs d = 17 en el paper (850 vs 950 Hz).
9. eq:p_sw del paper parece no tener el factor 2 (2d eventos/periodo) ni
   P_sw0: verificar contra Julia.

**Diapos vs codigo** (las ecuaciones normales coinciden termino a termino):
|sin| vs seno firmado; phi en T_i/S_i (diapo lo omite en T, S pero lo usa en
derivadas); peso fundamental 100 (diapo) vs 1 (codigo); perdida reportada
lineal (codigo) vs c||J||^2 (diapo); x* con fondo de red.

## 7. Resultados numericos ya obtenidos

- **Escala de la FO** (M = 0.87, phi = -15): en W, J'QJ ~ 100, conduccion ~1.5e-3,
  conmutacion ~9.4e-12; la conmutacion no se minimiza en la practica.
- **Figura D (convergencia, 4 escenarios, 6000 muestras)**:
  punto de rejilla: TDD 4 % -> 1.7 %; fuera de rejilla (M 0.875, phi -22.5):
  TDD queda en 5.0 % (tope); red con 5o 4 % + 7o 3 %: TDD 26 %, I/Ilim 5.7 ->
  cumple en ~13 ms; semilla con ruido +-0.05 rad: TDD 203 % -> cumple en ~20 ms.
  Perdidas de modelo ~8.07 W, cambian < 1 % (fuera de rejilla 8.14 -> 8.21).
- **Figura E (barrido lam_l en M 0.87, phi -15, red limpia)**: el TDD va de
  0.04 % (lam 0) a ~4.7-5 %; las perdidas cambian < 0.3 % (8.05-8.07 W) en las tres
  variantes (cuadratica implementada; conmutacion en watts; gradiente lineal real).
  La cuadratica sobre lam ~0.01 sube TDD **y** perdidas (efecto de maximizar
  sum T^2). Lectura: desde la LUT las perdidas son localmente planas; el RT
  corrige armonicos, las perdidas las fija el off-line. lam_l = 0.01 deja el TDD
  en ~1/3 del limite.
- **Tolerancia a fondo armonico de red**: ~9 % de la fundamental en cualquier
  armonico individual (pruebas previas).
- Caveats: perdidas = modelo del bloque (I = 20 A fijo), no PLECS; TDD solo sobre
  armonicos modelados (<= 49, sin triples).

## 8. Plan de figuras de la seccion RT

- A (diagrama de flujo): **rechazada** -> se hizo pseudocodigo (Algorithm 1).
- B (ganancia LCL/pesos): **rechazada** (es una formula).
- C (geometria de perdidas sobre el patron, t_i sombreado, eventos |sin|): el
  usuario **lo va a considerar**.
- D (convergencia): **hecha y aceptada**; aun no insertada en el .tex.
- E (lambda): **hecha, pendiente de aprobacion**; no insertada.
- Futuras: transitorio por escalon de M/phi, espectro LUT vs RT con red
  distorsionada, histograma de tiempo de ejecucion OPAL (100 us), tolerancia
  por armonico.

## 9. Notas rojas/verdes en `main_conf_EN.tex`

30 notas `\upd` (rojo) y 25 `\sug` (verde) + 1 de cada una en `sec_rtopp.tex`.
Placeholders en **negrita entre corchetes** (`[XX] us`, `[REF MP3C]`,
`[validated on OPAL-RT OP4510]`, `Fig. [X]`). Sin sugerencia (requieren datos
nuevos): Fig. 4 con d = 19, Fig. 5, Loss Comparison, Fig. 6, Tabla IV.
Referencias candidatas en la nota 30 escritas de memoria: verificar.

## 10. Convenciones y restricciones del usuario (respetar siempre)

- No modificar `RTOPP_D19.m`, los `.slx`, ni archivos Julia; copias
  instrumentadas solo en carpetas temporales.
- No escribir en `C:\Users\PC07PEC\Desktop\Workspace_Opal4510\...`.
- Optimizacion (GN, FO) "como la tenia el usuario": solo reportar diferencias,
  no cambiarlas. `gammas` y PHI siguen como Parameter, PHI en radianes.
- Comentarios en codigo y en fuentes .tex: espanol **sin tildes**.
- Al reportar diferencias matematicas: solo las que cambian el resultado, no
  reformulaciones equivalentes.
- Respuestas en espanol, directas; el paper en ingles estilo IEEE.

## 11. Proximos pasos sugeridos

1. Escribir la subseccion RT de **restricciones** (R1 discos IEEE con margen RHO,
   R4 bola TDD, R2 fundamental + trim, R3 angulos; proyecciones ciclicas con
   OMEGA; region de confianza LIN_FRAC; modo reparacion/re-siembra) en el mismo
   estilo que la FO.
2. Insertar figura D (y E si se aprueba) con caption y referencias; reemplazar
   los `Fig. [X]` de las sugerencias.
3. Decidir d = 17 vs 19 y unificar tabla, figuras y conclusiones.
4. Decidir la presentacion del termino de perdidas en el RT (ver Figura E).
5. Completar placeholders (tiempos OPAL, referencias).
