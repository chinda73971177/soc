CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'analyst',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ip_address INET NOT NULL,
    mac_address VARCHAR(17),
    hostname VARCHAR(255),
    os_type VARCHAR(100),
    os_version VARCHAR(100),
    asset_type VARCHAR(50),
    criticality VARCHAR(20) DEFAULT 'medium',
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    tags JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS asset_ports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
    port INTEGER NOT NULL,
    protocol VARCHAR(10) NOT NULL,
    service VARCHAR(100),
    version VARCHAR(255),
    state VARCHAR(20) NOT NULL,
    last_scan TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS network_scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_type VARCHAR(50),
    target VARCHAR(255),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'running',
    hosts_found INTEGER DEFAULT 0,
    initiated_by UUID REFERENCES users(id),
    results JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS network_changes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID REFERENCES assets(id),
    change_type VARCHAR(50),
    previous JSONB,
    current JSONB,
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged BOOLEAN DEFAULT FALSE,
    ack_by UUID REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS security_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    source_ip INET,
    destination_ip INET,
    source_port INTEGER,
    destination_port INTEGER,
    protocol VARCHAR(20),
    service VARCHAR(100),
    rule_id VARCHAR(100),
    raw_event JSONB,
    status VARCHAR(20) DEFAULT 'open',
    assigned_to UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    notifications_sent JSONB DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS alert_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    conditions JSONB NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    is_active BOOLEAN DEFAULT TRUE,
    notify_telegram BOOLEAN DEFAULT FALSE,
    notify_whatsapp BOOLEAN DEFAULT FALSE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ids_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mode VARCHAR(10) DEFAULT 'ids',
    interface VARCHAR(50),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by UUID REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS notification_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider VARCHAR(50) NOT NULL,
    config JSONB NOT NULL,
    min_severity VARCHAR(20) DEFAULT 'high',
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_assets_ip ON assets(ip_address);
CREATE INDEX IF NOT EXISTS idx_assets_last_seen ON assets(last_seen);
CREATE INDEX IF NOT EXISTS idx_asset_ports_asset ON asset_ports(asset_id);
CREATE INDEX IF NOT EXISTS idx_asset_ports_port ON asset_ports(port, protocol);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON security_alerts(severity, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON security_alerts(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_source_ip ON security_alerts(source_ip);
CREATE INDEX IF NOT EXISTS idx_network_changes_asset ON network_changes(asset_id, detected_at DESC);

INSERT INTO ids_config (mode, interface) VALUES ('ids', 'eth0') ON CONFLICT DO NOTHING;

INSERT INTO users (username, email, password_hash, role)
VALUES ('admin', 'admin@soc.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5udem', 'admin')
ON CONFLICT (username) DO NOTHING;
