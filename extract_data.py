from sqlalchemy import create_engine
from urllib.parse import quote_plus
import pandas as pd
import os
from dotenv import load_dotenv

# --- 0. CONFIGURACIÓN ---
load_dotenv()
RUTA_CARPETA_DATOS = "data"
NOMBRE_ARCHIVO = "data_all.csv"
RUTA_COMPLETA_SALIDA = os.path.join(RUTA_CARPETA_DATOS, NOMBRE_ARCHIVO)

# --- 1. DATOS DE CONEXIÓN ---
servidor = os.getenv("MI_SERVIDOR")
base_de_datos = os.getenv("MI_BASE_DE_DATOS")
usuario = os.getenv("MI_USUARIO")
contrasena = os.getenv("MI_CONTRASENA")
driver = os.getenv("DRIVER")

if not all([servidor, base_de_datos, usuario, contrasena, driver]):
    print("ERROR: Faltan una o más variables de entorno. Revisa tu archivo .env.")
    exit()

# --- 2. CONSTRUCCIÓN DE LA URL ---
contrasena_codificada = quote_plus(contrasena)
driver_codificado = quote_plus(driver)
url = f"mssql+pyodbc://{usuario}:{contrasena_codificada}@{servidor}/{base_de_datos}?driver={driver_codificado}"

# --- 3. QUERY SQL ---
query_completa = """
SELECT
    -- Hechos
    fv.Sales,
    fv.Quantity,
    fv.Discount,
    fv.Profit,
    fv.OrderDate,
    fv.ShipDate,
    fv.ShipMode,
    fv.OrderID,
    
    -- Dimension Cliente
    dc.CustomerName,
    dc.Segment,
    
    -- Dimension Producto
    dp.ProductName,
    dp.SubCategory,
    dp.Category,
    
    -- Dimension Region
    dr.City,
    dr.States,
    dr.Region,
    dr.Country
FROM
    factVentas AS fv
JOIN
    dimCustomer AS dc ON fv.CustomerID = dc.CustomerID
JOIN
    dimProduct AS dp ON fv.ProductID = dp.ProductID
JOIN
    dimRegion AS dr ON fv.PostalCode = dr.PostalCode;
"""

print("Iniciando proceso de extracción de datos...")

# --- 4. CONEXIÓN Y EXTRACCIÓN ---
try:
    print(f"Conectando a la base de datos '{base_de_datos}' en el servidor '{servidor}'...")
    engine = create_engine(url)
    
    df = pd.read_sql_query(query_completa, engine)
    print(f"¡Carga exitosa! Se han extraído {len(df)} filas.")

    # --- 5. GUARDADO DEL DATAFRAME ---
    if not df.empty:
        
        os.makedirs(RUTA_CARPETA_DATOS, exist_ok=True)
        print(f"Asegurando que la carpeta '{RUTA_CARPETA_DATOS}' existe.")
        
        print(f"Guardando los datos en el archivo '{RUTA_COMPLETA_SALIDA}'...")
        df.to_csv(RUTA_COMPLETA_SALIDA, index=False, encoding='utf-8-sig')
        
        print("¡Proceso completado! El archivo ha sido guardado exitosamente.")
    else:
        print("El DataFrame está vacío. No se guardará ningún archivo.")

except Exception as e:
    print(f"ERROR durante el proceso: {e}")
    