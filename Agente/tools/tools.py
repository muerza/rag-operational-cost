from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import joblib

from statsmodels.tsa.holtwinters import ExponentialSmoothing


from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, root_mean_squared_error


import requests

FOLDER = Path.cwd()

RANDOM_STATE = 484616

# Desde:  1. rag-operational-cost>
# Usar fastapi dev API\main.py para simular las APIs

PRICE_Y_API_URL = 'http://127.0.0.1:8000/price_y'

PRICE_Z_API_URL = 'http://127.0.0.1:8000/price_z'


# ------------------------------------------------------------------ API -----------

def price_y(fecha_inicial: str, fecha_final: str, price_url: str):
    '''API DEMO para conocer el precio de la materia prima Price_Y,
    Basada en el archivo Y.csv debe tener formato '%Y-%m-%d' '''

    response = requests.get(
        f"{price_url}/",
        params={"fecha_inicial": fecha_inicial, "fecha_final": fecha_final}
    )

    historic_price_y = response.json()

    if not historic_price_y:
        return "No existen datos con esas fechas"

    return pd.DataFrame(historic_price_y)


#precio_historico = price_y("2010-01-01", "2023-01-31")

#print(precio_historico)


# ----------------------------------------------------------- Proyectar_precio -----


def proyectar_precio(dataset_m_prima, col_objetivo: str, meses_a_proyectar: int = 6):
    '''Función para entrenar el modelo a partir de un data set nuevo '''

    dataset_materia_prima = dataset_m_prima.copy()
    dataset_materia_prima.index = pd.to_datetime(dataset_materia_prima.index)
    dataset_materia_prima = dataset_materia_prima.sort_index()
    dataset_materia_prima = dataset_materia_prima.resample('ME').mean()

    # max_lag= 12 para capturar los movimientos durante el año

    serie_temporal = dataset_materia_prima[col_objetivo].dropna()

    modelo_hw = ExponentialSmoothing(
        serie_temporal, trend='add', seasonal='add', seasonal_periods=12)

    modelo_hw_train = modelo_hw.fit()
    # TODO Crear funcion separada de entrenamiento
    # modelo_hw_train = joblib.dump(FOLDER/'Models/modelo_hw_train')
    proyeccion = modelo_hw_train.forecast(meses_a_proyectar)

    return proyeccion


# proyeccion = proyectar_precio(
    #dataset_m_prima=precio_historico, col_objetivo="Price", meses_a_proyectar=6)

#print(proyeccion)

# --------------------------------------------------------------- Equipo 1 --------


def predict_e1(precio):
    '''Función para predecir el precio del equipo 1 en función del 
    Precio de la materia prima Price_Y'''

    precio_y = pd.DataFrame([precio], columns=['Price_Y'])

    model_lr_e1 = joblib.load(FOLDER/'Models/model_lr_e1')
    e1_pred = model_lr_e1.predict(precio_y)
    # TODO Dar formato JSON
    # retornar intervalo de confianza

    return e1_pred[0]


# ultimo_precio_proyectado = proyeccion.iloc[-1]

# print(predict_e1(ultimo_precio_proyectado))


# ----------------------------------------------------------- Entrenar el modelo E1 -----PENDIENTE


def train_equipo_1(equipo_1_data):
    ''' Función para entrenar el modelo a partir de un data set nuevo 
        a partir del dataset de Price_Z '''

    # TODO  Crear una sola funcion de entrenamiento
    price_y
    train_e1, test_e1 = train_test_split(
        equipo_1_data, test_size=0.2, random_state=RANDOM_STATE)
    features_train_e1 = train_e1.drop('Price_Equipo1', axis=1)
    target_train_e1 = train_e1['Price_Equipo1']
    features_test_e1 = test_e1.drop('Price_Equipo1', axis=1)
    target_test_e1 = test_e1['Price_Equipo1']

    model_lr_e1 = joblib.load(FOLDER/'Models/model_lr_e1')
    model_lr_e1 = LinearRegression()

    model_lr_e1.fit(features_train_e1, target_train_e1)

    predictions_e1 = model_lr_e1.predict(features_test_e1)

    r2 = r2_score(target_test_e1, predictions_e1)

    # TODO Dar formato JSON
    # retornar r2

    return f'Modelo entrenado R2: {r2}'


# TODO - TEMPORAL Separar a nuevo archivo funciones no relacionadas con el Agente
