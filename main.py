from typing import Optional, Union
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.train_sentiments import predict_sentiment
from tutorFSM import TutorFSM
import joblib

from dotenv import load_dotenv
import os

app = FastAPI(title="Tutor FSM API")

# Cargar variables desde .env
load_dotenv()

# Acceder a las variables
APP_NAME = os.getenv("APP_NAME")

@app.get("/", tags=["Questions"])
def read_root():
    return {
        "app_name": f"Bienvenidos al nuestro {APP_NAME}",
    }

class QnaRequest(BaseModel):
    pregunta: Optional[str] = ""
    sentimiento: Optional[str] = ""
    intension: Optional[str] = ""
    respuestaIA: Optional[str] = ""
    curso: Optional[str] = ""
    tema: Optional[str] = ""
    nivel: Optional[str] = ""
    prompt: Optional[str] = ""
    respuestaAgent: Optional[str] = ""
    questionarios: Optional[str] = ""
    contenido: Optional[str] = ""
    
def intension(pregunta):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    modelo_path = os.path.join(BASE_DIR, "train2", "modelo_intencion.pkl")
    modelo_path = os.path.normpath(modelo_path)  
    clf = joblib.load("/train2/modelo_intencion.pkl")
    intencion_predicha = clf.predict([pregunta])[0]
    print(f"Intención detectada: {intencion_predicha}")
    return intencion_predicha


async def sentimiento(pregunta):
    sentimiento, conf = await predict_sentiment(pregunta)
    print(f"Pregunta: {pregunta}")
    print(f"→ Sentimiento detectado: {sentimiento} (conf={conf:.2f})")
    return sentimiento

@app.post("/questions", response_model=QnaRequest, tags=["Questions"])
def process_qna(payload: QnaRequest):
    
    
    if not payload.curso:
        raise HTTPException(status_code=422, detail="Campo 'curso' requerido.")
    if not payload.tema:
        raise HTTPException(status_code=422, detail="Campo 'tema' requerido.")
    if not payload.nivel:
        raise HTTPException(status_code=422, detail="Campo 'nivel' requerido.")
    if not payload.pregunta:
        raise HTTPException(status_code=422, detail="Campo 'pregunta' requerido.")
    
    status = {
        "intencion": intension(pregunta=payload.pregunta), 
        "sentimiento": sentimiento(pregunta=payload.pregunta)
    }

    fsm = TutorFSM()
    try:
        fsm.begin()
        fsm.answer_course({"course": payload.curso})
        fsm.answer_topic({"topic": payload.tema})
        fsm.answer_level({"level": payload.nivel})
        fsm.generar_prompt({"intencion": status["intencion"] | "aprender"})
        fsm.start_learning()
        fsm.question({
            "intencion": status["intencion"] | "aprender",
            "question": payload.pregunta,
            "sentimiento": status["sentimiento"] | "positivo"
        })
        final_result = fsm.resultado_qna.model_dump()

        return final_result

    except Exception as e:
        # captura errores de transición u otros
        raise HTTPException(status_code=500, detail=f"Error ejecutando FSM: {str(e)}")