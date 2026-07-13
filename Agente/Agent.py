
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain.chat_models import init_chat_model
from langchain.tools import tool

import requests 

# Desde:  1. rag-operational-cost>
# Usar fastapi dev API\main.py para simular las APIs 

PRICE_Y_API_ULR = 'http://127.0.0.1:8000/price_y'

PRICE_Z_API_ULR = 'http://127.0.0.1:8000/price_z'

##------------------------------------------------------ API -----------

def price_y (fecha_inicial, fecha_final):
    '''Calcular el precio del equipo uno en bace 
       a el precio proyectado de la materia prima Price_Z'''
    
    response = requests.get(
        f"{PRICE_Y_API_ULR}/",
        params={"fecha_inicial": fecha_inicial, "fecha_final": fecha_final}
    )

    historic_price_y = response.json()

    return pd.DataFrame(historic_price_y)

print((price_y('2010-01-01','2023-01-31')).head())
    
