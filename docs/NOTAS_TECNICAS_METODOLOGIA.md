# 📘 Fichas Técnicas y Metodología de Obtención de Indicadores Económicos

> **Repositorio Oficial de Datos Macroeconómicos de Chile**  
> *Universidad Central de Chile (UCEN) • Datos Abiertos de Alta Disponibilidad*

Este documento establece las especificaciones técnicas, institucionales y normativas de las **10 variables macroeconómicas y financieras fundamentales** consolidadas en este repositorio y en el portal interactivo [jpqb.github.io/datos_economicos_chile](https://jpqb.github.io/datos_economicos_chile/).

---

## Índice de Indicadores

1. [🇨🇱 Unidad de Fomento (UF)](#1-unidad-de-fomento-uf)
2. [💵 Dólar Observado (USD/CLP)](#2-dólar-observado-usdeclp)
3. [💶 Euro Observado (EUR/CLP)](#3-euro-observado-eurclp)
4. [💴 Yuan Chino (CNY/CLP)](#4-yuan-chino-cnyclp)
5. [🪙 Precio del Cobre Spot (LME / Cochilco)](#5-precio-del-cobre-spot-lme--cochilco)
6. [🛢️ Petróleo Brent](#6-petróleo-brent)
7. [⛽ Petróleo WTI (West Texas Intermediate)](#7-petróleo-wti-west-texas-intermediate)
8. [🏛️ Tasa de Política Monetaria (TPM)](#8-tasa-de-política-monetaria-tpm)
9. [📈 Inflación Mensual (IPC)](#9-índice-de-precios-al-consumidor-ipc)
10. [👥 Tasa de Desocupación Nacional (Desempleo ENE)](#10-tasa-de-desocupación-nacional-desempleo)

---

### 1. Unidad de Fomento (UF)

- **Unidad de Medida:** Pesos Chilenos ($ CLP por UF).
- **Institución Emisora Legal:** Banco Central de Chile y Servicio de Impuestos Internos (SII).
- **Marco Normativo:** Decreto Ley N° 3.588 de 1980 y D.F.L. N° 320 de 1960.
- **¿Cómo se obtiene y calcula?:**  
  La UF no es una moneda física ni un activo financiero de libre flotación. Es una **unidad de cuenta reajustable legal**. Su valor se actualiza diariamente entre el día 10 de cada mes y el día 9 del mes calendario siguiente mediante una tasa geométrica diaria calculada a partir de la variación del Índice de Precios al Consumidor (IPC) del mes anterior informado oficialmente por el INE:
  $$\text{UF}_t = \text{UF}_{t-1} \times (1 + \pi_{\text{IPC}})^{1/k}$$
  donde $k$ corresponde al número de días del período mensual de reajuste.
- **Frecuencia y Horario:** Reajuste diario a las 00:00 hrs. El calendario mensual completo se publica el día 9 de cada mes tras conocerse el IPC.
- **⚠️ Advertencia de Discrepancia:**  
  Aunque el Banco Central fija la fórmula legal y el SII publica el calendario tributario anticipado de los próximos 30 días, este repositorio **excluye estrictamente las proyecciones futuras** para garantizar comparabilidad y consistencia econométrica con el resto de los activos spot.
- **Enlace Directo Oficial Verificado:** [Tabla Anual Oficial de la UF - SII](https://www.sii.cl/valores_y_fechas/uf/uf2026.htm)

---

### 2. Dólar Observado (USD/CLP)

- **Unidad de Medida:** Pesos Chilenos ($ CLP por US$ 1).
- **Institución Emisora Primaria:** Banco Central de Chile (BCCh).
- **Marco Normativo:** Artículo 44 de la Ley Orgánica Constitucional del Banco Central (Ley N° 18.840) y Capítulo I del Compendio de Normas de Cambios Internacionales.
- **¿Cómo se obtiene y calcula?:**  
  Corresponde al **promedio aritmético ponderado por volumen** de la totalidad de las operaciones cambiarias spot de compra y venta de dólares estadounidenses ejecutadas en el mercado cambiario formal (bancos comerciales e instituciones financieras autorizadas) en el día hábil bancario inmediatamente anterior.
- **Frecuencia y Horario:** Diario (días hábiles bancarios). Se publica cada mañana a las **08:30 hrs** (vigente para la jornada). A contar de las **17:00 – 18:00 hrs**, el Banco Central calcula y adelanta en su portada el valor oficial correspondiente al **siguiente día hábil bancario**.
- **⚠️ Advertencia de Discrepancia (Spot Forex vs. Dólar Observado):**
  1. *Mercado Continuo:* La cotización de mercado libre interbancario (Yahoo Finance `CLP=X` o terminales Bloomberg/Reuters) varía segundo a segundo. El Dólar Observado es una media fija calculada con las operaciones del día anterior.
  2. *Rezago del SII:* El SII **no calcula el dólar**; es un replicador tributario que transcribe las cifras del Banco Central con rezagos de semanas. La fuente originaria e indiscutible es el Banco Central.
- **Enlace Directo Oficial Verificado:** [Indicadores Diarios Oficiales - Banco Central de Chile (BDE)](https://si3.bcentral.cl/Indicadoressiete/secure/Indicadoresdiarios.aspx)

---

### 3. Euro Observado (EUR/CLP)

- **Unidad de Medida:** Pesos Chilenos ($ CLP por € 1).
- **Institución Emisora Legal:** Banco Central de Chile (BCCh).
- **Marco Normativo:** Compendio de Normas de Cambios Internacionales del BCCh.
- **¿Cómo se obtiene y calcula?:**  
  No surge de transacciones directas masivas entre pesos y euros en Santiago, sino que es una **paridad cruzada oficial**. Se obtiene multiplicando el Dólar Observado vigente del Banco Central por la cotización de arbitraje internacional Euro/Dólar (EUR/USD) fijada en los mercados cambiarios globales a las 13:30 hrs de Santiago.
- **Frecuencia y Horario:** Días hábiles bancarios a las 14:00 hrs.
- **Enlace Directo Oficial Verificado:** [Indicadores Diarios y Paridades Oficiales - Banco Central de Chile (BDE)](https://si3.bcentral.cl/Indicadoressiete/secure/Indicadoresdiarios.aspx)

---

### 4. Yuan Chino (CNY/CLP)

- **Unidad de Medida:** Pesos Chilenos ($ CLP por ¥ 1).
- **Institución Emisora Legal:** Banco Central de Chile (BCCh) / People's Bank of China (PBOC).
- **Marco Normativo:** Estadísticas Monetarias y Financieras Internacionales del BCCh.
- **¿Cómo se obtiene y calcula?:**  
  Paridad cruzada implícita calculada a partir de la razón entre el Dólar Observado oficial (USD/CLP) del Banco Central de Chile y la paridad oficial Dólar/Renminbi (USD/CNY) publicada por el Banco Popular de China. Esencial para evaluar la competitividad con el principal destino de las exportaciones mineras y agroindustriales chilenas.
- **Frecuencia y Horario:** Diaria (días hábiles bancarios).
- **Enlace Directo Oficial Verificado:** [Indicadores Diarios y Paridades Oficiales - Banco Central de Chile (BDE)](https://si3.bcentral.cl/Indicadoressiete/secure/Indicadoresdiarios.aspx)

---

### 5. Precio del Cobre Spot (LME / Cochilco)

- **Unidad de Medida:** Dólares de EE.UU. por libra física (US$/lb).
- **Mercado Primario Originario:** London Metal Exchange (LME / Bolsa de Metales de Londres).
- **Institución Certificadora Oficial en Chile:** Comisión Chilena del Cobre (Cochilco).
- **Marco Normativo:** Decreto Ley N° 1.349 de 1976 (Creación de Cochilco).
- **¿Cómo se obtiene y calcula?:**  
  1. *Mercado Primario (LME):* El precio originario mundial se determina en las sesiones de negociación de la **Bolsa de Metales de Londres (LME)** como el **Precio Spot de Liquidación en Efectivo (Cash Settlement)** para Cátodos de Cobre Grado A.
  2. *Certificación Oficial de Cochilco:* Cochilco no fija un precio propio; recibe la cotización oficial de la LME tras la segunda rueda matutina de Londres y la publica oficialmente en Chile a través de **"La Rueda Diaria"**, certificando el valor en dólares por tonelada métrica y centavos de dólar por libra física ($1 \text{ TM} = 2.204,62 \text{ lb}$). Esta cifra certificada por Cochilco es la referencia legal vinculante para la recaudación del Royalty Minero y el presupuesto de la Nación.
- **Frecuencia y Horario:** Lunes a viernes entre 09:30 y 11:00 hrs CLT (tras el cierre de rueda matutina en Londres).
- **⚠️ Advertencia de Discrepancia (Spot LME vs. Futuros COMEX):**  
  Muchos sitios financieros (como Yahoo Finance ticker `HG=F`) reportan los contratos de futuros de cobre en el COMEX de Nueva York. El contrato de futuros cotiza con primas de entrega, costos de flete financiero y expectativas a meses futuros. Cochilco certifica el **precio spot físico en Londres (BML)**, que es el valor legal de referencia en Chile.
- **Enlaces Oficiales Verificados:**
  - *Mercado Primario Global:* [London Metal Exchange (LME Copper)](https://www.lme.com/Metals/Non-ferrous/LME-Copper)
  - *Certificación Oficial en Chile:* [La Rueda Diaria - Cochilco](https://www.cochilco.cl/web/la-rueda-diaria/)

---

### 6. Petróleo Brent

- **Unidad de Medida:** Dólares de EE.UU. por barril (US$/bbl).
- **Institución Emisora de Referencia:** U.S. Energy Information Administration (EIA) / Federal Reserve Bank of St. Louis (FRED).
- **Código de Serie Canónica:** FRED Series `DCOILBRENTEU` (Crude Oil Prices: Brent - Europe).
- **¿Cómo se obtiene y calcula?:**  
  Precio spot en boca de terminal para el crudo ligero extraído en los campos del Mar del Norte (Brent Blend, Forties, Oseberg, Ekofisk, Troll). Constituye el marcador de referencia para más del 65% de las compras internacionales de hidrocarburos de ENAP y rige los parámetros de cálculo semanal del Mecanismo de Estabilización de Precios de los Combustibles (MEPCO) en Chile.
- **Frecuencia:** Diaria (días de negociación bursátil en Europa e ICE).
- **⚠️ Desfase Oficial de Publicación T-1 (EIA / FRED):**  
  La EIA y FRED consolidan y certifican el precio spot oficial de cierre una vez concluidas las operaciones bursátiles, publicando formalmente la serie en FRED **al día hábil siguiente (desfase normativo T-1)**. Por ello, el dato más reciente disponible en las bases oficiales certificadas de FRED corresponde siempre al día hábil inmediatamente anterior al momento de la consulta.
- **Enlace Directo Oficial Verificado:** [FRED Series DCOILBRENTEU (Brent Spot - EIA)](https://fred.stlouisfed.org/series/DCOILBRENTEU)

---

### 7. Petróleo WTI (West Texas Intermediate)

- **Unidad de Medida:** Dólares de EE.UU. por barril (US$/bbl).
- **Institución Emisora de Referencia:** U.S. Energy Information Administration (EIA) / Federal Reserve Bank of St. Louis (FRED).
- **Código de Serie Canónica:** FRED Series `DCOILWTICO` (Crude Oil Prices: WTI - Cushing, Oklahoma).
- **¿Cómo se obtiene y calcula?:**  
  Cotización spot física para entrega en el centro de distribución de oleoductos de Cushing, Oklahoma. Representa el crudo dulce ligero de referencia estadounidense.
- **Frecuencia:** Diaria (días hábiles en EE.UU.).
- **⚠️ Desfase Oficial de Publicación T-1 (EIA / FRED):**  
  Al igual que con el Brent, la serie canónica de la EIA en FRED se actualiza con un desfase de 1 día hábil ($T-1$) tras el cierre oficial de Cushing, reflejando el último día hábil anterior.
- **Enlace Directo Oficial Verificado:** [FRED Series DCOILWTICO (WTI Spot - EIA)](https://fred.stlouisfed.org/series/DCOILWTICO)

---

### 8. Tasa de Política Monetaria (TPM)

- **Unidad de Medida:** Porcentaje anual (%).
- **Institución Emisora Legal:** Banco Central de Chile (BCCh).
- **Marco Normativo:** Artículos 34 y 35 de la Ley Orgánica Constitucional del Banco Central (Ley 18.840).
- **¿Cómo se obtiene y calcula?:**  
  Es la tasa de interés objetivo fijada por el Consejo del Banco Central para las operaciones de crédito interbancario a un día plazo (overnight). **No es una tasa determinada por el mercado**, sino una decisión de política macroeconómica votada formalmente por los cinco consejeros del Banco Central en sus Reuniones de Política Monetaria (RPM), celebradas 8 veces al año conforme a un calendario predefinido.
- **Frecuencia:** Se reúne 8 veces al año. Permanece idéntica entre reuniones a menos que ocurra una sesión de emergencia. En el cuadro semanal se etiqueta como *"▬ Estable"* cuando la semana no coincide con una decisión de RPM.
- **Enlace Directo Oficial Verificado:** [Política Monetaria y Comunicados RPM - Banco Central de Chile](https://www.bcentral.cl/areas/politica-monetaria)

---

### 9. Índice de Precios al Consumidor (IPC)

- **Unidad de Medida:** Variación porcentual mensual (% m/m), acumulada en el año (% a/a) y a doce meses.
- **Institución Emisora Legal:** Instituto Nacional de Estadísticas (INE).
- **Marco Normativo:** Ley N° 17.374 y Decreto N° 35 del Ministerio de Economía.
- **¿Cómo se obtiene y calcula?:**  
  Mide la evolución mensual ponderada del costo de una canasta de 303 productos y servicios representativos del gasto de los hogares de las 16 capitales regionales (base 2023=100). El INE recolecta presencial y digitalmente más de 120.000 cotizaciones de precios en todo el territorio nacional a lo largo del mes.
- **Frecuencia y Horario:** Publicación estrictamente mensual el **día 8 de cada mes** (o el día hábil previo si es festivo o fin de semana) a las **08:00 hrs**.
- **Enlace Directo Oficial Verificado:** [Sección Oficial del IPC y Boletines Mensuales - INE](https://www.ine.gob.cl/estadisticas-por-tema/precios-e-inflacion/indice-de-precios-al-consumidor)

---

### 10. Tasa de Desocupación Nacional (Desempleo)

- **Unidad de Medida:** Porcentaje de la Fuerza de Trabajo (%).
- **Institución Emisora Legal:** Instituto Nacional de Estadísticas (INE).
- **Marco Normativo:** Ley N° 17.374.
- **¿Cómo se obtiene y calcula?:**  
  Generada mediante la **Encuesta Nacional de Empleo (ENE)** aplicada a más de 35.000 hogares en todo Chile. Cuantifica a las personas en edad de trabajar que no tienen empleo, buscaron activamente trabajo durante las 4 semanas previas y están disponibles para trabajar de inmediato:
  $$\text{Tasa de Desocupación} = \frac{\text{Personas Desocupadas}}{\text{Fuerza de Trabajo}} \times 100$$
- **Periodicidad:** **Trimestre móvil** (ej. Junio – Agosto 2026, tasa oficial vigente: 9,6%). Se publica el **último día hábil de cada mes** a las **09:00 hrs** con un mes de rezago (por ejemplo, el boletín del trimestre Julio – Septiembre se difunde formalmente el 30 de octubre).
- **⚠️ Advertencia de Discrepancia:** No refleja un mes aislado, sino un promedio móvil trimestral para neutralizar la alta volatilidad estacional del mercado laboral (empleo agrícola, construcción y turismo).
- **Enlace Directo Oficial Verificado:** [Estadísticas de Ocupación y Desocupación (ENE) - INE](https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/ocupacion-y-desocupacion)

---

## 🏛️ Matriz de Gobernanza y Resumen de Enlaces Canónicos

| Variable | Tipo de Dato | Institución Emisora / Certificadora | Enlace Canónico Directo |
| :--- | :--- | :--- | :--- |
| **UF** | Reajuste legal diario | Servicio de Impuestos Internos (SII) | [sii.cl/valores_y_fechas/uf/uf2026.htm](https://www.sii.cl/valores_y_fechas/uf/uf2026.htm) |
| **Dólar Obs.** | Media ponderada diaria | Banco Central de Chile (BCCh) | [si3.bcentral.cl/.../Indicadoresdiarios.aspx](https://si3.bcentral.cl/Indicadoressiete/secure/Indicadoresdiarios.aspx) |
| **Euro Obs.** | Paridad cruzada oficial | Banco Central de Chile (BDE) | [si3.bcentral.cl/.../Indicadoresdiarios.aspx](https://si3.bcentral.cl/Indicadoressiete/secure/Indicadoresdiarios.aspx) |
| **Yuan Chino** | Paridad cruzada oficial | Banco Central de Chile (BDE) | [si3.bcentral.cl/.../Indicadoresdiarios.aspx](https://si3.bcentral.cl/Indicadoressiete/secure/Indicadoresdiarios.aspx) |
| **Cobre LME** | Precio spot físico BML | London Metal Exchange / Cochilco | [cochilco.cl/web/la-rueda-diaria/](https://www.cochilco.cl/web/la-rueda-diaria/) |
| **Petróleo Brent** | Spot FOB Mar del Norte (T-1) | FRED (St. Louis Fed) / EIA | [fred.stlouisfed.org/series/DCOILBRENTEU](https://fred.stlouisfed.org/series/DCOILBRENTEU) |
| **Petróleo WTI** | Spot Cushing (T-1) | FRED (St. Louis Fed) / EIA | [fred.stlouisfed.org/series/DCOILWTICO](https://fred.stlouisfed.org/series/DCOILWTICO) |
| **TPM** | Tasa objetivo Consejo | Banco Central de Chile (BCCh) | [bcentral.cl/.../politica-monetaria](https://www.bcentral.cl/areas/politica-monetaria) |
| **Inflación IPC** | Canasta ponderada mensual | Instituto Nacional de Estadísticas (INE) | [ine.gob.cl/.../indice-de-precios-al-consumidor](https://www.ine.gob.cl/estadisticas-por-tema/precios-e-inflacion/indice-de-precios-al-consumidor) |
| **Desempleo** | Trimestre móvil ENE | Instituto Nacional de Estadísticas (INE) | [ine.gob.cl/.../ocupacion-y-desocupacion](https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/ocupacion-y-desocupacion) |
