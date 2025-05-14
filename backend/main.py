from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import subprocess
from typing import Optional

app = FastAPI()

# Habilita CORS para que el frontend se pueda conectar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringir esto en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos que recibirá el backend
class StrategyRequest(BaseModel):
    descripcion_empresa: Optional[str] = Field("", alias="descripcion")
    sector: str
    tamano: str
    ubicacion: str
    objetivo_principal: str = Field(..., alias="objetivo")


# Función para consultar al modelo local con Ollama
def consultar_ollama(prompt: str) -> str:
    comando = ["ollama", "run", "llama3", prompt]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    return resultado.stdout.strip()

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
    respuesta = consultar_ollama(prompt)
    return {"respuesta": respuesta}
