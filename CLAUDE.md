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
- Guardar en el repo todo lo que haga falta para retomar el trabajo entre
  sesiones (contexto, pendientes, decisiones) en `docs/`.

## Convenciones

- Respuestas al autor en espanol, directas. El paper en ingles, estilo IEEE.
- Comentarios en `.tex` y codigo: espanol sin tildes.
- Notas en el `.tex`: `\upd{}` rojo (que actualizar), `\sug{}` verde (texto
  sugerido), `\textcolor{blue}{Comentario: ...}` son comentarios del autor
  para Claude. Al aplicar un comentario azul, borrar el comentario y las
  notas `\upd`/`\sug` asociadas; dejar los azules que dicen "pendiente".
- Las sugerencias deben ser texto listo para pegar y decir exactamente donde
  va; el autor prefiere texto breve.
- No modificar el codigo del autor (`code/*.m`, `RTOPP_D19.m`), los `.slx`
  ni los archivos Julia. La
  optimizacion (GN, FO) se deja como la tiene el autor: solo reportar
  diferencias que cambien el resultado.
- No hay LaTeX en el entorno: no se compila aqui; revisar braces y labels a
  mano (script rapido en Python).

## Archivos

- `main_conf_EN.tex`: paper completo, en un solo archivo. La seccion
  "Real-Time Implementation" (antes `sec_rtopp.tex`) esta pegada dentro,
  despues de `sec:implementacion` y antes de Simulation Results.
- `code/RTOPP_D19_simple_rip.m`: optimizador RT vigente (referencia, solo
  lectura). Difiere de lo descrito en `docs/CONTEXTO_PAPER_RT.md` (que es de
  `RTOPP_D19.m`): ver diferencias en `docs/BITACORA.md`.
- Figuras (`Figures/`, `figuras/`) aun no estan en el repo.
