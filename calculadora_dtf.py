
import streamlit as st
from PIL import Image, ImageOps
import numpy as np
import cv2
from io import BytesIO
import base64

st.set_page_config(page_title="Calculadora DTF", layout="centered")
st.markdown("""<h1 style='text-align: center; color: white;'>Calculadora de Metros de DTF</h1>""", unsafe_allow_html=True)

modo = st.radio("Selecciona el método para eliminar el fondo:", ["Automático (IA)", "Manual (seleccionar color)"])

uploaded_file = st.file_uploader("Sube tu diseño", type=["png", "jpg", "jpeg"])
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGBA")
    img_np = np.array(image)

    if modo == "Automático (IA)":
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGBA2GRAY)
        _, mask = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)
        img_np[mask == 255] = (0, 0, 0, 0)
    else:
        st.write("Haz clic en el fondo que deseas eliminar (implementación simplificada)")
        click_color = st.color_picker("Selecciona el color del fondo", "#FFFFFF")
        click_rgb = tuple(int(click_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        lower = np.array([c - 20 for c in click_rgb])
        upper = np.array([c + 20 for c in click_rgb])
        mask = cv2.inRange(img_np[:, :, :3], lower, upper)
        img_np[mask > 0] = (0, 0, 0, 0)

    image_no_bg = Image.fromarray(img_np)
    st.image(image_no_bg, caption="Diseño sin fondo", use_column_width=True)

    dimension = st.radio("¿Qué dimensión quieres ingresar?", ["Ancho (cm)", "Alto (cm)"])
    user_size = st.number_input(f"Ingrese el {dimension.lower()} del diseño en cm", min_value=1.0)

    width, height = image_no_bg.size
    aspect_ratio = height / width

    if dimension == "Ancho (cm)":
        width_cm = user_size
        height_cm = user_size * aspect_ratio
    else:
        height_cm = user_size
        width_cm = user_size / aspect_ratio

    st.markdown(f"**Tamaño final del diseño (sin fondo, proporcional):** {width_cm:.2f}cm x {height_cm:.2f}cm")

    # Agregar margen de separación de 1 cm
    width_cm += 1
    height_cm += 1

    cantidad_disenos = st.number_input("¿Cuántos diseños necesitas?", min_value=1)
    DTF_alto = 100  # cm
    DTF_largo = 58  # cm

    diseños_por_fila = int(DTF_largo // width_cm)
    filas_por_metro = int(DTF_alto // height_cm)
    total_diseños_por_metro = diseños_por_fila * filas_por_metro

    metros_necesarios = cantidad_disenos / total_diseños_por_metro
    metros_necesarios = np.ceil(metros_necesarios * 100) / 100  # redondear a 2 decimales

    st.markdown(f"**Diseños por metro:** {total_diseños_por_metro}")
    st.markdown(f"**Metros necesarios:** {metros_necesarios:.2f} m")

    precio_metro = st.number_input("Precio por metro de DTF (MXN)", min_value=0.0)
    costo_total = metros_necesarios * precio_metro
    precio_unitario = costo_total / cantidad_disenos if cantidad_disenos else 0

    st.markdown(f"**Costo total:** ${costo_total:.2f} MXN")
    st.markdown(f"**Precio por diseño:** ${precio_unitario:.2f} MXN")
