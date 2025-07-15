

/*1. Análisis de Descuentos y Rentabilidad por Sub-Categoría
Pregunta de Negocio: Queremos entender la relación entre los descuentos que ofrecemos y la rentabilidad. 
Para cada sub-categoría de producto, calcula el descuento promedio aplicado y el beneficio promedio por venta. 
Ordena los resultados para ver primero las sub-categorías con el mayor descuento promedio.
.*/

SELECT
    fv.ShipMode,
    SUM(fv.Sales) AS Total_Ventas_2017
FROM 
    factVentas AS fv
WHERE 
    YEAR(fv.OrderDate) = 2017
GROUP BY 
    fv.ShipMode
ORDER BY
    Total_Ventas_2017 DESC;

/*2. Rendimiento de Ventas en un Año Específico
Pregunta de Negocio: El equipo de dirección quiere un informe detallado de las ventas del año 2017. 
Filtra todas las ventas que ocurrieron en ese año y luego muestra el total de ingresos por cada ShipMode (Modo de envío) durante ese período.
.*/

SELECT
    ShipMode,
    SUM(Sales) AS Total_Ventas_2017
FROM 
    factVentas
WHERE 
    YEAR(OrderDate) = 2017 
GROUP BY 
    ShipMode
ORDER BY
    Total_Ventas_2017 DESC;


/*3. Identificación de Clientes de Alto Valor en una Región Específica
Pregunta de Negocio: El equipo de marketing de la región 'Central' quiere lanzar una campaña de fidelización. 
Necesitan una lista de los 5 mejores clientes de esa región, basada en el total de sus compras. Para cada cliente, muestra su nombre y el total gastado.*/

SELECT TOP 5
    dc.CustomerName,
    SUM(fv.Sales) AS Total_Gastado
FROM 
    factVentas AS fv
JOIN 
    dimCustomer AS dc ON fv.CustomerID = dc.CustomerID
JOIN 
    dimRegion AS dr ON fv.PostalCode = dr.PostalCode
WHERE 
    dr.Region = 'Central'
GROUP BY 
    dc.CustomerName
ORDER BY 
    Total_Gastado DESC;

/*4.Pregunta de Negocio: ¿Qué segmento nos genera más ingresos, el corporativo o el de consumidores? Muestra los ingresos totales para solo esos dos segmentos.*/

SELECT
    dc.Segment,
    SUM(fv.Sales) AS Total_Ingresos
FROM
    factVentas AS fv
JOIN
    dimCustomer AS dc ON fv.CustomerID = dc.CustomerID
WHERE
    dc.Segment IN ('Corporate', 'Consumer')
GROUP BY
    dc.Segment;