# Referencias

Estado de la bibliografia de `main_conf_EN.tex` (28 entradas, orden de cita).
Los textos completos de los papers no se suben al repo (copyright IEEE); aqui
solo queda el registro.

## 1. Referencias de la version de conferencia (segundo zip, 2026-10-25)

El autor entrego los 8 que faltaban. Datos verificados contra cada paper:

| Clave | Referencia | DOI |
|---|---|---|
| `edpuganti_survey` | Edpuganti, Rathore, TIA vol. 51, no. 5, pp. 4212-4228, Sep./Oct. 2015 | 10.1109/TIA.2015.2437351 |
| `lee_npc_ttype` | Lee, Shin, Choi, conferencia (el PDF no imprime el venue; bib dice INTELEC 2015) | verificar |
| `alemi_ttype` | Alemi, Lee, Trans. KIPE vol. 19, no. 2, pp. 173-183, Apr. 2014 (no IEEE) | 10.6113/TKPE.2014.19.2.173 |
| `yang_sic_gan` | Yang, Zhang, Zhang, Yang, PEAC 2022, pp. 55-59 | 10.1109/PEAC56338.2022.9959358 |
| `narasimhan_sic` | Narasimhan et al., WiPDA 2021, pp. 366-371 | 10.1109/WiPDA49284.2021.9645089 |
| `nielsen_10kv` | Nielsen et al., IPEMC2024-ECCE Asia, pp. 1250-1255 | 10.1109/IPEMC-ECCEAsia60879.2024.10567349 |
| `koukoula_junction` | Koukoula et al., ECCE 2024, pp. 3877-3884 | 10.1109/ECCE55643.2024.10861166 |
| `filho_ann` | Filho et al., TIA vol. 47, no. 5, pp. 2117-2124, Sep./Oct. 2011 | 10.1109/TIA.2011.2161533 |

Hallazgos al revisarlos:
- `koukoula_junction`, `geyer_bounded`, `koukoula_ecce23` y `dorfling_thermal`
  usan NPC de media tension con IGCT (no IGBT). Corregido en la intro.
- `koukoula_junction` toma el angulo virtual de Perez-Basante et al. TPEL 2019
  (su ref. [15]). Sugerencia `\sug` en la intro para citarlo.
- El rango 10-15 kHz del punto de cruce NPC/T-Type es de `alemi_ttype`
  (dispositivos Si), no de `yang_sic_gan`; y alemi muestra que el T-Type pierde
  menos a modulacion alta (a modulacion baja gana el NPC). Sugerencia `\sug`
  en el parrafo del T-Type.

## 2. Papers del zip (todos citados en la intro nueva)

El zip coincide con la lista de referencias de Tsekouras TPEL 2026 (excepto
libros). Cuatro `.md` vienen vacios (PDF escaneado, solo la marca de IEEE):
Patel-Hoft 1973, Buja 1980, Kennedy 2003, Cardoso 2006; los datos se tomaron
de la lista de Tsekouras.

| Clave | Uso en la intro |
|---|---|
| `ieee519` (Std 519-2022) | codigo de red |
| `david_mgmt`, `david_aggr` | distorsion de red desconocida |
| `tsekouras_tpel` | antecesor directo: RT-OPP con QP, NPC, secuencia alternada |
| `tsekouras_ecce` | OPP recalculado online con armonicos estimados (Kalman) |
| `patel_she`, `buja_opp` | origen SHE y OPP |
| `franquelo_shm`, `zhou_shc` | SHM / SHC para codigos de red |
| `dahidah_review`, `wang_review`, `buccella_analytic` | metodos de solucion SHE |
| `geyer_bounded`, `koukoula_ecce23`, `dorfling_thermal` | OPP con perdidas / temperatura |
| `rahmanpour_lcl`, `rahmanpour_distorted` | OPP con LCL y red distorsionada |
| `zhao_rt`, `ahmed_rt`, `yang_rt`, `buccella_recursive` | SHE/SHC en tiempo real (QWS) |
| `ibanez_ojies` | SHC-PWM con ANN + refinamiento |
| `geyer_mp3c`, `dorfling_gp3c` | MP3C (modificacion en lazo cerrado) |
| `kennedy_kf`, `cardoso_kf`, `kanieski_kf` | estimacion de armonicos con Kalman |

No citados aun (candidatos para la seccion RT, estimacion de x*):
Fischer-Mariethoz-Morari IECON 2013 (MPC con LCL y armonicos), Vazquez et al.
TPEL 2022 (FCS-MPC con armonicos de carga).

`geyer_mp3c` no venia en el zip; datos verificados en la web (TIA vol. 48,
no. 2, pp. 663-676, 2012, DOI 10.1109/TIA.2011.2181289).

## 2b. Quitadas de la intro por pedido del autor (2026-10-26)

El autor pidio menos citas y no tan antiguas. Se quitaron: `david_mgmt`,
`patel_she`, `buja_opp`, `dahidah_review`, `buccella_analytic`, `zhao_rt`,
`ahmed_rt`, `ibanez_ojies`, `kennedy_kf`, `cardoso_kf`, `kanieski_kf`. Los
datos completos siguen en la lista de referencias de Tsekouras TPEL 2026.
Los de Kalman (`kennedy_kf`, `cardoso_kf`, `kanieski_kf`) pueden servir en la
seccion RT si se describe la estimacion de x*.

Agregada: `perez_basante_hws` (origen del angulo virtual).

## 3. Candidatas encontradas (para que el autor decida)

| # | Referencia | Por que | Donde iria |
|---|---|---|---|
| 1 | S. Rahmanpour, P. Karamanakos, T. Geyer, "Harmonic-constrained three-level optimized pulse patterns for grid-connected converters with LCL filters," IEEE TIA, vol. 61, no. 5, pp. 7481-7492, 2025, DOI 10.1109/TIA.2025.3561700 | Version revista de `rahmanpour_lcl`: limites armonicos de red como restricciones, relaja QWS y posiciones unipolares (multipolar). Es el trabajo mas cercano al problema off-line | Parrafo 3 y 4; diferenciar: minimiza distorsion, no perdidas; NPC |
| 2 | I. Koukoula, P. Karamanakos, T. Geyer, "Loss-constrained three-level optimized pulse patterns with robustness to power factor variations," IEEE TIA, 2025, DOI 10.1109/TIA.2025.3544561 | Version revista de `koukoula_ecce23` | Reemplazar o acompanar `koukoula_ecce23` |
| 3 | I. Koukoula, P. Karamanakos, T. Geyer, "Three-level optimized pulse patterns with bounded junction temperature and relaxed properties," IEEE TPEL, 2025, DOI 10.1109/TPEL.2025.3626863 | Version revista de `koukoula_junction` | Reemplazar o acompanar `koukoula_junction` |
| 4 | A. Perez-Basante et al., "A universal formulation for multilevel selective-harmonic-eliminated PWM with half-wave symmetry," IEEE TPEL, vol. 34, no. 1, pp. 943-957, 2019, DOI 10.1109/TPEL.2018.2819724 | Origen de los "virtual switching angles" en HWS (lo dice Ibanez-Hidalgo TPEL 2024, ref. [7]). Hoy el paper atribuye el angulo virtual a `koukoula_junction` | Parrafo 4 y Seccion II (angulo virtual) |
| 5 | M. Begh, P. Karamanakos, T. Geyer, "Gradient-based predictive pulse pattern control of medium-voltage drives, Part I/II," IEEE TPEL, 2022, DOI 10.1109/TPEL.2022.3190708 / 3190713 | Modificacion en tiempo real de OPP precalculados (familia MP3C) | Parrafo 5, junto a `geyer_mp3c` |
| 6 | S. Rahmanpour, P. Karamanakos, T. Geyer, "Robust optimized pulse patterns for converters connected to a distorted grid via LCL filters," ECCE 2025 | OPP robusto a armonicos desconocidos de la red (hasta 55 % de los niveles maximos de la norma) | Parrafo 5; y para discutir la cifra del 9 % |
| 7 | A. K. Rathore, J. Holtz, T. Boller, "Synchronous optimal pulsewidth modulation for low-switching-frequency control of medium-voltage multilevel inverters," IEEE TIE, vol. 57, no. 7, pp. 2374-2381, 2010 | Referencia clasica de OPP multinivel a baja frecuencia | Parrafo 3 |
| 8 | R. Teichmann, S. Bernet, "A comparison of three-level converters versus two-level converters for low-voltage drives, traction, and utility applications," IEEE TIA, 2005 | Comparacion clasica NPC/T-Type (verificar) | Parrafo 2 |
| 9 | "The benefits of SiC MOSFETs in a T-type inverter for grid-tie applications," IEEE TPEL (RMIT/DTU, verificar autores y anio) | T-Type con SiC en conexion a red | Parrafo 2, junto a `yang_sic_gan` |

Fuentes de la busqueda: trepo.tuni.fi, researchportal.tuni.fi,
tobiasgeyer.org, research.tue.nl, ekoizpen-zientifikoa.ehu.eus, dblp,
orbit.dtu.dk. Verificar volumen y paginas en IEEE Xplore antes de citar.
