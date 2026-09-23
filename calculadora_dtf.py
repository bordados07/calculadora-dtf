import streamlit as st
from PIL import Image
import numpy as np
import cv2
import matplotlib.pyplot as plt

st.set_page_config(page_title="Calculadora DTF PRO", layout="centered")

ANCHO_ROLLO = 58.0
LARGO_METRO = 100.0

st.title("📦 Calculadora DTF PRO MAX 4K HD")
st.write("Recorte automático, rotación inteligente, validación y vista previa de acomodo.")

archivo = st.file_uploader("Sube una imagen", type=["png", "jpg", "jpeg"])

if archivo is not None:

    image = Image.open(archivo).convert("RGBA")
    st.image(image, caption="Imagen original", width="stretch")

    img_np = np.array(image)

    quitar_fondo = st.checkbox("Quitar fondo automáticamente", value=True)

    if quitar_fondo:
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGBA2GRAY)
        _, alpha = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
        img_np[:, :, 3] = alpha

    alpha = img_np[:, :, 3]
    coords = cv2.findNonZero(alpha)

    if coords is None:
        st.error("No se detectó contenido en la imagen.")
        st.stop()

    x, y, w, h = cv2.boundingRect(coords)
    recorte = img_np[y:y+h, x:x+w]

    st.image(Image.fromarray(recorte), caption="Diseño recortado automáticamente", width="stretch")

    aspect_ratio = w / h

    modo = st.radio("Medida a ingresar", ["Ancho (cm)", "Alto (cm)"])

    if modo == "Ancho (cm)":
        ancho_cm = st.number_input("Ancho", min_value=1.0, value=10.0)
        alto_cm = ancho_cm / aspect_ratio
    else:
        alto_cm = st.number_input("Alto", min_value=1.0, value=10.0)
        ancho_cm = alto_cm * aspect_ratio

    margen = st.number_input(
        "Margen entre diseños (cm)",
        min_value=0.0,
        max_value=15.0,
        value=1.0,
        step=0.1
    )
    cantidad = st.number_input("Cantidad de diseños", 1, 100000, 100)

    orientacion_usuario = st.radio(
        "Orientación del diseño",
        ["Automática", "Horizontal", "Vertical"]
    )

    logo_base = Image.fromarray(recorte)

    if orientacion_usuario == "Horizontal":
        opciones = [("Horizontal", ancho_cm + margen, alto_cm + margen)]
        logo_vista = logo_base

    elif orientacion_usuario == "Vertical":
        opciones = [("Vertical", alto_cm + margen, ancho_cm + margen)]
        logo_vista = logo_base.rotate(90, expand=True)

    else:
        opciones = [
            ("Horizontal", ancho_cm + margen, alto_cm + margen),
            ("Vertical", alto_cm + margen, ancho_cm + margen)
        ]
        logo_vista = None

    mejor = None
    mejor_total = -1

    for nombre, ancho, alto in opciones:

        if ancho > ANCHO_ROLLO:
            continue

        por_fila = int(ANCHO_ROLLO // ancho)
        filas = int(LARGO_METRO // alto)
        total = por_fila * filas

        if total > mejor_total:
            mejor_total = total
            mejor = (nombre, ancho, alto, por_fila, filas, total)

    if mejor is None:
        st.error("El diseño no cabe en el rollo de 58 cm.")
        st.stop()

    nombre, ancho_u, alto_u, por_fila, filas, total = mejor

    if orientacion_usuario == "Automática":
        if nombre == "Vertical":
            logo_vista = logo_base.rotate(90, expand=True)
        else:
            logo_vista = logo_base

    st.success(f"Orientación utilizada: {nombre}")
    st.write(f"Diseños por ANCHO: {por_fila}")
    st.write(f"Diseños por ALTO: {filas}")
    st.write(f"Total por metro: {total}")

    metros = cantidad / total if total else 0

    st.write(f"Metros necesarios: {metros:.2f}")

    precio_metro = st.number_input("Precio por metro (MXN)", min_value=0.0, value=100.0)

    costo_total = metros * precio_metro
    costo_unitario = costo_total / cantidad

    st.success(f"Costo total: ${costo_total:.2f} MXN")
    st.info(f"Costo por diseño: ${costo_unitario:.4f} MXN")

    import math

    st.subheader("Vista previa de acomodo")

    logo = logo_vista

    disenos_por_metro = total
    metros_vista = math.ceil(cantidad / disenos_por_metro)

    for pagina in range(metros_vista):

        restantes = cantidad - (pagina * disenos_por_metro)
        mostrar = min(disenos_por_metro, restantes)

        st.markdown(f"### Metro {pagina + 1}")

        fig, ax = plt.subplots(figsize=(6, 10))

        ax.set_xlim(0, ANCHO_ROLLO)
        ax.set_ylim(0, LARGO_METRO)

        contador = 0

        for fila in range(filas):
            for columna in range(por_fila):

                if contador >= mostrar:
                    break

                x0 = columna * ancho_u
                y0 = fila * alto_u

                logo_ancho = max(ancho_u - margen, 0.1)
                logo_alto = max(alto_u - margen, 0.1)

                ax.imshow(
                    logo,
                    extent=[
                        x0,
                        x0 + logo_ancho,
                        y0,
                        y0 + logo_alto
                    ]
                )

                ax.add_patch(
                    plt.Rectangle(
                        (x0, y0),
                        ancho_u,
                        alto_u,
                        fill=False,
                        linewidth=1
                    )
                )

                contador += 1

            if contador >= mostrar:
                break

        ax.set_title(f"{mostrar} diseños")
        ax.set_aspect("equal")

        st.pyplot(fig)
