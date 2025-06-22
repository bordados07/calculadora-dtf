
import streamlit as st
from PIL import Image
import numpy as np
import cv2

st.set_page_config(page_title="Calculadora DTF", layout="centered")

# Estilo visual
st.markdown(
    """
    <style>
        .stApp {
            background-color: #0c0c0c;
            color: white;
        }
        .title {
            text-align: center;
            font-size: 36px;
            color: #ffcc00;
        }
        .subtitle {
            font-size: 20px;
            margin-top: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='title'>🎨 Calculadora de DTF</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Sube tu diseño y te diremos cuántos metros de DTF necesitas</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Sube tu diseño (PNG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    np_img = np.array(image)

    # Eliminar fondo blanco con HSV
    hsv = cv2.cvtColor(np_img, cv2.COLOR_RGB2HSV)
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 40, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)
    no_bg = cv2.bitwise_and(np_img, np_img, mask=cv2.bitwise_not(mask))
    st.image(no_bg, caption="Diseño sin fondo", use_container_width=True)

    # Proporción original
    height_px, width_px = no_bg.shape[:2]
    aspect_ratio = width_px / height_px

    st.markdown("### 📏 Medidas del diseño")
    col1, col2 = st.columns(2)
    with col1:
        input_mode = st.radio("¿Qué medida deseas ingresar?", ["Ancho (cm)", "Alto (cm)"])

    with col2:
        valor = st.number_input("Introduce el valor en cm", min_value=1.0, value=10.0, step=0.5)

    if input_mode == "Ancho (cm)":
        width_cm = valor
        height_cm = round(width_cm / aspect_ratio, 2)
    else:
        height_cm = valor
        width_cm = round(height_cm * aspect_ratio, 2)

    # Agregar 1 cm de margen en cada dirección
    width_cm += 1
    height_cm += 1

    st.markdown(f"📐 Tamaño con márgenes incluidos: **{width_cm} cm x {height_cm} cm**")

    cantidad = st.number_input("🧾 ¿Cuántos diseños necesitas?", min_value=1, value=10, step=1)

    # Área del rollo de DTF
    rollo_alto = 100.0  # cm
    rollo_ancho = 58.0  # cm

    diseños_x_fila = int(rollo_ancho // width_cm)
    filas_por_metro = int(rollo_alto // height_cm)
    diseños_por_metro = diseños_x_fila * filas_por_metro

    if diseños_por_metro == 0:
        st.error("❌ El diseño es demasiado grande para caber en un metro de DTF.")
    else:
        metros_necesarios = round(cantidad / diseños_por_metro, 2)
        st.success(f"📦 En 1 metro caben {diseños_por_metro} diseños ({diseños_x_fila} por fila, {filas_por_metro} filas)")
        st.info(f"🧮 Para {cantidad} diseños necesitas aproximadamente **{metros_necesarios} metros** de DTF.")
