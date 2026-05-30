# Porra Mundial 2026

Base tecnica para una porra privada del Mundial 2026:

- `src/porra_mundial`: motor Python de puntuacion y generacion de `datos.json`.
- `tests`: pruebas unitarias de las reglas de negocio.
- `data`: datos semilla y salida generada.
- `public`: web estatica para GitHub Pages.
- `.github/workflows`: automatizacion preparada para generar y publicar datos.

## Comandos utiles

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
python -m porra_mundial.build_data --out public/datos.json
```

## Siguiente integracion

El motor ya esta separado de las fuentes de datos. Los proximos pasos naturales son:

1. Conectar lectura de Google Sheet para `quinielas`.
2. Sondear TheSportsDB `idLeague=4429`, temporada `2026`.
3. Aplicar `overrides` manuales cuando falten datos a 90 minutos, clasificados o goleadores.

## Google Form y Google Sheet

Crear un Google Form con estos campos:

- Nombre real
- Alias
- Email
- Equipo del Bombo 1
- Equipo del Bombo 2
- Equipo del Bombo 3
- Equipo del Bombo 4
- Campeon
- Subcampeon
- Pichichi

Conectar el Form a un Google Sheet y renombrar la pestana de respuestas a
`quinielas`. Crear tambien una pestana `overrides` para correcciones manuales.

El generador solo publica datos sanitizados: `alias`, equipos, predicciones
visibles y puntuacion. No exporta nombre real ni email al `datos.json`.

### Secrets de GitHub Actions

Crear una service account en Google Cloud con permiso de lectura sobre Google
Sheets, compartir el Sheet con el email de esa service account, y anadir estos
secrets al repositorio:

- `GOOGLE_SHEET_ID`: el ID del Sheet, tomado de la URL.
- `GOOGLE_SERVICE_ACCOUNT_JSON`: el JSON completo de credenciales de la service account.

Si faltan esos secrets, el workflow usa `data/seed.json` como demo.
