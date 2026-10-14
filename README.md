# 🇨🇱 Datos Económicos Abiertos de Chile: Unidad de Fomento (UF)

> **Repositorio público y automatizado de indicadores económicos oficiales de Chile.**  
> Diseñado bajo la arquitectura de *Git-Scraping / Flat Data*, garantizando acceso libre, gratuito, sin límites de cuota y con actualización diaria directa desde fuentes oficiales.

---

## 🎯 ¿Por qué existe este proyecto?

Muchas aplicaciones, reportes semanales y modelos econométricos en Chile dependen de APIs intermediarias abiertas (como `mindicador.cl`). Si bien prestan un gran servicio comunitario, con frecuencia presentan caídas de certificados SSL, demoras en la actualización o cuotas de peticiones restrictivas.

Este proyecto resuelve ese problema de raíz:
1. **Va directo a la fuente legal y oficial:** Consulta directamente la tabla oficial del **Servicio de Impuestos Internos (SII)** y las series del **Banco Central de Chile**.
2. **Sin llaves API ni barreras:** Cualquier persona u organización puede consumir los datos directamente desde las URLs crudas de GitHub (`raw.githubusercontent.com`).
3. **Proyecciones futuras:** A diferencia de la mayoría de las APIs que solo dan el valor del día, este repositorio extrae y expone los valores **proyectados** de la UF (que por ley se conocen hasta el día 9 del mes siguiente tras publicarse el IPC).
4. **Resiliencia total:** Si GitHub Actions se detiene un día, los datos históricos y los días futuros ya proyectados continúan disponibles.

---

## 📂 Archivos y Endpoints Públicos

Una vez publicado en tu cuenta de GitHub (`https://github.com/jpqb/datos_economicos_chile`), los datos quedan accesibles en:

| Archivo | Formato | Propósito | Enlace Crudo de Consumo |
| :--- | :---: | :--- | :--- |
| `data/uf_hoy.json` | JSON | Valor de hoy, variación diaria, metadatos y proyecciones de los próximos 15 días. | `https://raw.githubusercontent.com/jpqb/datos_economicos_chile/main/data/uf_hoy.json` |
| `data/uf_ultimo_ano.csv` | CSV | Serie histórica completa del año en curso en formato tabular limpio (*tidy data*). | `https://raw.githubusercontent.com/jpqb/datos_economicos_chile/main/data/uf_ultimo_ano.csv` |
| `data/uf_serie_2026.csv` | CSV | Archivo versionado específico para el año 2026. | `https://raw.githubusercontent.com/jpqb/datos_economicos_chile/main/data/uf_serie_2026.csv` |

---

## 💡 Ejemplos de Consumo

### 1. Desde Python (`MINUTA SEMANAL`, notebooks o scripts)
```python
import requests

# Consumir el valor de hoy en 2 líneas
url = "https://raw.githubusercontent.com/jpqb/datos_economicos_chile/main/data/uf_hoy.json"
datos = requests.get(url).json()

print(f"Fecha: {datos['hoy']['fecha']}")
print(f"Valor UF: ${datos['hoy']['valor_clp']:,.2f} CLP")
print(f"Variación: {datos['hoy']['variacion_diaria_pct']:+.4f}%")
```

### 2. Desde R (`dashboard_economico` o Shiny)
```r
library(jsonlite)
library(readr)

# Lectura directa del JSON
url_json <- "https://raw.githubusercontent.com/jpqb/datos_economicos_chile/main/data/uf_hoy.json"
uf_hoy <- fromJSON(url_json)
cat("UF hoy:", uf_hoy$hoy$valor_clp, "\n")

# Lectura directa de la serie anual en CSV
url_csv <- "https://raw.githubusercontent.com/jpqb/datos_economicos_chile/main/data/uf_ultimo_ano.csv"
serie_anual <- read_csv(url_csv)
head(serie_anual)
```

### 3. Desde JavaScript / Web
```javascript
fetch("https://raw.githubusercontent.com/jpqb/datos_economicos_chile/main/data/uf_hoy.json")
  .then(res => res.json())
  .then(data => {
    console.log("UF Hoy:", data.hoy.valor_clp);
  });
```

### 4. Desde Excel o Power BI
- En Excel: **Datos > Obtener datos > Desde la web** e ingresa la URL del archivo `uf_ultimo_ano.csv`. Se actualizará automáticamente al presionar *Actualizar todo*.

---

## 🛠️ Estructura del Proyecto

```text
datos_economicos_chile/
├── README.md                          # Este documento
├── requirements.txt                   # Dependencias de Python mínimas (requests, pandas, lxml)
├── .gitignore                         # Exclusiones de caché y entornos virtuales
├── .github/
│   └── workflows/
│       └── actualizar_datos.yml       # Automatización programada (GitHub Actions)
├── src/
│   └── extraer_uf.py                  # Script principal con código legible y humanizado
└── data/
    ├── uf_hoy.json                    # Valor del día actual y proyecciones
    ├── uf_ultimo_ano.csv              # Serie completa del año en curso
    └── uf_serie_2026.csv              # Archivo anual versionado
```

---

## 🚀 Publicación inicial en GitHub

Para subir este proyecto a tu GitHub:

1. Abre tu terminal en esta carpeta:
   ```bash
   cd "C:\Users\jpqui\OneDrive - Universidad Central de Chile\UCEN\IA UCEN\datos_economicos_chile"
   ```
2. Inicializa Git y crea el commit inicial:
   ```bash
   git init
   git add .
   git commit -m "feat: inicialización repositorio datos económicos de Chile"
   ```
3. Conéctalo con tu repositorio en GitHub y haz push:
   ```bash
   git branch -M main
   git remote add origin https://github.com/jpqb/datos_economicos_chile.git
   git push -u origin main
   ```
4. En GitHub, ve a **Settings > Actions > General > Workflow permissions** y asegúrate de marcar:
   - **Read and write permissions** (para permitir que GitHub Actions guarde los datos diariamente).

---

## 📜 Citas y Fuentes Oficiales
- **Servicio de Impuestos Internos (SII):** Tabla oficial anual de valores de la UF según D.L. N° 455 de 1974 y D.S. N° 675 de 1975.
- **Banco Central de Chile:** Cálculo y fijación de la variación diaria de la UF en base al IPC publicado por el Instituto Nacional de Estadísticas (INE).
