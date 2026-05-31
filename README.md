# Porra Mundial 2026

Porra privada del Mundial 2026 con web estatica en GitHub Pages y datos
publicados de forma saneada.

## Como participar

1. Completa el formulario de participacion:
   https://forms.gle/YBDFtSPVChP3aSGu5
2. Elige una seleccion de cada bombo.
3. Completa tambien campeon, subcampeon y pichichi.
4. Revisa las reglas completas en la pagina de la porra:
   `public/index.html` -> pestaña `Reglas`.

## Resumen de reglas

- Cada participante elige 1 seleccion de cada bombo.
- No se permiten combinaciones demasiado parecidas entre participantes.
- La cuota de participacion es de 10 EUR.
- El bote se reparte 80% para el primer clasificado y 20% para el segundo.
- La puntuacion combina fase de grupos, eliminatorias y bonuses finales.
- Para eliminatorias solo cuenta el resultado a 90 minutos.
- El campeon, subcampeon y pichichi dan puntos extra.

La referencia completa para participantes esta en
[`REGLAS_PARTICIPANTES.md`](REGLAS_PARTICIPANTES.md).

## Web publica

La pagina esta pensada para GitHub Pages y muestra:

- Clasificacion viva.
- Selecciones y puntuacion.
- Grupos y eliminatorias.
- Bombos del torneo.
- Reglas de participacion.

## Funcionamiento de los datos

Los datos visibles en la web se publican como `datos.json` y se generan de
forma automatica a partir de una fuente saneada.

Cuando no hay datos reales disponibles, el proyecto usa los datos de ejemplo
en `data/seed.json`.

## Operacion basica

Para validar el proyecto en local:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
python -m porra_mundial.build_data --out public/datos.json
```

## Estructura del repo

- `public/`: sitio estatico para GitHub Pages.
- `src/porra_mundial/`: logica de puntuacion y generacion de datos.
- `data/`: datos semilla y salidas intermedias.
- `tests/`: pruebas unitarias.
- `.github/workflows/`: automatizacion de build y publicacion.

## Privacidad

La publicacion en Pages solo expone datos sanitizados:

- alias publico
- selecciones
- puntuacion

No se publican nombre real ni email.
