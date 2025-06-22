
import streamlit as st
import numpy as np
import cv2
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import io
import base64

st.set_page_config(page_title="Calculadora DTF", layout="centered")

def image_to_url(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_b64}"

def remove_background(image, method="Auto", color_to_remove=(255, 255, 255)):
    image_np = np.array(image.convert("RGBA"))
    if method == "Auto":
        hsv = cv2.cvtColor(image_np, cv2.COLOR_RGBA2RGB)
        hsv = cv2.cvtColor(hsv, cv2.COLOR_RGB2HSV)
        lower = np.array([0, 0, 230], dtype=np.uint8)
        upper = np.array([180, 30, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)
    else:
        lower = np.array(color_to_remove) - 30
        upper = np.array(color_to_remove) + 30
        lower = np.clip(lower, 0, 255)
        upper = np.clip(upper, 0, 255)
        mask = cv2.inRange(image_np[:, :, :3], lower, upper)

    image_np[mask != 0] = [0, 0, 0, 0]
    return Image.fromarray(image_np)

st.markdown("<h2 style='text-align: center; color: white;'>Calculadora DTF</h2>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Sube tu imagen", type=["png", "jpg", "jpeg"])
if uploaded_file:
    image = Image.open(uploaded_file)
    method = st.radio("¿Cómo deseas eliminar el fondo?", ["Auto", "Manual"])

    if method == "Manual":
        st.write("Selecciona el color a eliminar")
        color = st.color_picker("Selecciona un color", "#FFFFFF")
        rgb_color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        image = remove_background(image, method="Manual", color_to_remove=rgb_color)
    else:
        image = remove_background(image, method="Auto")

    st.image(image, caption="Diseño sin fondo", use_column_width=True)

    st.subheader("Ingresa el tamaño del diseño (cm)")
    col1, col2 = st.columns(2)
    with col1:
        ancho = st.number_input("Ancho (cm)", min_value=1.0, value=10.0)
    with col2:
        alto = st.number_input("Alto (cm)", min_value=1.0, value=10.0)

    margen = 1
    ancho_total = ancho + margen
    alto_total = alto + margen

    cantidad_disenos = st.number_input("Cantidad de diseños", min_value=1, value=1)
    precio_metro = st.number_input("Precio por metro de DTF (MXN)", min_value=1.0, value=100.0)

    disenos_por_fila = int(58 // ancho_total)
    filas_por_metro = int(100 // alto_total)
    disenos_por_metro = disenos_por_fila * filas_por_metro

    metros_requeridos = cantidad_disenos / disenos_por_metro
    precio_total = metros_requeridos * precio_metro
    precio_unitario = precio_total / cantidad_disenos

    st.markdown(f"<h4 style='color:white'>Cabrian <b>{disenos_por_metro}</b> diseños por metro</h4>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='color:white'>Necesitarás aproximadamente <b>{metros_requeridos:.2f}</b> metros de DTF</h4>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='color:white'>Costo total: <b>${precio_total:.2f} MXN</b></h4>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='color:white'>Costo por diseño: <b>${precio_unitario:.2f} MXN</b></h4>", unsafe_allow_html=True)
