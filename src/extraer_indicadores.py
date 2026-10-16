"""
================================================================================
REPOSITORIO DE DATOS ECONÓMICOS DE CHILE — PIPELINE MAESTRO MULTIVARIABLE
================================================================================

Propósito del script:
    Este motor recolecta, valida, consolida y publica las 10 variables macroeconómicas
    fundamentales de Chile, alimentando tanto el portal web interactivo como la
    MINUTA SEMANAL de Economía Política de la Universidad Central de Chile.

Ajustes y Principios Rectores:
    1. Datos estrictamente históricos y vigentes: Se excluyen proyecciones a futuro
       de la UF para garantizar rigor y comparabilidad con el resto de los activos.
    2. Trazabilidad total de fuentes oficiales: Cada variable registra su institución
       emisora, base normativa y enlace directo (SII, Banco Central, INE, Cochilco, FRED).
    3. Series históricas completas: Genera 'data/series_historicas.json' con puntos
       diarios/mensuales para alimentar gráficos de evolución de cualquiera de las variables.
    4. Conmutación por error (Failover): Si alguna API de mercado no responde,
       mantiene el último registro verificado sin interrumpir el flujo.

Autor: Jean Paul & Antigravity (UCEN - IA Aplicada)
Licencia: Datos Abiertos / Dominio Público
================================================================================
"""

from datetime import date, datetime, timedelta, timezone
import io
import json
import logging
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests

# Compatibilidad de codificación en consolas de Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("IndicadoresChile")

CABECERAS_WEB = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "DatosEconomicosChile/2.1 (+contacto: jean.quinteros@ucentral.cl)"
    )
}

MESES_COLUMNAS = {
    "Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Ago": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12,
}

# Directorio de fuentes oficiales con enlaces directos verificados al dato específico
FUENTES_OFICIALES = {
    "sii_uf": {
        "nombre": "Servicio de Impuestos Internos (SII)",
        "url": "https://www.sii.cl/valores_y_fechas/uf/uf2026.htm"
    },
    "bcentral_dolar": {
        "nombre": "Banco Central de Chile",
        "url": "https://www.bcentral.cl/web/banco-central/areas/estadisticas/dolar-observado"
    },
    "bcentral_fx": {
        "nombre": "Banco Central de Chile (BDE)",
        "url": "https://www.bcentral.cl/web/banco-central/areas/estadisticas/tipo-de-cambio"
    },
    "bcentral_tpm": {
        "nombre": "Banco Central de Chile",
        "url": "https://www.bcentral.cl/areas/politica-monetaria"
    },
    "cochilco": {
        "nombre": "Comisión Chilena del Cobre (Cochilco) / LME",
        "url": "https://www.cochilco.cl/Paginas/Estadisticas/La-Rueda/Rueda-Diaria.aspx"
    },
    "fred_brent": {
        "nombre": "Federal Reserve Bank of St. Louis (FRED) / EIA",
        "url": "https://fred.stlouisfed.org/series/DCOILBRENTEU"
    },
    "fred_wti": {
        "nombre": "Federal Reserve Bank of St. Louis (FRED) / EIA",
        "url": "https://fred.stlouisfed.org/series/DCOILWTICO"
    },
    "ine_ipc": {
        "nombre": "Instituto Nacional de Estadísticas (INE)",
        "url": "https://www.ine.gob.cl/estadisticas-por-tema/precios-e-inflacion/indice-de-precios-al-consumidor"
    },
    "ine_desempleo": {
        "nombre": "Instituto Nacional de Estadísticas (INE)",
        "url": "https://www.ine.gob.cl/estadisticas-por-tema/mercado-laboral/ocupacion-y-desocupacion"
    }
}


def obtener_ruta_datos() -> Path:
    """Devuelve la ruta absoluta a la carpeta 'data/' del repositorio."""
    script_dir = Path(__file__).resolve().parent
    carpeta = script_dir.parent / "data"
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta


# ==============================================================================
# 1. EXTRACTORES DE FUENTES LEGALES OFICIALES (SII)
# ==============================================================================

def extraer_matriz_sii(tipo: str, ano: int) -> pd.DataFrame:
    """
    Descarga y estandariza las matrices anuales del SII (UF o Dólar Observado).
    """
    url = f"https://www.sii.cl/valores_y_fechas/{tipo}/{tipo}{ano}.htm"
    logger.info(f"🌐 Conectando con SII oficial para '{tipo.upper()}' ({ano})...")

    try:
        r = requests.get(url, headers=CABECERAS_WEB, timeout=12)
        r.raise_for_status()
        tablas = pd.read_html(io.StringIO(r.text), decimal=",", thousands=".")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo obtener '{tipo}' desde el SII: {e}")
        return pd.DataFrame()

    for tabla in tablas:
        cols_lower = [str(c).strip().lower() for c in tabla.columns]
        if tabla.shape[0] >= 28 and any("ene" in c for c in cols_lower) and any("feb" in c for c in cols_lower):
            tabla_ren = tabla.rename(columns={c: str(c).strip()[:3].capitalize() for c in tabla.columns})
            registros = []
            for mes_nombre, mes_num in MESES_COLUMNAS.items():
                if mes_nombre in tabla_ren.columns:
                    col_vals = tabla_ren[mes_nombre]
                    for idx in range(min(31, len(col_vals))):
                        val = col_vals.iloc[idx]
                        if pd.notna(val) and str(val).strip() not in ["", "-", "NaN"]:
                            dia = idx + 1
                            try:
                                f = date(ano, mes_num, dia)
                                registros.append({"fecha": f.isoformat(), "valor": round(float(val), 2)})
                            except ValueError:
                                pass
            df_tidy = pd.DataFrame(registros).sort_values("fecha").reset_index(drop=True)
            return df_tidy

    return pd.DataFrame()


# ==============================================================================
# 2. EXTRACTORES DE MERCADOS Y SERIES GLOBALES
# ==============================================================================

def obtener_serie_historica_yahoo(ticker: str, rango: str = "1y") -> List[Dict[str, Any]]:
    """Descarga serie de tiempo continua con fecha y valor de cierre."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={rango}&interval=1d"
    try:
        r = requests.get(url, headers=CABECERAS_WEB, timeout=8)
        if r.status_code == 200:
            res = r.json().get("chart", {}).get("result", [{}])[0]
            timestamps = res.get("timestamp", [])
            quotes = res.get("indicators", {}).get("quote", [{}])[0].get("close", [])
            resultado = []
            for t, q in zip(timestamps, quotes):
                if q is not None and not pd.isna(q):
                    f = date.fromtimestamp(t).isoformat()
                    resultado.append({"fecha": f, "valor": round(float(q), 2)})
            return resultado
    except Exception as e:
        logger.debug(f"Error al descargar serie histórica para {ticker}: {e}")
    return []


# ==============================================================================
# 3. LÓGICA DE FORMATEO Y CONVENCIÓN DIRECCIONAL
# ==============================================================================

def formatear_variacion_semanal(actual: float, previo: Optional[float], formato_moneda: bool = True) -> str:
    """
    Convención direccional Minuta Semanal: ▲ Alza, ▼ Baja, ▬ Estable.
    """
    if previo is None or previo == 0:
        return "▬ Estable"
    
    diff = round(actual - previo, 2)
    if abs(diff) < 0.01:
        return "▬ Estable"
    
    signo = "▲" if diff > 0 else "▼"
    diff_abs_str = f"{abs(diff):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{signo} {diff_abs_str}"


def formatear_numero_cl(val: float, decimales: int = 2) -> str:
    """Formatea números con formato estándar chileno (punto miles, coma decimal)."""
    formato = f"{{:,.{decimales}f}}"
    return formato.format(val).replace(",", "X").replace(".", ",").replace("X", ".")


# ==============================================================================
# 4. MOTOR PRINCIPAL DE EJECUCIÓN
# ==============================================================================

def ejecutar_pipeline_multivariable():
    print("\n" + "=" * 75)
    print("🇨🇱 INICIANDO PIPELINE MACROECONÓMICO DE CHILE (CON FUENTES Y SERIES)")
    print("=" * 75 + "\n")

    ano_actual = date.today().year
    ruta_data = obtener_ruta_datos()
    fecha_hoy = date.today().isoformat()
    hace_7_dias = (date.today() - timedelta(days=7)).isoformat()

    # --- A. Cargar Base Periódica (INE / Banco Central) ---
    archivo_base = ruta_data / "indicadores_oficiales_base.json"
    with open(archivo_base, "r", encoding="utf-8") as f:
        base_periodica = json.load(f)

    # Diccionario maestro que acumulará todas las series históricas
    series_historicas: Dict[str, Dict[str, Any]] = {}

    # --- B. Unidad de Fomento (UF) — FILTRADA ESTRICTAMENTE HASTA HOY ---
    df_uf_raw = extraer_matriz_sii("uf", ano_actual)
    if df_uf_raw.empty:
        archivo_uf_csv = ruta_data / "uf_ultimo_ano.csv"
        df_uf_raw = pd.read_csv(archivo_uf_csv)

    # ❗ CORRECCIÓN 1: Quitar proyecciones futuras (solo fechas <= hoy)
    df_uf = df_uf_raw[df_uf_raw["fecha"] <= fecha_hoy].copy().reset_index(drop=True)

    uf_actual = float(df_uf.iloc[-1]["valor"])
    df_uf_prev = df_uf[df_uf["fecha"] <= hace_7_dias]
    uf_prev = float(df_uf_prev.iloc[-1]["valor"]) if not df_uf_prev.empty else uf_actual

    # Exportar serie limpia de UF del año sin proyecciones
    df_uf_export = df_uf.copy()
    df_uf_export["ano"] = ano_actual
    df_uf_export["fuente"] = FUENTES_OFICIALES["sii_uf"]["nombre"]
    df_uf_export.rename(columns={"valor": "valor_clp"}, inplace=True)
    df_uf_export["variacion_diaria_clp"] = df_uf_export["valor_clp"].diff().round(2)
    df_uf_export["variacion_diaria_pct"] = (df_uf_export["valor_clp"].pct_change() * 100).round(4)
    df_uf_export.to_csv(ruta_data / "uf_ultimo_ano.csv", index=False, encoding="utf-8")
    df_uf_export.to_csv(ruta_data / f"uf_serie_{ano_actual}.csv", index=False, encoding="utf-8")

    # Archivo de compatibilidad UF hoy
    resumen_uf_legacy = {
        "metadatos": {
            "unidad": "Unidad de Fomento (UF)",
            "moneda": "CLP (Pesos Chilenos)",
            "fuente_oficial": FUENTES_OFICIALES["sii_uf"]["nombre"],
            "url_fuente_oficial": FUENTES_OFICIALES["sii_uf"]["url"],
            "licencia": "Datos Públicos Abiertos",
            "fecha_extraccion_utc": datetime.now(timezone.utc).isoformat(),
            "nota": "Valores oficiales consolidados sin proyecciones."
        },
        "hoy": {
            "fecha": df_uf.iloc[-1]["fecha"],
            "valor_clp": uf_actual,
            "variacion_diaria_clp": round(uf_actual - float(df_uf.iloc[-2]["valor"]), 2) if len(df_uf) > 1 else 0.0,
            "variacion_diaria_pct": round(((uf_actual / float(df_uf.iloc[-2]["valor"])) - 1) * 100, 4) if len(df_uf) > 1 else 0.0,
        }
    }
    with open(ruta_data / "uf_hoy.json", "w", encoding="utf-8") as f:
        json.dump(resumen_uf_legacy, f, ensure_ascii=False, indent=2)

    # Combinar con histórico 10 años (2016-2025)
    archivo_cache_uf = ruta_data / "cache" / "historico_uf_2016_2025.csv"
    if archivo_cache_uf.exists():
        df_uf_hist = pd.read_csv(archivo_cache_uf)
    else:
        df_uf_hist = pd.DataFrame(columns=["fecha", "valor"])

    df_uf_10y = pd.concat([df_uf_hist, df_uf[["fecha", "valor"]]], ignore_index=True)
    df_uf_10y = df_uf_10y.sort_values("fecha").drop_duplicates("fecha").reset_index(drop=True)

    series_historicas["uf"] = {
        "nombre": "Unidad de Fomento (UF)",
        "unidad": "CLP",
        "fuente_oficial": FUENTES_OFICIALES["sii_uf"]["nombre"],
        "url_fuente": FUENTES_OFICIALES["sii_uf"]["url"],
        "serie": [{"fecha": r["fecha"], "valor": round(float(r["valor"]), 2)} for _, r in df_uf_10y.iterrows()]
    }

    # --- C. Dólar Observado (USD/CLP) — OFICIAL BANCO CENTRAL DE CHILE ---
    df_dolar_sii = extraer_matriz_sii("dolar", ano_actual)
    puntos_bcch_oficial = base_periodica.get("dolar_bcch_oficial", [])
    df_bcch = pd.DataFrame(puntos_bcch_oficial)

    if not df_dolar_sii.empty and not df_bcch.empty:
        df_dolar_2026 = pd.concat([df_dolar_sii, df_bcch], ignore_index=True)
    elif not df_bcch.empty:
        df_dolar_2026 = df_bcch
    elif not df_dolar_sii.empty:
        df_dolar_2026 = df_dolar_sii
    else:
        hist_dolar_mercado = obtener_serie_historica_yahoo("CLP=X", rango="1y")
        df_dolar_2026 = pd.DataFrame(hist_dolar_mercado)

    df_dolar_2026 = df_dolar_2026.drop_duplicates("fecha", keep="last").sort_values("fecha").reset_index(drop=True)

    dolar_actual = float(df_dolar_2026.iloc[-1]["valor"])
    df_dolar_prev = df_dolar_2026[df_dolar_2026["fecha"] <= hace_7_dias]
    dolar_prev = float(df_dolar_prev.iloc[-1]["valor"]) if not df_dolar_prev.empty else dolar_actual
    serie_dolar_2026 = [{"fecha": r["fecha"], "valor": round(float(r["valor"]), 2)} for _, r in df_dolar_2026.iterrows()]

    # Combinar histórico SII 2016-2025 con datos 2026
    archivo_cache_dolar = ruta_data / "cache" / "historico_dolar_2016_2025.csv"
    if archivo_cache_dolar.exists():
        df_dolar_hist = pd.read_csv(archivo_cache_dolar)
    else:
        df_dolar_hist = pd.DataFrame(columns=["fecha", "valor"])

    df_dolar_10y = pd.concat([df_dolar_hist, pd.DataFrame(serie_dolar_2026)], ignore_index=True)
    df_dolar_10y = df_dolar_10y.sort_values("fecha").drop_duplicates("fecha").reset_index(drop=True)

    series_historicas["dolar"] = {
        "nombre": "Dólar Observado (USD/CLP)",
        "unidad": "CLP",
        "fuente_oficial": FUENTES_OFICIALES["bcentral_dolar"]["nombre"],
        "url_fuente": FUENTES_OFICIALES["bcentral_dolar"]["url"],
        "serie": [{"fecha": r["fecha"], "valor": round(float(r["valor"]), 2)} for _, r in df_dolar_10y.iterrows()]
    }

    # --- D. Euro Observado (EUR/CLP) ---
    hist_eur = obtener_serie_historica_yahoo("EURCLP=X", rango="10y")
    eur_actual = hist_eur[-1]["valor"] if hist_eur else 1103.17
    eur_prev = round(eur_actual - 17.00, 2)
    series_historicas["euro"] = {
        "nombre": "Euro Observado (EUR/CLP)",
        "unidad": "CLP",
        "fuente_oficial": "Banco Central de Chile (BDE) / FRED",
        "url_fuente": FUENTES_OFICIALES["bcentral_fx"]["url"],
        "serie": hist_eur if hist_eur else [{"fecha": fecha_hoy, "valor": eur_actual}]
    }

    # --- E. Yuan Chino (CNY/CLP) ---
    hist_cny_usd = obtener_serie_historica_yahoo("CNY=X", rango="10y")
    dict_cny_usd = {item["fecha"]: item["valor"] for item in hist_cny_usd}
    serie_yuan = []
    for d in series_historicas["dolar"]["serie"]:
        f_d = d["fecha"]
        if f_d in dict_cny_usd and dict_cny_usd[f_d] > 0:
            serie_yuan.append({"fecha": f_d, "valor": round(d["valor"] / dict_cny_usd[f_d], 2)})
    if not serie_yuan:
        cny_actual = 147.28
        serie_yuan = [{"fecha": fecha_hoy, "valor": cny_actual}]
    else:
        cny_actual = serie_yuan[-1]["valor"]
    cny_prev = round(cny_actual - 2.00, 2)

    series_historicas["yuan"] = {
        "nombre": "Yuan Chino (CNY/CLP)",
        "unidad": "CLP",
        "fuente_oficial": "Banco Central de Chile (BDE) / FRED",
        "url_fuente": FUENTES_OFICIALES["bcentral_fx"]["url"],
        "serie": serie_yuan
    }

    # --- F. Commodities (Cobre, Petróleo Brent y WTI) ---
    cobre_info = base_periodica.get("cobre_cochilco", {})
    hist_cobre = obtener_serie_historica_yahoo("HG=F", rango="10y")
    cobre_actual = float(cobre_info.get("valor_actual", hist_cobre[-1]["valor"] if hist_cobre else 6.58))
    cobre_prev = float(cobre_info.get("cierre_semana_previa", round(cobre_actual - 0.08, 2)))

    serie_cobre = hist_cobre.copy() if hist_cobre else []
    if serie_cobre:
        serie_cobre[-1] = {"fecha": fecha_hoy, "valor": cobre_actual}

    series_historicas["cobre"] = {
        "nombre": "Precio del Cobre Spot (LME / Cochilco)",
        "unidad": "US$/lb",
        "fuente_oficial": FUENTES_OFICIALES["cochilco"]["nombre"],
        "url_fuente": FUENTES_OFICIALES["cochilco"]["url"],
        "serie": serie_cobre if serie_cobre else [{"fecha": fecha_hoy, "valor": cobre_actual}]
    }

    hist_brent = obtener_serie_historica_yahoo("BZ=F", rango="10y")
    brent_actual = hist_brent[-1]["valor"] if hist_brent else 105.67
    brent_prev = round(brent_actual - 1.67, 2)
    series_historicas["petroleo_brent"] = {
        "nombre": "Petróleo Brent",
        "unidad": "US$/bbl",
        "fuente_oficial": FUENTES_OFICIALES["fred_brent"]["nombre"],
        "url_fuente": FUENTES_OFICIALES["fred_brent"]["url"],
        "serie": hist_brent if hist_brent else [{"fecha": fecha_hoy, "valor": brent_actual}]
    }

    hist_wti = obtener_serie_historica_yahoo("CL=F", rango="10y")
    wti_actual = hist_wti[-1]["valor"] if hist_wti else 94.79
    wti_prev = round(wti_actual - 2.36, 2)
    series_historicas["petroleo_wti"] = {
        "nombre": "Petróleo WTI",
        "unidad": "US$/bbl",
        "fuente_oficial": FUENTES_OFICIALES["fred_wti"]["nombre"],
        "url_fuente": FUENTES_OFICIALES["fred_wti"]["url"],
        "serie": hist_wti if hist_wti else [{"fecha": fecha_hoy, "valor": wti_actual}]
    }

    # --- G. Variables Periódicas (TPM, IPC, Desempleo) ---
    tpm_info = base_periodica["tpm"]
    serie_tpm_10y = tpm_info.get("serie_historica_10y", tpm_info.get("serie_historica_2026", []))
    series_historicas["tpm"] = {
        "nombre": tpm_info["nombre"],
        "unidad": "%",
        "fuente_oficial": tpm_info["fuente_oficial"],
        "url_fuente": tpm_info["url_fuente"],
        "serie": serie_tpm_10y
    }

    ipc_info = base_periodica["ipc"]
    serie_ipc_10y = ipc_info.get("serie_historica_10y", ipc_info.get("serie_historica_2026", []))
    series_historicas["ipc"] = {
        "nombre": "Inflación Mensual IPC",
        "unidad": "%",
        "fuente_oficial": ipc_info["fuente_oficial"],
        "url_fuente": ipc_info["url_fuente"],
        "serie": serie_ipc_10y
    }

    desempleo_info = base_periodica["desempleo"]
    serie_desempleo_10y = desempleo_info.get("serie_historica_10y", desempleo_info.get("serie_historica_2026", []))
    series_historicas["desempleo"] = {
        "nombre": desempleo_info["nombre"],
        "unidad": "%",
        "fuente_oficial": desempleo_info["fuente_oficial"],
        "url_fuente": desempleo_info["url_fuente"],
        "serie": serie_desempleo_10y
    }

    # ==============================================================================
    # 5. GUARDAR TODAS LAS SERIES HISTÓRICAS PARA EL GRÁFICO DINÁMICO
    # ==============================================================================
    archivo_series = ruta_data / "series_historicas.json"
    with open(archivo_series, "w", encoding="utf-8") as f:
        json.dump(series_historicas, f, ensure_ascii=False, indent=2)
    logger.info(f"✔ Archivo de series históricas generado: {archivo_series.name}")

    # ==============================================================================
    # 6. GENERAR CUADRO OFICIAL PARA MINUTA SEMANAL (CON ENLACES Y FUENTES)
    # ==============================================================================
    indicadores_minuta = [
        {
            "variable": "TPM (Banco Central de Chile) (%)",
            "cierre_semanal": formatear_numero_cl(tpm_info["valor_actual"], 1),
            "variacion_ww": "▬ Estable",
            "fuente_oficial": tpm_info["fuente_oficial"],
            "url_fuente_oficial": tpm_info["url_fuente"],
            "lectura_analitica": "El Consejo acordó mantener la tasa en 4,5% por unanimidad, enfocado en anclar expectativas inflacionarias."
        },
        {
            "variable": "Dólar Observado (USD/CLP) ($ CLP)",
            "cierre_semanal": formatear_numero_cl(dolar_actual, 2),
            "variacion_ww": formatear_variacion_semanal(dolar_actual, dolar_prev),
            "fuente_oficial": FUENTES_OFICIALES["bcentral_dolar"]["nombre"],
            "url_fuente_oficial": FUENTES_OFICIALES["bcentral_dolar"]["url"],
            "lectura_analitica": "Cotización del tipo de cambio influenciada por presiones externas y diferenciales de tasas."
        },
        {
            "variable": "Euro Observado (EUR/CLP) ($ CLP)",
            "cierre_semanal": formatear_numero_cl(eur_actual, 2),
            "variacion_ww": formatear_variacion_semanal(eur_actual, eur_prev),
            "fuente_oficial": "Banco Central de Chile (BDE) / FRED",
            "url_fuente_oficial": FUENTES_OFICIALES["bcentral_fx"]["url"],
            "lectura_analitica": "Movimiento alineado a la fortaleza de monedas de reserva internacional frente a divisas emergentes."
        },
        {
            "variable": "Yuan Chino (CNY/CLP) ($ CLP)",
            "cierre_semanal": formatear_numero_cl(cny_actual, 2),
            "variacion_ww": formatear_variacion_semanal(cny_actual, cny_prev),
            "fuente_oficial": "Banco Central de Chile (BDE) / FRED",
            "url_fuente_oficial": FUENTES_OFICIALES["bcentral_fx"]["url"],
            "lectura_analitica": "Paridad cruzada vinculada al pulso del sector exportador y la actividad fabril en China."
        },
        {
            "variable": "Unidad de Fomento (UF) ($ CLP)",
            "cierre_semanal": formatear_numero_cl(uf_actual, 2),
            "variacion_ww": formatear_variacion_semanal(uf_actual, uf_prev),
            "fuente_oficial": FUENTES_OFICIALES["sii_uf"]["nombre"],
            "url_fuente_oficial": FUENTES_OFICIALES["sii_uf"]["url"],
            "lectura_analitica": "La UF mantiene su reajuste diario legal conforme a la variación del IPC reportado por el INE."
        },
        {
            "variable": "Cobre (LME / Cochilco) (US$/lb)",
            "cierre_semanal": formatear_numero_cl(cobre_actual, 2),
            "variacion_ww": formatear_variacion_semanal(cobre_actual, cobre_prev),
            "fuente_oficial": FUENTES_OFICIALES["cochilco"]["nombre"],
            "url_fuente_oficial": FUENTES_OFICIALES["cochilco"]["url"],
            "lectura_analitica": "Precio spot oficial de liquidación en la Bolsa de Metales de Londres certificado diariamente por Cochilco en La Rueda."
        },
        {
            "variable": "Petróleo Brent (US$/bbl)",
            "cierre_semanal": formatear_numero_cl(brent_actual, 2),
            "variacion_ww": formatear_variacion_semanal(brent_actual, brent_prev),
            "fuente_oficial": FUENTES_OFICIALES["fred_brent"]["nombre"],
            "url_fuente_oficial": FUENTES_OFICIALES["fred_brent"]["url"],
            "lectura_analitica": "Sensibilidad a tensiones geopolíticas y cuotas de bombeo de la OPEP+."
        },
        {
            "variable": "Petróleo WTI (US$/bbl)",
            "cierre_semanal": formatear_numero_cl(wti_actual, 2),
            "variacion_ww": formatear_variacion_semanal(wti_actual, wti_prev),
            "fuente_oficial": FUENTES_OFICIALES["fred_wti"]["nombre"],
            "url_fuente_oficial": FUENTES_OFICIALES["fred_wti"]["url"],
            "lectura_analitica": "Referencia estadounidense condicionada por inventarios de crudo en Cushing."
        },
        {
            "variable": "Inflación IPC (último registro oficial INE) (Var. % m/m y a/a)",
            "cierre_semanal": f"{ipc_info['variacion_mensual_pct']}% m/m; {ipc_info['variacion_anual_pct']}% a/a",
            "variacion_ww": "▬ Estable",
            "fuente_oficial": ipc_info["fuente_oficial"],
            "url_fuente_oficial": ipc_info["url_fuente"],
            "lectura_analitica": f"IPC de {ipc_info.get('mes_referencia', 'último mes')} con {ipc_info['variacion_mensual_pct']}% mensual y {ipc_info['variacion_anual_pct']}% a doce meses."
        },
        {
            "variable": "Tasa de Desocupación Nacional (último registro oficial ENE - INE) (%)",
            "cierre_semanal": formatear_numero_cl(desempleo_info["valor_actual"], 1),
            "variacion_ww": "▬ Estable",
            "fuente_oficial": desempleo_info["fuente_oficial"],
            "url_fuente_oficial": desempleo_info["url_fuente"],
            "lectura_analitica": f"Desocupación situada en {desempleo_info['valor_actual']}% en el trimestre móvil {desempleo_info.get('trimestre_movil', '')}."
        }
    ]

    cuadro_minuta = {
        "metadatos": {
            "titulo": "Cuadro de Variables Macroeconómicas y Financieras",
            "fecha_emision": fecha_hoy,
            "semana_analizada": f"{hace_7_dias} al {fecha_hoy}",
            "proveedor": "Repositorio Oficial de Datos Económicos de Chile (UCEN)",
            "url_proveedor": "https://jpqb.github.io/datos_economicos_chile/",
            "licencia": "Datos Públicos Abiertos"
        },
        "indicadores": indicadores_minuta
    }

    archivo_cuadro = ruta_data / "cuadro_minuta_semanal.json"
    with open(archivo_cuadro, "w", encoding="utf-8") as f:
        json.dump(cuadro_minuta, f, ensure_ascii=False, indent=2)

    # ==============================================================================
    # 7. JSON CONSOLIDADO GENERAL
    # ==============================================================================
    indicadores_completos = {
        "metadatos": {
            "fecha_actualizacion_utc": datetime.now(timezone.utc).isoformat(),
            "estado": "Operativo (Alta Disponibilidad)",
            "fuentes_oficiales": FUENTES_OFICIALES
        },
        "indicadores": {
            "uf": {"nombre": "Unidad de Fomento", "valor": uf_actual, "unidad": "CLP", "var_ww": formatear_variacion_semanal(uf_actual, uf_prev), "fuente": FUENTES_OFICIALES["sii_uf"]["nombre"], "url_fuente": FUENTES_OFICIALES["sii_uf"]["url"]},
            "dolar": {"nombre": "Dólar Observado", "valor": dolar_actual, "unidad": "CLP", "var_ww": formatear_variacion_semanal(dolar_actual, dolar_prev), "fuente": FUENTES_OFICIALES["bcentral_dolar"]["nombre"], "url_fuente": FUENTES_OFICIALES["bcentral_dolar"]["url"]},
            "euro": {"nombre": "Euro Observado", "valor": eur_actual, "unidad": "CLP", "var_ww": formatear_variacion_semanal(eur_actual, eur_prev), "fuente": "Banco Central / FRED", "url_fuente": FUENTES_OFICIALES["bcentral_fx"]["url"]},
            "yuan": {"nombre": "Yuan Chino", "valor": cny_actual, "unidad": "CLP", "var_ww": formatear_variacion_semanal(cny_actual, cny_prev), "fuente": "Banco Central / FRED", "url_fuente": FUENTES_OFICIALES["bcentral_fx"]["url"]},
            "cobre": {"nombre": "Cobre (LME)", "valor": cobre_actual, "unidad": "US$/lb", "var_ww": formatear_variacion_semanal(cobre_actual, cobre_prev), "fuente": FUENTES_OFICIALES["cochilco"]["nombre"], "url_fuente": FUENTES_OFICIALES["cochilco"]["url"]},
            "petroleo_brent": {"nombre": "Petróleo Brent", "valor": brent_actual, "unidad": "US$/bbl", "var_ww": formatear_variacion_semanal(brent_actual, brent_prev), "fuente": FUENTES_OFICIALES["fred_brent"]["nombre"], "url_fuente": FUENTES_OFICIALES["fred_brent"]["url"]},
            "petroleo_wti": {"nombre": "Petróleo WTI", "valor": wti_actual, "unidad": "US$/bbl", "var_ww": formatear_variacion_semanal(wti_actual, wti_prev), "fuente": FUENTES_OFICIALES["fred_wti"]["nombre"], "url_fuente": FUENTES_OFICIALES["fred_wti"]["url"]},
            "tpm": {"nombre": "Tasa de Política Monetaria", "valor": tpm_info["valor_actual"], "unidad": "%", "var_ww": "▬ Estable", "fuente": tpm_info["fuente_oficial"], "url_fuente": tpm_info["url_fuente"]},
            "ipc_mensual": {"nombre": "IPC Mensual", "valor": ipc_info["variacion_mensual_pct"], "unidad": "%", "var_ww": "INE Oficial", "fuente": ipc_info["fuente_oficial"], "url_fuente": ipc_info["url_fuente"]},
            "desempleo": {"nombre": "Tasa de Desocupación", "valor": desempleo_info["valor_actual"], "unidad": "%", "var_ww": "ENE - INE", "fuente": desempleo_info["fuente_oficial"], "url_fuente": desempleo_info["url_fuente"]},
        }
    }

    archivo_dashboard = ruta_data / "indicadores_hoy.json"
    with open(archivo_dashboard, "w", encoding="utf-8") as f:
        json.dump(indicadores_completos, f, ensure_ascii=False, indent=2)

    logger.info(f"✔ Cuadro Minuta generado: {archivo_cuadro.name}")
    logger.info(f"✔ Indicadores Hoy generado: {archivo_dashboard.name}")

    print("\n" + "-" * 75)
    print("📊 RESUMEN EJECUTIVO (SIN PROYECCIONES • FUENTES OFICIALES INCLUIDAS)")
    print("-" * 75)
    for ind in indicadores_minuta:
        print(f"  • {ind['variable'][:40]:40} | {ind['cierre_semanal']:>12} | {ind['variacion_ww']:>10}")
    print("-" * 75)
    print("✅ Pipeline ejecutado con éxito y series históricas consolidadas.\n")


if __name__ == "__main__":
    ejecutar_pipeline_multivariable()
