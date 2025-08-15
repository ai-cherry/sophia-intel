-- Migration: Create operational_telemetry table for SOPHIA Intel Comptroller Agent
-- This table stores telemetry data, alerts, and monitoring information

-- Create operational_telemetry table
CREATE TABLE IF NOT EXISTS operational_telemetry (
    id SERIAL PRIMARY KEY,
    
    -- Service identification
    service_name VARCHAR(100) NOT NULL,
    service_category VARCHAR(50) NOT NULL,
    
    -- Telemetry data
    telemetry_type VARCHAR(50) NOT NULL, -- 'usage', 'billing', 'health'
    telemetry_data JSONB NOT NULL,
    
    -- Metrics and thresholds
    metric_name VARCHAR(100),
    metric_value DECIMAL(15,4),
    metric_unit VARCHAR(20),
    threshold_warning DECIMAL(15,4),
    threshold_critical DECIMAL(15,4),
    
    -- Alert information
    alert_level VARCHAR(20), -- 'info', 'warning', 'critical'
    alert_message TEXT,
    alert_triggered BOOLEAN DEFAULT FALSE,
    alert_acknowledged BOOLEAN DEFAULT FALSE,
    alert_resolved BOOLEAN DEFAULT FALSE,
    
    -- Status and health
    service_status VARCHAR(20) DEFAULT 'unknown', -- 'healthy', 'warning', 'critical', 'unknown'
    health_score DECIMAL(3,2), -- 0.00 to 1.00
    uptime_percentage DECIMAL(5,2),
    response_time_ms DECIMAL(10,2),
    error_rate DECIMAL(5,4),
    
    -- Cost tracking
    cost_estimate DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    billing_period VARCHAR(20), -- 'daily', 'monthly', 'yearly'
    
    -- Timestamps
    collected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    source VARCHAR(100) DEFAULT 'comptroller-agent',
    
    -- Constraints
    CONSTRAINT valid_alert_level CHECK (alert_level IN ('info', 'warning', 'critical')),
    CONSTRAINT valid_service_status CHECK (service_status IN ('healthy', 'warning', 'critical', 'unknown')),
    CONSTRAINT valid_health_score CHECK (health_score >= 0.00 AND health_score <= 1.00),
    CONSTRAINT valid_uptime CHECK (uptime_percentage >= 0.00 AND uptime_percentage <= 100.00),
    CONSTRAINT valid_error_rate CHECK (error_rate >= 0.0000 AND error_rate <= 1.0000)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_operational_telemetry_service_name ON operational_telemetry(service_name);
CREATE INDEX IF NOT EXISTS idx_operational_telemetry_service_category ON operational_telemetry(service_category);
CREATE INDEX IF NOT EXISTS idx_operational_telemetry_telemetry_type ON operational_telemetry(telemetry_type);
CREATE INDEX IF NOT EXISTS idx_operational_telemetry_alert_level ON operational_telemetry(alert_level);
CREATE INDEX IF NOT EXISTS idx_operational_telemetry_service_status ON operational_telemetry(service_status);
CREATE INDEX IF NOT EXISTS idx_operational_telemetry_collected_at ON operational_telemetry(collected_at);
CREATE INDEX IF NOT EXISTS idx_operational_telemetry_alert_triggered ON operational_telemetry(alert_triggered);
CREATE INDEX IF NOT EXISTS idx_operational_telemetry_alert_resolved ON operational_telemetry(alert_resolved);

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_operational_telemetry_service_time ON operational_telemetry(service_name, collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_operational_telemetry_alerts_active ON operational_telemetry(alert_triggered, alert_resolved, collected_at DESC) 
    WHERE alert_triggered = TRUE AND alert_resolved = FALSE;

-- Create GIN index for JSONB columns
CREATE INDEX IF NOT EXISTS idx_operational_telemetry_telemetry_data_gin ON operational_telemetry USING GIN(telemetry_data);
CREATE INDEX IF NOT EXISTS idx_operational_telemetry_metadata_gin ON operational_telemetry USING GIN(metadata);

-- Create trigger for automatic updated_at timestamp
CREATE OR REPLACE FUNCTION update_operational_telemetry_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_operational_telemetry_updated_at
    BEFORE UPDATE ON operational_telemetry
    FOR EACH ROW
    EXECUTE FUNCTION update_operational_telemetry_updated_at();

-- Create alerts summary view
CREATE OR REPLACE VIEW operational_alerts_summary AS
SELECT 
    service_name,
    service_category,
    alert_level,
    COUNT(*) as alert_count,
    COUNT(*) FILTER (WHERE alert_triggered = TRUE AND alert_resolved = FALSE) as active_alerts,
    COUNT(*) FILTER (WHERE alert_acknowledged = TRUE) as acknowledged_alerts,
    MAX(collected_at) as latest_alert,
    AVG(health_score) as avg_health_score,
    AVG(uptime_percentage) as avg_uptime
FROM operational_telemetry 
WHERE alert_level IS NOT NULL
GROUP BY service_name, service_category, alert_level
ORDER BY service_name, alert_level;

-- Create service health summary view
CREATE OR REPLACE VIEW service_health_summary AS
SELECT 
    service_name,
    service_category,
    service_status,
    AVG(health_score) as avg_health_score,
    AVG(uptime_percentage) as avg_uptime,
    AVG(response_time_ms) as avg_response_time,
    AVG(error_rate) as avg_error_rate,
    SUM(cost_estimate) as total_cost_estimate,
    COUNT(*) as measurement_count,
    MAX(collected_at) as latest_measurement,
    MIN(collected_at) as earliest_measurement
FROM operational_telemetry 
WHERE telemetry_type = 'health'
GROUP BY service_name, service_category, service_status
ORDER BY service_name;

-- Create cost tracking view
CREATE OR REPLACE VIEW cost_tracking_summary AS
SELECT 
    service_name,
    service_category,
    billing_period,
    currency,
    SUM(cost_estimate) as total_cost,
    AVG(cost_estimate) as avg_cost,
    COUNT(*) as cost_entries,
    MAX(collected_at) as latest_cost_update,
    DATE_TRUNC('day', collected_at) as cost_date
FROM operational_telemetry 
WHERE telemetry_type = 'billing' AND cost_estimate IS NOT NULL
GROUP BY service_name, service_category, billing_period, currency, DATE_TRUNC('day', collected_at)
ORDER BY service_name, cost_date DESC;

-- Insert sample telemetry data for testing
INSERT INTO operational_telemetry (
    service_name, service_category, telemetry_type, telemetry_data,
    metric_name, metric_value, metric_unit, threshold_warning, threshold_critical,
    alert_level, alert_message, service_status, health_score, uptime_percentage,
    response_time_ms, error_rate, cost_estimate, currency, billing_period
) VALUES 
-- OpenRouter sample data
('openrouter', 'ai_inference', 'usage', '{"tokens_used": 125000, "requests": 450}', 
 'tokens_used', 125000, 'tokens', 1000000, 2000000, 
 'info', 'Usage within normal limits', 'healthy', 0.98, 99.5, 
 1250.5, 0.02, 45.67, 'USD', 'monthly'),

-- Lambda Labs sample data
('lambda_labs', 'infrastructure', 'billing', '{"compute_hours": 156.7, "cost_per_hour": 0.15}',
 'monthly_spend', 23.45, 'USD', 600.00, 1200.00,
 'info', 'Billing within budget', 'healthy', 0.99, 99.8,
 245.0, 0.01, 23.45, 'USD', 'monthly'),

-- BrightData sample data
('brightdata', 'data_ingestion', 'health', '{"success_rate": 0.95, "proxy_count": 1000}',
 'success_rate', 0.95, 'percentage', 0.90, 0.80,
 'info', 'High success rate maintained', 'healthy', 0.95, 98.5,
 8500.0, 0.05, 18.67, 'USD', 'monthly'),

-- Weaviate sample data
('weaviate', 'vector_database', 'usage', '{"storage_gb": 2.3, "queries_per_day": 15000}',
 'storage_usage', 2.3, 'GB', 8.0, 9.0,
 'info', 'Storage usage optimal', 'healthy', 0.97, 99.2,
 450.0, 0.01, 12.50, 'USD', 'monthly'),

-- Qdrant sample data
('qdrant', 'vector_database', 'health', '{"vectors_stored": 150000, "memory_usage": 0.65}',
 'memory_usage', 0.65, 'percentage', 0.80, 0.90,
 'info', 'Memory usage within limits', 'healthy', 0.96, 99.7,
 180.0, 0.005, 8.90, 'USD', 'monthly');

-- Create function to get active alerts
CREATE OR REPLACE FUNCTION get_active_alerts(p_service_name VARCHAR DEFAULT NULL)
RETURNS TABLE (
    service_name VARCHAR,
    service_category VARCHAR,
    alert_level VARCHAR,
    alert_message TEXT,
    metric_name VARCHAR,
    metric_value DECIMAL,
    threshold_value DECIMAL,
    collected_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ot.service_name,
        ot.service_category,
        ot.alert_level,
        ot.alert_message,
        ot.metric_name,
        ot.metric_value,
        CASE 
            WHEN ot.alert_level = 'critical' THEN ot.threshold_critical
            ELSE ot.threshold_warning
        END as threshold_value,
        ot.collected_at
    FROM operational_telemetry ot
    WHERE ot.alert_triggered = TRUE 
      AND ot.alert_resolved = FALSE
      AND (p_service_name IS NULL OR ot.service_name = p_service_name)
    ORDER BY 
        CASE ot.alert_level 
            WHEN 'critical' THEN 1
            WHEN 'warning' THEN 2
            ELSE 3
        END,
        ot.collected_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Create function to calculate service health score
CREATE OR REPLACE FUNCTION calculate_service_health_score(p_service_name VARCHAR)
RETURNS DECIMAL(3,2) AS $$
DECLARE
    health_score DECIMAL(3,2);
BEGIN
    SELECT AVG(ot.health_score)
    INTO health_score
    FROM operational_telemetry ot
    WHERE ot.service_name = p_service_name
      AND ot.telemetry_type = 'health'
      AND ot.collected_at >= NOW() - INTERVAL '24 hours';
    
    RETURN COALESCE(health_score, 0.00);
END;
$$ LANGUAGE plpgsql;

-- Create function to get cost summary
CREATE OR REPLACE FUNCTION get_cost_summary(p_period VARCHAR DEFAULT 'monthly')
RETURNS TABLE (
    service_name VARCHAR,
    service_category VARCHAR,
    total_cost DECIMAL,
    currency VARCHAR,
    last_updated TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ot.service_name,
        ot.service_category,
        SUM(ot.cost_estimate) as total_cost,
        ot.currency,
        MAX(ot.collected_at) as last_updated
    FROM operational_telemetry ot
    WHERE ot.telemetry_type = 'billing'
      AND ot.billing_period = p_period
      AND ot.collected_at >= NOW() - INTERVAL '30 days'
    GROUP BY ot.service_name, ot.service_category, ot.currency
    ORDER BY total_cost DESC;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON operational_telemetry TO sophia_app_user;
-- GRANT SELECT ON operational_alerts_summary TO sophia_app_user;
-- GRANT SELECT ON service_health_summary TO sophia_app_user;
-- GRANT SELECT ON cost_tracking_summary TO sophia_app_user;
-- GRANT EXECUTE ON FUNCTION get_active_alerts TO sophia_app_user;
-- GRANT EXECUTE ON FUNCTION calculate_service_health_score TO sophia_app_user;
-- GRANT EXECUTE ON FUNCTION get_cost_summary TO sophia_app_user;

-- Add comments for documentation
COMMENT ON TABLE operational_telemetry IS 'Stores telemetry data, alerts, and monitoring information for all SOPHIA Intel services';
COMMENT ON COLUMN operational_telemetry.service_name IS 'Name of the monitored service (e.g., openrouter, lambda_labs)';
COMMENT ON COLUMN operational_telemetry.telemetry_type IS 'Type of telemetry data: usage, billing, or health';
COMMENT ON COLUMN operational_telemetry.telemetry_data IS 'Raw telemetry data in JSON format';
COMMENT ON COLUMN operational_telemetry.alert_level IS 'Alert severity level: info, warning, or critical';
COMMENT ON COLUMN operational_telemetry.health_score IS 'Service health score from 0.00 to 1.00';
COMMENT ON VIEW operational_alerts_summary IS 'Summary view of alerts grouped by service and alert level';
COMMENT ON VIEW service_health_summary IS 'Summary view of service health metrics';
COMMENT ON VIEW cost_tracking_summary IS 'Summary view of cost tracking data';

-- Migration complete
SELECT 'Migration 003_create_operational_telemetry completed successfully' as status;

