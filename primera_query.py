import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import os
from dotenv import load_dotenv

MI_SERVIDOR = os.getenv("DB_SERVER")
MI_BASE_DE_DATOS = os.getenv("DB_NAME")
MI_USUARIO = os.getenv("DB_USER")
MI_CONTRASENA = os.getenv("DB_PASS")
DRIVER = os.getenv("DB_DRIVER")

DATABASE_URL = f"mssql+pyodbc://{MI_USUARIO}:{MI_CONTRASENA}@{MI_SERVIDOR}/{MI_BASE_DE_DATOS}?driver={DRIVER}"

query = """
SELECT TOP 5
    fv.Sales,
    dc.CustomerName,
    dp.ProductName
FROM
    factVentas AS fv
JOIN
    dimCustomer AS dc ON fv.CustomerID = dc.CustomerID
JOIN
    dimProduct AS dp ON fv.ProductID = dp.ProductID;
"""

print(f"Intentando conectar a '{MI_SERVIDOR}'...")

try:
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql_query(query, engine)
    print(f"¡Carga exitosa! Se han cargado {len(df)} filas en el DataFrame.")
except Exception as e:
    print(f"ERROR al cargar datos: {e}")
    df = pd.DataFrame()


df.head()