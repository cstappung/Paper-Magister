# Revision del hilo conductor (2026-11-09)

Revision hecha por un agente revisor sobre `MAIN_FINAL.tex` (commit `ed3a667`),
usando los IDs de `main_plan.tex`. Los numeros de linea son de esa version.
Los hallazgos de severidad alta se verificaron contra el texto.

## A. Diagnostico general

La parte off-line se sostiene bien: la cadena va de S2 (formulacion) a S3
(perdidas), a S4.1 (problema) y a S6.3 (comparacion). Ademas, abstract, intro,
S6.3 y conclusiones usan los mismos numeros. La costura esta en el RT:

- se vende como *loss-minimizing* (titulo, contribucion 3, brecha 2), pero en
  S5.4 las perdidas solo actuan como regularizador;
- el RT baja la TDD de 5 % a 1.7 % sin costo en perdidas, lo que contradice la
  tesis off-line de convertir el margen de TDD en perdidas.

Tambien hay contenido fuera de lugar en ambas direcciones: metodo en
Resultados (multi-start, grilla de la LUT, plataforma) y resultados en el
Metodo (barrido de lambda_l). El LCL y el esquema de control estan mal
ubicados y obligan a usar referencias hacia adelante. Faltan dos piezas que el
texto da por existentes: el observador de armonicos y el montaje experimental.

## B. Hallazgos

### Alta

1. **El RT no minimiza perdidas, pero se presenta asi.**
   - Donde: titulo (l. 75), brecha 2 (l. 245), contribucion 3 (l. 257) frente
     a S5.4 (l. 1023-1041: "regularizer rather than a loss minimizer").
   - Propuesta: plantear el RT como "recupera el cumplimiento de IEEE 519 en
     linea preservando las perdidas del patron off-line". Revisar el titulo.
2. **Tesis "margen de TDD -> perdidas" frente al 1.7 % del RT.**
   - Donde: S6.2 (l. 1204-1221), S7 (l. 1401), S5.4.
   - El problema: si el RT baja la TDD sin cambiar las perdidas, el limite de
     TDD no estaba costando perdidas.
   - Propuesta: decir que restriccion esta activa en el optimo off-line (los
     limites individuales del 19 y 23, o la TDD) y matizar las frases.
3. **Validacion experimental del RT declarada y negada a la vez.**
   - Se afirma en la contribucion 4 (l. 259) y en "with the OPP refined
     online" (l. 1262).
   - La `\sug` de las conclusiones dice que es trabajo futuro.
   - Propuesta: ajustar ambas frases segun lo que se midio.
4. **El observador de armonicos nunca se describe.**
   - Aparece solo en F3 y como fuente de x*_h (l. 491, 699, 857).
   - Propuesta: un parrafo con el metodo, la cita y la conversion a unidades
     espectrales. Influye en los 13 ms de recuperacion.

### Media

5. El LCL (S3.3) esta dentro de "Loss Estimation", pero lo usan g_n, phi y Q.
   Moverlo a una seccion de sistema.
6. F3 flota en S3.2 y se cita desde S3.1 para definir phi; pertenece a S4.2.
7. `\delta` tiene dos significados: la cota de continuidad en
   `eq:opp_propuesto` (l. 544, sin definir) y la fase del bloque polar
   (l. 695). Renombrar la cota.
8. Tres corrientes distintas: I en `eq:p_con`, I_cond "corresponding to the
   modulation index" en `eq:p_sw` (l. 476) e I_nom en el RT. Ademas, S5.3 dice
   "reused" aunque el modelo de conmutacion cambia (2f_1, P_sw0, R_G).
9. Hay metodo en Resultados (multi-start l. 1115, grilla 9x25 l. 1128, OPAL
   l. 1130) y resultados en el Metodo (barrido de lambda_l en S5.4).
10. S4.2 adelanta el RT (proximal term, re-siembra) antes de S5. La re-siembra
    se explica tres veces y la motivacion del RT cuatro.
11. La continuidad se argumenta solo en M; en phi, la re-siembra salta. Falta
    una frase sobre el transitorio al re-sembrar.
12. Costura con la LUT de conferencia: "now addressed by both" (l. 746) y
    "1000-point LUT ... 8 min" en las conclusiones (l. 1377). Falta explicar
    por que M tiene un rango estrecho y phi uno completo.
13. El rizado aparece en piezas sueltas que no se conectan: restriccion off-line
    comentada, termino lambda_r en el RT y brecha medida atribuida al rizado.
14. La contribucion 2 no tiene su brecha en la intro (el koukoula_junction con
    restriccion entera aparece recien en S2.3). El orden de las contribuciones
    es inverso al del cuerpo.
15. En S6 no se dice que resultado es simulacion, cual HIL y cual medicion.
    Falta el montaje.

### Baja

16. epsilon_sep (l. 345) se define como algo del RT, pero S5.5 y T4 no lo
    usan.
17. Tres cifras para el cambio de perdidas en el RT: <0.3 %, 0.4 % y 1 %.
18. M = 0.87 no cae en la grilla de 9 indices entre 0.835 y 0.9 (paso
    ~0.0081), pero se la llama "table point".
19. Las medias 6.8/10.1/10.3 W dan reducciones de 33/34 %, no las 34/36 % del
    texto: estas ultimas son la media de las reducciones punto a punto.
    Aclararlo.
20. Referencias hacia adelante innecesarias:
    - Fig. de perdidas citada en S5.4;
    - "Section~\ref{sec:rt}" desde el LCL;
    - "OF" usado antes de definirse.
21. "Hessian positive definite by construction" (contribucion 3): en realidad
    solo vale si lambda_u > 2 lambda_l c.
22. phi no se nombra "load angle" en su definicion (l. 370).
23. El rango de operacion se describe de tres formas (potencia, plano
    (I_d, I_q), M) sin relacionarlas.

## C. Esqueleto propuesto (no aplicado)

1. **S1 Introduction**: contribuciones en el orden del cuerpo.
2. **S2 nueva, System Description**: topologia + F1 + T1, LCL, T3, F3 con la
   cadena de control resumida y el observador.
3. **S3 = S2 actual (formulacion)**, sin epsilon_sep.
4. **S4 = S3.1-S3.2 actual (perdidas).**
5. **S5 = S4.1 actual, "Off-Line Pattern Design"**: suma el multi-start, la
   LUT (M, phi) 9x25 y la continuidad en M y phi.
6. **S6 = S5 actual (RT-OPP)**:
   - abre con la cadena LUT -> semilla -> observador -> generador;
   - la re-siembra queda solo en S5.5;
   - la plataforma y T_s se describen aqui;
   - sin el barrido de lambda_l.
7. **S7 Results**:
   - 7.1 montaje y plataformas (nueva);
   - 7.2 = S6.1 (angulos);
   - 7.3 = cumplimiento off-line;
   - 7.4 = resultados RT (cumplimiento RT, barrido de lambda_l, convergencia,
     transitorios, costo);
   - 7.5 = perdidas.
8. **S8 Conclusions**: off-line -> RT -> medicion, en el mismo orden que el
   cuerpo.

## D. Preguntas probables del revisor

1. Si el RT baja la TDD de 5 % a 1.7 % sin cambiar perdidas, ¿que restriccion
   esta activa off-line?
2. ¿Se midieron las perdidas con el RT activo? ¿Donde esta la validacion
   experimental del RT?
3. ¿Como funciona el observador y que parte de los 13 ms le corresponde?
4. ¿Como se evitan los transitorios al re-sembrar en phi?
5. ¿Es justo comparar 950 Hz por dispositivo con portadoras de 2850 y
   4050 Hz? ¿Por que SV-GDPWM tiene el mayor offset medido?
