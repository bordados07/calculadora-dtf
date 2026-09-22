```python
import streamlit as st
from PIL import Image
import numpy as np
import cv2

st.set_page_config(page_title="Calculadora DTF", layout="centered")

st.markdown(
    "<h1 style='text-align: center; color: white;'>Calculadora de Metros de DTF</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center; color: gray;'>Sube tu diseño, elimina el fondo automáticamente y calcula el costo y metros de impresión en DTF.</p>",
    unsafe_allow_html=True
)

st.markdown("<hr>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "📤 Sube tu imagen",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:

    image = Image.open(uploaded_file).convert("RGBA")

    original_width, original_height = image.size
    aspect_ratio = original_width / original_height

    image_np = np.array(image)

    # Imagen original
    st.image(
        image,
        caption="🖼️ Imagen original",
        width="stretch"
    )

    # Activar/desactivar eliminación de fondo
    eliminar_fondo = st.checkbox(
        "Quitar fondo automáticamente",
        value=True
    )

    if eliminar_fondo:

        image_gray = cv2.cvtColor(
            image_np,
            cv2.COLOR_RGBA2GRAY
        )

        _, alpha = cv2.threshold(
            image_gray,
            250,
            255,
            cv2.THRESH_BINARY_INV
        )

        image_np[:, :, 3] = alpha

        image_sin_fondo = Image.fromarray(image_np)

        st.image(
            image_sin_fondo,
            caption="🧽 Fondo eliminado automáticamente",
            width="stretch"
        )

    else:

        st.image(
            image,
            caption="🖼️ Imagen sin modificar",
            width="stretch"
        )

    st.markdown("### ✏️ Define una medida del diseño")

    modo = st.radio(
        "¿Qué medida deseas ingresar?",
        ["Ancho (cm)", "Alto (cm)"]
    )

    if modo == "Ancho (cm)":

        ancho_cm = st.number_input(
            "Ancho (cm)",
            min_value=1.0,
            value=10.0
        )

        alto_cm = ancho_cm / aspect_ratio

    else:

        alto_cm = st.number_input(
            "Alto (cm)",
            min_value=1.0,
            value=10.0
        )

        ancho_cm = alto_cm * aspect_ratio

    st.markdown(
        f"📏 Medidas proporcionales del diseño: **{ancho_cm:.2f} cm x {alto_cm:.2f} cm**"
    )

    # Margen de separación
    margen = 1

    ancho_total = ancho_cm + margen
    alto_total = alto_cm + margen

    cantidad = st.number_input(
        "🎨 ¿Cuántos diseños necesitas?",
        min_value=1,
        step=1
    )

    # Medidas del metro DTF
    largo_dtf_cm = 58
    alto_dtf_cm = 100

    diseños_por_fila = int(largo_dtf_cm // ancho_total)
    filas_por_metro = int(alto_dtf_cm // alto_total)

    total_por_metro = diseños_por_fila * filas_por_metro

    if total_por_metro > 0:
        metros_necesarios = cantidad / total_por_metro
    else:
        metros_necesarios = 0

    st.markdown(f"🧾 **Diseños por metro:** {total_por_metro}")
    st.markdown(f"📐 **Metros de DTF necesarios:** {metros_necesarios:.2f}")

    st.markdown("### 💰 Costo del DTF")

    precio_metro = st.number_input(
        "Precio por metro (MXN)",
        min_value=0.0,
        value=100.0
    )

    if metros_necesarios > 0:

        total = metros_necesarios * precio_metro
        precio_unitario = total / cantidad

        st.success(
            f"💸 Precio total: ${total:.2f} MXN"
        )

        st.info(
            f"🧾 Precio por diseño: ${precio_unitario:.2f} MXN"
        )

st.markdown("---")

st.markdown("### ¿Duda con la eliminación de fondo?")

st.markdown(
    "[Haz clic aquí para quitar el fondo manualmente](https://www.iloveimg.com/es/eliminar-fondo)",
    unsafe_allow_html=True
)
```
