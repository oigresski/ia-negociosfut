import streamlit as st
import requests

API_URL = "http://localhost:8000/generar-estrategia"

st.set_page_config(page_title="Estrategias con IA", layout="centered")
st.title("🧠 Generador de Estrategias para Negocios")

sector      = st.selectbox("Sector", ["Ropa", "Comida rápida", "Servicios", "Tecnología", "Otro"])
tamano      = st.selectbox("Tamaño", ["Micro", "Pequeña", "Mediana", "Grande"])
ubicacion   = st.selectbox("Ubicación", ["Lima", "Ancash", "La Libertad", "Cajamarca"])
objetivo    = st.text_area("Objetivo principal", placeholder="Ej: Aumentar ventas…")
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
                r = requests.post(API_URL, json=payload, timeout=300) 
                r.raise_for_status()
                st.success("✅ Estrategia generada:")
                st.text_area("Resultado:", r.json()["respuesta"], height=260)
            except requests.RequestException as e:
                st.error("❌ Error al conectar con el backend")
                st.code(str(e))
