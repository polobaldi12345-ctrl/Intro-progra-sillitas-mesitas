from pathlib import Path
import streamlit as st

from introprogracalculos import (
    COSTO_MESITA_INICIAL,
    COSTO_SILLITA_INICIAL,
    DESCUENTO_COMBO_PORCENTAJE_INICIAL,
    PRECIO_MESITA_INICIAL,
    PRECIO_SILLITA_INICIAL,
    calcular_detalle_venta,
    calcular_resumen_general,
    cargar_ventas_csv,
    registrar_venta_csv,
)

RUTA_VENTAS_CSV = Path("ventas_emprendimiento.csv")


def configurar_pagina() -> None:
    """Configura los metadatos y el encabezado principal de la aplicación."""
    st.set_page_config(
        page_title="Gestión - Sillitas y Mesitas",
        page_icon="🪑",
        layout="wide",
    )
    st.title("🪑 Gestión de Sillitas y Mesitas")
    st.caption("Cotizador, registro de ventas y control de ganancias para tu emprendimiento.")


def renderizar_configuracion_precios() -> dict[str, float]:
    """Renderiza los controles de precios, costos y descuento en la barra lateral."""
    st.sidebar.header("⚙️ Precios y costos unitarios")

    precio_sillita = st.sidebar.number_input(
        "Precio sillita (Bs)", min_value=0.0, step=5.0, value=PRECIO_SILLITA_INICIAL
    )
    costo_sillita = st.sidebar.number_input(
        "Costo sillita (Bs)", min_value=0.0, step=5.0, value=COSTO_SILLITA_INICIAL
    )
    precio_mesita = st.sidebar.number_input(
        "Precio mesita (Bs)", min_value=0.0, step=5.0, value=PRECIO_MESITA_INICIAL
    )
    costo_mesita = st.sidebar.number_input(
        "Costo mesita (Bs)", min_value=0.0, step=5.0, value=COSTO_MESITA_INICIAL
    )
    porcentaje_descuento = st.sidebar.number_input(
        "Descuento combo (%)",
        min_value=0.0,
        max_value=100.0,
        step=1.0,
        value=DESCUENTO_COMBO_PORCENTAJE_INICIAL * 100,
    )

    return {
        "precio_sillita": float(precio_sillita),
        "costo_sillita": float(costo_sillita),
        "precio_mesita": float(precio_mesita),
        "costo_mesita": float(costo_mesita),
        "porcentaje_descuento": float(porcentaje_descuento),
    }


def renderizar_metricas_generales(resumen: dict[str, int | float]) -> None:
    """Muestra las métricas acumuladas del emprendimiento."""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ventas registradas", resumen["total_ventas"])
    col2.metric("Ingresos totales", f"Bs {resumen['ingresos_totales']:.2f}")
    col3.metric("Costos totales", f"Bs {resumen['costos_totales']:.2f}")
    col4.metric("Ganancia neta total", f"Bs {resumen['ganancias_totales']:.2f}")


def renderizar_cotizador_y_registro(config: dict[str, float]) -> None:
    """Permite calcular una cotización y guardar la venta en el CSV."""
    st.subheader("🧾 Nueva cotización / venta")

    col_cliente, col_sillitas, col_mesitas = st.columns([2, 1, 1])
    cliente = col_cliente.text_input("Nombre del cliente (opcional)", placeholder="Ej. Camila")
    cantidad_sillitas = col_sillitas.number_input("Sillitas", min_value=0, step=1, value=2)
    cantidad_mesitas = col_mesitas.number_input("Mesitas", min_value=0, step=1, value=1)

    try:
        detalle = calcular_detalle_venta(
            cantidad_sillitas=int(cantidad_sillitas),
            cantidad_mesitas=int(cantidad_mesitas),
            precio_sillita=config["precio_sillita"],
            precio_mesita=config["precio_mesita"],
            costo_sillita=config["costo_sillita"],
            costo_mesita=config["costo_mesita"],
            porcentaje_descuento=config["porcentaje_descuento"],
            cliente=cliente,
        )
    except ValueError as error:
        st.error(str(error))
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Subtotal", f"Bs {detalle['subtotal']:.2f}")
    c2.metric("Descuento", f"-Bs {detalle['descuento']:.2f}")
    c3.metric("Total a cobrar", f"Bs {detalle['ingreso_total']:.2f}")
    c4.metric("Ganancia estimada", f"Bs {detalle['ganancia_neta']:.2f}")

    if st.button("Registrar venta", type="primary"):
        if int(cantidad_sillitas) == 0 and int(cantidad_mesitas) == 0:
            st.warning("Ingresa al menos 1 sillita o 1 mesita para registrar una venta.")
            return

        registrar_venta_csv(RUTA_VENTAS_CSV, detalle)
        st.success("Venta registrada correctamente en `ventas_emprendimiento.csv`.")
        st.rerun()


def renderizar_historial_ventas(ventas: list[dict[str, str | int | float]]) -> None:
    """Muestra el historial de ventas registradas."""
    st.subheader("📋 Historial de ventas")
    if not ventas:
        st.info("Todavía no hay ventas registradas. ¡Registra la primera arriba!")
        return

    st.dataframe(ventas, use_container_width=True, hide_index=True)


def main() -> None:
    """Punto de entrada principal de la aplicación."""
    configurar_pagina()
    config_precios = renderizar_configuracion_precios()

    ventas = cargar_ventas_csv(RUTA_VENTAS_CSV)
    resumen = calcular_resumen_general(ventas)

    renderizar_metricas_generales(resumen)
    st.divider()
    renderizar_cotizador_y_registro(config_precios)
    st.divider()
    renderizar_historial_ventas(ventas)


if __name__ == "__main__":
    main()