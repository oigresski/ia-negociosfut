from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import subprocess
import os
import shutil
import sqlite3
from fastapi import Form

from transformers import pipeline
from fastapi import HTTPException

toxicity_classifier = pipeline(
    "text-classification",
    model="unitary/toxic-bert",
    truncation=True
)

BANNED_KEYWORDS = {"violencia", "odio", "insulto", "ilegal", "discriminación", "ofensivo"}
def input_guardrail(prompt: str) -> (bool, str):
    print("🛡 Ejecutando Guardrail de ENTRADA...")
    for keyword in BANNED_KEYWORDS:
        if keyword in prompt.lower():
            reason = f"El prompt contiene la palabra clave prohibida: '{keyword}'."
            print(f"🚨 ALERTA (Entrada): {reason}")
            return False, reason

    results = toxicity_classifier(prompt)
    for result in results:
        if result['label'] == 'toxic' and result['score'] > 0.8:
            reason = f"El prompt ha sido clasificado como tóxico con una confianza del {result['score']:.2f}."
            print(f"🚨 ALERTA (Entrada): {reason}")
            return False, reason

    print("✅ Guardrail de ENTRADA: El prompt es seguro.")
    return True, "El prompt es seguro."

def output_guardrail(text: str) -> (bool, str):
    print("🛡 Ejecutando Guardrail de SALIDA...")
    for keyword in BANNED_KEYWORDS:
        if keyword in text.lower():
            reason = f"La respuesta generada contiene la palabra clave prohibida: '{keyword}'."
            print(f"🚨 ALERTA (Salida): {reason}")
            return False, reason

    results = toxicity_classifier(text)
    for result in results:
        if result['label'] == 'toxic' and result['score'] > 0.8:
            reason = f"La respuesta generada ha sido clasificada como tóxica con una confianza del {result['score']:.2f}."
            print(f"🚨 ALERTA (Salida): {reason}")
            return False, reason

    print("✅ Guardrail de SALIDA: La respuesta es segura.")
    return True, "La respuesta es segura."


from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter



app = FastAPI()

# Habilita CORS para que el frontend se pueda conectar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir esto en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

# Modelo de datos que recibirá el backend
class StrategyRequest(BaseModel):
    descripcion_empresa: Optional[str] = Field("", alias="descripcion")
    sector: str
    tamano: str
    ubicacion: str
    objetivo_principal: str = Field(..., alias="objetivo")


# Función para consultar al modelo local con Ollama
def consultar_ollama(prompt: str) -> str:
    with open("temp_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    comando = ["ollama", "run", "mistral", "<", "temp_prompt.txt"]
    resultado = subprocess.run(" ".join(comando), capture_output=True, text=True, shell=True, encoding="utf-8")

    if resultado.stdout:
        return resultado.stdout.strip()
    else:
        raise RuntimeError(f"Error al ejecutar ollama:\n{resultado.stderr}")


# Ruta principal
@app.post("/generar-estrategia")
async def generar_estrategia(data: StrategyRequest):
    prompt = f"""
Eres un asesor senior en estrategias de negocios para startups.

A continuación, te presento una empresa con estas características:

Descripción de la empresa: {data.descripcion_empresa}
Sector: {data.sector}
Tamaño de la empresa: {data.tamano}
Ubicación geográfica: {data.ubicacion}
Objetivo principal: {data.objetivo_principal}

Con base en esta información, por favor responde con:
1. Tres estrategias iniciales bien definidas, accionables y alineadas al objetivo
2. Una tendencia importante en ese sector y ubicación
3. Un ejemplo de empresa similar que haya tenido éxito y por qué
4. Canales de marketing inicial recomendados para su contexto

Responde de forma profesional, concreta y útil para que puedan aplicarlo en el corto plazo.
"""

    # === GUARDRAIL DE ENTRADA ===
    is_safe, reason = input_guardrail(prompt)
    if not is_safe:
        # En lugar de lanzar error 400, devolvemos mensaje controlado
        return {"respuesta": f"⚠️ El contenido no es válido: {reason}"}

    # === GENERAR RESPUESTA CON OLLAMA ===
    respuesta = consultar_ollama(prompt)

    # === GUARDRAIL DE SALIDA ===
    is_safe, reason = output_guardrail(respuesta)
    if not is_safe:
        final_response = f"⚠️ No se puede mostrar la respuesta generada: {reason}"
    else:
        final_response = respuesta

    return {"respuesta": final_response}


@app.post("/consultar-documento")
async def consultar_documento(
    archivo: UploadFile = File(...),
    pregunta: str = Form(...)
):
    print("📁 Paso 1: recibiendo archivo...")

    # 1. Guardar archivo temporalmente
    temp_path = f"temp_docs/{archivo.filename}"
    os.makedirs("temp_docs", exist_ok=True)
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(archivo.file, buffer)

    print("✅ Archivo guardado en:", temp_path)

    # 2. Cargar texto y fragmentarlo
    loader = UnstructuredFileLoader(temp_path)
    documentos = loader.load()
    print("📄 Documento cargado y convertido")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    docs_divididos = splitter.split_documents(documentos)
    print(f"🧩 Documento dividido en {len(docs_divididos)} partes")

    # 3. Crear vectorstore
    embeddings = OllamaEmbeddings(model="llama3")
    db = Chroma.from_documents(docs_divididos, embeddings)
    print("📦 Embeddings generados y vectorstore creado")

    # 4. Recuperar contexto
    resultados = db.similarity_search(pregunta, k=3)
    contexto = "\n".join([r.page_content for r in resultados])
    print("🔎 Contexto más relevante recuperado")

    # 5. Generar respuesta
    prompt = f"""Usa el siguiente contexto para responder...

    Contexto:
    {contexto}

    Pregunta:
    {pregunta}
    """

    respuesta = consultar_ollama(prompt)
    print("✅ Respuesta generada")

    os.remove(temp_path)
    print("🧹 Archivo temporal eliminado")

    return {"respuesta": respuesta}
# Aquí comienza tu nueva ruta de login
@app.post("/login")
async def login(usuario: str = Form(...), contrasena: str = Form(...)):
    cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND contraseña=?", (usuario, contrasena))
    user = cursor.fetchone()
    if user:
        return {"mensaje": "Login exitoso", "usuario": usuario}
    else:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")


