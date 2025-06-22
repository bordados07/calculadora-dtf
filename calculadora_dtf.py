
import streamlit as st
from PIL import Image
import numpy as np
import cv2
import io
from streamlit_image_coordinates import image_coordinates

st.set_page_config(page_title="Calculadora DTF", layout="centered")
st.markdown(
    "<h1 style='text-align: center; color: white;'>Calculadora DTF</h1>",
    unsafe_allow_html=True,
)

modo = st.radio("Modo de eliminación de fondo", ["Automático", "Manual"])

imagen_subida = st.file_uploader("Sube tu diseño", type=["png", "jpg", "jpeg"])
imagen = None
if imagen_subida:
    imagen = Image.open(imagen_subida).convert("RGBA")
    original = np.array(imagen)

    if modo == "Automático":
        fondo_blanco = np.array([255, 255, 255, 255])
        sin_fondo = np.where(original[:, :, :4] == fondo_blanco, (0, 0, 0, 0), original)
        imagen_sin_fondo = Image.fromarray(sin_fondo.astype("uint8"), "RGBA")

    elif modo == "Manual":
        coords = image_coordinates(imagen, key="img_coords")
        if coords:
            x, y = int(coords["x"]), int(coords["y"])
            color_bgr = np.array(imagen)[y, x][:3]
            tolerancia = 40
            lower = np.clip(color_bgr - tolerancia, 0, 255)
            upper = np.clip(color_bgr + tolerancia, 0, 255)
            mask = cv2.inRange(np.array(imagen)[:, :, :3], lower, upper)
            resultado = np.array(imagen)
            resultado[mask != 0] = [0, 0, 0, 0]
            imagen_sin_fondo = Image.fromarray(resultado)

    st.image(imagen_sin_fondo if modo == "Automático" else imagen, caption="Vista previa", use_column_width=True)

    if modo == "Manual" and coords:
        st.image(imagen_sin_fondo, caption="Imagen sin fondo (Manual)", use_column_width=True)
