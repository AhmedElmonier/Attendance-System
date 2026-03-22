CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    device_name TEXT NOT NULL,
    device_type TEXT DEFAULT 'kiosk',
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'active',
    certificate_cn TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS employees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name_ar TEXT NOT NULL,
    name_en TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    enrolled_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS attendance_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    employee_id UUID NOT NULL REFERENCES employees(id),
    device_id UUID REFERENCES devices(id),
    event_timestamp TIMESTAMPTZ NOT NULL,
    confidence_score REAL NOT NULL,
    event_type TEXT DEFAULT 'clock_in',
    integrity_hash TEXT,
    client_timestamp TIMESTAMPTZ,
    synced_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT valid_confidence CHECK (confidence_score >= 0 AND confidence_score <= 1),
    CONSTRAINT valid_event_type CHECK (event_type IN ('clock_in', 'clock_out'))
);

CREATE TABLE IF NOT EXISTS pending_approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    maker_id UUID NOT NULL,
    checker_id UUID NULL,
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    original_data JSONB NOT NULL,
    proposed_data JSONB NOT NULL,
    change_reason TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ NULL,
    
    CONSTRAINT valid_status CHECK (status IN ('pending', 'approved', 'rejected'))
);

CREATE INDEX idx_attendance_tenant ON attendance_events(tenant_id);
CREATE INDEX idx_attendance_employee ON attendance_events(employee_id);
CREATE INDEX idx_attendance_timestamp ON attendance_events(event_timestamp);
CREATE INDEX idx_employees_tenant ON employees(tenant_id);
CREATE INDEX idx_devices_tenant ON devices(tenant_id);
CREATE INDEX idx_pending_tenant_status ON pending_approvals(tenant_id, status);

ALTER TABLE attendance_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE pending_approvals ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_attendance ON attendance_events
    USING (tenant_id = current_setting('app.tenant_id')::UUID);

CREATE POLICY tenant_isolation_employees ON employees
    USING (tenant_id = current_setting('app.tenant_id')::UUID);

CREATE POLICY tenant_isolation_devices ON devices
    USING (tenant_id = current_setting('app.tenant_id')::UUID);

CREATE POLICY tenant_isolation_approvals ON pending_approvals
    USING (tenant_id = current_setting('app.tenant_id')::UUID);

CREATE OR REPLACE FUNCTION set_tenant_context(tenant_uuid UUID)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.tenant_id', tenant_uuid::TEXT, TRUE);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION device_heartbeat(device_uuid UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE devices SET last_seen = NOW() WHERE id = device_uuid;
END;
$$ LANGUAGE plpgsql;
