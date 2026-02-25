export interface User {
  id: string
  username: string
  email: string
  role: string
  is_active: boolean
  created_at: string
  last_login?: string
}

export interface LogEntry {
  id?: string
  timestamp?: string
  message?: string
  host_name?: string
  log_source?: string
  log_type?: string
  severity?: string
  program?: string
  src_ip?: string
  dst_ip?: string
  src_port?: number
  dst_port?: number
  protocol?: string
  service?: string
}

export interface SecurityAlert {
  id?: string
  alert_type: string
  severity: string
  title: string
  description?: string
  source_ip?: string
  destination_ip?: string
  source_port?: number
  destination_port?: number
  protocol?: string
  service?: string
  rule_id?: string
  status: string
  created_at?: string
  updated_at?: string
}

export interface IDSAlert {
  id?: string
  timestamp?: string
  alert_type?: string
  severity?: string
  message?: string
  src_ip?: string
  src_port?: number
  dst_ip?: string
  dst_port?: number
  protocol?: string
  rule_id?: string
  action?: string
  category?: string
}

export interface IDSStatus {
  mode: string
  interface: string
  is_running: boolean
  alerts_today: number
  top_categories: Array<{ category: string; count: number }>
}

export interface Asset {
  id?: string
  ip_address: string
  mac_address?: string
  hostname?: string
  os_type?: string
  os_version?: string
  asset_type?: string
  criticality: string
  first_seen?: string
  last_seen?: string
  is_active: boolean
  ports?: PortInfo[]
}

export interface PortInfo {
  port: number
  protocol: string
  service?: string
  version?: string
  state: string
}

export interface NetworkChange {
  id: string
  asset_id?: string
  change_type: string
  previous?: Record<string, unknown>
  current?: Record<string, unknown>
  detected_at: string
  acknowledged: boolean
}

export interface DashboardSummary {
  alerts_today: number
  critical_alerts: number
  open_alerts: number
  total_assets: number
  ids_alerts_today: number
  logs_today: number
  timestamp: string
}

export interface TimelinePoint {
  time: string
  count: number
}

export interface ScanResult {
  id: string
  target: string
  scan_type: string
  status: string
  started_at: string
  completed_at?: string
  hosts_found: number
}
