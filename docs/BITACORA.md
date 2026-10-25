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

### Pendientes

- [ ] Subir `sec_rtopp.tex` al repo y hacerlo coherente: citar `eq:t_i`
      (ya no "reemplaza a Simpson"), usar el N definido en la Seccion II.
- [ ] Unificar Ts: OPAL a 200 us vs. 100 us / 800 us por iteracion GN en
      `sec_rtopp.tex` y `tab:rt_param`.
- [ ] Julia calculo los patrones con Simpson; el texto ahora describe la
      integral exacta (diferencia < 1.9 % de P_cond). Decidir si se menciona.
- [ ] Verificar en `RTOPP_D19.m` si la perdida reportada usa sum(T0) con
      signo: con pulsos negativos (T_i < 0) quedaria sobreestimada. No afecta
      la optimizacion (el termino entra al cuadrado).
- [ ] Como se impuso la continuidad en phi en Julia (comentario % en el
      problema off-line).
- [ ] Cifra del 9 % de tolerancia a fondo armonico: definir el ensayo.
- [ ] `[REF MP3C]` y demas referencias: completar al rehacer la intro.
- [ ] Intro: actualizarla (proximo paso pedido por el autor).
- Pendientes del autor (no tocar sin que lo pida): abstract, figura de
  control y su caption, Tabla III (d = 17 vs 19), Fig. 4, conclusiones,
  bibliografia, resultados experimentales.
