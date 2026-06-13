/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export type QsStatus = 'frei' | 'gesperrt' | 'in_pruefung' | 'reinigung' | 'reserviert';

export interface SiloCell {
  id: string;
  tenant_id: string;
  warehouse_id: string;
  zone_id: string | null;
  aisle_id: string | null;
  bin_id: string | null;
  silo_system_id: string;
  cell_code: string;
  name: string;
  capacity_kg: number;
  current_material_id: string | null;
  current_material_name: string | null; // Display helper
  current_lot_id: string | null;
  qs_status: QsStatus;
  contamination_risk_class: string | null; // e.g., 'BIO', 'GMO', 'CONVENTIONAL'
  is_active: boolean;
  created_at: string;
}

export type NodeType =
  | 'intake'
  | 'scale'
  | 'elevator'
  | 'conveyor'
  | 'valve'
  | 'diverter'
  | 'silo_cell'
  | 'mixer'
  | 'loader'
  | 'mobile_unit';

export type NodeStatus = 'active' | 'blocked' | 'maintenance' | 'cleaning';

export interface MaterialFlowNode {
  id: string;
  tenant_id: string;
  warehouse_id: string;
  node_type: NodeType;
  ref_type: string | null;
  ref_id: string | null;
  code: string;
  name: string;
  status: NodeStatus;
  geo_lat: number | null;
  geo_lng: number | null;
  layout_x: number | null;
  layout_y: number | null;
  is_active: boolean;
}

export type ConveyorType =
  | 'screw'
  | 'elevator'
  | 'belt'
  | 'slide'
  | 'chain'
  | 'pneumatic'
  | 'gravity'
  | 'manual';

export type EdgeStatus = 'open' | 'blocked' | 'maintenance' | 'cleaning';

export interface MaterialFlowEdge {
  id: string;
  tenant_id: string;
  warehouse_id: string;
  from_node_id: string;
  to_node_id: string;
  conveyor_type: ConveyorType;
  status: EdgeStatus;
  contamination_guard_enabled: boolean;
  flush_required: boolean;
  max_capacity_kg_h: number | null;
}

export interface RouteValidationRequest {
  fromNodeId: string;
  toNodeId: string;
  materialId?: string;
  materialName?: string;
  contaminationRiskClass?: string;
}

export interface RouteValidationResult {
  isValid: boolean;
  violations: string[]; // List of reasons why route may be invalid
  warnings: string[]; // E.g., Spülchargenwarning / Contamination hazard
  flushRequired: boolean;
  path: string[]; // Node IDs in order
}
