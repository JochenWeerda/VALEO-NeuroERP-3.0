/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useRef, useState } from 'react';
import { ConveyorType, MaterialFlowEdge, MaterialFlowNode, NodeStatus, NodeType, QsStatus, SiloCell } from '../types';
import {
  Activity,
  Compass,
  CornerDownRight,
  Cpu,
  Grid,
  Layers,
  MapPin,
  Plus,
  RefreshCw,
  Settings,
  Sliders,
  Terminal,
  Trash2,
  Truck,
  Zap,
} from 'lucide-react';

interface SiloFlowsheetProps {
  nodes: MaterialFlowNode[];
  edges: MaterialFlowEdge[];
  activePath: string[];
  selectedSourceId: string;
  selectedTargetId: string;
  onSelectNode: (_id: string, _role: 'source' | 'target') => void;
  isSimulating: boolean;
  onUpdateNodes: (_updated: MaterialFlowNode[]) => void;
  onUpdateEdges: (_updated: MaterialFlowEdge[]) => void;
  onUpdateCells?: (_updated: SiloCell[]) => void;
  cells: SiloCell[];
}

type TabType = 'flowsheet' | 'maplibre' | 'konva' | 'scada';

export default function SiloFlowsheet({
  nodes,
  edges,
  activePath,
  selectedSourceId,
  selectedTargetId,
  onSelectNode,
  isSimulating,
  onUpdateNodes,
  onUpdateEdges,
  onUpdateCells,
  cells
}: SiloFlowsheetProps) {
  const [activeTab, setActiveTab] = useState<TabType>('flowsheet');

  // --- TAB 1: FLOWSHEET (XYFLOW / REACT FLOW ENGINE) STATES ---
  const [zoomScale, setZoomScale] = useState<number>(1);
  const [draggedNodeId, setDraggedNodeId] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [selectedNode, setSelectedNode] = useState<MaterialFlowNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<MaterialFlowEdge | null>(null);
  
  // Custom Node Planner state
  const [newNodeCode, setNewNodeCode] = useState('');
  const [newNodeName, setNewNodeName] = useState('');
  const [newNodeType, setNewNodeType] = useState<NodeType>('valve');
  const [newFromNodeId, setNewFromNodeId] = useState('');
  const [newConveyorType, setNewConveyorType] = useState<ConveyorType>('slide');

  // Flowsheet Container Ref
  const containerRef = useRef<HTMLDivElement>(null);

  // --- TAB 2: MAPLIBRE / GPS BIRD EYE STATES ---
  const [mmxCoords, setMmxCoords] = useState({ lat: 53.48301, lng: 8.91402, x: 350, y: 350 });
  const [mmxHeading, setMmxHeading] = useState<number>(45);
  const [mmxSpeed, setMmxSpeed] = useState<number>(12);
  const [_mmxPathIndex, setMmxPathIndex] = useState(0);
  const [customPins, setCustomPins] = useState<{ id: string; name: string; lat: number; lng: number; x: number; y: number }[]>([]);
  const [_selectedMapTarget, setSelectedMapTarget] = useState<string | null>(null);

  // Path coordinates loop for mobile MMX
  const mmxRoutePoints = [
    { lat: 53.48301, lng: 8.91402, x: 280, y: 340, heading: 45 },
    { lat: 53.48315, lng: 8.91418, x: 390, y: 280, heading: 45 },
    { lat: 53.48335, lng: 8.91438, x: 500, y: 200, heading: 0 },
    { lat: 53.48350, lng: 8.91428, x: 450, y: 110, heading: 270 },
    { lat: 53.48330, lng: 8.91398, x: 300, y: 180, heading: 225 },
    { lat: 53.48308, lng: 8.91380, x: 190, y: 290, heading: 180 }
  ];

  // --- TAB 3: KONVA / CAD VIEW STATES ---
  const [cadSiloHeight, setCadSiloHeight] = useState<number>(240);
  const [cadSiloWidth, setCadSiloWidth] = useState<number>(140);
  const [cadHopperAngle, setCadHopperAngle] = useState<number>(45); // degree
  const [cadDensity, setCadDensity] = useState<number>(750); // kg / m^3 (weizen = 750)
  const [cadSiloFillPct, setCadSiloFillPct] = useState<number>(65);
  const [cadSiloRotation, setCadSiloRotation] = useState<number>(0);
  const [isResizingSilo, setIsResizingSilo] = useState<boolean>(false);
  const [resizeStart, setResizeStart] = useState({ height: 240, width: 140, clientX: 0, clientY: 0 });

  // --- TAB 4: SCADA/FUXA PLC MONITOR STATES ---
  const [forcedRegAddress, setForcedRegAddress] = useState('DB100.DBX0.1');
  const [forcedRegValue, setForcedRegValue] = useState('1');
  const [mqttLogs, setMqttLogs] = useState<string[]>([]);
  const [_mqttIndex, setMqttIndex] = useState(0);

  // Trigger telemetry timers
  useEffect(() => {
    // 1. MMX movement loop representing live GPS telemetry
    const mmxTimer = setInterval(() => {
      setMmxPathIndex((prev) => {
        const nextIdx = (prev + 1) % mmxRoutePoints.length;
        const currentPt = mmxRoutePoints[nextIdx];
        setMmxCoords({
          lat: currentPt.lat + (Math.random() - 0.5) * 0.00002,
          lng: currentPt.lng + (Math.random() - 0.5) * 0.00002,
          x: currentPt.x,
          y: currentPt.y
        });
        setMmxHeading(currentPt.heading);
        setMmxSpeed(Math.floor(10 + Math.random() * 8));
        return nextIdx;
      });
    }, 3000);

    // 2. FUXA / MQTT Stream simulate logger
    const logPool = [
      "SYSTEM: OPC-UA Connection Alive (Ping 14ms)",
      "POLL: Modbus TCP Register 40012 updated (Valves status word)",
      "MQTT: [wh-elbe-weser-01/IN-GOSSE-1/valve] state: OPEN",
      "MQTT: [wh-elbe-weser-01/WA-DURCH-1/weight] raw_value: 4192 kg",
      "SYS: Silo temperature sensor cell A1 reads: 14.2°C",
      "ALARM: Contamination guard checks edge WE-VERT-1 to BIO cell A2",
      "PLC: Watchdog tick ok, status: 0x00A1",
      "MQTT: [wh-elbe-weser-01/MMX-WAG-45/gps] lat: 53.483120N, lng: 8.914210E",
      "SYS: Volume math re-calibrated for silos block A",
      "POLL: Siemens S7 state: RUN, Active connections: 4"
    ];

    const mqttTimer = setInterval(() => {
      setMqttIndex((prevIdx) => {
        const nextIdx = (prevIdx + 1) % logPool.length;
        const log = `[${new Date().toLocaleTimeString()}] ${logPool[nextIdx]}`;
        setMqttLogs(prev => [log, ...prev].slice(0, 50));
        return nextIdx;
      });
    }, 2000);

    return () => {
      clearInterval(mmxTimer);
      clearInterval(mqttTimer);
    };
  }, []);

  // --- DETAILED HELPER OPERATIONS ---

  // Handle flow element mouse drag start
  const handleNodeDragStart = (e: React.MouseEvent, nodeId: string) => {
    if (activeTab !== 'flowsheet') return;
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return;
    
    setDraggedNodeId(nodeId);
    
    // Scale offset correctly
    setDragOffset({
      x: e.clientX - (node.layout_x || 0) * zoomScale,
      y: e.clientY - (node.layout_y || 0) * zoomScale
    });
    e.stopPropagation();
  };

  // Drag in progress
  const handleContainerMouseMove = (e: React.MouseEvent) => {
    if (draggedNodeId && activeTab === 'flowsheet') {
      const x = Math.round((e.clientX - dragOffset.x) / zoomScale);
      const y = Math.round((e.clientY - dragOffset.y) / zoomScale);
      
      // Boundaries
      const boundedX = Math.max(10, Math.min(x, 1200));
      const boundedY = Math.max(10, Math.min(y, 800));

      onUpdateNodes(
        nodes.map(node => node.id === draggedNodeId ? { ...node, layout_x: boundedX, layout_y: boundedY } : node)
      );
    }

    if (isResizingSilo && activeTab === 'konva') {
      const deltaX = e.clientX - resizeStart.clientX;
      const deltaY = e.clientY - resizeStart.clientY;
      setCadSiloWidth(Math.max(80, Math.min(resizeStart.width + deltaX, 350)));
      setCadSiloHeight(Math.max(100, Math.min(resizeStart.height + deltaY, 320)));
    }
  };

  // Drag completed
  const handleMouseUpOrLeave = () => {
    setDraggedNodeId(null);
    setIsResizingSilo(false);
  };

  // Add Custom Node & automatic routing
  const handleCreateNode = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNodeCode.trim() || !newNodeName.trim()) return;

    const codeUpper = newNodeCode.toUpperCase();
    const createdId = `node-custom-${Date.now()}`;
    
    // Position intelligently with some random offset
    const randomOffset = Math.floor(Math.random() * 50);
    const newNode: MaterialFlowNode = {
      id: createdId,
      tenant_id: 'jochen-weerda-agrar',
      warehouse_id: 'wh-elbe-weser-01',
      node_type: newNodeType,
      ref_type: null,
      ref_id: null,
      code: codeUpper,
      name: newNodeName,
      status: 'active',
      geo_lat: 53.483 + (Math.random() - 0.5) * 0.001,
      geo_lng: 8.914 + (Math.random() - 0.5) * 0.001,
      layout_x: 200 + randomOffset,
      layout_y: 200 + randomOffset,
      is_active: true
    };

    const updatedNodes = [...nodes, newNode];
    onUpdateNodes(updatedNodes);

    // Create edge link if requested
    if (newFromNodeId) {
      const newEdge: MaterialFlowEdge = {
        id: `edge-custom-${Date.now()}`,
        tenant_id: 'jochen-weerda-agrar',
        warehouse_id: 'wh-elbe-weser-01',
        from_node_id: newFromNodeId,
        to_node_id: createdId,
        conveyor_type: newConveyorType,
        status: 'open',
        contamination_guard_enabled: true,
        flush_required: false,
        max_capacity_kg_h: 40000
      };
      onUpdateEdges([...edges, newEdge]);
    }

    // Reset fields
    setNewNodeCode('');
    setNewNodeName('');
    setSelectedNode(newNode); // focus
  };

  // Delete node and its corresponding edges
  const handleDeleteNode = (nodeId: string) => {
    onUpdateNodes(nodes.filter(n => n.id !== nodeId));
    onUpdateEdges(edges.filter(e => e.from_node_id !== nodeId && e.to_node_id !== nodeId));
    setSelectedNode(null);
  };

  // Force register state in FUXA/PLC view
  const handleRegisterForceSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Determine which register matches which node code
    // Let's match based on input text e.g. "IN-GOSSE-1" or specific keywords
    const matchCode = forcedRegAddress.split('.')[0] || '';
    
    // Write forced event to MQTT output
    const timestamp = new Date().toLocaleTimeString();
    const logMessage = `[${timestamp}] ⚡ PLC FORCE COMMAND REGISTER [${forcedRegAddress}] -> Value: ${forcedRegValue}`;
    setMqttLogs(prev => [logMessage, ...prev]);

    // Let's visually toggle the corresponding node
    // Simple mock logic: if value is "0", block it. If "1" or "active", activate it.
    const targetNode = nodes.find(n => forcedRegAddress.toUpperCase().includes(n.code.toUpperCase()) || n.code.toUpperCase() === matchCode.toUpperCase());
    
    if (targetNode) {
      const tn = targetNode;
      const newStatus: NodeStatus = (forcedRegValue === '0' || forcedRegValue.toLowerCase() === 'false') ? 'blocked' : 'active';
      onUpdateNodes(nodes.map(n => (n.id === tn.id ? { ...n, status: newStatus } : n)));

      // Force update Silo QsStatus if node is a silo cell
      if (tn.node_type === 'silo_cell' && tn.ref_id && onUpdateCells) {
        const newQs: QsStatus = (forcedRegValue === '0' || forcedRegValue.toLowerCase() === 'false') ? 'gesperrt' : 'frei';
        const refId = tn.ref_id;
        onUpdateCells(cells.map(c => (c.id === refId ? { ...c, qs_status: newQs } : c)));
      }
    }
  };

  // Handle map satellite grid placement click
  const handleMapGridClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = Math.round(e.clientX - rect.left);
    const y = Math.round(e.clientY - rect.top);

    // Turn click offset into relative lat/lng inside our Elbe-Weser paddock coordinates bounds
    const centerLat = 53.48312;
    const centerLng = 8.91421;
    // Map bounds represents ~100m scaling
    const computedLat = centerLat + (300 - y) * 0.000004;
    const computedLng = centerLng + (x - 400) * 0.000006;

    const newPin = {
      id: `pin-custom-${Date.now()}`,
      name: `Kombisensor #${Math.floor(100 + Math.random() * 900)}`,
      lat: computedLat,
      lng: computedLng,
      x,
      y
    };

    setCustomPins(prev => [...prev, newPin]);
    setSelectedMapTarget(newPin.id);
  };

  // Calc CAD silo dimensions helper
  const calculateSiloCapacity = () => {
    // Volume approx = area (based on box + hopper cone cylinder slice)
    // Silo Height in px corresponding to meters (scaled 1px = 5cm, so 200px = 10m)
    const mHeight = cadSiloHeight / 20;
    const mWidth = cadSiloWidth / 20;
    const radius = mWidth / 2;
    // Volume of cylindrical section
    const cylVolume = Math.PI * radius * radius * (mHeight * 0.7);
    // Volume of conical hopper (Trichter) bottom
    const hopperHeight = radius * Math.tan((cadHopperAngle * Math.PI) / 180);
    const coneVolume = (Math.PI * radius * radius * hopperHeight) / 3;
    const totalVolumeM3 = cylVolume + coneVolume;
    
    // total capacity in kg
    const totalKg = totalVolumeM3 * cadDensity;
    const currentKg = totalKg * (cadSiloFillPct / 100);

    return {
      totalVolumeM3: Math.round(totalVolumeM3),
      totalKg: Math.round(totalKg),
      currentKg: Math.round(currentKg)
    };
  };

  const cadMetrics = calculateSiloCapacity();

  // Return dynamic color according to node type for React Flow / xyflow
  function getNodeBorderColor(node: MaterialFlowNode) {
    if (selectedSourceId === node.id) return 'border-emerald-500 ring-2 ring-emerald-500/30';
    if (selectedTargetId === node.id) return 'border-sky-500 ring-2 ring-sky-500/30';
    if (activePath.includes(node.id)) return 'border-emerald-400 bg-white shadow-[0_0_8px_rgba(16,185,129,0.25)]';
    if (node.status === 'blocked') return 'border-rose-400 bg-rose-50/10';
    if (node.status === 'cleaning') return 'border-amber-400 bg-amber-50/10';
    if (node.status === 'maintenance') return 'border-indigo-400 bg-indigo-50/10';
    return 'border-slate-200 bg-white hover:border-slate-300';
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden flex flex-col min-h-[640px]" id="silo-material-flow-module">
      
      {/* 🧭 PREMIUM WORKBENCH TAB MENU BAR */}
      <div className="bg-slate-900 px-4 py-3 flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-slate-800 gap-3">
        
        {/* Module Title */}
        <div className="flex items-center space-x-2.5">
          <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></div>
          <div>
            <h3 className="text-sm font-black tracking-tight text-white uppercase">Schnittstellen-Visualisierung & Edit-Koffer</h3>
            <p className="text-[10px] text-slate-400 font-semibold font-mono">VALEO NeuroERP 3.0 • Evaluation Open-Source-Frameworks</p>
          </div>
        </div>

        {/* Tab Toggle buttons */}
        <div className="flex bg-slate-800 p-1 rounded-lg border border-slate-700/80 w-full sm:w-auto">
          <button
            onClick={() => setActiveTab('flowsheet')}
            className={`flex-1 sm:flex-initial text-xs px-2.5 py-1.5 rounded-md font-bold tracking-tight transition-all flex items-center justify-center space-x-1 cursor-pointer ${
              activeTab === 'flowsheet' 
                ? 'bg-emerald-600 text-white shadow-xs' 
                : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
            }`}
            title="React Flow / xyflow Prototyp"
          >
            <Activity className="h-3.5 w-3.5" />
            <span>xyflow Editor</span>
          </button>
          
          <button
            onClick={() => setActiveTab('maplibre')}
            className={`flex-1 sm:flex-initial text-xs px-2.5 py-1.5 rounded-md font-bold tracking-tight transition-all flex items-center justify-center space-x-1 cursor-pointer ${
              activeTab === 'maplibre' 
                ? 'bg-emerald-600 text-white shadow-xs' 
                : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
            }`}
            title="MapLibre GL Gesteuerter Hof-Bird-View"
          >
            <MapPin className="h-3.5 w-3.5" />
            <span>MapLibre GPS</span>
          </button>

          <button
            onClick={() => setActiveTab('konva')}
            className={`flex-1 sm:flex-initial text-xs px-2.5 py-1.5 rounded-md font-bold tracking-tight transition-all flex items-center justify-center space-x-1 cursor-pointer ${
              activeTab === 'konva' 
                ? 'bg-emerald-600 text-white shadow-xs' 
                : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
            }`}
            title="Konva.js CAD 2D Canvas Editor"
          >
            <Sliders className="h-3.5 w-3.5" />
            <span>Konvas CAD</span>
          </button>

          <button
            onClick={() => setActiveTab('scada')}
            className={`flex-1 sm:flex-initial text-xs px-2.5 py-1.5 rounded-md font-bold tracking-tight transition-all flex items-center justify-center space-x-1 cursor-pointer ${
              activeTab === 'scada' 
                ? 'bg-emerald-600 text-white shadow-xs' 
                : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
            }`}
            title="FUXA HMI SCADA PLC Registers"
          >
            <Cpu className="h-3.5 w-3.5" />
            <span>FUXA SCADA</span>
          </button>

        </div>
      </div>

      {/* 📦 WORKBENCH CENTRAL ACTIVE VIEWPORT */}
      <div className="flex-1 bg-slate-50 relative p-4" onMouseMove={handleContainerMouseMove} onMouseUp={handleMouseUpOrLeave} onMouseLeave={handleMouseUpOrLeave}>

        {/* ========================================== */}
        {/* TAB 1: FLOWSHEET (XYFLOW / REACT FLOW GRIDS) */}
        {/* ========================================== */}
        {activeTab === 'flowsheet' && (
          <div className="space-y-4">
            
            {/* Workbench Info header */}
            <div className="bg-emerald-50/50 border border-emerald-100 rounded-lg p-3.5 flex flex-col md:flex-row md:items-center justify-between gap-3 shadow-2xs">
              <div className="flex items-start space-x-2.5">
                <div className="p-1.5 rounded bg-emerald-500 text-white mt-0.5">
                  <Activity className="h-4 w-4 animate-pulse" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider leading-none">xyflow Process Flow Editor</h4>
                  <p className="text-[11px] text-slate-500 font-medium mt-1">
                    Drag elements inside the workbench to move coordinates. Double-click any element to configure register settings, delete nodes, or review capacities.
                  </p>
                </div>
              </div>
              
              {/* Zoom & Action controller */}
              <div className="flex items-center space-x-3 text-xs">
                <span className="text-[10px] font-mono font-bold text-slate-500 uppercase">Maßstab (Zoom): {Math.round(zoomScale * 100)}%</span>
                <input 
                  type="range" 
                  min="0.6" 
                  max="1.4" 
                  step="0.1" 
                  value={zoomScale} 
                  onChange={e => setZoomScale(parseFloat(e.target.value))}
                  className="w-24 cursor-pointer"
                />
                <button 
                  onClick={() => setZoomScale(1)} 
                  className="border border-slate-200 hover:bg-white text-slate-600 p-1 px-1.5 rounded text-[10px] bg-slate-50 cursor-pointer font-bold"
                >
                  Reset
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-4 gap-4 items-start">
              
              {/* Left Side Add Custom Node palette */}
              <div className="xl:col-span-1 bg-white border border-slate-200 rounded-xl p-4 shadow-2xs space-y-4">
                <div className="border-b border-slate-100 pb-2">
                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
                    <Plus className="h-3.5 w-3.5 text-emerald-600" />
                    Knoten-Projektierer
                  </h4>
                  <p className="text-[11px] text-slate-500 font-medium">Neuen mechanischen Träger in den Flowsheet-Baum setzen.</p>
                </div>

                <form onSubmit={handleCreateNode} className="space-y-3">
                  <div>
                    <label className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">Typ-Klassifizierung</label>
                    <select
                      value={newNodeType}
                      onChange={e => setNewNodeType(e.target.value as NodeType)}
                      className="w-full text-xs border border-slate-300 rounded px-2 py-1.5 bg-white text-slate-800"
                    >
                      <option value="intake">Gosse / Annahme (Intake)</option>
                      <option value="scale">Durchlaufwaage (Scale)</option>
                      <option value="elevator">Hopperelevator (Elevator)</option>
                      <option value="conveyor">Förderband (Conveyor)</option>
                      <option value="valve">Umlenk-Ventil (Valve)</option>
                      <option value="diverter">Dreiwegeweiche (Diverter)</option>
                      <option value="mixer">Präzisionsmischer (Mixer)</option>
                      <option value="mobile_unit">Mobile Mahlgruppe (MMX)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">Knoten-Code (Nummer)</label>
                    <input 
                      type="text" 
                      placeholder="Z.B. VE-BYPASS-02" 
                      value={newNodeCode} 
                      onChange={e => setNewNodeCode(e.target.value)}
                      className="w-full text-xs border border-slate-300 rounded px-2.5 py-1.5 bg-white text-slate-800"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">Individueller Name</label>
                    <input 
                      type="text" 
                      placeholder="Bypass-Weiche West" 
                      value={newNodeName} 
                      onChange={e => setNewNodeName(e.target.value)}
                      className="w-full text-xs border border-slate-300 rounded px-2.5 py-1.5 bg-white text-slate-800"
                      required
                    />
                  </div>

                  <div className="border-t border-dashed border-slate-100 pt-2 space-y-2">
                    <p className="text-[9px] font-bold text-slate-400 uppercase tracking-wider">Verbindung legen</p>
                    <div>
                      <label className="block text-[9px] text-slate-500 mb-1">Von vorhandenem Knoten:</label>
                      <select
                        value={newFromNodeId}
                        onChange={e => setNewFromNodeId(e.target.value)}
                        className="w-full text-xs border border-slate-300 rounded px-2 py-1 bg-white text-slate-800"
                      >
                        <option value="">-- Keine Verbindung --</option>
                        {nodes.map(n => <option key={n.id} value={n.id}>{n.name} ({n.code})</option>)}
                      </select>
                    </div>

                    {newFromNodeId && (
                      <div>
                        <label className="block text-[9px] text-slate-500 mb-1">Mechanische Förderungsart:</label>
                        <select
                          value={newConveyorType}
                          onChange={e => setNewConveyorType(e.target.value as ConveyorType)}
                          className="w-full text-xs border border-slate-300 rounded px-2 py-1 bg-white text-slate-800"
                        >
                          <option value="slide">Rohrschieber</option>
                          <option value="belt">Förderband</option>
                          <option value="screw">Förderschnecke</option>
                          <option value="elevator">Vertikal-Elevator</option>
                          <option value="gravity">Gefällestrom Fallrohr</option>
                        </select>
                      </div>
                    )}
                  </div>

                  <button
                    type="submit"
                    className="w-full py-1.5 text-xs text-white bg-emerald-600 hover:bg-emerald-700 rounded-md font-bold transition-colors cursor-pointer"
                  >
                    Knoten platzieren
                  </button>
                </form>

              </div>

              {/* Central Draggable Node Canvas Workspace Area */}
              <div className="xl:col-span-3 border border-slate-200 rounded-xl relative overflow-hidden bg-slate-900/5 min-h-[480px]" id="xyflow-sandbox-board">
                
                {/* SVG connection lines layer */}
                <div 
                  ref={containerRef}
                  className="absolute inset-0 select-none z-0"
                  style={{
                    backgroundImage: 'radial-gradient(ellipse at center, rgba(148,163,184,0.15) 1px, transparent 1px)',
                    backgroundSize: `${24 * zoomScale}px ${24 * zoomScale}px`,
                    transformOrigin: 'top left'
                  }}
                >
                  <svg className="absolute inset-0 pointer-events-none w-full h-full">
                    {/* Draw connected lines */}
                    {edges.map(edge => {
                      const fromNode = nodes.find(n => n.id === edge.from_node_id);
                      const toNode = nodes.find(n => n.id === edge.to_node_id);
                      if (!fromNode || !toNode) return null;

                      const fx = ((fromNode.layout_x || 0) + 70) * zoomScale;
                      const fy = ((fromNode.layout_y || 0) + 30) * zoomScale;
                      const tx = ((toNode.layout_x || 0) + 70) * zoomScale;
                      const ty = ((toNode.layout_y || 0) + 30) * zoomScale;

                      const isActivePath = activePath.includes(edge.from_node_id) && activePath.includes(edge.to_node_id);
                      const isSim = isSimulating && isActivePath;

                      let stroke = '#cbd5e1';
                      let strokeWidth = 2;
                      let dash = '';
                      let strokeClass = '';

                      if (edge.status === 'blocked') {
                        stroke = '#f87171';
                        strokeWidth = 2.5;
                        dash = '4 4';
                      } else if (isSim) {
                        stroke = '#10b981';
                        strokeWidth = 3.5;
                        dash = '6 6';
                        strokeClass = 'animate-[flow_1.5s_linear_infinite]';
                      } else if (isActivePath) {
                        stroke = '#059669';
                        strokeWidth = 3;
                      }

                      return (
                        <g key={edge.id} className="cursor-pointer pointer-events-auto" onClick={() => setSelectedEdge(edge)}>
                          <path
                            d={`M ${fx} ${fy} C ${(fx+tx)/2} ${fy}, ${(fx+tx)/2} ${ty}, ${tx} ${ty}`}
                            fill="none"
                            stroke={stroke}
                            strokeWidth={strokeWidth}
                            strokeDasharray={dash}
                            className={strokeClass}
                          />
                          {/* Mini path hover spot */}
                          <path
                            d={`M ${fx} ${fy} C ${(fx+tx)/2} ${fy}, ${(fx+tx)/2} ${ty}, ${tx} ${ty}`}
                            fill="none"
                            stroke="transparent"
                            strokeWidth="10"
                            className="hover:stroke-emerald-200/40"
                          />
                        </g>
                      );
                    })}
                  </svg>

                  {/* DOM Interactive nodes absolute positioning */}
                  {nodes.map(node => {
                    const isSelected = selectedNode?.id === node.id;
                    const borderProps = getNodeBorderColor(node);

                    return (
                      <div
                        key={node.id}
                        onMouseDown={(e) => handleNodeDragStart(e, node.id)}
                        onDoubleClick={() => setSelectedNode(node)}
                        style={{
                          left: `${(node.layout_x || 0) * zoomScale}px`,
                          top: `${(node.layout_y || 0) * zoomScale}px`,
                          transform: `scale(${zoomScale})`,
                          transformOrigin: 'top left',
                          zIndex: isSelected ? 40 : 10
                        }}
                        className={`absolute w-[140px] px-2.5 py-1.5 rounded-lg border shadow-xs bg-white select-none transition-shadow cursor-move flex items-center space-x-2 ${borderProps}`}
                      >
                        {/* Type Icon */}
                        <div className={`p-1.5 rounded ${
                          node.status === 'blocked' ? 'bg-rose-50 text-rose-500' : 'bg-slate-50 text-slate-600'
                        }`}>
                          {node.node_type === 'silo_cell' && <Layers className="h-4 w-4" />}
                          {node.node_type === 'scale' && <Grid className="h-4 w-4" />}
                          {node.node_type === 'elevator' && <RefreshCw className="h-4 w-4" />}
                          {node.node_type === 'diverter' && <Settings className="h-4 w-4" />}
                          {node.node_type === 'mixer' && <RefreshCw className="h-4 w-4 animate-spin" style={{ animationDuration: '6s' }} />}
                          {node.node_type === 'intake' && <CornerDownRight className="h-4 w-4" />}
                          {node.node_type === 'mobile_unit' && <Truck className="h-4 w-4" />}
                        </div>

                        {/* Node details */}
                        <div className="min-w-0 flex-1">
                          <p className="text-[8px] font-mono leading-none text-slate-400 font-bold uppercase">{node.code}</p>
                          <p className="text-[10px] font-bold text-slate-700 truncate mt-0.5" title={node.name}>{node.name}</p>
                          <div className="flex mt-1">
                            {node.status !== 'active' && (
                              <span className="text-[7px] font-black uppercase tracking-wider px-1 rounded-sm bg-rose-500 text-white">
                                {node.status.toUpperCase()}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Grid watermark label overlay */}
                <div className="absolute top-2.5 left-2.5 pointer-events-none bg-white/70 backdrop-blur-md px-1.5 py-0.5 rounded border border-slate-200 text-[10px] tracking-wider text-slate-500 uppercase font-bold">
                  xyflow Interactive Canvas
                </div>

                {/* Selected Node Inspector Sidebar overlay */}
                {selectedNode && (
                  <div className="absolute right-0 top-0 bottom-0 w-64 bg-white border-l border-slate-200 shadow-xl p-4 z-50 flex flex-col justify-between overflow-y-auto">
                    <div>
                      <div className="flex items-center justify-between border-b border-slate-100 pb-2 mb-3">
                        <span className="text-[10px] font-bold font-mono tracking-wider bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">
                          DETAILS: {selectedNode.code}
                        </span>
                        <button 
                          onClick={() => setSelectedNode(null)} 
                          className="text-slate-400 hover:text-slate-700 font-bold text-xs"
                        >
                          ✕
                        </button>
                      </div>

                      <div className="space-y-4">
                        <div>
                          <label className="block text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-1">Anzeigename</label>
                          <input 
                            type="text" 
                            value={selectedNode.name} 
                            onChange={(e) => {
                              const updatedName = e.target.value;
                              onUpdateNodes(nodes.map(n => n.id === selectedNode.id ? { ...n, name: updatedName } : n));
                              setSelectedNode({ ...selectedNode, name: updatedName });
                            }}
                            className="w-full text-xs font-semibold border border-slate-200 rounded px-2.5 py-1.5 bg-slate-50 text-slate-800"
                          />
                        </div>

                        <div>
                          <label className="block text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-1">Maschinen-Status</label>
                          <select 
                            value={selectedNode.status} 
                            onChange={(e) => {
                              const updatedStatus = e.target.value as NodeStatus;
                              onUpdateNodes(nodes.map(n => n.id === selectedNode.id ? { ...n, status: updatedStatus } : n));
                              setSelectedNode({ ...selectedNode, status: updatedStatus });
                            }}
                            className="w-full text-xs border border-slate-200 rounded px-2 py-1.5 bg-slate-50 text-slate-800 uppercase font-black"
                          >
                            <option value="active">🟢 Betriebsbereit (Active)</option>
                            <option value="blocked">🔴 Blockiert (Blocked)</option>
                            <option value="cleaning">🟡 Reinigung (Cleaning)</option>
                            <option value="maintenance">🔵 Wartung (Maintenance)</option>
                          </select>
                        </div>

                        <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5 space-y-1 text-[10px] font-mono">
                          <p className="text-slate-500">Koordinaten im Werk:</p>
                          <p className="text-slate-700 font-bold">X: {selectedNode.layout_x}px, Y: {selectedNode.layout_y}px</p>
                          <p className="text-slate-500 mt-2">Georeferenz (GPS):</p>
                          <p className="text-slate-700 font-bold">Lat: {selectedNode.geo_lat?.toFixed(5)}</p>
                          <p className="text-slate-700 font-bold">Lng: {selectedNode.geo_lng?.toFixed(5)}</p>
                        </div>
                      </div>
                    </div>

                    <div className="border-t border-slate-100 pt-3 flex flex-col space-y-2">
                      <div className="flex justify-between space-x-2">
                        <button
                          onClick={() => onSelectNode(selectedNode.id, 'source')}
                          className="flex-1 py-1 px-1.5 text-[9px] text-emerald-800 bg-emerald-50 border border-emerald-200 hover:bg-emerald-100 font-bold rounded cursor-pointer text-center"
                        >
                          Als Quelle
                        </button>
                        <button
                          onClick={() => onSelectNode(selectedNode.id, 'target')}
                          className="flex-1 py-1 px-1.5 text-[9px] text-sky-800 bg-sky-50 border border-sky-200 hover:bg-sky-100 font-bold rounded cursor-pointer text-center"
                        >
                          Als Ziel
                        </button>
                      </div>

                      <button
                        onClick={() => handleDeleteNode(selectedNode.id)}
                        className="w-full py-1.5 text-xs text-rose-600 hover:bg-rose-50 border border-rose-200 font-bold rounded-lg transition-colors cursor-pointer flex items-center justify-center space-x-1"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                        <span>Knoten entfernen</span>
                      </button>
                    </div>
                  </div>
                )}

                {/* Selected Edge Inspector overlay */}
                {selectedEdge && (
                  <div className="absolute left-2.5 bottom-2.5 bg-white border border-slate-300 rounded-xl p-3 shadow-lg max-w-sm z-50">
                    <div className="flex items-center justify-between pb-1.5 mb-2 border-b border-slate-100">
                      <span className="text-[10px] uppercase font-mono font-bold text-slate-500">Verbindung (Kante)</span>
                      <button onClick={() => setSelectedEdge(null)} className="text-slate-400 hover:text-slate-700 text-xs">✕</button>
                    </div>

                    <div className="space-y-2.5 text-[11px]">
                      <div className="flex justify-between">
                        <span className="text-slate-500">Kopplung:</span>
                        <span className="text-slate-700 font-bold">{selectedEdge.conveyor_type.toUpperCase()}</span>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <span className="text-slate-500">Verschleppungs-Wächter:</span>
                        <button 
                          onClick={() => {
                            const updated = edges.map(e => e.id === selectedEdge.id ? { ...e, contamination_guard_enabled: !e.contamination_guard_enabled } : e);
                            onUpdateEdges(updated);
                            setSelectedEdge({ ...selectedEdge, contamination_guard_enabled: !selectedEdge.contamination_guard_enabled });
                          }}
                          className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                            selectedEdge.contamination_guard_enabled ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-600'
                          }`}
                        >
                          {selectedEdge.contamination_guard_enabled ? "AKTIVIERT" : "AUSGESCHALTET"}
                        </button>
                      </div>

                      <div className="flex justify-between items-center">
                        <span className="text-slate-500">Weg-Zustand:</span>
                        <select 
                          value={selectedEdge.status} 
                          onChange={(e) => {
                            const updatedStatus = e.target.value as any;
                            const updated = edges.map(e => e.id === selectedEdge.id ? { ...e, status: updatedStatus } : e);
                            onUpdateEdges(updated);
                            setSelectedEdge({ ...selectedEdge, status: updatedStatus });
                          }}
                          className="text-[10px] border border-slate-200 rounded px-1"
                        >
                          <option value="open">🟢 GEÖFFNET</option>
                          <option value="blocked">🔴 VERSTOPFT</option>
                        </select>
                      </div>
                    </div>
                  </div>
                )}

              </div>

            </div>

          </div>
        )}

        {/* ========================================== */}
        {/* TAB 2: MAPLIBRE GL JS (GEOPOSITIONAL MAP) */}
        {/* ========================================== */}
        {activeTab === 'maplibre' && (
          <div className="space-y-4">
            
            {/* MapLibre Info */}
            <div className="bg-sky-50/50 border border-sky-100 rounded-lg p-3.5 flex flex-col md:flex-row md:items-center justify-between gap-3 shadow-2xs">
              <div className="flex items-start space-x-2.5">
                <div className="p-1.5 rounded bg-sky-500 text-white mt-0.5">
                  <MapPin className="h-4 w-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider leading-none">MapLibre Hof-Bird-View & Telemetrie-Sonnar</h4>
                  <p className="text-[11px] text-slate-500 font-medium mt-1">
                    Anzeige des Hofgeländes über georeferenzierte Rasterpunkte. Der **LKW-Mischwagen (MMX-Tropper)** sendet zyklische GPS-Signale an das VALEO-Register. Klicken Sie auf das Gitter, um weitere Sensoren zu verbauen.
                  </p>
                </div>
              </div>
              <div className="text-right text-xs">
                <span className="inline-block bg-sky-100 text-sky-800 font-mono px-2 py-0.5 rounded font-black">Center: 53.4831° N, 8.9142° E</span>
              </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-4 gap-4 items-start">
              
              {/* Telemetry sidebar */}
              <div className="xl:col-span-1 bg-white border border-slate-200 rounded-xl p-4 shadow-2xs space-y-4.5">
                
                {/* Delivery vehicle tracking */}
                <div>
                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 flex items-center gap-1">
                    <Truck className="h-4 w-4 text-sky-500" />
                    MMX LKW Telemetrie
                  </h4>
                  <div className="bg-slate-50 rounded-lg p-3 border border-slate-100 space-y-2 font-mono text-[11px]">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Fahrzeug:</span>
                      <span className="text-slate-800 font-bold">TRO-MMX LKW-04</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Breite:</span>
                      <span className="text-sky-700 font-bold">{mmxCoords.lat.toFixed(6)}° N</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Länge:</span>
                      <span className="text-sky-700 font-bold">{mmxCoords.lng.toFixed(6)}° E</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Kompass:</span>
                      <span className="text-slate-700 font-bold">{mmxHeading}° (Nordost)</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Geschwindigkeit:</span>
                      <span className="text-emerald-600 font-bold">{mmxSpeed} km/h</span>
                    </div>
                    <div className="flex justify-between border-t border-slate-200/60 pt-1.5 mt-1.5">
                      <span className="text-slate-500">Zustand:</span>
                      <span className="rounded bg-sky-100 text-sky-800 px-1 py-0.5 font-sans font-bold text-[9px]">AUSLIEFERUNG</span>
                    </div>
                  </div>
                </div>

                {/* Georeferenced Placed Bins list */}
                <div>
                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Georeferenzierte Silozellen</h4>
                  <div className="space-y-1.5">
                    {nodes.filter(n => n.node_type === 'silo_cell').map(node => (
                      <div key={node.id} className="flex justify-between items-center text-xs p-1.5 border border-slate-100 bg-slate-50 rounded">
                        <span className="font-bold text-slate-700">{node.code}</span>
                        <span className="font-mono text-[10px] text-slate-400">({node.geo_lat?.toFixed(5)}, {node.geo_lng?.toFixed(5)})</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Custom Placements */}
                {customPins.length > 0 && (
                  <div>
                    <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">Geplante Feldlager-Sensoren</h4>
                    <div className="space-y-1.5">
                      {customPins.map(pin => (
                        <div key={pin.id} className="flex justify-between items-center text-xs p-2 bg-slate-50 border border-sky-100 rounded">
                          <span className="font-bold text-sky-800">{pin.name}</span>
                          <button 
                            onClick={(e) => { e.stopPropagation(); setCustomPins(prev => prev.filter(p => p.id !== pin.id)); }}
                            className="text-slate-400 hover:text-red-500"
                          >
                            ✕
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              </div>

              {/* Map Canvas satellite simulator */}
              <div 
                onClick={handleMapGridClick}
                className="xl:col-span-3 h-[480px] rounded-xl border border-slate-200 overflow-hidden relative cursor-crosshair bg-slate-950"
                id="maplibre-satellite bg"
              >
                {/* Satellite Radar visual grids */}
                <div className="absolute inset-0 z-0 pointer-events-none opacity-40">
                  <div className="w-full h-full" style={{
                    backgroundImage: 'linear-gradient(rgba(14,165,233,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(14,165,233,0.1) 1px, transparent 1px)',
                    backgroundSize: '40px 40px'
                  }} />
                  {/* Concentric radar rings */}
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full border border-sky-500/10 w-[200px] h-[200px]" />
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full border border-sky-500/10 w-[400px] h-[400px]" />
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full border border-sky-500/5 w-[600px] h-[600px]" />
                </div>

                {/* Drawn Farm Satellite layout mock */}
                <div className="absolute inset-x-8 inset-y-12 border border-slate-700/50 bg-slate-900 rounded-2xl flex items-center justify-center pointer-events-none z-0">
                  <div className="text-center">
                    <span className="text-[10px] font-mono tracking-widest text-slate-500 font-bold uppercase">Hofgut Elbe-Weser 01 Satellitenbereich</span>
                    <p className="text-[9px] text-slate-600 mt-1 font-mono">BIRD'S EYE SCALE 1:1200 • ACCURACY ±0.8m</p>
                  </div>
                </div>

                {/* Isometric styled silhouettes representing physical structures */}
                <div className="absolute top-[60px] right-[100px] w-24 h-44 bg-slate-800/80 border border-slate-700 text-center rounded flex items-center justify-center font-mono text-[9px] text-sky-400 pointer-events-none uppercase tracking-widest">
                  <span>SILO BLOCK A</span>
                </div>
                
                <div className="absolute top-[280px] left-[150px] w-32 h-20 bg-slate-800/80 border border-slate-700 text-center rounded flex items-center justify-center font-mono text-[9px] text-sky-400 pointer-events-none uppercase tracking-widest">
                  <span>WERKS-ZUGANG</span>
                </div>

                {/* Station markers mapped inside coordinates */}
                {nodes.map(node => {
                  let mx = 400; // default middle
                  let my = 200;

                  if (node.node_type === 'silo_cell') {
                    mx = 650;
                    my = 100 + (node.code === 'S-A1' ? 20 : node.code === 'S-A2' ? 60 : node.code === 'S-A3' ? 100 : 140);
                  } else if (node.node_type === 'intake') { mx = 120; my = 150; }
                  else if (node.node_type === 'scale') { mx = 220; my = 150; }
                  else if (node.node_type === 'elevator') { mx = 320; my = 210; }
                  else if (node.node_type === 'mixer') { mx = 500; my = 280; }

                  return (
                    <div 
                      key={node.id}
                      style={{ left: `${mx}px`, top: `${my}px` }}
                      className="absolute -translate-x-1/2 -translate-y-1/2 z-20 pointer-events-none flex flex-col items-center"
                    >
                      <div className="h-2 w-2 rounded-full bg-sky-400 ring-4 ring-sky-400/20 shadow-xs" />
                      <div className="bg-slate-900 border border-slate-700 px-1 py-0.5 rounded text-[8px] font-mono mt-1 font-bold text-sky-300">
                        {node.code}
                      </div>
                    </div>
                  );
                })}

                {/* Custom placed sensor pins */}
                {customPins.map(pin => (
                  <div
                    key={pin.id}
                    style={{ left: `${pin.x}px`, top: `${pin.y}px` }}
                    className="absolute -translate-x-1/2 -translate-y-1/2 z-30 pointer-events-none flex flex-col items-center"
                  >
                    <div className="h-3.5 w-3.5 rounded-full bg-rose-500 border-2 border-white animate-pulse" />
                    <div className="bg-slate-900 border border-rose-500 px-1 py-0.5 rounded text-[8px] font-mono mt-1 text-rose-300 font-bold shadow-md">
                      {pin.name}
                    </div>
                  </div>
                ))}

                {/* Real-time moving MMX delivery truck on map */}
                <div 
                  style={{ 
                    left: `${mmxCoords.x}px`, 
                    top: `${mmxCoords.y}px`,
                    transition: 'left 3s linear, top 3s linear'
                  }}
                  className="absolute -translate-x-1/2 -translate-y-1/2 z-40 bg-sky-500 text-white rounded-full p-2 border-2 border-slate-900 shadow-xl flex items-center justify-center hover:bg-emerald-500 transition-colors pointer-events-none"
                >
                  <Truck className="h-4.5 w-4.5 pointer-events-none" style={{ transform: `rotate(${mmxHeading}deg)`, transition: 'transform 1s ease' }} />
                  {/* Ping signal ring */}
                  <span className="absolute -inset-1 rounded-full border border-sky-400 bg-sky-400/20 animate-ping" />
                </div>

                {/* UI Map Overlays */}
                <div className="absolute bottom-3 left-3 bg-slate-900/90 border border-slate-700 rounded-lg p-2 font-mono text-[9px] text-slate-400 space-y-1 z-30">
                  <div className="flex items-center gap-1.5 font-bold">
                    <span className="inline-block h-2.5 w-2.5 rounded-full bg-sky-500" />
                    <span>LKW-Mischwagen (MMX)</span>
                  </div>
                  <div className="flex items-center gap-1.5 font-bold">
                    <span className="inline-block h-2.5 w-2.5 rounded-full bg-sky-400" />
                    <span>Werksgebäude-Kopen</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="inline-block h-2.5 w-2.5 rounded-full bg-rose-600" />
                    <span>Klicksensoren (GPS verbucht)</span>
                  </div>
                </div>

                <div className="absolute top-3 right-3 bg-slate-900/90 border border-slate-700 rounded-lg p-2 font-mono text-[10px] text-slate-300 z-30 flex items-center gap-1.5">
                  <Compass className="h-4 w-4 text-sky-400 animate-spin" style={{ animationDuration: '20s' }} />
                  <span>NORD AUSRICHTUNG</span>
                </div>

              </div>

            </div>

          </div>
        )}

        {/* ========================================== */}
        {/* TAB 3: KONVA.JS / REACT-KONVA CAD DRAWING */}
        {/* ========================================== */}
        {activeTab === 'konva' && (
          <div className="space-y-4">
            
            {/* Konva Blueprint Info */}
            <div className="bg-amber-50/50 border border-amber-100 rounded-lg p-3.5 flex flex-col md:flex-row md:items-center justify-between gap-3 shadow-2xs">
              <div className="flex items-start space-x-2.5">
                <div className="p-1.5 rounded bg-amber-500 text-white mt-0.5">
                  <Sliders className="h-4 w-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider leading-none">Konva.js 2D CAD Konstruktionstafel & Statikrechner</h4>
                  <p className="text-[11px] text-slate-500 font-medium mt-1">
                    Simuliert die interaktiven Zeichnungs- und Manipulations-Features einer `react-konva` Leinwand. Ziehen Sie den CAD-Kopf oder verändern Sie mit dem Drehknopf die Neigung, um den statischen Druck zu ermitteln.
                  </p>
                </div>
              </div>
              <div className="text-right text-xs">
                <span className="inline-block bg-amber-100 text-amber-800 font-mono px-2 py-0.5 rounded font-bold">Konva Canvas: Active</span>
              </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-4 gap-4 items-start animate-[fadeIn_0.3s_ease]">
              
              {/* CAD Parameter Sidebar Controls */}
              <div className="xl:col-span-1 bg-white border border-slate-200 rounded-xl p-4 shadow-2xs space-y-4">
                
                <div className="border-b border-slate-100 pb-2">
                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Stammdaten Trichter</h4>
                  <p className="text-[11px] text-slate-500 font-medium">Physikalische Dimensionen anpassen.</p>
                </div>

                {/* Height & Width slide controls */}
                <div className="space-y-3">
                  <div>
                    <label className="flex justify-between text-[10px] font-bold text-slate-500 uppercase mb-1">
                      <span>Projekthöhe (m)</span>
                      <span className="text-amber-600 font-mono">{(cadSiloHeight / 20).toFixed(1)} m</span>
                    </label>
                    <input 
                      type="range" 
                      min="100" 
                      max="320" 
                      value={cadSiloHeight} 
                      onChange={e => setCadSiloHeight(parseInt(e.target.value))}
                      className="w-full cursor-pointer accent-amber-600"
                    />
                  </div>

                  <div>
                    <label className="flex justify-between text-[10px] font-bold text-slate-500 uppercase mb-1">
                      <span>Kammerbreite (m)</span>
                      <span className="text-amber-600 font-mono">{(cadSiloWidth / 20).toFixed(1)} m</span>
                    </label>
                    <input 
                      type="range" 
                      min="80" 
                      max="350" 
                      value={cadSiloWidth} 
                      onChange={e => setCadSiloWidth(parseInt(e.target.value))}
                      className="w-full cursor-pointer accent-amber-600"
                    />
                  </div>

                  <div>
                    <label className="flex justify-between text-[10px] font-bold text-slate-500 uppercase mb-1">
                      <span>Trichterwinkel</span>
                      <span className="text-amber-600 font-mono">{cadHopperAngle}°</span>
                    </label>
                    <input 
                      type="range" 
                      min="30" 
                      max="75" 
                      value={cadHopperAngle} 
                      onChange={e => setCadHopperAngle(parseInt(e.target.value))}
                      className="w-full cursor-pointer accent-amber-600"
                    />
                  </div>

                  <div>
                    <label className="flex justify-between text-[10px] font-bold text-slate-500 uppercase mb-1">
                      <span>Füllstand %</span>
                      <span className="text-amber-600 font-mono">{cadSiloFillPct}%</span>
                    </label>
                    <input 
                      type="range" 
                      min="0" 
                      max="100" 
                      value={cadSiloFillPct} 
                      onChange={e => setCadSiloFillPct(parseInt(e.target.value))}
                      className="w-full cursor-pointer accent-amber-600"
                    />
                  </div>

                  <div>
                    <label className="flex justify-between text-[10px] font-bold text-slate-500 uppercase mb-1">
                      <span>Dichte des Lagergutes</span>
                      <span className="text-amber-600 font-mono">{cadDensity} kg/m³</span>
                    </label>
                    <select 
                      value={cadDensity} 
                      onChange={e => setCadDensity(parseInt(e.target.value))}
                      className="w-full text-xs border border-slate-300 rounded px-2 py-1 bg-white text-slate-700"
                    >
                      <option value="750">Weizen / Gerste (~750 kg/m³)</option>
                      <option value="550">BIO-Sojamehl (~550 kg/m³)</option>
                      <option value="820">Mais feucht (~820 kg/m³)</option>
                    </select>
                  </div>
                </div>

                {/* Rotation Dial resembling Konva transformation ring */}
                <div className="border-t border-slate-100 pt-3">
                  <label className="flex justify-between text-[10px] font-bold text-slate-500 uppercase mb-1">
                    <span>CAD Transformation Drehung</span>
                    <span className="text-amber-600 font-mono">{cadSiloRotation}°</span>
                  </label>
                  <input 
                    type="range" 
                    min="-45"
                    max="45" 
                    value={cadSiloRotation} 
                    onChange={e => setCadSiloRotation(parseInt(e.target.value))}
                    className="w-full cursor-pointer accent-amber-600"
                  />
                </div>

              </div>

              {/* 2D Interactive CAD Drafting Table */}
              <div 
                className="xl:col-span-3 h-[480px] bg-sky-950/5 border border-slate-200 rounded-xl relative flex items-center justify-center p-6 overflow-hidden" 
                id="konva-cad-mesh"
              >
                {/* Visual Draft lines */}
                <div className="absolute inset-0 z-0 pointer-events-none opacity-30">
                  <div className="w-full h-full" style={{
                    backgroundImage: 'linear-gradient(rgba(180,180,180,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(180,180,180,0.1) 1px, transparent 1px)',
                    backgroundSize: '20px 20px'
                  }} />
                </div>

                {/* Interactive Drag & Resize Core Container */}
                <div 
                  className="relative flex flex-col items-center bg-white border border-slate-200 rounded-2xl shadow-xl transition-all p-8 md:p-12"
                  style={{
                    transform: `rotate(${cadSiloRotation}deg)`,
                    transition: 'transform 0.2s ease',
                    width: `${cadSiloWidth + 80}px`,
                    height: `${cadSiloHeight + 120}px`
                  }}
                >
                  {/* Dynamic Silhouette Chamber Shape representation */}
                  <div className="relative w-full h-full flex flex-col justify-between border-2 border-slate-800 rounded-md">
                    
                    {/* Top filling level overlay */}
                    <div className="absolute bottom-0 inset-x-0 bg-amber-500/10 pointer-events-none border-t border-amber-400" style={{ height: `${cadSiloFillPct}%` }}>
                      {/* Interactive Liquid Waves style fluid mock */}
                      {cadSiloFillPct > 0 && (
                        <div className="absolute top-0 inset-x-0 h-1 bg-amber-500 animate-pulse flex items-center justify-center">
                          <span className="text-[8px] text-amber-800 font-mono font-bold leading-none bg-white border border-amber-200 rounded px-1 -mt-4 uppercase tracking-widest">
                            {cadSiloFillPct}% FILL LEVEL
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Silo Title label */}
                    <div className="absolute top-2 inset-x-0 text-center pointer-events-none font-sans">
                      <span className="text-[10px] font-black tracking-wider text-slate-800 uppercase leading-none">CELL-A1 CAD SHAPE</span>
                      <p className="text-[8px] text-slate-500 leading-none mt-1">Konva Transfomer Active</p>
                    </div>

                    {/* Custom Cone Bottom representation representing the Hopper (Trichter) */}
                    <div 
                      className="absolute bottom-0 inset-x-0 bg-slate-100 border-t border-slate-300"
                      style={{
                        height: `${Math.min(50, 20 + cadHopperAngle / 2)}px`,
                        clipPath: 'polygon(0% 0%, 100% 0%, 70% 100%, 30% 100%)'
                      }}
                    >
                      <div className="w-full h-full flex items-center justify-center">
                        <span className="text-[7px] font-mono text-slate-500 font-bold bg-white px-1 py-0.5 rounded border border-slate-200">OUTLET</span>
                      </div>
                    </div>

                  </div>

                  {/* Transformation Nodes: Resize drag Handles styled resembling konva */}
                  <div 
                    onMouseDown={(e) => {
                      setResizeStart({ height: cadSiloHeight, width: cadSiloWidth, clientX: e.clientX, clientY: e.clientY });
                      setIsResizingSilo(true);
                      e.stopPropagation();
                    }}
                    className="absolute -bottom-1 -right-1 h-3.5 w-3.5 bg-amber-600 border border-white rounded-full cursor-se-resize z-50 hover:bg-slate-900 transition shadow" 
                    title="Click and drag to scale container boundaries"
                  />
                  <div className="absolute -top-1 -left-1 h-2.5 w-2.5 bg-slate-800 border border-white rounded-xs pointer-events-none" />
                  <div className="absolute -top-1 -right-1 h-2.5 w-2.5 bg-slate-800 border border-white rounded-xs pointer-events-none" />
                  <div className="absolute -bottom-1 -left-1 h-2.5 w-2.5 bg-slate-800 border border-white rounded-xs pointer-events-none" />

                </div>

                {/* Mathematical Statics Overlay Panel */}
                <div className="absolute bottom-4 right-4 bg-slate-900/90 border border-slate-700 rounded-xl p-4 text-white text-[11px] font-mono space-y-2 z-10 w-64 shadow-xl">
                  <div className="border-b border-slate-700 pb-1.5 flex items-center justify-between">
                    <span className="font-bold text-amber-400 flex items-center gap-1">
                      <Zap className="h-3.5 w-3.5" />
                      STATISK KALKULATION
                    </span>
                    <span className="text-[9px] text-slate-400">SI Einheit</span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-slate-400">Druck am Trichterboden (P):</span>
                    <span className="text-amber-300 font-bold">
                      {Math.round((cadDensity * 9.81 * (cadSiloHeight / 20) * (cadSiloFillPct / 100)) / 1000)} kPa
                    </span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-slate-400">Lagervolumen (V):</span>
                    <span className="text-slate-200">{cadMetrics.totalVolumeM3} m³</span>
                  </div>

                  <div className="flex justify-between border-t border-slate-800 pt-1.5 font-sans">
                    <span className="text-slate-400 font-medium font-mono text-[10px] uppercase">GUT-GEWICHT INLET:</span>
                    <span className="text-emerald-400 font-black text-xs">
                      {(cadMetrics.currentKg / 1000).toFixed(1)} t
                    </span>
                  </div>

                  <div className="text-[9px] text-slate-500 italic font-medium pt-1">
                    Statikberechnung nach Janssen-Gleichung für Rüttelsilos (2026-Norm).
                  </div>
                </div>

              </div>

            </div>

          </div>
        )}

        {/* ========================================== */}
        {/* TAB 4: FUXA SCADA PLC REGISTER / OPC-UA */}
        {/* ========================================== */}
        {activeTab === 'scada' && (
          <div className="space-y-4">
            
            {/* FUXA Info */}
            <div className="bg-indigo-50/50 border border-indigo-100 rounded-lg p-3.5 flex flex-col md:flex-row md:items-center justify-between gap-3 shadow-2xs">
              <div className="flex items-start space-x-2.5">
                <div className="p-1.5 rounded bg-indigo-500 text-white mt-0.5 animate-pulse">
                  <Cpu className="h-4 w-4" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider leading-none">FUXA SCADA HMI & OPC-UA Treiber-Cockpit</h4>
                  <p className="text-[11px] text-slate-500 font-medium mt-1">
                    Prototypische Anbindung stationärer Maschinensteuerungen. Wir simulieren Steuerungs-Registeradressen über OPC-UA und Modbus/TCP. Forcen Sie Register, um den Status der Systemknoten live zu verändern.
                  </p>
                </div>
              </div>
              <div className="text-right text-xs">
                <span className="inline-block bg-indigo-100 text-indigo-800 font-mono px-2 py-0.5 rounded font-bold">Driver: OPC_UA_S7_LAN</span>
              </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 items-start">
              
              {/* PLC Address register mappings */}
              <div className="xl:col-span-2 bg-white border border-slate-200 rounded-xl p-4 shadow-2xs">
                <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3.5 flex items-center justify-between">
                  <span>Register-Abbild (PLC Registers mapping)</span>
                  <span className="text-indigo-600 font-semibold text-[9px] font-mono leading-none">POLLING INTERVAL: 500MS</span>
                </h4>

                <div className="overflow-x-auto">
                  <table className="w-full text-xs font-mono text-slate-600">
                    <thead>
                      <tr className="border-b border-slate-100 text-[10px] text-slate-400 uppercase tracking-widest text-left font-bold bg-slate-50">
                        <th className="py-2.5 px-3">Aggregat-Kennung (ID)</th>
                        <th className="py-2.5 px-3">Treiber-Protokoll</th>
                        <th className="py-2.5 px-3">SPS-Registeradresse</th>
                        <th className="py-2.5 px-3">Typ</th>
                        <th className="py-2.5 px-3">Register-Wert</th>
                        <th className="py-2.5 px-3">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {nodes.map(node => {
                        // Generate mock register mappings
                        let protocol = "Modbus TCP";
                        let address = `HR-400${node.code.charCodeAt(0) || 12}`;
                        let type = "UINT";
                        let value = node.status === 'blocked' ? '0' : '1';

                        if (node.node_type === 'scale') {
                          protocol = "S7 Sercos";
                          address = "DB102.DBD10";
                          type = "FLOAT";
                          value = isSimulating ? "4210 kg" : "0 kg";
                        } else if (node.node_type === 'silo_cell') {
                          protocol = "OPC-UA";
                          address = `ns=4;s=wh/ElbeWeser/${node.code}/LevelPercent`;
                          type = "INT";
                          value = node.code === 'S-A1' ? '70%' : (node.code === 'S-A2' ? '45%' : (node.code === 'S-A3' ? '90%' : '5%'));
                        } else if (node.node_type === 'mixer') {
                          protocol = "OPC-UA";
                          address = "ns=4;s=wh/ElbeWeser/Mixer/Speed";
                          type = "WORD";
                          value = isSimulating ? "1420 RPM" : "0 RPM";
                        }

                        return (
                          <tr key={node.id} className={`hover:bg-slate-50 ${node.status === 'blocked' && 'bg-rose-50/20'}`}>
                            <td className="py-2 px-3 font-bold text-slate-800">{node.code}</td>
                            <td className="py-2 px-3 text-[11px] text-slate-500 font-sans font-semibold">{protocol}</td>
                            <td className="py-2 px-3 text-indigo-700 font-bold">{address}</td>
                            <td className="py-2 px-3 text-[10px] text-slate-400">{type}</td>
                            <td className="py-2 px-3 font-bold text-slate-700">{value}</td>
                            <td className="py-2 px-3">
                              <span className={`inline-flex px-1.5 py-0.5 rounded text-[9px] font-sans font-semibold ${
                                node.status === 'blocked' 
                                  ? 'bg-rose-100 text-rose-800' 
                                  : (node.status === 'cleaning' ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800')
                              }`}>
                                {node.status.toUpperCase()}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

              </div>

              {/* OPC-UA Command Force tool and scroll message monitor */}
              <div className="xl:col-span-1 space-y-4">
                
                {/* Active SPS Value register trigger form */}
                <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs">
                  <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3.5">
                    Register-Forcing (Steuerbox)
                  </h4>

                  <form onSubmit={handleRegisterForceSubmit} className="space-y-3">
                    <div>
                      <label className="block text-[9px] font-bold text-slate-500 uppercase mb-1">Target SPS Register-Adresse</label>
                      <select 
                        value={forcedRegAddress} 
                        onChange={e => setForcedRegAddress(e.target.value)}
                        className="w-full text-xs font-semibold border border-slate-300 rounded px-2.5 py-1.5 bg-slate-50 text-slate-800"
                      >
                        {nodes.map(n => (
                          <option key={n.id} value={`${n.code}.Value`}>
                            {n.code} ({n.name})
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-[9px] font-bold text-slate-500 uppercase mb-1">Forcierender Wert (Forced value)</label>
                      <select
                        value={forcedRegValue}
                        onChange={e => setForcedRegValue(e.target.value)}
                        className="w-full text-xs border border-slate-300 rounded px-2.5 py-1.5 bg-white text-slate-800 font-bold"
                      >
                        <option value="1">🟢 1 / ACTIVE (Einschalten / Freigeben)</option>
                        <option value="0">🔴 0 / BLOCKED (Gesperrt / Not-Aus)</option>
                      </select>
                    </div>

                    <button
                      type="submit"
                      className="w-full py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-md transition hover:shadow-xs cursor-pointer flex items-center justify-center space-x-1"
                    >
                      <Zap className="h-3.5 w-3.5 fill-current text-amber-300" />
                      <span>Registerwert forcen (SPS Force)</span>
                    </button>
                  </form>
                </div>

                {/* Subscribed live telemetry terminal logs */}
                <div className="bg-slate-900 rounded-xl p-4 shadow-lg h-72 flex flex-col justify-between">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-800/80 mb-2">
                    <span className="text-[10px] font-black text-slate-400 uppercase font-mono tracking-widest flex items-center gap-1.5">
                      <Terminal className="h-3.5 w-3.5 text-emerald-500" />
                      OPC-UA / MQTT SUBSCRIBE MONITOR
                    </span>
                    <span className="text-[8px] bg-emerald-500/20 text-emerald-400 font-bold font-mono px-1 rounded animate-pulse">SUBSCRIBED</span>
                  </div>

                  <div className="flex-1 overflow-y-auto space-y-1 font-mono text-[9px] text-emerald-400 pr-1 select-text scrollbar-thin scrollbar-thumb-slate-800">
                    {mqttLogs.map((log, i) => (
                      <p key={i} className={`leading-tight ${log.includes('FORCE') ? 'text-amber-300 font-bold' : ''}`}>
                        {log}
                      </p>
                    ))}
                    {mqttLogs.length === 0 && (
                      <p className="text-slate-600 italic">Verbinde mit Broker... Warte auf Telemetrie-Sendeintervalle.</p>
                    )}
                  </div>
                </div>

              </div>

            </div>

          </div>
        )}

      </div>
    </div>
  );
}
