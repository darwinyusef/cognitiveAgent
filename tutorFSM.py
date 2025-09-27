from transitions import Machine
from pydantic import BaseModel
from typing import Optional, Dict, Union
from copy import deepcopy

class TutorTypo(BaseModel):
    pregunta: str
    sentimiento: str
    intension: str
    respuestaIA: str
    curso: str
    tema: str
    nivel: str
    prompt: str
    respuestaAgent: Optional[str] = ""
    questionarios: Optional[str] = ""
    contenido: Optional[str] = ""

class TutorFSM:
    def __init__(self):
        self.data = {
            "pregunta": "",
            "sentimiento": "",
            "intension": "",
            "respuestaIA": "",
            "curso": "",
            "tema": "",
            "nivel": "",
            "prompt": "",
            "respuestaAgent": "",
            "questionarios": "",
            "contenido": ""
        }

        states = [
            "start",
            "course_selected",
            "topic_selected",
            "level_selected",
            "prompt_generated",
            "ready_for_learning",
            "question_asked",
            "completed"
        ]

        transitions = [
            {"trigger": "begin", "source": "start", "dest": "course_selected"},
            {"trigger": "answer_course", "source": "course_selected", "dest": "topic_selected", "after": "set_course"},
            {"trigger": "answer_topic", "source": "topic_selected", "dest": "level_selected", "after": "set_topic"},
            {"trigger": "answer_level", "source": "level_selected", "dest": "prompt_generated", "after": "set_level"},
            # <-- triggers renamed to avoid collision with method names:
            {"trigger": "generar_prompt", "source": "prompt_generated", "dest": "ready_for_learning", "after": "generar_prompt_agente"},
            {"trigger": "start_learning", "source": "ready_for_learning", "dest": "question_asked", "after": "continue_learning"},
            {"trigger": "question", "source": "question_asked", "dest": "completed", "after": "set_question"},
        ]

        self.machine = Machine(model=self, states=states, transitions=transitions, initial="start")

    def set_course(self, payload: Dict):
        self.data["curso"] = payload.get("course", "")

    def set_topic(self, payload: Dict):
        self.data["tema"] = payload.get("topic", "")

    def set_level(self, payload: Dict):
        self.data["nivel"] = payload.get("level", "")

    # callback name kept, but trigger is different ("generar_prompt")
    def generar_prompt_agente(self, payload: Dict):
        intencion = payload.get("intencion", "")
        curso = self.data.get("curso", "")
        tema = self.data.get("tema", "")
        nivel = self.data.get("nivel", "")
        prompt = (
            f"Eres un tutor de {curso}. El usuario quiere aprender sobre {tema} "
            f"en un nivel {nivel}. La intención es '{intencion}'. "
            f"Genera una respuesta adecuada."
        )
        self.data["prompt"] = prompt

    # callback name kept, trigger is "start_learning"
    def continue_learning(self, payload: Dict = None):
        # lógica extra opcional
        return

    def set_question(self, payload: Dict):
        self.data["intension"] = payload.get("intencion", "")
        self.data["pregunta"] = payload.get("question", "")
        self.data["sentimiento"] = payload.get("sentimiento", "")
        self.data["respuestaIA"] = "¡Genial que estés motivado! 🚀"
        self.data["respuestaAgent"] = ""
        self.data["questionarios"] = ""
        self.data["contenido"] = ""

    @property
    def resultado_qna(self) -> TutorTypo:
        return TutorTypo(**deepcopy(self.data))
