

from sqlalchemy import create_engine
import pandas as pd
import os  
from dotenv import load_dotenv  

# --- 1.DATOS DE CONEXIÓN LOCAL
servidor = os.getenv("MI_SERVIDOR")
base_de_datos = os.getenv("MI_BASE_DE_DATOS")
usuario = os.getenv("MI_USUARIO")
contrasena = os.getenv("MI_CONTRASENA")
driver = os.getenv("DRIVER")

url = f"mssql+pyodbc://{MI_USUARIO}:{MI_CONTRASENA}@{MI_SERVIDOR}/{MI_BASE_DE_DATOS}?driver={DRIVER}"

query_de_prueba = """
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
    # EL PASO CLAVE: Creamos el DataFrame 'df' que usaremos en toda la app
    df = pd.read_sql_query(query_de_prueba, engine)
    print(f"¡Carga exitosa! Se han cargado {len(df)} filas en el DataFrame.")
except Exception as e:
    print(f"ERROR al cargar datos: {e}")
    # Si hay un error, creamos un df vacío para que la app no se rompa
    df = pd.DataFrame()


df.head()