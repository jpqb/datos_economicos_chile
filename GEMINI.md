# Reglas de Proyecto: Repositorio de Datos Económicos y Laborales de Chile (UCEN)

Este archivo define las directrices metodológicas, restricciones técnicas y estándares de gobernanza estadística que Antigravity debe aplicar obligatoriamente al operar en este repositorio, sin importar el perfil de trabajo activo (P1, P2, P3, P4 o P5).

---

## 🏛️ 1. Principio Rector: Fuentes Primarias Legales
El repositorio se rige por el principio de **cero tolerancia a datos especulativos o replicadores no oficiales**. Cada indicador debe provenir de su emisor u organismo certificador legal originario:

1. **Dólar Observado (USD/CLP), Euro y Yuan Chino:**
   - *Emisor Legal:* Banco Central de Chile (Base de Datos Estadísticos - BDE).
   - *Enlace Canónico Verificado:* `https://si3.bcentral.cl/Indicadoressiete/secure/Indicadoresdiarios.aspx`
   - *Restricción:* Prohibido usar el SII como fuente de tipo de cambio (es un replicador tributario rezagado) o cotizaciones forex spot continuo intradiario de Yahoo/Google.
2. **Tasa de Política Monetaria (TPM):**
   - *Emisor Legal:* Banco Central de Chile (Reuniones de Política Monetaria - RPM).
   - *Enlace Canónico Verificado:* `https://www.bcentral.cl/areas/politica-monetaria`
3. **Unidad de Fomento (UF):**
   - *Emisor Originario:* Banco Central de Chile / Certificador Diario: Servicio de Impuestos Internos (SII).
   - *Enlace Canónico Verificado:* `https://www.sii.cl/valores_y_fechas/uf/uf2026.htm`
   - *Regla Crítica:* **No incluir valores futuros proyectados.** Aunque el SII publica los 30 días proyectados por el IPC, en este repositorio solo se registran días devengados hasta la fecha actual ($T$).
4. **Cobre Físico (LME / Cochilco):**
   - *Mercado Primario:* London Metal Exchange (LME - Cash Settlement Cátodos Grado A).
   - *Certificador Oficial en Chile:* Comisión Chilena del Cobre (Cochilco - La Rueda Diaria BML).
   - *Enlace Canónico Verificado:* `https://www.cochilco.cl/web/la-rueda-diaria/`
   - *Restricción:* Prohibido utilizar futuros de COMEX (`HG=F`).
5. **Petróleo Spot WTI y Brent:**
   - *Emisor / Certificador:* U.S. Energy Information Administration (EIA) / Federal Reserve Bank of St. Louis (FRED).
   - *Series Canónicas:* `DCOILWTICO` (WTI Cushing) y `DCOILBRENTEU` (Brent Mar del Norte).
   - *Restricción:* Prohibido sustituir por futuros bursátiles de meses posteriores (NYMEX `CL=F` o ICE). El dato spot en FRED opera con desfase normativo $T-1$ respecto al cierre bursátil estadounidense.
6. **Inflación (IPC):**
   - *Emisor Legal:* Instituto Nacional de Estadísticas (INE).
   - *Enlace Canónico Verificado:* `https://www.ine.gob.cl/estadisticas-por-tema/precios-e-inflacion/indice-de-precios-al-consumidor`
   - *Frecuencia:* Publicación mensual fija el día 8 de cada mes (a las 08:00 hrs).
7. **Estadísticas de Empleo y Mercado Laboral (ENE):**
   - *Emisor Legal:* Instituto Nacional de Estadísticas (INE - Encuesta Nacional de Empleo).
   - *Enlace Canónico Verificado:* `https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/ocupacion-y-desocupacion`
   - *Calendario de Difusión:* Se publica el último día hábil de cada mes a las 09:00 hrs con un mes de rezago respecto al trimestre móvil (ej. Junio–Agosto se publica el 30 de septiembre; Julio–Septiembre el 30 de octubre). Nunca proyectar ni asumir trimestres móviles que no hayan cumplido su fecha oficial de difusión.

---

## 🛡️ 2. Verificación Técnica de Enlaces y Prevención de WAF
1. **Auditoría HTTP previa:** Antes de actualizar o proponer un nuevo enlace a una institución oficial, debe verificarse mediante script o comando que la URL responda con `HTTP 200 OK` directo y no sufra redirección a `ErrorPage.html` ni bloqueos de cortafuegos WAF (Imperva Incapsula).
2. **Caché del Navegador (*Cache-Busting*):** Todas las solicitudes `fetch` de los archivos JSON (`indicadores_hoy.json`, `series_historicas.json`, `cuadro_minuta_semanal.json`) en `index.html` deben incluir siempre el parámetro anti-caché `?v=timestamp` y la cabecera `{ cache: "no-store" }`.

---

## 🔄 3. Protocolo de Sincronización en Cascada
Cada vez que se ajuste o actualice un dato, serie histórica o enlace oficial, se debe respetar estrictamente la cadena de sincronización:
1. `data/indicadores_oficiales_base.json` (configuración central y serie histórica decenal).
2. `src/extraer_indicadores.py` (motor de extracción y fuentes oficiales).
3. Ejecución de `python src/extraer_indicadores.py` para regenerar:
   - `data/indicadores_hoy.json`
   - `data/series_historicas.json`
   - `data/cuadro_minuta_semanal.json`
4. `index.html` (tarjetas interactivas, objeto `NOTAS_TECNICAS` y modal).
5. `docs/NOTAS_TECNICAS_METODOLOGIA.md` (manual metodológico de gobernanza).
6. Git: Commit descriptivo y push a `origin main` para su despliegue inmediato en GitHub Pages.

---

## 👥 4. Directrices para el Futuro Observatorio Laboral (INE / ENE)
- Desarrollar la sección como una pestaña dedicada dentro de la SPA (Single Page Application).
- Preprocesar los tabulados y microdatos de la ENE mediante scripts en `src/` (generando JSONs livianos de series históricas) para evitar cálculos pesados en el cliente.
- Mantener la separación metodológica entre datos formales, empleo por cuenta propia, informalidad (TOI) y brechas de género.
