/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useState } from 'react';
import Header from './components/Header';
import SiloFlowsheet from './components/SiloFlowsheet';
import SiloCellList from './components/SiloCellList';
import RoutePlanner from './components/RoutePlanner';
import { MaterialFlowEdge, MaterialFlowNode, RouteValidationResult, SiloCell } from './types';
import { BookOpen } from 'lucide-react';

export default function App() {
  const [cells, setCells] = useState<SiloCell[]>([]);
  const [nodes, setNodes] = useState<MaterialFlowNode[]>([]);
  const [edges, setEdges] = useState<MaterialFlowEdge[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Router planner state selections
  const [selectedSourceId, setSelectedSourceId] = useState('node-intake-01');
  const [selectedTargetId, setSelectedTargetId] = useState('node-silo-cell-A1');
  
  // Animation / simulation state
  const [isSimulating, setIsSimulating] = useState(false);
  const [validationResult, setValidationResult] = useState<RouteValidationResult | null>(null);

  useEffect(() => {
    fetchWarehouseData();
  }, []);

  async function fetchWarehouseData() {
    setIsLoading(true);
    try {
      const [cellsRes, nodesRes, edgesRes] = await Promise.all([
        fetch('/api/warehouse/silo-cells'),
        fetch('/api/warehouse/material-flow/nodes'),
        fetch('/api/warehouse/material-flow/edges')
      ]);

      if (cellsRes.ok && nodesRes.ok && edgesRes.ok) {
        const cData = await cellsRes.json();
        const nData = await nodesRes.json();
        const eData = await edgesRes.json();
        setCells(cData);
        setNodes(nData);
        setEdges(eData);
      }
    } catch (err) {
      console.error('Fehler beim Abrufen der Stammdaten:', err);
    } finally {
      setIsLoading(false);
    }
  }

  // Handle flow clicking from diagram
  function handleSelectNode(nodeId: string, role: 'source' | 'target') {
    if (role === 'source') {
      setSelectedSourceId(nodeId);
    } else {
      setSelectedTargetId(nodeId);
    }
  }

  // Detect unresolved alerts
  const lockedCellsCount = cells.filter(c => c.qs_status === 'gesperrt').length;
  const inInspectionCount = cells.filter(c => c.qs_status === 'in_pruefung').length;
  const totalWarnings = lockedCellsCount + inInspectionCount + (validationResult?.flushRequired ? 1 : 0);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans antialiased" id="agrar-wms-app-frame">
      
      {/* Master Top Header */}
      <Header hasAlerts={totalWarnings > 0} alertCount={totalWarnings} />

      {/* Main Grid Wrapper */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Side: Silo Cells List & Status Display */}
        <div className="lg:col-span-1 flex flex-col space-y-6">
          <SiloCellList 
            cells={cells} 
            onCellAdded={fetchWarehouseData} 
            isLoading={isLoading} 
          />
          
          {/* Quick Info Desk */}
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h4 className="font-sans font-bold text-slate-900 text-xs tracking-wider uppercase mb-2 flex items-center gap-1.5">
              <BookOpen className="h-4 w-4 text-emerald-600" />
              Bedienungshinweise
            </h4>
            <div className="text-xs text-slate-600 space-y-1.5 font-medium leading-relaxed">
              <p>
                1. Klicken Sie auf einen beliebigen Knoten im **Mittleren Fließbild** und schwebende Tabs zu starten, oder wählen Sie die Punkte direkt über die Dropdown-Menüs im Steuerpult.
              </p>
              <p>
                2. Wählen Sie die gewünschte **Güteklasse** (z.B. BIO oder GMO). Wechseln Sie die Klasse bei der Befüllung einer Zelle, schlägt der **Verschleppungsschutz** Alarm und fordert einen Spül-Arbeitsgang an.
              </p>
              <p>
                3. **QS-Sperre**: Zelle A3 ist qualitätsgesperrt (Feuchtemessung ausstehend). Das System blockiert jegliche Wege dorthin automatisch, um Fehlmischungen im Keim zu ersticken.
              </p>
            </div>
          </div>
        </div>

        {/* Center & Right Sides: Flowsheet Diagram, Simulation controls */}
        <div className="lg:col-span-2 flex flex-col space-y-6">
          
          {/* Schematic Diagram Flows */}
          <SiloFlowsheet
            nodes={nodes}
            edges={edges}
            activePath={validationResult?.path || []}
            selectedSourceId={selectedSourceId}
            selectedTargetId={selectedTargetId}
            onSelectNode={handleSelectNode}
            isSimulating={isSimulating}
            onUpdateNodes={setNodes}
            onUpdateEdges={setEdges}
            onUpdateCells={setCells}
            cells={cells}
          />

          {/* Route Planning control deck */}
          <div className="grid grid-cols-1 gap-6">
            <RoutePlanner
              nodes={nodes}
              selectedSourceId={selectedSourceId}
              selectedTargetId={selectedTargetId}
              onChangeSource={setSelectedSourceId}
              onChangeTarget={setSelectedTargetId}
              onSetSimulation={setIsSimulating}
              isSimulating={isSimulating}
              onValidationChange={setValidationResult}
            />
          </div>

        </div>

      </main>

      {/* Persistent Floor Action Guard Bar */}
      <footer className="border-t border-slate-200 bg-white py-4 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-xs text-slate-400 font-semibold flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>© 2026 VALEO Agrar Logistik Gruppe GmbH</span>
          <div className="flex space-x-4">
            <span className="text-slate-500 font-mono">Modul: WM-AGRI-SILO-001</span>
            <span className="text-emerald-600">Mahl- & Mischanlagen Leitschnittstelle</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
