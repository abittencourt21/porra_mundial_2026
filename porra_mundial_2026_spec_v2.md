# Porra Mundial 2026 — Especificación del proyecto (v2)

## Arquitectura

```
Google Form ──► Google Sheet ──┐
                               ├──► [Python en GitHub Actions] ──► datos.json ──► GitHub Pages
TheSportsDB (liga 4429) ───────┘         (cron cada hora)            (commit)      (web pública)
```

**Captación:** Google Form → Google Sheet.
**Cerebro:** script Python en GitHub Actions (cron horario durante el torneo).
**Front:** HTML/React estático en GitHub Pages que lee `datos.json`.
**Coste:** 0 €.

---

## Identidad visual (marca oficial FIFA World Cup 2026)

La marca oficial usa un núcleo sobrio de **negro, blanco y oro** (el trofeo), con tonos por país anfitrión: **Canadá en rojos, México en verdes, Estados Unidos en azules**. El emblema es el trofeo dentro del número **26** ("WE ARE 26").

### Paleta CSS (variables del front)

```css
:root{
  /* Núcleo */
  --bg:        #0a0a0a;   /* negro base */
  --surface:   #151515;   /* tarjetas */
  --surface2:  #1d1d1d;   /* tarjetas elevadas */
  --line:      #2a2a2a;   /* bordes */
  --white:     #f5f5f5;   /* texto principal */
  --muted:     #9a9a9a;   /* texto secundario */
  --dim:       #5c5c5c;   /* texto terciario */
  /* Oro (trofeo) */
  --gold:      #c8a24b;   /* oro principal */
  --gold-bright:#e6c766;  /* oro destacado (líder, campeón) */
  --gold-dim:  #8a7234;   /* oro apagado (bordes) */
  /* Acentos país anfitrión */
  --can:       #c8102e;   /* Canadá (rojo) */
  --mex:       #00833e;   /* México (verde) */
  --usa:       #0a3161;   /* Estados Unidos (azul) */
}
```

### Mapeo de bombos a color (en la web)

| Bombo | Color | Hex |
|---|---|---|
| 1 | Oro | `#c8a24b` |
| 2 | Plata | `#b8b8b8` |
| 3 | Bronce | `#cd7f32` |
| 4 | Azul claro | `#7da3d4` |

### Tipografía

- Display / titulares: **Barlow Condensed** (700/800). Evoca el aire condensado del lettering oficial.
- Texto / datos: **Barlow** (400/500/600).
- Ambas se cargan desde Google Fonts.

### Logo

El emblema oficial (trofeo dentro del "26") es marca registrada de la FIFA. Para una porra privada no comercial su uso es razonable, pero conviene tenerlo presente.
- **Fuente oficial de activos:** https://www.fifa.com/es/tournaments/mens/worldcup/canadamexicousa2026
- En la plantilla actual el logo se sustituye por un **emblema "26" hecho en CSS** (cuadro con borde oro y el número), como marcador de posición. Para usar el oficial: descargar el PNG/SVG desde la web de FIFA y reemplazar el `<div class="emblem">26</div>` de la cabecera por la imagen.

---

## Campos del Google Form

| Campo | Tipo |
|---|---|
| Nombre real | Texto libre |
| Alias | Texto libre (visible en clasificación pública) |
| Email | Texto (contacto y gestión de pago) |
| Equipo del Bombo 1 | Desplegable |
| Equipo del Bombo 2 | Desplegable |
| Equipo del Bombo 3 | Desplegable |
| Equipo del Bombo 4 | Desplegable |
| Campeón | Desplegable |
| Subcampeón | Desplegable |
| Pichichi | Texto libre |

---

## Reglas del juego

### Selección de equipos

Cada participante elige 4 equipos, uno por bombo.

**Restricción de combinación:** dos participantes no pueden coincidir en 3 o más de sus 4 equipos (intersección máxima permitida = 2). Ante conflicto, gana la quiniela con timestamp anterior; el segundo rehace. El script detecta el conflicto; la resolución es manual.

### Apuestas extra

Campeón, subcampeón y pichichi. Solo puntúan al final del torneo.

---

## Sistema de puntuación

### Fase de grupos
Por cada partido de cada uno de los 4 equipos del participante: victoria 3, empate 1, derrota 0.

### Playoffs
Puntuación por resultado **a los 90 minutos** (prórroga y penaltis no puntúan por resultado): victoria 3, empate 1, derrota 0.

**Extra por pasar la ronda** (acumulable en cada ronda superada):

| Bombo de origen | Extra por ronda superada |
|---|---|
| Bombo 1 | +1 |
| Bombo 2 | +2 |
| Bombo 3 | +3 |
| Bombo 4 | +4 |

Rondas que otorgan extra: R32, Octavos, Cuartos, Semifinal, Final (ganar la final = superar la última ronda). Un equipo de Bombo 4 que gana el torneo acumula hasta +20 de pase (5 rondas × 4).

### Bonus final (una vez acabado el torneo)

| Acierto | Puntos |
|---|---|
| Campeón acertado | +10 |
| Subcampeón acertado | +5 |
| Pichichi acertado | +7 |
| El campeón real está entre tus 4 equipos pero no es el que marcaste como campeón | +6 |

### Desempates
Criterios oficiales FIFA para equipos. Pichichi = Bota de Oro FIFA (goles, luego asistencias, luego menos minutos jugados).

---

## Logística

| Concepto | Detalle |
|---|---|
| Cuota | 10 € por participante |
| Plazo de registro | Hasta el **11/06/2026 a las 20:00 CET** |
| Plazo de pago | Antes del inicio de la **Jornada 2** (18/06/2026); si no, se anula |
| Reparto | 80% para el 1.º · 20% para el 2.º |

---

## Pestañas de la web (front)

| Pestaña | Contenido |
|---|---|
| 🏆 Clasificación | Ranking de participantes con desglose expandible (grupos / KO resultado / KO pase / bonus) por equipo y partido, más predicciones finales |
| 🌍 **Selecciones** | **Puntuación de las 48 selecciones**: lo que aporta cada una a quien la elija (grupos + KO resultado + KO pase por bombo). Ordenable por total / grupos / eliminatorias y filtrable por bombo |
| ⚔️ Eliminatorias | Partidos por ronda (R32 → Final), con marca de penaltis |
| 📊 Grupos | 12 clasificaciones de grupo |
| ⚽ Fase grupos | 72 partidos filtrables por jornada y grupo |
| 🎲 Bombos | Tabla del sorteo |

La pestaña **Selecciones** es nueva en v2: permite ver el "valor" de cada selección en la porra, útil para los participantes al elegir y para seguir qué equipos están rindiendo.

---

## Google Sheet — estructura de pestañas

| Pestaña | Contenido |
|---|---|
| `quinielas` | Volcado del Google Form (respuestas automáticas) |
| `overrides` | Entradas manuales: resultado a 90', quién pasa en playoffs, goleadores cuando TheSportsDB no los provea |

---

## Contrato `datos.json`

Estructura validada contra la simulación completa (fase de grupos + eliminatorias + final):

```json
{
  "meta": {
    "ultima_actualizacion": "",
    "fuente": "TheSportsDB liga 4429",
    "estado_torneo": "pre | grupos | playoffs | finalizado",
    "campeon": "",
    "subcampeon": "",
    "pichichi_nombre": "",
    "pichichi_goles": 0
  },
  "participantes": [
    {
      "alias": "",
      "equipos": ["", "", "", ""],
      "campeon": "", "subcampeon": "", "pichichi": "",
      "pagado": false,
      "puntos_total": 0,
      "desglose": {
        "grupos": 0,
        "playoffs_resultado": 0,
        "playoffs_pase": 0,
        "bonus_final": 0
      },
      "bonus_det": { "campeon": 10, "subcampeon": 5, "pichichi": 7, "campeon_surprise": 6 },
      "team_data": [
        {
          "team": "", "bombo": 1,
          "g_pts": 0, "ko_pts": 0,
          "rondas_pasadas": ["R32", "R16"],
          "ko_det": [
            { "ronda": "R32", "rival": "", "gf": 0, "gc": 0,
              "pts_resultado": 3, "pts_pase": 1, "paso": true }
          ]
        }
      ]
    }
  ],
  "partidos": [
    {
      "matchid": 0, "group": "A", "roundnumber": 1, "ronda": "grupos",
      "fecha": "11.06.2026", "home_team": "", "away_team": "",
      "home_score": 0, "away_score": 0,
      "home_score_90": 0, "away_score_90": 0,
      "pasa": null, "status": "FT"
    }
  ],
  "goleadores": [
    { "jugador": "", "goles": 0 }
  ]
}
```

Notas del contrato:
- `ronda` toma valores `grupos | R32 | R16 | QF | SF | 3RD | F`.
- En eliminatorias, `home_score_90`/`away_score_90` guardan el resultado a 90' (base de la puntuación); `pasa` indica el equipo que avanza (clave para el extra de bombo). El resultado de prórroga/penaltis no se puntúa.
- La pestaña **Selecciones** del front se calcula en cliente a partir de `partidos` + el bombo de cada equipo; no necesita campos extra en el JSON.

---

## Orden de desarrollo en Code

1. **Sondeo de TheSportsDB** (liga 4429): verificar qué campos devuelve para 2026 — marcadores, distinción resultado a 90' vs prórroga, quién pasa, goleadores. Determina cuánto cae en entrada manual.
2. **Esquema Google Sheet**: pestañas `quinielas` y `overrides`.
3. **Contrato `datos.json`**: ya validado contra la simulación; ajustar a lo que devuelva TheSportsDB.
4. **Motor de puntuación** en Python (TDD). Casos de test claros:
   - 3/1/0 en grupos (local y visitante).
   - 3/1/0 a 90' en playoffs; empate a 90' = 1 aunque luego haya penaltis.
   - Extra de bombo por cada ronda superada (acumulable).
   - Bonus: campeón +10, subcampeón +5, pichichi +7, campeón-entre-los-4 +6.
   - Validación de combinación (intersección ≥ 3 → conflicto).
5. **Workflow GitHub Actions**: cron horario; lee Sheet + TheSportsDB; ejecuta motor; commit de `datos.json`.
6. **Front (GitHub Pages)**: partir de la plantilla `porra_mundial_2026_v2.html`; sustituir los datos incrustados (`SIM_DATA`) por `fetch('datos.json')`; aplicar logo oficial.

### Riesgo principal
El cron de GitHub Actions en repos públicos es gratuito pero no de precisión al minuto. Para actualización horaria es irrelevante.

---

## Plantilla de referencia (front)

Archivo: **`porra_mundial_2026_v2.html`** (React vía CDN, paleta FIFA aplicada, 6 pestañas incluida Selecciones, datos de simulación incrustados).

Para pasar de plantilla a producción:
1. Eliminar el bloque `const SIM_DATA = {...}` incrustado.
2. Sustituirlo por una carga asíncrona:
   ```js
   const [D, setD] = useState(null);
   useEffect(() => { fetch('datos.json').then(r => r.json()).then(setD); }, []);
   if (!D) return <div>Cargando…</div>;
   ```
3. Reemplazar el emblema CSS `<div class="emblem">26</div>` por el logo oficial descargado de FIFA.
4. El resto del componente (cálculo de clasificaciones, pestaña Selecciones, desglose) ya funciona contra la estructura de `datos.json`.

---

## Fuente de datos

- **Principal:** TheSportsDB — FIFA World Cup, `idLeague = 4429`, temporada `2026`.
- **Plan B:** football-data.org (gratuito con token) o entrada manual vía pestaña `overrides`.
- **matchid:** número oficial FIFA 1–104 (1–72 grupos, 73–104 eliminatorias).
