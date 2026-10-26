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

### Pendientes


- [ ] Unificar Ts y M_cyc: OPAL a 200 us y M_CYC = 5 en el codigo (1 ms por
      iteracion GN) vs. Ts = 100 us, M_cyc = 8 en `tab:rt_param`.
- [ ] Actualizar la seccion RT al codigo `RTOPP_D19_simple_rip.m`: Algorithm 1
      dice "projection onto the constraints"; la FO no tiene el termino de
      rizado; la subseccion de restricciones (por escribir) debe describir
      pesos adaptativos + barrera, no proyecciones (ni Dykstra).
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
  control y su caption, Tabla III (d = 17 vs 19), Fig. 4, conclusiones,
  bibliografia, resultados experimentales.
