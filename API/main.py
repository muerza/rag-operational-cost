
import pandas as pd
from pathlib import Path
from fastapi import FastAPI

FOLDER = Path.cwd()
DATA_RUTE = FOLDER / 'Data'

# Warning por errores en el formato del csv
data_y = pd.read_csv(DATA_RUTE / 'Y.csv', index_col=[0], parse_dates=[0], dayfirst=True, sep=';', decimal=',')
data_y.sort_index(inplace=True)
data_y.resample('ME')

# Las columnas estan invertidas
data_z = pd.read_csv(DATA_RUTE / 'Z.csv', index_col='Date', parse_dates=['Date'])
data_z.sort_index(inplace=True)
data_z.resample('ME')

app = FastAPI()

FORMATO_FECHA = '%Y-%m-%d'

@app.get('/price_y')
def datos_price_y(fecha_inicial, fecha_final):
    
    try: 
         inicio_rango = pd.to_datetime(fecha_inicial, format=FORMATO_FECHA)
         final_rango = pd.to_datetime(fecha_final, format=FORMATO_FECHA)
        
    except ValueError:
        return {"error": f"Formato inválido utiliza {FORMATO_FECHA}"}
        

    if inicio_rango < data_y.index.min() or final_rango > data_y.index.max():
        
        rango_min = pd.to_datetime(data_y.index.min()).strftime(FORMATO_FECHA)
        rango_max = pd.to_datetime(data_y.index.max()).strftime(FORMATO_FECHA)
        
        return ({f'Error en el rango de fechas {rango_min} a {rango_max}'})
    
    return data_y[fecha_inicial:fecha_final]

@app.get('/price_z')
def datos_price_z(fecha_inicial, fecha_final):
    
    try: 
         inicio_rango = pd.to_datetime(fecha_inicial, format=FORMATO_FECHA)
         final_rango = pd.to_datetime(fecha_final, format=FORMATO_FECHA)
        
    except ValueError:
        return {"error": f"Formato inválido utiliza {FORMATO_FECHA}"}
        

    if inicio_rango < data_z.index.min() or final_rango > data_z.index.max():
        
        rango_min = pd.to_datetime(data_z.index.min()).strftime(FORMATO_FECHA)
        rango_max = pd.to_datetime(data_z.index.max()).strftime(FORMATO_FECHA)
        
        return ({f'Error en el rango de fechas {rango_min} a {rango_max}'})
    
    return data_z[fecha_inicial:fecha_final]
