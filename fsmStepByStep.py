from transitions import Machine

class TutorFSM:
    states = [
        "START", "SELECT_COURSE", "SELECT_TOPIC",
        "SELECT_LEVEL", "LEARNING", "QNA",
        "ADAPT_RESPONSE", "END"
    ]

    def __init__(self):
        self.context = {}
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

      if sentimiento == "negativo":
          respuesta = "Entiendo que esto puede ser confuso 🤗. " + respuesta
      elif sentimiento == "positivo":
          respuesta = "¡Genial que estés motivado! 🚀 " + respuesta

      self.resultado_qna = {
          "pregunta": pregunta,
          "sentimiento": sentimiento,
          "intension": payload.get("intencion", ""),
          "respuesta": respuesta,
          "curso": self.context["course"],
          "tema": self.context["topic"],
          "nivel": self.context["level"],
          "questionarios": "",
          "contenido": ""
       }

    def after_adapt(self):
        print("✅ Clase finalizada. ¡Buen trabajo!")
