# Caso de Negocio: Gestión de Costos Operativos en un Proyecto de Construcción

Una empresa en el sector de la construcción está en la fase de planificación de un proyecto. La empresa deberá gestionar el suministro continuo de dos tipos de equipos críticos para su operación; el costo de los equipos parece estar relacionado con el precio de algunas materias primas, algo que no se ha logrado validar estadísticamente.

## 1. Problema

La compañía, cada vez que cotiza la maquinaria para su proyecto, se ve afectada por las variaciones de los precios, ya que al no pronosticar correctamente, el precio que se paga es mayor al presupuestado.

## 2. Datos

Cuatro archivos CSV en la carpeta `Data/`.

El primero, `historico_equipos.csv`, cuenta con 6 columnas de datos históricos diarios, dando un total de 3530 filas sin datos faltantes o duplicados: `Date`, `Price_X`, `Price_Y`, `Price_Z`, `Price_Equipo1` y `Price_Equipo2`.

Series de tiempo de los precios de cada materia prima `Price_X`, `Price_Y`, `Price_Z`, con una frecuencia diaria de la variación:

- `X.csv`
- `Y.csv`
- `Z.csv`


El archivo `Y.csv` viene con un separador diferente al resto de los archivos y con un separador decimal `,` en lugar de `.`, lo cual genera un error en la importación e interpretación de los datos. `Z.csv` también tiene algunos errores, las columnas vienen invertidas. Ambos casos se corrigen al momento de la importación.

## 3. EDA

El proyecto empieza por una importación de los datos en una libreta de Jupyter Notebook (`Notebooks/eda.ipynb`), seguida de una exploración de la estructura de los datos. Iniciamos por el archivo `historico_equipos`, que nos indica que todos los datos se encuentran completos, en el formato correcto y en orden ascendente, importante al trabajar con series temporales. Continuamos por revisar las estadísticas de los datos con la función `describe`, y con un `pairplot` para ver de un vistazo cómo se distribuyen las variables y cómo se relacionan entre sí; ahí ya se nota que los precios de los equipos se mueven de forma parecida a los de algunas materias primas.

Después pasamos a cada materia prima por separado. Verificamos que las series cubren el mismo periodo que el histórico de equipos, las llevamos a una frecuencia mensual que es congruente con los tiempos de ejecución y diseño en el sector de la construccion; seguido de ello, las descomponemos con `seasonal_decompose` para separar tendencia, estacionalidad y residuales. Así verificamos cual es el movimiento general de 2010 a 2024, el comportamiento a lo largo del año, realizamos un acercamiento a un año puntual (2022) para ver el patrón de forma expandida para entender la tendencia. Para `Price_Z` probamos además medias móviles a distintas ventanas, al estilo del análisis técnico de trading y con ventanas de tiempo relevantes al giro del negocio como 3, 6 y 12 meses, para suavizar el ruido diario.

De este análisis salió la hipótesis que guía el resto del proyecto. La compañía realiza la presupuestación a inicios de año, que es justo el momento en que el precio se reduce respecto al resto del año y esa estacionalidad explicaría por qué se queda por debajo del precio que paga la compañía.

## 4. Modelos

En una segunda libreta (`Notebooks/modelos.ipynb`) empezamos por la matriz de correlaciones entre las materias primas y los equipos, logrando así validar estadísticamente la relación entre los diferentes equipos. El equipo 1 depende de `Price_Y`, y el equipo 2 de `Price_Y` y `Price_Z` .

Para proyectar el precio de las materias primas trabajamos con las series en frecuencia mensual. Antes de cualquier modelo sofisticado montamos dos modelos base para tener contra qué comparar, uno sobre la mediana y otro que repite el mes anterior. Luego probamos regresión lineal y Random Forest con variables de calendario, lags y medias móviles, y finalmente Holt-Winters (`ExponentialSmoothing` con tendencia y estacionalidad aditivas, periodo de 12 meses), que se apoya justamente en la descomposición que ya habíamos visto en el EDA y da mayor peso a las observaciones más recientes del mes. Ademas la implementación fue mucho más fácil que el resto. Fue el que se quedó para la proyección.

Para los equipos, una regresión lineal es suficiente: el equipo 1 se predice a partir de `Price_Y`, y el equipo 2 a partir de `Price_Y` y `Price_Z`. El modelo del equipo 1 quedó serializado con `joblib` en `Models/model_lr_e1` para poder reutilizarlo fuera del notebook.

## 5. API demo

Como en la vida real los precios de las materias primas vendrían de una fuente externa, montamos una API demo con FastAPI (`API/main.py`) que simula ese servicio: dos endpoints, `GET /price_y` y `GET /price_z`, que reciben un rango de fechas en formato `YYYY-MM-DD`, lo validan contra el histórico disponible y devuelven la serie filtrada.

## 6. Agente

La última pieza es un agente con LangChain (`Agente/Agent.py`). Empezamos con una primera app sencilla en Gradio (un LLM con un prompt personalizado para la constructora, que quedó guardada en `Agente/agentes backup/`) y de ahí pasamos al agente con herramientas.

El agente cuenta con dos tools que encadenan todo el flujo anterior:

- `query_proyectar_precio`: consulta el histórico de `Price_Y` a la API demo, entrena Holt-Winters y proyecta el precio a los meses que se le pidan.
- `calculate_e1_price`: toma ese precio proyectado, carga el modelo `model_lr_e1` y predice el precio del equipo 1.

Con esto se le puede preguntar al agente cuánto costará el equipo 1 dentro de N meses, y él solo resuelve la cadena API --> proyección --> predicción.

## 7. Cómo ejecutarlo

- 1. Crear el entorno e instalar dependencias
     python -m venv .venv
     .venv\Scripts\activate
     pip install -r requirements.txt

- 2. Crear un archivo .env en la raíz con la API key del LLM
     OPENAI_API_KEY=...

- 3. Levantar la API demo (desde la raíz del proyecto)
     fastapi dev API\main.py
     Disponible en http://127.0.0.1:8000

- 4. En otra terminal, correr el agente
     python Agente\Agent.py

## Estado actual y pendientes

El flujo completo ya funciona de punta a punta (datos -> EDA -> modelos -> API -> agente). Quedan pendientes que ya están marcados como TODO en el código: separar el entrenamiento de los modelos a sus propias funciones, devolver las respuestas en formato JSON con su intervalo de confianza, y terminar las funciones `train_equipo_2`, `train_equipo_1`, `predict_e2`, `price_z`(consumo de API materia prima Z) al igual que el alta de algunas herramientas para el LLM `proyectar_precio_z` para que pueda interactuar con la informacion. tambien queda pendiente la vectorizacion de los docuemtos para usarlo en RAG y la parte interactiva.
