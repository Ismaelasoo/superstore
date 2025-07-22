
-- Dataset Plano

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


SELECT distinct states
FROM dimRegion