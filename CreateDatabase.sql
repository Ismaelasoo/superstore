


USE superstore_db;
GO

CREATE TABLE factVentas (
    RowID INT PRIMARY KEY,
    OrderID VARCHAR(20),
    OrderDate DATE,
    ShipDate DATE,
    ShipMode VARCHAR(50),
    CustomerID VARCHAR(20),
    PostalCode VARCHAR(10),
    ProductID VARCHAR(25),
    Sales DECIMAL(10, 2),
    Quantity INT,
    Discount DECIMAL(4, 2),
    Profit DECIMAL(10, 4)
);

CREATE TABLE dimRegion (
    PostalCode VARCHAR(10) PRIMARY KEY,
    City VARCHAR(100),
    States VARCHAR(100),
    Region VARCHAR(50),
    Country VARCHAR(100)
);

CREATE TABLE dimProduct (
    ProductID VARCHAR(25) PRIMARY KEY,
    ProductName VARCHAR(255),
    SubCategory VARCHAR(100),
    Category VARCHAR(100)
);

CREATE TABLE dimCustomer (
    CustomerID VARCHAR(20) PRIMARY KEY,
    CustomerName VARCHAR(100),
    Segment VARCHAR(50)
);


