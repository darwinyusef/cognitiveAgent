from transitions import Machine

class TutorFSM:
    states = [
        "START", "SELECT_COURSE", "SELECT_TOPIC",
        "SELECT_LEVEL", "LEARNING", "QNA",
        "ADAPT_RESPONSE", "END"
    ]

    def __init__(self):
        self.context = {}
        self.prompt = ""
        self.resultado_qna = None
        self.machine = Machine(model=self, states=TutorFSM.states, initial="START")

        # Transiciones
        self.machine.add_transition(trigger="begin", source="START", dest="SELECT_COURSE", after="after_start")
        self.machine.add_transition(trigger="answer_course", source="SELECT_COURSE", dest="SELECT_TOPIC", after="after_select_course")
        self.machine.add_transition(trigger="answer_topic", source="SELECT_TOPIC", dest="SELECT_LEVEL", after="after_select_topic")
        self.machine.add_transition(trigger="answer_level", source="SELECT_LEVEL", dest="LEARNING", after="after_select_level")
        self.machine.add_transition(trigger="continue_learning", source="LEARNING", dest="QNA", after="after_learning")
        self.machine.add_transition(trigger="question", source="QNA", dest="ADAPT_RESPONSE", after="after_qna")
        self.machine.add_transition(trigger="continue_adapt", source="ADAPT_RESPONSE", dest="END", after="after_adapt")

    # --- Acciones después de transiciones ---
    def after_start(self):
        print("👋 Bienvenido al tutor inteligente. ¿Qué curso quieres iniciar? (Python / JavaScript)")

    def after_select_course(self, payload):
        course = payload.get("course", "").lower()
        self.context["course"] = course
        if course == "python":
            print("Has elegido Python 🐍. Temas disponibles: Funciones, Listas, Bucles.")
        else:
            print(f"Has elegido {course}. Temas próximamente.")

    def after_select_topic(self, payload):
        topic = payload.get("topic", "")
        self.context["topic"] = topic
        print(f"Perfecto, tema {topic}. Elige nivel: Bajo / Medio / Alto.")

    def after_select_level(self, payload):
        level = payload.get("level", "")
        self.context["level"] = level
        print(f"🔎 Iniciando curso de {self.context['course']} sobre {self.context['topic']} en nivel {level}...")

    def after_learning(self):
        print("📚 Aquí tienes el contenido. Ahora puedes hacer preguntas.")

    def after_qna(self, payload):
        pregunta = payload.get("question", "")
        respuesta = payload.get("respuesta", "")
        sentimiento = payload.get("sentimiento", "neutral")
        intension = payload.get("intension", "")

        if sentimiento == "negativo":
            respuesta = "Entiendo que esto puede ser confuso 🤗. " + respuesta
        elif sentimiento == "positivo":
            respuesta = "¡Genial que estés motivado! 🚀 " + respuesta

        # Guardamos prompt generado
        prompt_generado = self.generar_prompt_agente(intension)

        self.resultado_qna = {
            "pregunta": pregunta,
            "sentimiento": sentimiento,
            "intension": intension,
            "respuestaIA": respuesta,
            "curso": self.context["course"],
            "tema": self.context["topic"],
            "nivel": self.context["level"],
            "respuestaAgent": "",
            "questionarios": "",
            "contenido": "",
            "prompt": prompt_generado
        }

        print("🧠 Prompt generado para agente:\n", prompt_generado)

    def generar_prompt_agente(self, intension):
        curso = self.context.get("course", "")
        tema = self.context.get("topic", "")
        nivel = self.context.get("level", "")

        if intension.lower() == "definicion":
            prompt = f"""
Crea un taller de {curso} usando el tema de {tema} con temáticas de nivel {nivel.lower()}.
Incluye contenido explicativo claro, ejemplos funcionales y crea dos preguntas relacionadas al tema que puedan añadirse en la sección de "cuestionarios".
"""
        elif intension.lower() == "uso práctico":
            prompt = f"""
Proporciona un ejemplo claro y funcional sobre el tema de {tema} en {curso}, adaptado a un nivel {nivel.lower()}.
Agrega también una breve explicación del código para que sea entendible.
"""
        elif intension.lower() == "ejercicio":
            prompt = f"""
Diseña un ejercicio práctico sobre {tema} en {curso} para nivel {nivel.lower()}.
Incluye el enunciado del ejercicio, posibles pistas, y una solución comentada.
"""
        else:
            prompt = f"""
Crea contenido educativo adaptado a un curso de {curso}, tema: {tema}, nivel: {nivel.lower()}.
Incluye una pequeña introducción, ejemplos y un par de preguntas para reforzar el aprendizaje.
"""

        self.prompt = prompt.strip()
        return self.prompt

    def after_adapt(self):
        print("✅ Clase finalizada. ¡Buen trabajo!")
