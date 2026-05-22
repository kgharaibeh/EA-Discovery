// ---- Enums ----

export type AssetType =
  | 'server'
  | 'database'
  | 'app_server'
  | 'application'
  | 'api_endpoint'
  | 'network_device'
  | 'load_balancer'
  | 'storage'
  | 'container'
  | 'virtual_machine';

export type AssetStatus = 'active' | 'inactive' | 'decommissioned' | 'unknown';

export type OSFamily = 'linux' | 'windows' | 'macos' | 'network_os' | 'unknown';

export type RelationshipType =
  | 'connects_to'
  | 'depends_on'
  | 'hosts'
  | 'runs_on'
  | 'authenticates_to'
  | 'load_balances'
  | 'stores_data_in'
  | 'replicates_to'
  | 'monitors'
  | 'backs_up_to';

export type ScanStatus =
  | 'pending'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled';

// ---- Models ----

export interface PortInfo {
  port: number;
  protocol: string;
  state: string;
  service?: string;
  version?: string;
}

export interface ServiceInfo {
  name: string;
  version?: string;
  port?: number;
  status?: string;
}

export interface SoftwareInfo {
  name: string;
  version?: string;
  vendor?: string;
}

export interface Asset {
  id: string;
  hostname: string;
  ip_addresses: string[];
  asset_type: AssetType;
  status: AssetStatus;
  os_family?: OSFamily;
  os_version?: string;
  open_ports: PortInfo[];
  services: ServiceInfo[];
  software: SoftwareInfo[];
  configuration: Record<string, unknown>;
  ai_context?: string;
  first_seen: string;
  last_scanned?: string;
  created_at: string;
  updated_at: string;
}

export interface Relationship {
  id: string;
  source_asset_id: string;
  target_asset_id: string;
  relationship_type: RelationshipType;
  properties: Record<string, unknown>;
  confidence: number;
  discovered_by: string;
  created_at: string;
  updated_at: string;
}

export interface Scan {
  id: string;
  targets: string[];
  scan_type: string;
  status: ScanStatus;
  credential_id?: string;
  options: Record<string, unknown>;
  progress: number;
  assets_discovered: number;
  relationships_discovered: number;
  errors: string[];
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

export interface ScanCreate {
  targets: string[];
  scan_type?: string;
  credential_id?: string;
  options?: Record<string, unknown>;
}

export interface TopologyNode {
  id: string;
  hostname: string;
  asset_type: AssetType;
  status: AssetStatus;
  ip_addresses: string[];
  os_family?: OSFamily;
}

export interface TopologyEdge {
  id: string;
  source: string;
  target: string;
  relationship_type: RelationshipType;
  confidence: number;
}

export interface TopologyResponse {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
}

export interface Credential {
  id: string;
  name: string;
  credential_type: string;
  username?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface CredentialCreate {
  name: string;
  credential_type: string;
  username?: string;
  password?: string;
  ssh_key?: string;
  description?: string;
}

export interface IntelligenceSuggestion {
  id: string;
  suggestion_type: string;
  title: string;
  description: string;
  confidence: number;
  source_asset_id?: string;
  target_asset_id?: string;
  suggested_data: Record<string, unknown>;
  status: 'pending' | 'accepted' | 'rejected' | 'modified';
  reviewed_at?: string;
  created_at: string;
}

export interface SuggestionReview {
  status: 'accepted' | 'rejected' | 'modified';
  modifications?: Record<string, unknown>;
  notes?: string;
}

export interface DriftEvent {
  id: string;
  asset_id: string;
  asset_hostname: string;
  drift_type: string;
  field: string;
  old_value: unknown;
  new_value: unknown;
  detected_at: string;
  acknowledged: boolean;
  acknowledged_by?: string;
}

export interface DashboardStats {
  total_assets: number;
  total_relationships: number;
  recent_scans: number;
  pending_suggestions: number;
  drift_events: number;
  assets_by_type: Record<AssetType, number>;
  assets_by_status: Record<AssetStatus, number>;
  relationships_by_type: Record<RelationshipType, number>;
  scan_activity: Array<{ date: string; count: number }>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
