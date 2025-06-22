
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

uploaded_file = st.file_uploader("Sube tu imagen", type=["png", "jpg", "jpeg"])
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGBA")
    image_np = np.array(image)

    st.image(image, caption="Imagen original", use_column_width=True)

    # Eliminar fondo blanco automáticamente
    image_gray = cv2.cvtColor(image_np, cv2.COLOR_RGBA2GRAY)
    _, alpha = cv2.threshold(image_gray, 250, 255, cv2.THRESH_BINARY_INV)
    image_np[:, :, 3] = alpha
    st.image(image_np, caption="Fondo eliminado automáticamente", use_column_width=True)

    st.markdown("### Define las medidas del diseño")
    col1, col2 = st.columns(2)
    with col1:
        ancho_cm = st.number_input("Ancho (cm)", min_value=1.0, value=10.0)
    with col2:
        alto_cm = st.number_input("Alto (cm)", min_value=1.0, value=10.0)

    margen = 1
    ancho_total = ancho_cm + margen
    alto_total = alto_cm + margen

    cantidad = st.number_input("¿Cuántos diseños necesitas?", min_value=1, step=1)

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

    st.markdown("### Costo del DTF")
    precio_metro = st.number_input("Precio por metro (MXN)", min_value=0.0, value=100.0)
    if metros_necesarios > 0:
        total = metros_necesarios * precio_metro
        precio_unitario = total / cantidad
        st.success(f"Precio total: ${total:.2f} MXN")
        st.info(f"Precio por diseño: ${precio_unitario:.2f} MXN")

# Enlace alternativo para quitar fondo manual
st.markdown("---")
st.markdown("### ¿Duda con la eliminación de fondo?")
st.markdown("[Haz clic aquí para quitar el fondo manualmente](https://www.iloveimg.com/es/eliminar-fondo)", unsafe_allow_html=True)
