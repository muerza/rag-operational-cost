
import pandas as pd
import requests
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain.agents import create_agent
import gradio as gr
from tools.tools import price_y, proyectar_precio, predict_e1, PRICE_Y_API_URL
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()


FOLDER = Path.cwd()

RANDOM_STATE = 484616

# Desde:  1. rag-operational-cost>
# Usar fastapi dev API\main.py para simular las APIs



def check_weather(location: str) -> str:
    '''Return the weather forecast for the specified location.'''
    return f"It's always sunny in {location}"

graph = create_agent(
    model="anthropic:claude-sonnet-4-5-20250929",
    tools=[check_weather],
    system_prompt="You are a helpful assistant",
)

@tool
def query_proyectar_precio(fecha_inicial: str, fecha_final: str, meses_a_proyectar: int = 6):
    """Proyecta el precio futuro de la materia prima Price_Y.

    Args:
        fecha_inicial: Fecha inicial del histórico en formato YYYY-MM-DD.
        fecha_final: Fecha final del histórico en formato YYYY-MM-DD.
        meses_a_proyectar: Cantidad de meses que se desean proyectar.

    Returns:
        Proyección mensual del precio de Price_Y.
    """

    precio_historico = price_y(fecha_inicial=fecha_inicial, fecha_final=fecha_final, price_url=PRICE_Y_API_URL)

    proyeccion = proyectar_precio(dataset_m_prima=precio_historico,col_objetivo="Price", meses_a_proyectar=meses_a_proyectar)


    return proyeccion.iloc[-1]


# al cambiar a @tool necesitamos un diccionario para utilizar invoke 

precio=(
    query_proyectar_precio.invoke(
        {'fecha_inicial': "2010-01-01", 'fecha_final': "2023-01-31", 'meses_a_proyectar':' 6'}
    )
)

@tool
def calculate_e1_price(precio_y: float):
    """Calcula el precio futuro equipo_1 a partir de Price_Y.

    Args:
        precio_y: Precio proyectado a meses a futuro de materia prima Price_Y.
        
    Returns:
        Predicción del precio de equipo_1.
    """

    resultado = predict_e1(precio_y)

    return resultado

print(
    calculate_e1_price.invoke(
        {'precio_y': f"{precio}"}
    )
)
