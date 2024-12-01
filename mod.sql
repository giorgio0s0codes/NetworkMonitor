drop DATABASE if exists productosBake;
CREATE DATABASE productosBake;

CREATE TABLE buildings (
    id INT AUTO_INCREMENT PRIMARY KEY,       -- Unique identifier for each building
    name VARCHAR(255) NOT NULL,              -- Name of the building
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP -- Timestamp for when the record was created
);

CREATE TABLE speed_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,       -- Unique identifier for each log entry
    building_id INT NOT NULL,                -- Foreign key referencing the building
    timestamp DATETIME NOT NULL,             -- Date and time of the log entry
    download_speed FLOAT NOT NULL,           -- Download speed
    upload_speed FLOAT NOT NULL,             -- Upload speed
    FOREIGN KEY (building_id) REFERENCES buildings(id) 
        ON DELETE CASCADE ON UPDATE CASCADE  -- Ensures referential integrity
);

CREATE TABLE tracer_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,       -- Unique identifier for each trace log
    building_id INT NOT NULL,                -- Foreign key referencing the building
    timestamp DATETIME NOT NULL,             -- Date and time of the trace log
    target VARCHAR(255) NOT NULL,            -- Target hostname or domain being traced
    hop INT NOT NULL,                        -- Hop number in the traceroute
    hostname VARCHAR(255),                   -- Hostname of the hop (if available)
    ip_address VARCHAR(45),                  -- IP address of the hop (supports IPv4 and IPv6)
    response_time VARCHAR(255),              -- Response times for the hop (e.g., "5.755 ms 3.466 ms 3.852 ms")
    status VARCHAR(50) NOT NULL,             -- Status of the hop (e.g., "Success", "Timeout")
    FOREIGN KEY (building_id) REFERENCES buildings(id) 
        ON DELETE CASCADE ON UPDATE CASCADE  -- Ensures referential integrity
) 

