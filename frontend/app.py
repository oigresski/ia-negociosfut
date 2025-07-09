import streamlit as st
import requests

st.set_page_config(page_title="Login IA", layout="centered")

API_LOGIN = "http://localhost:8000/login"
API_ESTRATEGIA = "http://localhost:8000/generar-estrategia"
API_RAG = "http://localhost:8000/consultar-documento"

# Estado de sesión para login
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

# --- LOGIN ---
if not st.session_state.autenticado:
    st.title("🔐 Iniciar sesión")

    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        contrasena = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Iniciar sesión")

        if submit:
            data = {
                "usuario": usuario,
                "contrasena": contrasena
            }
            try:
                r = requests.post(API_LOGIN, data=data)
                if r.status_code == 200:
                    st.session_state.autenticado = True
                    st.session_state.usuario = r.json()["usuario"]
                    st.success("✅ Login exitoso. ¡Bienvenido!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
            except Exception as e:
                st.error("❌ Error al conectar con el backend.")
                st.code(str(e))
else:
    st.sidebar.success(f"Conectado como: {st.session_state.usuario}")
    if st.button("Cerrar sesión"):
        st.session_state.autenticado = False
        st.rerun()


    st.title("🧠 Generador de Estrategias para Negocios")

    # Generar estrategia
    sector = st.selectbox("Sector", ["Ropa", "Comida rápida", "Servicios", "Tecnología", "Otro"])
    tamano = st.selectbox("Tamaño", ["Micro", "Pequeña", "Mediana", "Grande"])
    ubicacion = st.selectbox("Ubicación", ["Lima", "Ancash", "La Libertad", "Cajamarca"])
    objetivo = st.text_area("Objetivo principal", placeholder="Ej: Aumentar ventas…")
    descripcion = st.text_input("Descripción de la empresa (opcional)", "")

    if st.button("Generar estrategia con IA"):
        if not objetivo.strip():
            st.warning("Completa al menos el objetivo.")
        else:
            payload = {
                "sector": sector,
                "tamano": tamano,
                "ubicacion": ubicacion,
                "objetivo": objetivo,
                "descripcion": descripcion,
            }
            with st.spinner("Generando…"):
                try:
                    r = requests.post(API_ESTRATEGIA, json=payload, timeout=300)
                    r.raise_for_status()
                    st.success("✅ Estrategia generada:")
                    st.text_area("Resultado:", r.json()["respuesta"], height=260)
                except requests.exceptions.RequestException as e:
                    st.error("❌ Error al conectar con el backend.")
                    st.code(str(e))

    # Consulta RAG
    st.markdown("---")
    st.subheader("📄 Consulta a partir de un documento (RAG)")

    archivo = st.file_uploader("Sube un archivo (PDF, TXT, DOCX)", type=["pdf", "txt", "docx"])
    pregunta = st.text_input("¿Qué deseas preguntarle al documento?", placeholder="Ej: ¿Qué estrategias se mencionan?")

    if st.button("Consultar documento con IA"):
        if not archivo or not pregunta.strip():
            st.warning("Por favor, sube un archivo y escribe una pregunta.")
        else:
            with st.spinner("Consultando al modelo..."):
                try:
                    respuesta = requests.post(
                        API_RAG,
                        files={"archivo": (archivo.name, archivo, archivo.type)},
                        data={"pregunta": pregunta},
                        timeout=500
                    )
                    respuesta.raise_for_status()
                    resultado = respuesta.json()["respuesta"]
                    st.success("✅ Respuesta generada con IA:")
                    st.text_area("Resultado:", resultado, height=300)
                except Exception as e:
                    st.error("❌ Hubo un error al conectar con el backend.")
                    st.code(str(e))
