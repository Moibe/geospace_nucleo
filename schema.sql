-- Tabla plana para almacenar interacciones de mapa
CREATE TABLE IF NOT EXISTS map_interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Metadata básica
    type VARCHAR(50) NOT NULL,
    search_method VARCHAR(50),
    
    -- Timestamps
    timestamp_utc DATETIME,
    timestamp_user VARCHAR(100),
    timestamp_cdmx VARCHAR(100),
    
    -- Usuario/Cliente
    ga_client_id VARCHAR(255),
    phone VARCHAR(20),
    language VARCHAR(10),
    
    -- Información geográfica
    country_iso VARCHAR(2),
    country_code VARCHAR(5),
    
    -- Ubicación mostrada en el mapa
    location_shown_lat DECIMAL(10, 8),
    location_shown_lng DECIMAL(11, 8),
    
    -- Detección por IP
    ip_detection_iso_code VARCHAR(2),
    ip_detection_country_code VARCHAR(5),
    ip_detection_lat DECIMAL(10, 8),
    ip_detection_lng DECIMAL(11, 8),
    
    -- Detección por GPS
    gps_detection_iso_code VARCHAR(2),
    gps_detection_country_code VARCHAR(5),
    gps_detection_lat DECIMAL(10, 8),
    gps_detection_lng DECIMAL(11, 8),
    
    -- Tracking UTM
    utm_source VARCHAR(255),
    utm_medium VARCHAR(255),
    utm_campaign VARCHAR(255),
    utm_term VARCHAR(255),
    utm_content VARCHAR(255),
    gclid VARCHAR(255),
    fbclid VARCHAR(255),
    
    -- Control
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Índices para búsquedas frecuentes
    INDEX idx_ga_client_id (ga_client_id),
    INDEX idx_timestamp_utc (timestamp_utc),
    INDEX idx_country_iso (country_iso),
    INDEX idx_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
