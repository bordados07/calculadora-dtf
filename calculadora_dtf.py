
import streamlit as st
from PIL import Image
import numpy as np
import cv2
from streamlit_drawable_canvas import st_canvas

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
st.markdown("<div class='subtitle'>Sube tu diseño, elimina el fondo y calcula tus metros</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Sube tu diseño (PNG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    np_img = np.array(image)

    st.markdown("### 🧼 Selecciona el método para eliminar el fondo")
    metodo = st.radio("Método de eliminación de fondo", ["Automático (blanco)", "Manual (seleccionar color)"])

    if metodo == "Automático (blanco)":
        hsv = cv2.cvtColor(np_img, cv2.COLOR_RGB2HSV)
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 40, 255])
        mask = cv2.inRange(hsv, lower_white, upper_white)
        no_bg = cv2.bitwise_and(np_img, np_img, mask=cv2.bitwise_not(mask))
    else:
        st.markdown("Haz clic sobre el color que deseas eliminar:")
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0.0)",
            stroke_width=1,
            stroke_color="#000000",
            background_image=image,
            update_streamlit=True,
            height=image.height,
            width=image.width,
            drawing_mode="point",
            key="canvas",
        )

        no_bg = np_img.copy()

        if canvas_result.json_data and canvas_result.json_data["objects"]:
            punto = canvas_result.json_data["objects"][-1]
            px = int(punto["left"])
            py = int(punto["top"])
            color_bgr = no_bg[py, px][::-1]
            color_hsv = cv2.cvtColor(np.uint8([[color_bgr]]), cv2.COLOR_BGR2HSV)[0][0]

            h, s, v = color_hsv
            lower = np.array([max(h - 10, 0), 50, 50])
            upper = np.array([min(h + 10, 179), 255, 255])
            hsv = cv2.cvtColor(no_bg, cv2.COLOR_RGB2HSV)
            mask = cv2.inRange(hsv, lower, upper)
            no_bg = cv2.bitwise_and(no_bg, no_bg, mask=cv2.bitwise_not(mask))

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

    # Agregar margen
    width_cm += 1
    height_cm += 1

    st.markdown(f"📐 Tamaño con márgenes incluidos: **{width_cm} cm x {height_cm} cm**")

    cantidad = st.number_input("🧾 ¿Cuántos diseños necesitas?", min_value=1, value=10, step=1)
    precio_metro = st.number_input("💸 Precio del metro de DTF (MXN)", min_value=1.0, value=80.0, step=1.0)

    # Área del rollo de DTF
    rollo_alto = 100.0
    rollo_ancho = 58.0

    diseños_x_fila = int(rollo_ancho // width_cm)
    filas_por_metro = int(rollo_alto // height_cm)
    diseños_por_metro = diseños_x_fila * filas_por_metro

    if diseños_por_metro == 0:
        st.error("❌ El diseño es demasiado grande para caber en un metro de DTF.")
    else:
        metros_necesarios = round(cantidad / diseños_por_metro, 2)
        precio_unitario = round(precio_metro / diseños_por_metro, 2)
        costo_total = round(metros_necesarios * precio_metro, 2)

        st.success(f"📦 En 1 metro caben {diseños_por_metro} diseños ({diseños_x_fila} por fila, {filas_por_metro} filas)")
        st.info(f"🧮 Para {cantidad} diseños necesitas aproximadamente **{metros_necesarios} metros** de DTF.")
        st.markdown(f"💲 **Precio por diseño:** ${precio_unitario} MXN")
        st.markdown(f"💰 **Costo total del pedido:** ${costo_total} MXN")
