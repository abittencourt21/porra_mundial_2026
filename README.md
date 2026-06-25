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
- La cuota de participacion es de 5 EUR.
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

Para generar datos leyendo la pestana publica del Google Sheet:

```powershell
$env:PYTHONPATH = "src"
$env:GOOGLE_SHEET_TSV_URL = "https://docs.google.com/spreadsheets/d/e/.../pub?gid=...&single=true&output=tsv"
$env:GOOGLE_OVERRIDES_TSV_URL = "https://docs.google.com/spreadsheets/d/e/.../pub?gid=...&single=true&output=tsv"
$env:SPORTSDB_SEASON = "2026"
$env:PREVIOUS_DATOS_URL = "https://abittencourt21.github.io/porra_mundial_2026/datos.json"
python -m porra_mundial.build_data --out public/datos.json
```

`GOOGLE_OVERRIDES_TSV_URL` es opcional. Si la pestana `overrides` no tiene
datos o no esta publicada, no hace falta configurarlo.

`PREVIOUS_DATOS_URL` permite mantener los resultados ya publicados y calcular
subidas/bajadas en la clasificacion. Para pruebas puntuales se puede fijar una
fecha concreta con `BUILD_DATE=YYYY-MM-DD`; si no se indica, se usa la fecha
actual en zona horaria `Europe/Madrid`.

Para revisar que TheSportsDB devuelve eventos del Mundial:

```powershell
$env:PYTHONPATH = "src"
python -m porra_mundial.probe_sportsdb --season 2026
```

## Actualizacion automatica

El workflow `.github/workflows/build-data.yml` publica GitHub Pages cuando:

- Hay un push a `main`.
- Se lanza manualmente desde `Actions` -> `Build and deploy Pages` -> `Run workflow`.
- Se ejecuta la programacion `17 * * * *`, es decir, cada hora en el minuto 17 UTC.

Secrets recomendados en GitHub:

- `GOOGLE_SHEET_TSV_URL`: URL publicada como TSV de la pestana saneada. Es la opcion recomendada y no requiere claves de Google Cloud.
- `GOOGLE_OVERRIDES_TSV_URL`: URL publicada como TSV de la pestana `overrides`. Es opcional.
- `PREVIOUS_DATOS_URL`: URL del `datos.json` publicado en Pages. El workflow ya lo define por defecto.
- `GOOGLE_SHEET_ID` y `GOOGLE_SERVICE_ACCOUNT_JSON`: alternativa para leer un Sheet privado con service account.

No hace falta una key de TheSportsDB con la configuracion actual; el codigo usa el endpoint publico `json/3`.

El build solo consulta SportsDB para los partidos de la fecha de ejecucion y el
dia anterior. Los resultados mas antiguos se conservan leyendo el `datos.json`
publicado en Pages. Si un partido esperado no aparece en la respuesta diaria, el
build intenta buscarlo por nombre de selecciones con `searchevents.php?e=...`
antes de aplicar overrides manuales. No se envia `d=...` en ese fallback porque
algunos partidos aparecen en SportsDB con `dateEvent` UTC del dia siguiente pero
con `dateEventLocal` correcto. Para cuidar el limite diario de la API, si los
partidos de la ventana ya tienen marcador conservado desde `datos.json`, el
build no vuelve a consultar SportsDB para esa ventana. Si SportsDB devuelve menos
partidos de los esperados o cambia nombres de selecciones, se anade una alerta
en `meta.alertas` y se muestra en la pestana de clasificacion.

## Overrides manuales

La pestana `overrides` permite corregir datos sin tocar el codigo. Las columnas
mas utiles son:

- `type`: `match`, `meta` o `goleador`.
- Para partidos: `matchid`, `home_team`, `away_team`, `fecha`, `home_score`, `away_score`, `home_score_90`, `away_score_90`, `pasa`, `status`.
- Para torneo: `estado_torneo`, `campeon`, `subcampeon`, `pichichi_nombre`, `pichichi_goles`.
- Para goleadores: `jugador`, `goles`.

TheSportsDB usa nombres en ingles. El generador normaliza acentos y vincula
selecciones ingles/espanol antes de actualizar resultados, por ejemplo
`South Africa` con `Sudafrica`, `Spain` con `Espana` o `Netherlands` con
`Paises Bajos`.

Hay una plantilla lista para importar en Google Sheets:
`data/overrides_template.csv`.

Si cambia el calendario base, regenerala con:

```powershell
$env:PYTHONPATH = "src"
python -m porra_mundial.overrides_template --out data/overrides_template.csv
```

Uso recomendado:

- Mantener siempre `type` y `matchid`; son la forma mas estable de localizar cada partido.
- Dejar vacios `home_score`, `away_score`, `home_score_90`, `away_score_90`, `pasa` y `status` hasta que quieras forzar una correccion manual.
- En fase de grupos basta con `home_score` y `away_score`; si se dejan vacios los campos a 90 minutos, el motor usa esos mismos valores.
- En eliminatorias usa `home_score_90` y `away_score_90` para el resultado a 90 minutos, y `pasa` para indicar la seleccion clasificada.
- Para cerrar torneo, usa una fila `type=meta` con `campeon`, `subcampeon`, `pichichi_nombre` y `pichichi_goles`.
- Para goleadores, duplica una fila `type=goleador` y rellena `jugador` y `goles`.

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
