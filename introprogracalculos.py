import csv
from datetime import datetime
from pathlib import Path

PRECIO_SILLITA_INICIAL = 85.0
COSTO_SILLITA_INICIAL = 45.0
PRECIO_MESITA_INICIAL = 140.0
COSTO_MESITA_INICIAL = 75.0
DESCUENTO_COMBO_PORCENTAJE_INICIAL = 0.10
CANTIDAD_MINIMA_COMBO = 2

COLUMNAS_VENTAS = [
    "fecha_hora",
    "cliente",
    "cantidad_sillitas",
    "cantidad_mesitas",
    "subtotal",
    "descuento",
    "ingreso_total",
    "costo_total",
    "ganancia_neta",
]


def validar_valores_positivos(valores: dict[str, float]) -> None:
    """Valida que los parámetros numéricos de configuración o cantidades no sean negativos."""
    for nombre, valor in valores.items():
        if valor < 0:
            raise ValueError(f"El valor de '{nombre}' no puede ser negativo.")


def aplica_descuento_combo(cantidad_sillitas: int, cantidad_mesitas: int) -> bool:
    """Indica si el pedido cumple la condición para aplicar descuento por combo."""
    return (
        cantidad_sillitas >= CANTIDAD_MINIMA_COMBO
        and cantidad_mesitas >= 1
    ) or (
        cantidad_sillitas >= 1
        and cantidad_mesitas >= CANTIDAD_MINIMA_COMBO
    )


def calcular_detalle_venta(
    cantidad_sillitas: int,
    cantidad_mesitas: int,
    precio_sillita: float,
    precio_mesita: float,
    costo_sillita: float,
    costo_mesita: float,
    porcentaje_descuento: float,
    cliente: str = "Cliente general",
) -> dict[str, str | int | float]:
    """Calcula ingresos, costos y ganancia neta de una venta sin modificar archivos."""
    validar_valores_positivos(
        {
            "cantidad_sillitas": float(cantidad_sillitas),
            "cantidad_mesitas": float(cantidad_mesitas),
            "precio_sillita": precio_sillita,
            "precio_mesita": precio_mesita,
            "costo_sillita": costo_sillita,
            "costo_mesita": costo_mesita,
            "porcentaje_descuento": porcentaje_descuento,
        }
    )

    subtotal = round(
        (cantidad_sillitas * precio_sillita) + (cantidad_mesitas * precio_mesita),
        2,
    )
    descuento = (
        round(subtotal * (porcentaje_descuento / 100.0), 2)
        if aplica_descuento_combo(cantidad_sillitas, cantidad_mesitas)
        else 0.0
    )
    ingreso_total = round(subtotal - descuento, 2)
    costo_total = round(
        (cantidad_sillitas * costo_sillita) + (cantidad_mesitas * costo_mesita),
        2,
    )
    ganancia_neta = round(ingreso_total - costo_total, 2)

    nombre_limpio = cliente.strip() if cliente.strip() else "Cliente general"
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "fecha_hora": fecha_actual,
        "cliente": nombre_limpio,
        "cantidad_sillitas": int(cantidad_sillitas),
        "cantidad_mesitas": int(cantidad_mesitas),
        "subtotal": subtotal,
        "descuento": descuento,
        "ingreso_total": ingreso_total,
        "costo_total": costo_total,
        "ganancia_neta": ganancia_neta,
    }


def registrar_venta_csv(ruta_archivo: Path, venta: dict[str, str | int | float]) -> None:
    """Guarda una venta en un archivo CSV creando el encabezado si no existe."""
    archivo_nuevo = not ruta_archivo.exists()
    with ruta_archivo.open(mode="a", newline="", encoding="utf-8") as archivo_csv:
        escritor = csv.DictWriter(archivo_csv, fieldnames=COLUMNAS_VENTAS)
        if archivo_nuevo:
            escritor.writeheader()
        escritor.writerow(venta)


def cargar_ventas_csv(ruta_archivo: Path) -> list[dict[str, str | int | float]]:
    """Lee y normaliza las ventas registradas desde el archivo CSV."""
    if not ruta_archivo.exists():
        return []

    ventas_cargadas: list[dict[str, str | int | float]] = []
    with ruta_archivo.open(mode="r", newline="", encoding="utf-8") as archivo_csv:
        lector = csv.DictReader(archivo_csv)
        for fila in lector:
            ventas_cargadas.append(
                {
                    "fecha_hora": fila["fecha_hora"],
                    "cliente": fila["cliente"],
                    "cantidad_sillitas": int(fila["cantidad_sillitas"]),
                    "cantidad_mesitas": int(fila["cantidad_mesitas"]),
                    "subtotal": float(fila["subtotal"]),
                    "descuento": float(fila["descuento"]),
                    "ingreso_total": float(fila["ingreso_total"]),
                    "costo_total": float(fila["costo_total"]),
                    "ganancia_neta": float(fila["ganancia_neta"]),
                }
            )
    return ventas_cargadas


def calcular_resumen_general(ventas: list[dict[str, str | int | float]]) -> dict[str, int | float]:
    """Calcula totales acumulados de ventas, ingresos, costos y ganancias."""
    total_ventas = len(ventas)
    total_sillitas = sum(int(v["cantidad_sillitas"]) for v in ventas)
    total_mesitas = sum(int(v["cantidad_mesitas"]) for v in ventas)
    ingresos_totales = round(sum(float(v["ingreso_total"]) for v in ventas), 2)
    costos_totales = round(sum(float(v["costo_total"]) for v in ventas), 2)
    ganancias_totales = round(sum(float(v["ganancia_neta"]) for v in ventas), 2)

    return {
        "total_ventas": total_ventas,
        "total_sillitas": total_sillitas,
        "total_mesitas": total_mesitas,
        "ingresos_totales": ingresos_totales,
        "costos_totales": costos_totales,
        "ganancias_totales": ganancias_totales,
    }