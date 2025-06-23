
import streamlit as st
from PIL import Image
import numpy as np
import cv2

st.set_page_config(page_title="Calculadora DTF", layout="centered")

st.markdown(
    "<h1 style='text-align: center; color: white;'>Calculadora de Metros de DTF</h1>",
    unsafe_allow_html=True
)
st.markdown("<hr>", unsafe_allow_html=True)

# Link para quitar fondo manualmente
st.markdown("### ¿Dificultades para quitar fondo?")
st.markdown("[Usa esta herramienta externa para eliminar el fondo](https://www.iloveimg.com/es/eliminar-fondo)")

# Cargar imagen
uploaded_file = st.file_uploader("Sube tu imagen", type=["png", "jpg", "jpeg"])
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGBA")
    image_np = np.array(image)

    # Activar o desactivar eliminación de fondo
    eliminar_fondo = st.checkbox("¿Deseas eliminar el fondo de la imagen?", value=True)

    if eliminar_fondo:
        # Eliminar fondo blanco automáticamente
        image_gray = cv2.cvtColor(image_np, cv2.COLOR_RGBA2GRAY)
        _, alpha = cv2.threshold(image_gray, 250, 255, cv2.THRESH_BINARY_INV)
        image_np[:, :, 3] = alpha
        st.image(image_np, caption="Fondo eliminado automáticamente", use_column_width=True)
    else:
        st.image(image_np, caption="Imagen sin eliminar fondo", use_column_width=True)

    # Medidas proporcionales
    st.markdown("### Define las medidas del diseño")
    col1, col2 = st.columns(2)
    ancho_cm = col1.number_input("Ancho (cm)", min_value=1.0, value=10.0)
    alto_cm = col2.number_input("Alto (cm)", min_value=1.0, value=10.0)

    # Activar proporcionalidad
    mantener_proporcion = st.checkbox("Mantener proporción", value=True)
    if mantener_proporcion:
        aspecto = image.width / image.height
        if ancho_cm != 0:
            alto_cm = ancho_cm / aspecto
            col2.number_input("Alto (cm)", value=alto_cm, key="auto_alto")
        else:
            ancho_cm = alto_cm * aspecto
            col1.number_input("Ancho (cm)", value=ancho_cm, key="auto_ancho")

    # Margen de separación
    margen = 1
    ancho_total = ancho_cm + margen
    alto_total = alto_cm + margen

    # Número de diseños deseados
    cantidad = st.number_input("¿Cuántos diseños necesitas?", min_value=1, step=1)

    # Área útil del DTF
    largo_dtf_cm = 58
    alto_dtf_cm = 100
    diseños_por_fila = int(largo_dtf_cm // ancho_total)
    filas_por_metro = int(alto_dtf_cm // alto_total)
    total_por_metro = diseños_por_fila * filas_por_metro

    if total_por_metro > 0:
        metros_necesarios = cantidad / total_por_metro
    else:
        metros_necesarios = 0

    st.markdown(f"**Diseños por metro:** {total_por_metro}")
    st.markdown(f"**Metros de DTF necesarios:** {metros_necesarios:.2f}")

    # Costo total
    st.markdown("### Costo del DTF")
    precio_metro = st.number_input("Precio por metro (MXN)", min_value=0.0, value=100.0)
    if metros_necesarios > 0:
        total = metros_necesarios * precio_metro
        precio_unitario = total / cantidad
        st.success(f"Precio total: ${total:.2f} MXN")
        st.info(f"Precio por diseño: ${precio_unitario:.2f} MXN")
