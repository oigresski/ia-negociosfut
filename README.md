# Generador de Estrategias con IA Local

Proyecto desarrollado para el curso AD5018 – Inteligencia Artificial para Negocios.

Esta aplicación permite generar estrategias empresariales personalizadas usando un modelo de lenguaje local (`llama3`) ejecutado con Ollama, junto con un backend FastAPI y una interfaz frontend en Streamlit.

## 🛠️ Tecnologías utilizadas

- 🧠 Ollama + llama3 (modelo local)
- 🚀 FastAPI (backend)
- 🎛️ Streamlit (frontend)
- 🐍 Python 3.11

## 📦 Estructura del proyecto

ia-estrategias/
├─ frontend/ → app.py (Streamlit)
├─ backend/ → main.py (FastAPI)
└─ README.md



## 💡 ¿Cómo ejecutarlo?

### 1. Iniciar backend

cd backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000
2. Iniciar frontend

cd frontend
.\.venv\Scripts\Activate.ps1
streamlit run app.py
3. Consultar modelo local
La app interactúa con llama3 vía Ollama:



ollama pull llama3
🔐 Privacidad
Toda la ejecución es local: no se almacenan datos ni se envía información a la nube.





git add README.md
git commit -m "Agrego README al proyecto"
git push
✅ 3. ¿Qué más puedes agregar?
Elemento	¿Lo necesitas?	Te lo armo
✅ Logo o imagen para portada de informe	Si quieres algo más visual	🎨 Sí
✅ Código QR del GitHub para la presentación	Para insertarlo en la PPT o Word	📎 Sí
✅ Mini pitch o guion para tu video demo	Si necesitas grabarlo	🎤 Sí
