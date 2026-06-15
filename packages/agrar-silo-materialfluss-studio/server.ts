/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import express from 'express';
import path from 'path';
import { createServer as createViteServer } from 'vite';
import { 
  MaterialFlowEdge, 
  MaterialFlowNode, 
  RouteValidationRequest, 
  RouteValidationResult, 
  SiloCell 
} from './src/types.js';

// In-memory Database of Agricultural Warehouse Entities
const TENANT_ID = 'jochen-weerda-agrar';
const WAREHOUSE_ID = 'wh-elbe-weser-01';

const siloCells: SiloCell[] = [
  {
    id: 'silo-cell-A1',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    zone_id: 'zone-silo-block-A',
    aisle_id: 'aisle-1',
    bin_id: 'bin-A1',
    silo_system_id: 'silosys-haupt',
    cell_code: 'ZELLE-A1',
    name: 'Silozelle A1 (Weizen)',
    capacity_kg: 150000,
    current_material_id: 'mat-wheat-premium',
    current_material_name: 'Premium-Brotweizen',
    current_lot_id: 'LOT-2026-WE-09',
    qs_status: 'frei',
    contamination_risk_class: 'CONV', // Conventional
    is_active: true,
    created_at: new Date('2026-01-10T08:00:00Z').toISOString()
  },
  {
    id: 'silo-cell-A2',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    zone_id: 'zone-silo-block-A',
    aisle_id: 'aisle-1',
    bin_id: 'bin-A2',
    silo_system_id: 'silosys-haupt',
    cell_code: 'ZELLE-A2',
    name: 'Silozelle A2 (BIO-Sojamehl)',
    capacity_kg: 120000,
    current_material_id: 'mat-soy-bio',
    current_material_name: 'BIO-Sojamehl (GVO-Frei)',
    current_lot_id: 'LOT-2026-SO-03',
    qs_status: 'in_pruefung',
    contamination_risk_class: 'BIO', // Organic
    is_active: true,
    created_at: new Date('2026-02-15T09:30:00Z').toISOString()
  },
  {
    id: 'silo-cell-A3',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    zone_id: 'zone-silo-block-A',
    aisle_id: 'aisle-1',
    bin_id: 'bin-A3',
    silo_system_id: 'silosys-haupt',
    cell_code: 'ZELLE-A3',
    name: 'Silozelle A3 (Futtergerste - GESPERRT)',
    capacity_kg: 200000,
    current_material_id: 'mat-barley-feed',
    current_material_name: 'Futtergerste Standard',
    current_lot_id: 'LOT-2026-BA-01',
    qs_status: 'gesperrt', // Locked due to heating/inspection issues
    contamination_risk_class: 'CONV',
    is_active: true,
    created_at: new Date('2025-11-20T14:00:00Z').toISOString()
  },
  {
    id: 'silo-cell-A4',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    zone_id: 'zone-silo-block-A',
    aisle_id: 'aisle-1',
    bin_id: 'bin-A4',
    silo_system_id: 'silosys-haupt',
    cell_code: 'ZELLE-A4',
    name: 'Silozelle A4 (Mais GVO)',
    capacity_kg: 95000,
    current_material_id: 'mat-corn-gmo',
    current_material_name: 'Futtermittelmais (GMO)',
    current_lot_id: 'LOT-2026-CO-44',
    qs_status: 'frei',
    contamination_risk_class: 'GMO', // GMO
    is_active: true,
    created_at: new Date('2026-03-01T11:15:00Z').toISOString()
  }
];

const flowNodes: MaterialFlowNode[] = [
  {
    id: 'node-intake-01',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    node_type: 'intake',
    ref_type: null,
    ref_id: null,
    code: 'IN-GOSSE-1',
    name: 'Hauptannahme-Gosse 1',
    status: 'active',
    geo_lat: 53.48312,
    geo_lng: 8.91421,
    layout_x: 60,
    layout_y: 110,
    is_active: true
  },
  {
    id: 'node-scale-01',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    node_type: 'scale',
    ref_type: null,
    ref_id: null,
    code: 'WA-DURCH-1',
    name: 'Durchlaufwaage Hauptstrom',
    status: 'active',
    geo_lat: 53.48318,
    geo_lng: 8.91435,
    layout_x: 230,
    layout_y: 110,
    is_active: true
  },
  {
    id: 'node-elevator-01',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    node_type: 'elevator',
    ref_type: null,
    ref_id: null,
    code: 'EL-HAUPT-1',
    name: 'Hauptelevator West',
    status: 'active',
    geo_lat: 53.48325,
    geo_lng: 8.91448,
    layout_x: 390,
    layout_y: 170,
    is_active: true
  },
  {
    id: 'node-diverter-01',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    node_type: 'diverter',
    ref_type: null,
    ref_id: null,
    code: 'WE-VERT-1',
    name: 'Pneumatischer Verteilerkopf',
    status: 'active',
    geo_lat: 53.48328,
    geo_lng: 8.91452,
    layout_x: 550,
    layout_y: 170,
    is_active: true
  },
  // Silocell nodes linking to Silo cells
  {
    id: 'node-silo-cell-A1',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    node_type: 'silo_cell',
    ref_type: 'silo_cells',
    ref_id: 'silo-cell-A1',
    code: 'S-A1',
    name: 'Silo Zelle A1',
    status: 'active',
    geo_lat: 53.48340,
    geo_lng: 8.91470,
    layout_x: 750,
    layout_y: 60,
    is_active: true
  },
  {
    id: 'node-silo-cell-A2',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    node_type: 'silo_cell',
    ref_type: 'silo_cells',
    ref_id: 'silo-cell-A2',
    code: 'S-A2',
    name: 'Silo Zelle A2',
    status: 'active',
    geo_lat: 53.48344,
    geo_lng: 8.91475,
    layout_x: 750,
    layout_y: 150,
    is_active: true
  },
  {
    id: 'node-silo-cell-A3',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    node_type: 'silo_cell',
    ref_type: 'silo_cells',
    ref_id: 'silo-cell-A3',
    code: 'S-A3',
    name: 'Silo Zelle A3',
    status: 'active',
    geo_lat: 53.48348,
    geo_lng: 8.91480,
    layout_x: 750,
    layout_y: 240,
    is_active: true
  },
  {
    id: 'node-silo-cell-A4',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    node_type: 'silo_cell',
    ref_type: 'silo_cells',
    ref_id: 'silo-cell-A4',
    code: 'S-A4',
    name: 'Silo Zelle A4',
    status: 'active',
    geo_lat: 53.48352,
    geo_lng: 8.91485,
    layout_x: 750,
    layout_y: 330,
    is_active: true
  },
  {
    id: 'node-mixer-01',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    node_type: 'mixer',
    ref_type: null,
    ref_id: null,
    code: 'CH-MISCHER-1',
    name: 'Chargenmischer-Anlage Werksbereich',
    status: 'active',
    geo_lat: 53.48360,
    geo_lng: 8.91495,
    layout_x: 950,
    layout_y: 190,
    is_active: true
  },
  {
    id: 'node-mobile-mmx-1',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    node_type: 'mobile_unit',
    ref_type: null,
    ref_id: null,
    code: 'MMX-WAG-45',
    name: 'MMX-Mobilmischer LKW (Tropper)',
    status: 'active',
    geo_lat: 53.48301,
    geo_lng: 8.91402,
    layout_x: 350,
    layout_y: 350,
    is_active: true
  }
];

const flowEdges: MaterialFlowEdge[] = [
  {
    id: 'edge-01',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    from_node_id: 'node-intake-01',
    to_node_id: 'node-scale-01',
    conveyor_type: 'gravity',
    status: 'open',
    contamination_guard_enabled: false,
    flush_required: false,
    max_capacity_kg_h: 60000
  },
  {
    id: 'edge-02',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    from_node_id: 'node-scale-01',
    to_node_id: 'node-elevator-01',
    conveyor_type: 'belt',
    status: 'open',
    contamination_guard_enabled: false,
    flush_required: false,
    max_capacity_kg_h: 60000
  },
  {
    id: 'edge-03',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    from_node_id: 'node-elevator-01',
    to_node_id: 'node-diverter-01',
    conveyor_type: 'elevator',
    status: 'open',
    contamination_guard_enabled: true,
    flush_required: false,
    max_capacity_kg_h: 50000
  },
  // Paths from diverter head to silo chambers
  {
    id: 'edge-to-A1',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    from_node_id: 'node-diverter-01',
    to_node_id: 'node-silo-cell-A1',
    conveyor_type: 'slide',
    status: 'open',
    contamination_guard_enabled: true,
    flush_required: false,
    max_capacity_kg_h: 40000
  },
  {
    id: 'edge-to-A2',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    from_node_id: 'node-diverter-01',
    to_node_id: 'node-silo-cell-A2',
    conveyor_type: 'slide',
    status: 'open',
    contamination_guard_enabled: true,
    flush_required: false,
    max_capacity_kg_h: 40000
  },
  {
    id: 'edge-to-A3',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    from_node_id: 'node-diverter-01',
    to_node_id: 'node-silo-cell-A3',
    conveyor_type: 'slide',
    status: 'blocked', // Physically closed/maintenance due to A3 locked state
    contamination_guard_enabled: true,
    flush_required: false,
    max_capacity_kg_h: 40000
  },
  {
    id: 'edge-to-A4',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    from_node_id: 'node-diverter-01',
    to_node_id: 'node-silo-cell-A4',
    conveyor_type: 'slide',
    status: 'open',
    contamination_guard_enabled: true,
    flush_required: false,
    max_capacity_kg_h: 40000
  },
  // Conveyance from Silo cells into Mixer
  {
    id: 'edge-A1-to-mixer',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    from_node_id: 'node-silo-cell-A1',
    to_node_id: 'node-mixer-01',
    conveyor_type: 'screw',
    status: 'open',
    contamination_guard_enabled: true,
    flush_required: false,
    max_capacity_kg_h: 30000
  },
  {
    id: 'edge-A2-to-mixer',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    from_node_id: 'node-silo-cell-A2',
    to_node_id: 'node-mixer-01',
    conveyor_type: 'screw',
    status: 'open',
    contamination_guard_enabled: true,
    flush_required: false,
    max_capacity_kg_h: 30000
  },
  {
    id: 'edge-A3-to-mixer',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    from_node_id: 'node-silo-cell-A3',
    to_node_id: 'node-mixer-01',
    conveyor_type: 'screw',
    status: 'blocked',
    contamination_guard_enabled: true,
    flush_required: false,
    max_capacity_kg_h: 30000
  },
  {
    id: 'edge-A4-to-mixer',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    from_node_id: 'node-silo-cell-A4',
    to_node_id: 'node-mixer-01',
    conveyor_type: 'screw',
    status: 'open',
    contamination_guard_enabled: true,
    flush_required: false,
    max_capacity_kg_h: 30000
  },
  // Mobile intake path connecting to elevator
  {
    id: 'edge-mmx-to-elevator',
    tenant_id: TENANT_ID,
    warehouse_id: WAREHOUSE_ID,
    from_node_id: 'node-mobile-mmx-1',
    to_node_id: 'node-elevator-01',
    conveyor_type: 'gravity',
    status: 'open',
    contamination_guard_enabled: true,
    flush_required: false,
    max_capacity_kg_h: 50000
  }
];

async function run() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // API Endpoints: Silo-Cells
  app.get('/api/warehouse/silo-cells', (req, res) => {
    res.json(siloCells);
  });

  app.post('/api/warehouse/silo-cells', (req, res) => {
    const { 
      cell_code, 
      name, 
      capacity_kg, 
      current_material_id, 
      current_material_name,
      current_lot_id, 
      qs_status, 
      contamination_risk_class 
    } = req.body;

    if (!cell_code || !name || isNaN(Number(capacity_kg))) {
      return res.status(400).json({ error: 'Ungültige Felder. cell_code, name, capacity_kg sind erforderlich.' });
    }

    const newCell: SiloCell = {
      id: `silo-cell-${Date.now()}`,
      tenant_id: TENANT_ID,
      warehouse_id: WAREHOUSE_ID,
      zone_id: 'zone-silo-block-A',
      aisle_id: 'aisle-1',
      bin_id: `bin-${cell_code}`,
      silo_system_id: 'silosys-haupt',
      cell_code,
      name,
      capacity_kg: Number(capacity_kg),
      current_material_id: current_material_id || null,
      current_material_name: current_material_name || null,
      current_lot_id: current_lot_id || null,
      qs_status: qs_status || 'frei',
      contamination_risk_class: contamination_risk_class || 'CONV',
      is_active: true,
      created_at: new Date().toISOString()
    };

    siloCells.push(newCell);

    // Create a corresponding node in the material flow to expose it in flowsheet
    const newNode: MaterialFlowNode = {
      id: `node-${newCell.id}`,
      tenant_id: TENANT_ID,
      warehouse_id: WAREHOUSE_ID,
      node_type: 'silo_cell',
      ref_type: 'silo_cells',
      ref_id: newCell.id,
      code: `S-${cell_code}`,
      name: `Silo ${name}`,
      status: newCell.qs_status === 'gesperrt' ? 'blocked' : 'active',
      geo_lat: 53.48355,
      geo_lng: 8.91490,
      layout_x: 750,
      layout_y: 60 + (siloCells.length - 1) * 90,
      is_active: true
    };
    flowNodes.push(newNode);

    // Automatic route connection from Diverter head to new Silo cell
    const newEdge: MaterialFlowEdge = {
      id: `edge-to-${newCell.id}`,
      tenant_id: TENANT_ID,
      warehouse_id: WAREHOUSE_ID,
      from_node_id: 'node-diverter-01',
      to_node_id: newNode.id,
      conveyor_type: 'slide',
      status: newCell.qs_status === 'gesperrt' ? 'blocked' : 'open',
      contamination_guard_enabled: true,
      flush_required: false,
      max_capacity_kg_h: 40000
    };
    flowEdges.push(newEdge);

    res.status(201).json(newCell);
  });

  // API Endpoints: Material Flow Nodes
  app.get('/api/warehouse/material-flow/nodes', (req, res) => {
    res.json(flowNodes);
  });

  app.post('/api/warehouse/material-flow/nodes', (req, res) => {
    const { node_type, code, name, status, layout_x, layout_y } = req.body;

    if (!node_type || !code || !name) {
      return res.status(400).json({ error: 'node_type, code, name sind erforderlich.' });
    }

    const newNode: MaterialFlowNode = {
      id: `node-custom-${Date.now()}`,
      tenant_id: TENANT_ID,
      warehouse_id: WAREHOUSE_ID,
      node_type,
      ref_type: null,
      ref_id: null,
      code,
      name,
      status: status || 'active',
      geo_lat: 53.4830,
      geo_lng: 8.9140,
      layout_x: Number(layout_x) || 100,
      layout_y: Number(layout_y) || 100,
      is_active: true
    };

    flowNodes.push(newNode);
    res.status(201).json(newNode);
  });

  // API Endpoints: Material Flow Edges
  app.get('/api/warehouse/material-flow/edges', (req, res) => {
    res.json(flowEdges);
  });

  app.post('/api/warehouse/material-flow/edges', (req, res) => {
    const { from_node_id, to_node_id, conveyor_type, max_capacity_kg_h, contamination_guard_enabled } = req.body;

    if (!from_node_id || !to_node_id || !conveyor_type) {
      return res.status(400).json({ error: 'from_node_id, to_node_id, conveyor_type sind erforderlich.' });
    }

    // Verify nodes exist
    const fromExists = flowNodes.some(n => n.id === from_node_id);
    const toExists = flowNodes.some(n => n.id === to_node_id);

    if (!fromExists || !toExists) {
      return res.status(400).json({ error: 'Sender- oder Empfänger-Knoten existiert nicht.' });
    }

    const newEdge: MaterialFlowEdge = {
      id: `edge-custom-${Date.now()}`,
      tenant_id: TENANT_ID,
      warehouse_id: WAREHOUSE_ID,
      from_node_id,
      to_node_id,
      conveyor_type,
      status: 'open',
      contamination_guard_enabled: !!contamination_guard_enabled,
      flush_required: false,
      max_capacity_kg_h: Number(max_capacity_kg_h) || null
    };

    flowEdges.push(newEdge);
    res.status(201).json(newEdge);
  });

  // API Endpoint: Plausibilitäts- & Routen-Prüfung (validate-route)
  app.post('/api/warehouse/material-flow/validate-route', (req, res) => {
    const { fromNodeId, toNodeId, materialId: _materialId, materialName: _materialName, contaminationRiskClass } =
      req.body as RouteValidationRequest;

    if (!fromNodeId || !toNodeId) {
      return res.status(400).json({ error: 'fromNodeId und toNodeId sind erforderlich.' });
    }

    const sourceNode = flowNodes.find(n => n.id === fromNodeId);
    const targetNode = flowNodes.find(n => n.id === toNodeId);

    if (!sourceNode || !targetNode) {
      return res.status(404).json({ error: 'Knoten konnte nicht gefunden werden.' });
    }

    // Perform routing search (BFS) on the open edges
    const path = findPath(fromNodeId, toNodeId);

    if (!path || path.length === 0) {
      return res.json({
        isValid: false,
        violations: ['Keine Verbindung zwischen diesen Knoten vorhanden, oder eine Teilstrecke ist physisch gesperrt (`blocked`).'],
        warnings: [],
        flushRequired: false,
        path: []
      } as RouteValidationResult);
    }

    const violations: string[] = [];
    const warnings: string[] = [];
    let flushRequired = false;

    // Evaluate nodes along the path
    for (const nodeId of path) {
      const node = flowNodes.find(n => n.id === nodeId);
      if (!node) continue;

      // Rule 1: No routing if node is blocked, cleaning or maintenance
      if (node.status === 'blocked') {
        violations.push(`Knotenpunkt '${node.name}' (${node.code}) ist aktuell blockiert!`);
      } else if (node.status === 'cleaning') {
        violations.push(`Knotenpunkt '${node.name}' befindet sich zurzeit im Reinigungsarbeitsgang!`);
      } else if (node.status === 'maintenance') {
        violations.push(`Knotenpunkt '${node.name}' ist wegen Wartung außer Betrieb!`);
      }

      // Rule 2: If node is a Silo Cell, check its QA Status
      if (node.node_type === 'silo_cell' && node.ref_id) {
        const siloCell = siloCells.find(c => c.id === node.ref_id);
        if (siloCell) {
          if (siloCell.qs_status === 'gesperrt') {
            violations.push(`Ziel-Silozelle '${siloCell.name}' ist QS-GESPERRT! Materialfluss abgefangen.`);
          } else if (siloCell.qs_status === 'reinigung') {
            violations.push(`Ziel-Silozelle '${siloCell.name}' wird gereinigt und darf nicht beschickt werden.`);
          } else if (siloCell.qs_status === 'in_pruefung') {
            warnings.push(`Ziel-Silozelle '${siloCell.name}' befindet sich in QS-Prüfung. Beschickung erfolgt auf eigenes Risiko.`);
          }

          // Rule 3: Contamination warning (Spülcharge required when mixing BIO/CONV/GMO)
          if (contaminationRiskClass && siloCell.contamination_risk_class) {
            if (contaminationRiskClass !== siloCell.contamination_risk_class) {
              flushRequired = true;
              warnings.push(
                `Verschleppungsrisiko! Das einströmende Material (${contaminationRiskClass}) weicht von der Klasse der Zelle (${siloCell.contamination_risk_class}) ab.` +
                ` Eine vorherige Spülcharge des Förderwegs ist zwingend erforderlich!`
              );
            }
          }
        }
      }
    }

    // Evaluate edges along the path for Contamination Guard
    for (let i = 0; i < path.length - 1; i++) {
      const curr = path[i];
      const next = path[i + 1];
      const edge = flowEdges.find(e => e.from_node_id === curr && e.to_node_id === next);
      
      if (edge) {
        if (edge.status === 'blocked') {
          violations.push(`Förderkante von '${curr}' nach '${next}' ist mechanisch gesperrt.`);
        }
        if (edge.contamination_guard_enabled && edge.flush_required) {
          flushRequired = true;
          warnings.push(`Sicherheitswächter: Eine unbestätigte Spülung auf Förderabschnitt ${edge.conveyor_type.toUpperCase()} liegt vor.`);
        }
      }
    }

    const isValid = violations.length === 0;

    res.json({
      isValid,
      violations,
      warnings,
      flushRequired,
      path
    } as RouteValidationResult);
  });

  // Simple BFS Path-search
  function findPath(start: string, end: string): string[] | null {
    const queue: string[][] = [[start]];
    const visited = new Set<string>();

    while (queue.length > 0) {
      const shifted = queue.shift();
      if (!shifted) break;
      const currentPath = shifted;
      const lastNode = currentPath[currentPath.length - 1];

      if (lastNode === end) {
        return currentPath;
      }

      if (!visited.has(lastNode)) {
        visited.add(lastNode);
        
        // Find outgoing open borders
        const neighbors = flowEdges
          .filter(e => e.from_node_id === lastNode && e.status !== 'blocked')
          .map(e => e.to_node_id);

        for (const neighbor of neighbors) {
          if (!visited.has(neighbor)) {
            queue.push([...currentPath, neighbor]);
          }
        }
      }
    }

    return null;
  }

  // Vite development middleware
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on port ${PORT}`);
  });
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
