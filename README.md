# 🇨🇱 Datos Macroeconómicos de Chile (Alta Disponibilidad)

> **Proveedor público y autónomo de indicadores económicos oficiales de Chile.**  
> Diseñado bajo la arquitectura de *Git-Scraping / Flat Data* para brindar máxima disponibilidad (SLA 99.9%), alimentando la **MINUTA SEMANAL de Economía Política de la Universidad Central de Chile (UCEN)** y proyectos analíticos abiertos.

🌐 **Portal Web en Vivo:** [https://jpqb.github.io/datos_economicos_chile/](https://jpqb.github.io/datos_economicos_chile/)

---

## 🎯 ¿Por qué existe este proyecto?

Muchos reportes y modelos dependen de intermediarios como `mindicador.cl`, que frecuentemente sufren caídas por tiempo de espera (*read timeout*) o certificados caídos.

Este proyecto garantiza **resiliencia total** mediante una arquitectura de capas:
1. **Fuentes Primarias Oficiales:**
   - **UF y Dólar Observado:** Servicio de Impuestos Internos (SII) y Banco Central de Chile.
   - **Euro, Yuan, Petróleo (Brent y WTI):** Banco Central de Chile y Reserva Federal de St. Louis (FRED).
   - **Cobre (US$/lb):** Cochilco / London Metal Exchange (LME) y mercado spot.
   - **TPM, IPC y Desempleo:** Banco Central de Chile e Instituto Nacional de Estadísticas (INE).
2. **Formato Minuta Semanal:** Genera el cuadro semanal exacto con variaciones semana contra semana (*w/w*) y convención simbólica (`▲` Alza, `▼` Baja, `▬` Estable).
3. **Persistencia Inmutable:** Si alguna red externa tiene problemas temporales, el sistema mantiene el último valor oficial confirmado sin interrumpir los reportes.

---

## 📂 Endpoints Públicos de Alta Disponibilidad

Consume los datos directamente vía HTTP sin necesidad de API keys:

| Archivo | Formato | Contenido | URL Cruda de Consumo |
| :--- | :---: | :--- | :--- |
| **`data/cuadro_minuta_semanal.json`** | JSON | **Las 10 variables de la Minuta Semanal UCEN** con cierre semanal, variación *w/w*, fuente oficial y lectura analítica. | `https://raw.githubusercontent.com/jpqb/datos_economicos_chile/main/data/cuadro_minuta_semanal.json` |
| **`data/indicadores_hoy.json`** | JSON | Tablero consolidado con divisas, commodities, tasas y proyecciones de UF. | `https://raw.githubusercontent.com/jpqb/datos_economicos_chile/main/data/indicadores_hoy.json` |
| **`data/uf_hoy.json`** | JSON | Valor de hoy de la UF, variación y proyecciones futuras (hasta 15 días). | `https://raw.githubusercontent.com/jpqb/datos_economicos_chile/main/data/uf_hoy.json` |
| **`data/uf_ultimo_ano.csv`** | CSV | Serie anual continua de la UF en formato tabular limpio (*tidy*). | `https://raw.githubusercontent.com/jpqb/datos_economicos_chile/main/data/uf_ultimo_ano.csv` |

---

## 💡 Ejemplos de Consumo

### 1. Consumo Directo desde `MINUTA SEMANAL` (Python)

```python
import requests

# Descargar el cuadro completo listo para insertar en Word o Markdown
url = "https://raw.githubusercontent.com/jpqb/datos_economicos_chile/main/data/cuadro_minuta_semanal.json"
cuadro = requests.get(url).json()

print(f"Semana analizada: {cuadro['metadatos']['semana_analizada']}")
for item in cuadro['indicadores']:
    print(f"{item['variable'][:35]:35} | {item['cierre_semanal']:>10} | {item['variacion_ww']:>10}")
```

### 2. Consumo desde R (`dashboard_economico`)

```r
library(jsonlite)

# Obtener todos los indicadores de hoy
datos <- fromJSON("https://raw.githubusercontent.com/jpqb/datos_economicos_chile/main/data/indicadores_hoy.json")
cat("Dólar:", datos$divisas_y_unidades$dolar$valor, "\n")
cat("UF:", datos$divisas_y_unidades$uf$valor, "\n")
cat("Cobre:", datos$commodities$cobre$valor, "\n")
```

---

## 🛠️ Ejecución Local

Si deseas ejecutar la extracción multivariable en tu máquina:

```bash
pip install -r requirements.txt
python src/extraer_indicadores.py
```

El script actualizará inmediatamente todos los archivos en la carpeta `data/`.

---

## 📜 Citas y Gobernanza
- **Servicio de Impuestos Internos (SII) & Banco Central de Chile:** Fijación oficial de UF y Dólar Observado.
- **Instituto Nacional de Estadísticas (INE):** IPC y Encuesta Nacional de Empleo (ENE).
- **Comisión Chilena del Cobre (Cochilco) & LME:** Cotización oficial del cobre.
- **Federal Reserve Bank of St. Louis (FRED):** Divisas internacionales y marcadores de petróleo.
