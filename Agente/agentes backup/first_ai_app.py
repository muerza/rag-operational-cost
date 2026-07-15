import os
from dotenv import load_dotenv


import gradio as gr

from langchain_core.prompts import PromptTemplate

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain.chat_models import init_chat_model
from langchain.tools import tool

load_dotenv()

# Creamos la interfaz del LLM (Conexión y selección de modelo)
model = init_chat_model("gpt-4o-mini", model_provider="openai")

prompt_template_str = """
Tu tarea es responder las dudas sobre **{concepto}** como se relaciona con los precios del equipo_1 y del equipo_2 de esta forma:

1. Claro e intuitivo
2. Consistente (menos de 100 palabras)
3. Diseñado específicamente para una constructora

Utiliza la siguiente información sobre mí para personalizar tu explicación:

- Background: Arquitecto o ingeniero
- Enfoque profesional: Constructor con maquinaria enfocado en obra.
- Meta: Entender cómo la información puede afectar mi negocio 

La personalización debe ser sutil y natural. Evita las referencias forzadas que no aporten una mejora genuina a la comprensión.
"""


# Crear Plantilla a partir del objeto 
prompt_template = PromptTemplate.from_template(prompt_template_str)


#-----------------------------------------Funcion que genera la respuesta ------

def generate_explication(input_text):

    # Reemplazamos el texto del concepto con el tema relacionado
    prompt = prompt_template.format(concepto=input_text)

    # Mandamos la instrucción al modelo LLM
    response = model.invoke(prompt)

    # Imprimimos la respuesta 
    return response.text



demo = gr.Interface(
    fn=generate_explication,
    inputs=[gr.Textbox(label="Concepto", lines=1)],
    outputs=[gr.Textbox(label="Explicación", lines=5)],
    flagging_mode="never",
    title="Explicación de conceptos",
    description="Obtén una explicación personalizada"
)

demo.launch()
