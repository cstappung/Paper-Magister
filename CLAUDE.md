# Paper-Magister

Paper de revista RT-OPP (T-Type multipolar, SiC) de Carlos Stappung y Javier
Pereda (PUC Chile). Version de conferencia ya enviada; se esta extendiendo con
la implementacion en tiempo real.

Contexto completo y decisiones tecnicas: `docs/CONTEXTO_PAPER_RT.md`.
Bitacora de cambios y pendientes: `docs/BITACORA.md` (mantenerla al dia).

## Flujo de trabajo (pedido explicito del autor)

- Cada cambio va en una rama, se abre PR hacia `main` y se hace el merge
  siempre, sin volver a preguntar.
- Si el autor pega un `.tex` nuevo, subirlo primero tal cual en un commit
  propio y luego aplicar los cambios en otro commit, para que el diff muestre
  solo lo modificado.
- Despues de cada cambio al paper, enviar al autor el `MAIN_FINAL.tex`
  actualizado como archivo adjunto (lo compila en su equipo).
- Guardar en el repo todo lo que haga falta para retomar el trabajo entre
  sesiones (contexto, pendientes, decisiones) en `docs/`.

## Convenciones

- Respuestas al autor en espanol, directas. El paper en ingles, estilo IEEE.
- Comentarios en `.tex` y codigo: espanol sin tildes.
- Notas en el `.tex`: `\upd{}` rojo (que actualizar), `\sug{}` verde (texto
  sugerido), `\com{Comentario: ...}` (antes `\textcolor{blue}{...}`) son
  comentarios del autor para Claude. `\old{}` gris muestra el texto anterior bajo un parrafo
  reescrito, para que el autor compare; se borra cuando lo decide. Al aplicar un comentario azul, borrar el comentario y las
  notas `\upd`/`\sug` asociadas; dejar los azules que dicen "pendiente".
- Las sugerencias deben ser texto listo para pegar y decir exactamente donde
  va; el autor prefiere texto breve.
- Desde 2026-11-09 (pedido del autor): en `MAIN_FINAL.tex` NO editar texto
  del paper directamente. Solo agregar `\upd{}` con el comentario y `\sug{}`
  con el texto propuesto; el autor aplica o responde. Se pueden borrar notas
  `\upd`/`\sug` ya resueltas.
- Si el autor responde "aplicar" en un comentario azul, aplicar el cambio en
  el texto, borrar el azul y sus `\upd`/`\sug`, y dejar el texto anterior en
  `\old{}` cuando se reescribe un parrafo o una frase con contenido.
- No modificar el codigo del autor (`code/*.m`, `RTOPP_D19.m`), los `.slx`
  ni los archivos Julia. La
  optimizacion (GN, FO) se deja como la tiene el autor: solo reportar
  diferencias que cambien el resultado.
- LaTeX no viene instalado, pero se puede instalar con apt (unos minutos):
  `apt-get update && apt-get install -y --no-install-recommends
  texlive-latex-base texlive-latex-recommended texlive-latex-extra
  texlive-fonts-recommended texlive-science texlive-pictures lmodern`.
  Compilar en el scratchpad (no subir el PDF) para revisar layout de
  figuras y overfull; si no, revisar braces y labels con Python.
- Visibilidad de notas en el preambulo de `MAIN_FINAL.tex`: lineas
  `\renewcommand{\upd|\sug|\old|\com}[1]{}` (comentar una para mostrar
  esas notas). Los comentarios azules del autor van con `\com{...}`; si el
  autor pega `\textcolor{blue}{...}`, convertirlos a `\com`.
- Figuras: una `figure*` por pagina (`dbltopnumber` = 1, `[t]` sin `!`);
  las de resultados estan adelantadas en el fuente para caer junto a su
  texto. Si cambia el texto, recompilar y revisar que sigan repartidas.

## Archivos

- `MAIN_FINAL.tex`: paper completo, en un solo archivo, mismo nombre que en
  Overleaf (antes `main_conf_EN.tex` en el repo). La seccion
  "Real-Time Implementation" (antes `sec_rtopp.tex`) esta pegada dentro,
  despues de `sec:implementacion` y antes de Simulation Results.
- `main_plan.tex`: esqueleto del paper (no es el manuscrito). IDs de bloque
  S1..S7, figuras F1..F8, tablas T1..T5, algoritmo A1; mantenerlo al dia
  cuando cambie la estructura de `MAIN_FINAL.tex`. Revision del hilo
  conductor en `docs/REVISION_HILO.md`.
- `code/RTOPP_D19_simple_rip.m`: optimizador RT vigente (referencia, solo
  lectura). Difiere de lo descrito en `docs/CONTEXTO_PAPER_RT.md` (que es de
  `RTOPP_D19.m`): ver diferencias en `docs/BITACORA.md`.
- `IEEEtran.cls`, `Figures/` y `figuras/`: solo lo que compila
  `MAIN_FINAL.tex` (espejo del Overleaf). Cada figura va con su PNG/PDF y su
  fuente `-export.svg`. El esquema de control v4 lo rediseno el autor; el
  generador anterior (`tools/figura_control/`) se borro y queda en el historial.
- Si el autor sube un proyecto nuevo, comparar con `MAIN_FINAL.tex` y no
  subir figuras que el `.tex` no use.
