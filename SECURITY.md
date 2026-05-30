# Seguridad y privacidad

Este repositorio esta pensado para poder ser publico y desplegarse gratis con
GitHub Pages, siempre que los datos sensibles se mantengan fuera del codigo.

## No subir nunca

- Emails, nombres reales, telefonos o datos de pago de participantes.
- Tokens de Google, claves de service account, ficheros `credentials*.json`,
  `token*.json`, `*.pem` o `*.key`.
- Exportaciones completas del Google Sheet.
- `public/datos.json` con datos reales si contiene algo mas que informacion
  publica de la clasificacion.

## Datos permitidos en la web publica

- Alias publico.
- Equipos elegidos.
- Puntos, desglose y predicciones visibles de la porra.
- Partidos, resultados y goleadores.

## Flujo recomendado

GitHub Actions debe leer las fuentes privadas mediante secrets del repositorio,
generar `public/datos.json` durante el workflow y desplegarlo como artefacto de
GitHub Pages. El workflow no debe commitear datos generados a `main`.

