--------Events table----------------
CREATE TABLE
IF NOT EXISTS Events
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

--- Materials Table
CREATE TABLE IF NOT EXISTS Materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    Category TEXT NOT NULL,
    Weight REAL NOT NULL,
    Quantity REAL NOT NULL,
    Emission REAL NOT NULL,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event) REFERENCES Events(name) ON UPDATE CASCADE
);

-- Transport Emissions Table
CREATE TABLE IF NOT EXISTS TransportEmissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    Mode TEXT NOT NULL,
    Vehicle TEXT NOT NULL,
    WeightOrDistance REAL NOT NULL,
    Emission REAL NOT NULL,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event) REFERENCES Events(name) ON UPDATE CASCADE
    
);

-- Electric Vehicles Consumption Table
CREATE TABLE IF NOT EXISTS ElectricConsumption (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    Vehicle TEXT NOT NULL,
    ConsumptionPerKm REAL NOT NULL,  -- kWh per km
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event) REFERENCES Events(name) ON UPDATE CASCADE
);

-- Electricity Emissions Table
CREATE TABLE IF NOT EXISTS ElectricityEmissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    Usage TEXT NOT NULL,  -- Type of electricity use (e.g., Lighting, Cooling, Heating)
    Value REAL NOT NULL,  -- Consumption in kWh
    Emission REAL NOT NULL,  -- Emissions in kg CO₂
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event) REFERENCES Events(name) ON UPDATE CASCADE
);


-- HVAC Emissions Table
CREATE TABLE IF NOT EXISTS HVACEmissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    Refrigerant TEXT NOT NULL,
    MassLeak REAL NOT NULL,
    Emission REAL NOT NULL,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event) REFERENCES Events(name) ON UPDATE CASCADE
);



-- Food Emissions Table
CREATE TABLE IF NOT EXISTS FoodItemsEmissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    food_items TEXT NOT NULL,
    quantity REAL NOT NULL,  -- Quantity in kg
    emission REAL NOT NULL,  -- Emissions in kg CO₂
    total_emission REAL NOT NULL,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event) REFERENCES Events(name) ON UPDATE CASCADE
);

-- Food Items Table
CREATE TABLE IF NOT EXISTS FoodItems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    FoodItem TEXT NOT NULL,
    Quantity REAL NOT NULL,
    Emission REAL NOT NULL,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event) REFERENCES Events(name) ON UPDATE CASCADE
);

-- Scope 1 Table
CREATE TABLE IF NOT EXISTS Scope1 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    fuels TEXT NOT NULL,  -- Store multiple fuel types as JSON
    consumptions TEXT NOT NULL,  -- Store multiple consumption values as JSON
    emissions TEXT NOT NULL,  -- Store multiple emissions as JSON
    total_emission REAL NOT NULL,  -- Store total emission
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event) REFERENCES Events(name) ON UPDATE CASCADE
);

-- Master Emissions Table
CREATE TABLE IF NOT EXISTS MasterEmissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    SourceTable TEXT NOT NULL,
    Category TEXT NOT NULL,
    Event TEXT NOT NULL,
    Description TEXT NOT NULL,
    Quantity REAL NOT NULL,
    Weight REAL NOT NULL,
    Emission REAL NOT NULL,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Trigger for Materials Emissions
CREATE TRIGGER IF NOT EXISTS Insert_MaterialsEmissions 
AFTER INSERT ON Materials
BEGIN
    INSERT INTO MasterEmissions 
        (SourceTable, Category, Event, Description, Quantity, Weight, Emission, Timestamp)
    VALUES 
        ('Materials', 'Scope3', NEW.event, NEW.Category, NEW.Quantity, NEW.Weight, NEW.Emission, CURRENT_TIMESTAMP);
END;

-- Trigger for electricity consumption
CREATE TRIGGER IF NOT EXISTS Insert_ElectricConsumption 
AFTER INSERT ON ElectricConsumption
BEGIN
    INSERT INTO MasterEmissions 
        (SourceTable, Category, Event, Description, Quantity, Weight, Emission, Timestamp)
    VALUES 
        ('ElectricConsumption', 'Scope2', NEW.Event, NEW.Vehicle, NEW.ConsumptionPerKm, 0, 0, CURRENT_TIMESTAMP);
END;


-- Trigger for electricity emission
CREATE TRIGGER IF NOT EXISTS Insert_ElectricityEmissions 
AFTER INSERT ON ElectricityEmissions
BEGIN
    INSERT INTO MasterEmissions 
        (SourceTable, Category, Event, Description, Quantity, Weight, Emission, Timestamp)
    VALUES 
        ('ElectricityEmissions', 'Scope2', NEW.event, NEW.Usage, NEW.Value, 0, NEW.Emission, CURRENT_TIMESTAMP);
END;

-- Trigger for HVAC emissions table
CREATE TRIGGER IF NOT EXISTS Insert_HVACEmissions 
AFTER INSERT ON HVACEmissions
BEGIN
    INSERT INTO MasterEmissions 
        (SourceTable, Category, Event, Description, Quantity, Weight, Emission, Timestamp)
    VALUES 
        ('HVACEmissions', 'Scope2', NEW.event, NEW.Refrigerant, NEW.MassLeak, 0, NEW.Emission, CURRENT_TIMESTAMP);
END;



-- Trigger for FoodItems
CREATE TRIGGER IF NOT EXISTS Insert_FoodItems 
AFTER INSERT ON FoodItems
BEGIN
    INSERT INTO MasterEmissions 
        (SourceTable, Category, Event, Description, Quantity, Weight, Emission, Timestamp)
    VALUES 
        ('FoodItems', 'Scope3', NEW.event, NEW.FoodItem, NEW.Quantity, 0, NEW.Emission, CURRENT_TIMESTAMP);
END;



-- Insert from Scope1 table
CREATE TRIGGER IF NOT EXISTS Insert_Scope1 
AFTER INSERT ON Scope1
BEGIN
    INSERT INTO MasterEmissions (SourceTable, Category, Event, Description, Quantity, Weight, Emission, Timestamp)
    SELECT 
        'Scope1', 
        'Scope1', 
        NEW.event, 
        fuels.value, 
        consumptions.value, 
        0, 
        emissions.value, 
        CURRENT_TIMESTAMP
    FROM json_each(NEW.fuels) AS fuels
    JOIN json_each(NEW.consumptions) AS consumptions ON fuels.key = consumptions.key
    JOIN json_each(NEW.emissions) AS emissions ON fuels.key = emissions.key;
END;

-- Trigger for food item emission (Individual food items)
CREATE TRIGGER IF NOT EXISTS Insert_FoodItemsEmissions 
AFTER INSERT ON FoodItemsEmissions
BEGIN
    INSERT INTO MasterEmissions 
        (SourceTable, Category, Event, Description, Quantity, Weight, Emission, Timestamp)
        SELECT
        'FoodItemsEmissions',
        'Scope3',
        NEW.event, 
        NEW.food_items, 
        NEW.quantity, 
        0, 
        NEW.emission, 
        CURRENT_TIMESTAMP
    FROM json_each(NEW.food_items) AS food_items
    JOIN json_each(NEW.quantity) AS quantity ON food_items.key = quantity.key
    JOIN json_each(NEW.emissions) AS emissions ON food_items.key = emissions.key;

END;

