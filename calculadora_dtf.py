
from PIL import Image
import numpy as np
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import io

# Configuración visual
st.set_page_config(page_title="Calculadora DTF", layout="centered")
st.markdown("<h1 style='text-align: center; color: white;'>Calculadora DTF</h1>", unsafe_allow_html=True)
st.markdown("""
    <style>
        body {
            background-color: #000000;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Subir imagen
uploaded_file = st.file_uploader("Sube tu diseño en PNG (fondo blanco o de color):", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGBA")
    np_image = np.array(image)

    st.subheader("Selecciona el modo de eliminación de fondo")
    modo = st.radio("Modo de eliminación de fondo", options=["Automático (blanco)", "Manual (clic sobre el fondo)"])

    if modo == "Manual (clic sobre el fondo)":
        st.markdown("Haz clic en el fondo de la imagen para seleccionarlo y eliminarlo")

        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0.0)",
            stroke_width=1,
            stroke_color="rgba(255, 255, 255, 0.0)",
            background_image=image,
            update_streamlit=True,
            height=image.height,
            width=image.width,
            drawing_mode="transform",
            key="canvas"
        )

        if canvas_result.json_data and canvas_result.image_data is not None:
            if canvas_result.json_data["objects"]:
                x = int(canvas_result.json_data["objects"][-1]["left"])
                y = int(canvas_result.json_data["objects"][-1]["top"])
                if 0 <= y < np_image.shape[0] and 0 <= x < np_image.shape[1]:
                    pixel = np_image[y, x, :3]
                    st.success(f"Color seleccionado: {pixel.tolist()}")

                    mask = np.all(np_image[:, :, :3] == pixel, axis=-1)
                    np_image[mask] = [255, 255, 255, 0]
                    image = Image.fromarray(np_image)

    elif modo == "Automático (blanco)":
        st.info("Eliminando fondo blanco automáticamente...")
        threshold = 240
        r, g, b, a = np.rollaxis(np_image, axis=-1)
        mask = (r > threshold) & (g > threshold) & (b > threshold)
        np_image[mask] = [255, 255, 255, 0]
        image = Image.fromarray(np_image)

    st.image(image, caption="Diseño sin fondo", use_column_width=True)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    byte_im = buffer.getvalue()
    st.download_button("Descargar imagen sin fondo", data=byte_im, file_name="diseño_sin_fondo.png", mime="image/png")
