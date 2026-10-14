"""
================================================================================
REPOSITORIO DE DATOS ECONÓMICOS DE CHILE - EXTRACCIÓN OFICIAL DE LA UF
================================================================================

Propósito del script:
    Este programa automatiza la recolección, limpieza y publicación de la serie
    oficial de la Unidad de Fomento (UF) de Chile, utilizando como fuente primaria
    el Servicio de Impuestos Internos (SII) y el Banco Central de Chile.

¿Por qué nació este desarrollo?
    Frecuentemente, las aplicaciones y dashboards dependen de intermediarios o 
    servicios web de terceros que sufren caídas de certificados, límites de cuota
    o lentitud. Este script va directo a la fuente legal oficial y genera 
    archivos abiertos (JSON y CSV) que cualquier persona o sistema puede consumir
    sin restricciones.

Nota sobre la naturaleza de la UF:
    La UF es calculada por el Banco Central de Chile para cada día entre el 10
    del mes en curso y el 9 del mes subsiguiente, en función de la variación del
    Índice de Precios al Consumidor (IPC) del mes anterior. Por esta razón,
    la tabla oficial suele tener valores proyectados a futuro para los próximos
    días del mes.

Autor: Jean Paul & Antigravity (UCEN - IA Aplicada)
Licencia: Datos Abiertos / Dominio Público
================================================================================
"""

from datetime import date, datetime, timezone
import io
import json
import logging
from pathlib import Path
import sys
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests

# Garantizamos compatibilidad de codificación en consolas de Windows (evita errores con cp1252)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ------------------------------------------------------------------------------
# Configuración amigable de logs para entender qué ocurre paso a paso
# ------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ExtractorUF")

# Mapeo de meses en español según la convención estándar del SII
MESES_COLUMNAS = {
    "Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4,
    "May": 5, "Jun": 6, "Jul": 7, "Ago": 8,
    "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12,
}


def obtener_ruta_datos() -> Path:
    """
    Determina la ruta absoluta donde se guardarán los datos generados.
    Funciona de manera inteligente tanto si se ejecuta desde la raíz del
    repositorio como desde la carpeta 'src/'.
    """
    script_dir = Path(__file__).resolve().parent
    carpeta_data = script_dir.parent / "data"
    carpeta_data.mkdir(parents=True, exist_ok=True)
    return carpeta_data


def descargar_matriz_sii(ano: int) -> pd.DataFrame:
    """
    Descarga la tabla anual de la UF desde la página oficial del SII.

    Parámetros:
        ano (int): Año a consultar (ej. 2026).

    Retorna:
        pd.DataFrame: Tabla mensual de 31 filas con las columnas de los 12 meses.
    """
    url_oficial = f"https://www.sii.cl/valores_y_fechas/uf/uf{ano}.htm"
    logger.info(f"🌐 Conectando con la fuente oficial del SII para el año {ano}...")
    logger.info(f"   URL: {url_oficial}")

    encabezados = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "RepositorioDatosEconomicosChile/1.0 (+contacto: educacion@ucen.cl)"
        )
    }

    try:
        respuesta = requests.get(url_oficial, headers=encabezados, timeout=15)
        respuesta.raise_for_status()
    except requests.exceptions.RequestException as error_red:
        logger.error(f"❌ Error al contactar el servidor del SII: {error_red}")
        raise

    # El SII usa coma para decimales y punto para separador de miles.
    # Envolvemos el texto HTML en io.StringIO para cumplir con los estándares modernos de Pandas.
    tablas = pd.read_html(io.StringIO(respuesta.text), decimal=",", thousands=".")
    logger.info(f"📄 Se detectaron {len(tablas)} tablas en la página oficial.")

    # Buscamos de forma flexible la tabla que contiene la matriz anual (31 días y columnas de meses)
    for tabla in tablas:
        columnas_minuscula = [str(col).strip().lower() for col in tabla.columns]
        es_matriz_dias = tabla.shape[0] >= 28
        tiene_meses = any("ene" in col for col in columnas_minuscula) and any("feb" in col for col in columnas_minuscula)

        if es_matriz_dias and tiene_meses:
            logger.info("🎯 Matriz anual oficial identificada correctamente.")
            return tabla

    raise ValueError("No se pudo localizar la matriz anual de la UF en la página del SII.")


def transformar_matriz_a_serie_temporal(tabla_matriz: pd.DataFrame, ano: int) -> pd.DataFrame:
    """
    Convierte la matriz tabular de 31 filas x 12 columnas en un formato 'tidy data'
    (una fila por cada día válido: fecha, valor en CLP y fuente).

    Parámetros:
        tabla_matriz (pd.DataFrame): Matriz original del SII.
        ano (int): Año correspondiente a los datos.

    Retorna:
        pd.DataFrame: Serie temporal limpia y ordenada cronológicamente.
    """
    logger.info("🧹 Estructurando y depurando la serie temporal de valores...")
    registros_limpios: List[Dict] = []

    # Normalizamos los nombres de las columnas para evitar problemas con acentos o espacios
    columnas_limpias = {col: str(col).strip()[:3].capitalize() for col in tabla_matriz.columns}
    tabla_renombrada = tabla_matriz.rename(columns=columnas_limpias)

    for nombre_mes, numero_mes in MESES_COLUMNAS.items():
        if nombre_mes not in tabla_renombrada.columns:
            continue

        valores_mes = tabla_renombrada[nombre_mes]
        for indice_fila, valor_celda in enumerate(valores_mes):
            dia = indice_fila + 1

            # Descartamos celdas vacías (días inexistentes como 30 de febrero o días futuros sin publicar)
            if pd.isna(valor_celda) or str(valor_celda).strip() == "":
                continue

            try:
                # Verificamos que sea una fecha válida del calendario gregoriano
                fecha_dia = date(ano, numero_mes, dia)
                valor_numerico = round(float(valor_celda), 2)

                registros_limpios.append({
                    "fecha": fecha_dia.isoformat(),
                    "valor_clp": valor_numerico,
                    "dia": dia,
                    "mes": numero_mes,
                    "ano": ano,
                    "fuente": "Servicio de Impuestos Internos (SII) / Banco Central de Chile"
                })
            except (ValueError, TypeError):
                # Ocurre naturalmente para días no válidos según el mes (ej: 29/30/31 en meses de 28/30 días)
                continue

    dataframe_resultado = pd.DataFrame(registros_limpios)
    dataframe_resultado = dataframe_resultado.sort_values("fecha").reset_index(drop=True)

    # Calculamos la variación diaria absoluta y porcentual para agregar valor al consumidor
    dataframe_resultado["variacion_diaria_clp"] = dataframe_resultado["valor_clp"].diff().round(2)
    dataframe_resultado["variacion_diaria_pct"] = (
        (dataframe_resultado["valor_clp"].pct_change() * 100).round(4)
    )

    logger.info(f"✨ Se consolidaron {len(dataframe_resultado)} observaciones oficiales válidas para el año {ano}.")
    return dataframe_resultado


def generar_artefactos_publicos(serie_uf: pd.DataFrame, ruta_data: Path) -> Tuple[Dict, Path, Path]:
    """
    Crea los archivos públicos listos para que cualquier persona, minuta o dashboard
    pueda consumirlos vía API estática o descarga directa.
    """
    logger.info("💾 Guardando archivos en el directorio público de datos...")

    fecha_hoy = date.today().isoformat()

    # 1. Identificar el valor de hoy y el último valor disponible
    filtro_hoy = serie_uf[serie_uf["fecha"] == fecha_hoy]

    if not filtro_hoy.empty:
        registro_hoy = filtro_hoy.iloc[0].to_dict()
        mensaje_estado = "Valor oficial exacto para el día de hoy."
    else:
        # Si hoy es un feriado especial o aún no se publica, tomamos el valor más reciente registrado
        registro_hoy = serie_uf.iloc[-1].to_dict()
        mensaje_estado = f"Último valor oficial disponible en la serie ({registro_hoy['fecha']})."

    # 2. Identificar valores proyectados hacia adelante (el valor agregado que pocos dan)
    proyecciones_futuras = serie_uf[serie_uf["fecha"] > fecha_hoy][["fecha", "valor_clp"]].to_dict(orient="records")

    resumen_actual = {
        "metadatos": {
            "unidad": "Unidad de Fomento (UF)",
            "moneda": "CLP (Pesos Chilenos)",
            "pais": "Chile",
            "fuente_oficial": "Servicio de Impuestos Internos (SII) y Banco Central de Chile",
            "licencia": "Datos Públicos Abiertos",
            "fecha_extraccion_utc": datetime.now(timezone.utc).isoformat(),
            "nota": mensaje_estado,
        },
        "hoy": {
            "fecha": registro_hoy["fecha"],
            "valor_clp": registro_hoy["valor_clp"],
            "variacion_diaria_clp": registro_hoy["variacion_diaria_clp"] if pd.notna(registro_hoy["variacion_diaria_clp"]) else 0.0,
            "variacion_diaria_pct": registro_hoy["variacion_diaria_pct"] if pd.notna(registro_hoy["variacion_diaria_pct"]) else 0.0,
        },
        "proyecciones_publicadas_dias_siguientes": proyecciones_futuras[:15],
    }

    # Guardar JSON con el valor actual y proyecciones inmediatas
    archivo_hoy_json = ruta_data / "uf_hoy.json"
    with open(archivo_hoy_json, "w", encoding="utf-8") as f:
        json.dump(resumen_actual, f, ensure_ascii=False, indent=2)

    # Guardar CSV consolidado para análisis cuantitativo (R, Python, Excel)
    archivo_csv = ruta_data / f"uf_serie_{serie_uf['ano'].iloc[0]}.csv"
    serie_uf.to_csv(archivo_csv, index=False, encoding="utf-8")

    # Guardar también una copia como 'uf_actual_ano.csv' para consumo con URL fija
    archivo_csv_fijo = ruta_data / "uf_ultimo_ano.csv"
    serie_uf.to_csv(archivo_csv_fijo, index=False, encoding="utf-8")

    logger.info(f"   ✔ Archivo JSON de hoy: {archivo_hoy_json.name}")
    logger.info(f"   ✔ Archivo CSV histórico: {archivo_csv.name}")
    logger.info(f"   ✔ Archivo CSV enlace directo: {archivo_csv_fijo.name}")

    return resumen_actual, archivo_hoy_json, archivo_csv


def ejecutar_extraccion_completa():
    """
    Punto de entrada principal que orquesta todo el proceso de forma clara y resiliente.
    """
    print("\n" + "=" * 70)
    print("🇨🇱 INICIANDO EXTRACCIÓN DE LA UNIDAD DE FOMENTO (UF)")
    print("   Fuente: Servicio de Impuestos Internos (SII)")
    print("=" * 70 + "\n")

    ano_actual = date.today().year
    ruta_data = obtener_ruta_datos()

    try:
        matriz_sii = descargar_matriz_sii(ano_actual)
        serie_temporal = transformar_matriz_a_serie_temporal(matriz_sii, ano_actual)
        resumen, ruta_json, ruta_csv = generar_artefactos_publicos(serie_temporal, ruta_data)

        print("\n" + "-" * 70)
        print("📊 REPORTE DE RESULTADOS")
        print("-" * 70)
        print(f"  • Fecha evaluada: {resumen['hoy']['fecha']}")
        print(f"  • Valor UF:       ${resumen['hoy']['valor_clp']:,.2f} CLP")
        print(f"  • Variación día:  ${resumen['hoy']['variacion_diaria_clp']:+,.2f} CLP ({resumen['hoy']['variacion_diaria_pct']:+.4f}%)")
        print(f"  • Proyecciones:   {len(resumen['proyecciones_publicadas_dias_siguientes'])} días futuros registrados")
        print("-" * 70)
        print("✅ Proceso completado con éxito y datos listos para publicación.\n")

    except Exception as error_inesperado:
        logger.critical(f"💥 Ocurrió un inconveniente durante el proceso: {error_inesperado}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    ejecutar_extraccion_completa()
