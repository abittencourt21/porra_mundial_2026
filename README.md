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
