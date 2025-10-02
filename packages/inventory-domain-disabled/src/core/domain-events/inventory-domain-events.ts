/**
 * VALEO NeuroERP 3.0 - Inventory Domain Events
 *
 * Domain events for WMS operations
 */

export interface InventoryDomainEvent {
  eventId: string;
  eventType: string;
  aggregateId: string;
  aggregateType: string;
  eventVersion: number;
  occurredOn: Date;
  tenantId: string;
  type: string;
  occurredAt: Date;
  aggregateVersion: number;
}

// Receiving Events
export interface GoodsReceivedEvent extends InventoryDomainEvent {
  eventType: 'inventory.goods.received';
  type: 'inventory.goods.received';
  occurredAt: Date;
  aggregateVersion: number;
  asnId: string;
  poId: string;
  dock: string;
  lines: Array<{
    sku: string;
    gtin?: string;
    qty: number;
    uom: string;
    lot?: string;
    serial?: string;
    expDate?: Date;
    mfgDate?: Date;
    qualityStatus: 'pending' | 'passed' | 'failed';
  }>;
}

export interface ReceivingMismatchEvent extends InventoryDomainEvent {
  eventType: 'inventory.receiving.mismatch';
  type: 'inventory.receiving.mismatch';
  occurredAt: Date;
  aggregateVersion: number;
  asnId: string;
  poId: string;
  discrepancies: Array<{
    sku: string;
    expectedQty: number;
    receivedQty: number;
    reason: string;
  }>;
}

// Return Events
export interface ReturnReceivedEvent extends InventoryDomainEvent {
  eventType: 'inventory.return.received';
  type: 'inventory.return.received';
  occurredAt: Date;
  aggregateVersion: number;
  returnId: string;
  orderId: string;
  items: Array<{
    sku: string;
    orderedQty: number;
    returnedQty: number;
    approvedQty: number;
    condition: 'new' | 'used' | 'damaged' | 'defective';
    disposition: 'pending' | 'restock' | 'scrap' | 'repair' | 'return_to_supplier' | 'donate';
    notes?: string;
    images?: string[];
  }>;
}


// Quarantine Events
export interface QuarantineCreatedEvent extends InventoryDomainEvent {
  eventType: 'inventory.quarantine.created';
  type: 'inventory.quarantine.created';
  occurredAt: Date;
  aggregateVersion: number;
  quarantineId: string;
  sku: string;
  location: string;
  quantity: number;
  reason: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface QuarantineReleasedEvent extends InventoryDomainEvent {
   eventType: 'inventory.quarantine.released';
   type: 'inventory.quarantine.released';
   occurredAt: Date;
   aggregateVersion: number;
   quarantineId: string;
   releasedBy: string;
   disposition: 'restock' | 'scrap' | 'repair' | 'return_to_supplier' | 'donate';
   reason: string;
 }


// Traceability Events
export interface TraceabilityEventCreatedEvent extends InventoryDomainEvent {
  eventType: 'inventory.traceability.event.created';
  type: 'inventory.traceability.event.created';
  occurredAt: Date;
  aggregateVersion: number;
  eventId: string;
  traceabilityEventType: 'object' | 'aggregation' | 'transformation' | 'transaction';
  epcList: string[];
  businessLocation: string;
}

export interface EPCISDocumentGeneratedEvent extends InventoryDomainEvent {
  eventType: 'inventory.epcis.document.generated';
  type: 'inventory.epcis.document.generated';
  occurredAt: Date;
  aggregateVersion: number;
  documentId: string;
  documentType: 'master_data' | 'events' | 'query_response';
  eventCount: number;
  businessLocation: string;
}

// AI Events
export interface AISlottingOptimizedEvent extends InventoryDomainEvent {
  eventType: 'inventory.ai.slotting.optimized';
  type: 'inventory.ai.slotting.optimized';
  occurredAt: Date;
  aggregateVersion: number;
  sku: string;
  oldLocation: string;
  newLocation: string;
  confidence: number;
  expectedImprovement: {
    travelTime: number;
    throughput: number;
    spaceUtilization: number;
  };
}

export interface AIForecastEnhancedEvent extends InventoryDomainEvent {
  eventType: 'inventory.ai.forecast.enhanced';
  type: 'inventory.ai.forecast.enhanced';
  occurredAt: Date;
  aggregateVersion: number;
  sku: string;
  forecastType: 'demand' | 'inventory' | 'replenishment';
  accuracy: number;
  confidence: number;
}

export interface AIModelTrainedEvent extends InventoryDomainEvent {
  eventType: 'inventory.ai.model.trained';
  type: 'inventory.ai.model.trained';
  occurredAt: Date;
  aggregateVersion: number;
  modelId: string;
  modelType: 'slotting' | 'forecasting' | 'anomaly_detection';
  accuracy: number;
  trainingDataSize: number;
}

// EDI Events
export interface EDI940ReceivedEvent extends InventoryDomainEvent {
  eventType: 'inventory.edi.940.received';
  type: 'inventory.edi.940.received';
  occurredAt: Date;
  aggregateVersion: number;
  shipmentId: string;
  warehouseId: string;
  itemCount: number;
  totalQuantity: number;
}

export interface EDI943GeneratedEvent extends InventoryDomainEvent {
  eventType: 'inventory.edi.943.generated';
  type: 'inventory.edi.943.generated';
  occurredAt: Date;
  aggregateVersion: number;
  transferId: string;
  warehouseId: string;
  itemCount: number;
  totalQuantity: number;
}

export interface EDI944ReceivedEvent extends InventoryDomainEvent {
  eventType: 'inventory.edi.944.received';
  type: 'inventory.edi.944.received';
  occurredAt: Date;
  aggregateVersion: number;
  transferId: string;
  warehouseId: string;
  itemCount: number;
  totalReceived: number;
  discrepancies: number;
}

export interface EDI945GeneratedEvent extends InventoryDomainEvent {
  eventType: 'inventory.edi.945.generated';
  type: 'inventory.edi.945.generated';
  occurredAt: Date;
  aggregateVersion: number;
  shipmentId: string;
  warehouseId: string;
  itemCount: number;
  totalWeight: number;
  totalVolume: number;
}

export interface EDI947GeneratedEvent extends InventoryDomainEvent {
  eventType: 'inventory.edi.947.generated';
  type: 'inventory.edi.947.generated';
  occurredAt: Date;
  aggregateVersion: number;
  adjustmentId: string;
  warehouseId: string;
  itemCount: number;
  netAdjustment: number;
  adjustmentType: 'increase' | 'decrease' | 'reset';
}

// Putaway Events
export interface PutawayPlannedEvent extends InventoryDomainEvent {
  eventType: 'inventory.putaway.planned';
  asnId: string;
  tasks: Array<{
    taskId: string;
    sku: string;
    fromLocation: string;
    toLocation: string;
    qty: number;
    priority: number;
    strategy: string;
  }>;
}

export interface PutawayCompletedEvent extends InventoryDomainEvent {
  eventType: 'inventory.putaway.completed';
  taskId: string;
  asnId: string;
  sku: string;
  location: string;
  quantity: number;
  completedBy: string;
  duration: number; // seconds
}

// Slotting Events
export interface SlottingUpdatedEvent extends InventoryDomainEvent {
  eventType: 'inventory.slotting.updated';
  sku: string;
  oldLocation?: string;
  newLocation: string;
  reason: string;
  aiConfidence: number;
}

// Inventory Control Events
export interface InventoryAdjustedEvent extends InventoryDomainEvent {
  eventType: 'inventory.adjusted';
  sku: string;
  location: string;
  lot?: string;
  serial?: string;
  adjustmentQty: number;
  reason: 'cycle_count' | 'damage' | 'theft' | 'correction' | 'return' | 'transfer';
  approvedBy: string;
}

export interface ReservationCreatedEvent extends InventoryDomainEvent {
  eventType: 'inventory.reservation.created';
  sku: string;
  location: string;
  lot?: string;
  serial?: string;
  quantity: number;
  reservedFor: string;
  reservationType: 'sales_order' | 'transfer' | 'production' | 'allocation';
}

export interface ReservationReleasedEvent extends InventoryDomainEvent {
  eventType: 'inventory.reservation.released';
  reservationId: string;
  releasedQty: number;
  reason: string;
}

// Lot/Serial Events
export interface LotCreatedEvent extends InventoryDomainEvent {
  eventType: 'inventory.lot.created';
  lotCode: string;
  sku: string;
  supplierId: string;
  supplierLot?: string;
  initialQty: number;
  mfgDate?: Date;
  expDate?: Date;
}

export interface LotConsumedEvent extends InventoryDomainEvent {
  eventType: 'inventory.lot.consumed';
  lotCode: string;
  sku: string;
  consumedQty: number;
  remainingQty: number;
  consumedBy: string;
  reference: string;
}

export interface SerialAssignedEvent extends InventoryDomainEvent {
  eventType: 'inventory.serial.assigned';
  serialNumber: string;
  sku: string;
  lot?: string;
  assignedTo: string;
  location: string;
}

// Picking Events
export interface PickTaskCreatedEvent extends InventoryDomainEvent {
  eventType: 'inventory.pick.created';
  orderId: string;
  waveId?: string;
  tasks: Array<{
    taskId: string;
    sku: string;
    location: string;
    lot?: string;
    serial?: string;
    quantity: number;
    priority: number;
  }>;
}

export interface PickTaskAssignedEvent extends InventoryDomainEvent {
  eventType: 'inventory.pick.assigned';
  taskId: string;
  pickerId: string;
  assignedAt: Date;
}

export interface PickCompletedEvent extends InventoryDomainEvent {
  eventType: 'inventory.pick.completed';
  taskId: string;
  orderId: string;
  sku: string;
  quantity: number;
  pickedBy: string;
  duration: number;
  accuracy: number;
}

export interface WaveCreatedEvent extends InventoryDomainEvent {
  eventType: 'inventory.wave.created';
  waveId: string;
  waveNumber: string;
  strategy: string;
  totalTasks: number;
  totalQuantity: number;
  zone: string;
}

export interface WaveCompletedEvent extends InventoryDomainEvent {
  eventType: 'inventory.wave.completed';
  waveId: string;
  completedTasks: number;
  totalTasks: number;
  duration: number;
  productivity: number;
}

// Packing Events
export interface PackTaskCreatedEvent extends InventoryDomainEvent {
  eventType: 'inventory.pack.created';
  orderId: string;
  shipmentId: string;
  items: Array<{
    sku: string;
    quantity: number;
    lot?: string;
    serial?: string;
  }>;
}

export interface PackCompletedEvent extends InventoryDomainEvent {
  eventType: 'inventory.pack.completed';
  orderId: string;
  shipmentId: string;
  packedBy: string;
  weight: number;
  dimensions: {
    length: number;
    width: number;
    height: number;
  };
  carrier: string;
}

// Shipping Events
export interface ShipmentCreatedEvent extends InventoryDomainEvent {
  eventType: 'inventory.shipment.created';
  shipmentId: string;
  orderId: string;
  carrier: string;
  trackingNumber?: string;
  items: Array<{
    sku: string;
    quantity: number;
    lot?: string;
    serial?: string;
  }>;
}

export interface ShipmentShippedEvent extends InventoryDomainEvent {
  eventType: 'inventory.shipment.shipped';
  shipmentId: string;
  orderId: string;
  carrier: string;
  trackingNumber: string;
  shippedAt: Date;
  shippedBy: string;
}

// Cycle Count Events
export interface CycleCountCreatedEvent extends InventoryDomainEvent {
  eventType: 'inventory.cyclecount.created';
  countId: string;
  locations: string[];
  method: 'ABC' | 'XYZ' | 'manual';
  scheduledDate: Date;
}

export interface CycleCountCompletedEvent extends InventoryDomainEvent {
  eventType: 'inventory.cyclecount.completed';
  countId: string;
  countedBy: string;
  discrepancies: Array<{
    sku: string;
    location: string;
    expectedQty: number;
    countedQty: number;
    variance: number;
  }>;
  accuracy: number;
}

// Returns Events
export interface ReturnReceivedEvent extends InventoryDomainEvent {
   eventType: 'inventory.return.received';
   type: 'inventory.return.received';
   occurredAt: Date;
   aggregateVersion: number;
   returnId: string;
   orderId: string;
   items: Array<{
     sku: string;
     orderedQty: number;
     returnedQty: number;
     approvedQty: number;
     condition: 'new' | 'used' | 'damaged' | 'defective';
     disposition: 'pending' | 'restock' | 'scrap' | 'repair' | 'return_to_supplier' | 'donate';
     notes?: string;
     images?: string[];
   }>;
 }

  export interface ReturnProcessedEvent extends InventoryDomainEvent {
    eventType: 'inventory.return.processed';
    type: 'inventory.return.processed';
    occurredAt: Date;
    aggregateVersion: number;
    returnId: string;
    processedBy: string;
    disposition: 'restock' | 'scrap' | 'repair' | 'return_to_supplier' | 'donate';
  }

  export interface QuarantineCreatedEvent extends InventoryDomainEvent {
    eventType: 'inventory.quarantine.created';
    type: 'inventory.quarantine.created';
    occurredAt: Date;
    aggregateVersion: number;
    quarantineId: string;
    itemId: string;
    sku: string;
    location: string;
    quantity: number;
    reason: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    createdBy: string;
  }

  export interface QuarantineReleasedEvent extends InventoryDomainEvent {
    eventType: 'inventory.quarantine.released';
    type: 'inventory.quarantine.released';
    occurredAt: Date;
    aggregateVersion: number;
    quarantineId: string;
    releasedBy: string;
    disposition: 'restock' | 'scrap' | 'repair' | 'return_to_supplier' | 'donate';
    reason: string;
  }

 export interface ReturnDispositionEvent extends InventoryDomainEvent {
   eventType: 'inventory.return.disposition';
   type: 'inventory.return.disposition';
   occurredAt: Date;
   aggregateVersion: number;
   returnId: string;
   disposition: 'restock' | 'scrap' | 'repair' | 'return_to_supplier' | 'donate';
   reason: string;
 }

// AI Events
export interface AIAnomalyDetectedEvent extends InventoryDomainEvent {
  eventType: 'inventory.ai.anomaly.detected';
  type: 'inventory.ai.anomaly.detected';
  occurredAt: Date;
  aggregateVersion: number;
  anomalyId: string;
  anomalyType: 'demand_spike' | 'inventory_discrepancy' | 'location_issue';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  affectedItems: string[];
}

export interface AIForecastGeneratedEvent extends InventoryDomainEvent {
  eventType: 'inventory.ai.forecast.generated';
  type: 'inventory.ai.forecast.generated';
  occurredAt: Date;
  aggregateVersion: number;
  forecastId: string;
  sku: string;
  forecastType: 'demand' | 'inventory' | 'replenishment';
  horizon: number;
  confidence: number;
}

export interface AISlottingOptimizedEvent extends InventoryDomainEvent {
  eventType: 'inventory.ai.slotting.optimized';
  type: 'inventory.ai.slotting.optimized';
  occurredAt: Date;
  aggregateVersion: number;
  sku: string;
  oldLocation: string;
  newLocation: string;
  reason: string;
  aiConfidence: number;
}

export interface AIForecastEnhancedEvent extends InventoryDomainEvent {
  eventType: 'inventory.ai.forecast.enhanced';
  type: 'inventory.ai.forecast.enhanced';
  occurredAt: Date;
  aggregateVersion: number;
  forecastId: string;
  sku: string;
  forecastType: 'demand' | 'inventory' | 'replenishment';
  horizon: number;
  confidence: number;
}

export interface AIModelTrainedEvent extends InventoryDomainEvent {
  eventType: 'inventory.ai.model.trained';
  type: 'inventory.ai.model.trained';
  occurredAt: Date;
  aggregateVersion: number;
  modelId: string;
  modelType: 'slotting' | 'forecasting' | 'anomaly_detection';
  accuracy: number;
  trainingDataSize: number;
}


// Traceability Events
export interface TraceabilityQueryEvent extends InventoryDomainEvent {
  eventType: 'inventory.traceability.queried';
  type: 'inventory.traceability.queried';
  occurredAt: Date;
  aggregateVersion: number;
  queryType: 'lot' | 'serial' | 'product';
  queryId: string;
  queriedBy: string;
  results: any;
}

export interface TraceabilityEventCreatedEvent extends InventoryDomainEvent {
  eventType: 'inventory.traceability.event.created';
  type: 'inventory.traceability.event.created';
  occurredAt: Date;
  aggregateVersion: number;
  eventId: string;
  traceabilityEventType: 'object' | 'aggregation' | 'transformation' | 'transaction';
  identifier: string;
  location: string;
  timestamp: Date;
  actor: string;
}

export interface EPCISDocumentGeneratedEvent extends InventoryDomainEvent {
  eventType: 'inventory.epcis.document.generated';
  type: 'inventory.epcis.document.generated';
  occurredAt: Date;
  aggregateVersion: number;
  documentId: string;
  documentType: 'master_data' | 'events' | 'query_response';
  businessProcess: string;
  sender: string;
  receiver: string;
  eventCount: number;
}

// WCS/WES Events
export interface RoboticsTaskCreatedEvent extends InventoryDomainEvent {
  eventType: 'inventory.robotics.task.created';
  type: 'inventory.robotics.task.created';
  occurredAt: Date;
  aggregateVersion: number;
  taskId: string;
  robotId: string;
  operation: 'pick' | 'put' | 'move' | 'count';
  location: string;
  sku?: string;
  quantity?: number;
}

export interface RoboticsTaskCompletedEvent extends InventoryDomainEvent {
  eventType: 'inventory.robotics.task.completed';
  type: 'inventory.robotics.task.completed';
  occurredAt: Date;
  aggregateVersion: number;
  taskId: string;
  robotId: string;
  duration: number;
  success: boolean;
  errorMessage?: string;
}

// EDI Events
export interface EDI940ReceivedEvent extends InventoryDomainEvent {
  eventType: 'inventory.edi.940.received';
  type: 'inventory.edi.940.received';
  occurredAt: Date;
  aggregateVersion: number;
  warehouseId: string;
  items: Array<{
    sku: string;
    orderedQty: number;
    returnedQty: number;
    approvedQty: number;
    condition: 'new' | 'used' | 'damaged' | 'defective';
    disposition: 'pending' | 'restock' | 'scrap' | 'repair' | 'return_to_supplier' | 'donate';
    notes?: string;
    images?: string[];
  }>;
}

export interface EDI943GeneratedEvent extends InventoryDomainEvent {
  eventType: 'inventory.edi.943.generated';
  type: 'inventory.edi.943.generated';
  occurredAt: Date;
  aggregateVersion: number;
  warehouseId: string;
  shipmentId: string;
  carrier: string;
  trackingNumber: string;
}

export interface EDI944ReceivedEvent extends InventoryDomainEvent {
  eventType: 'inventory.edi.944.received';
  type: 'inventory.edi.944.received';
  occurredAt: Date;
  aggregateVersion: number;
  warehouseId: string;
  items: Array<{
    sku: string;
    orderedQty: number;
    returnedQty: number;
    approvedQty: number;
    condition: 'new' | 'used' | 'damaged' | 'defective';
    disposition: 'pending' | 'restock' | 'scrap' | 'repair' | 'return_to_supplier' | 'donate';
    notes?: string;
    images?: string[];
  }>;
}

export interface EDI945GeneratedEvent extends InventoryDomainEvent {
  eventType: 'inventory.edi.945.generated';
  type: 'inventory.edi.945.generated';
  occurredAt: Date;
  aggregateVersion: number;
  warehouseId: string;
  inventoryId: string;
  location: string;
  quantity: number;
}

export interface EDI947GeneratedEvent extends InventoryDomainEvent {
  eventType: 'inventory.edi.947.generated';
  type: 'inventory.edi.947.generated';
  occurredAt: Date;
  aggregateVersion: number;
  warehouseId: string;
  inventoryId: string;
  location: string;
  quantity: number;
}

// AI Events
export interface AIForecastGeneratedEvent extends InventoryDomainEvent {
  eventType: 'inventory.ai.forecast.generated';
  sku: string;
  forecastType: 'demand' | 'inventory' | 'replenishment';
  forecast: Array<{
    date: Date;
    quantity: number;
    confidence: number;
  }>;
  model: string;
  accuracy: number;
}

export interface AIAnomalyDetectedEvent extends InventoryDomainEvent {
  eventType: 'inventory.ai.anomaly.detected';
  anomalyType: 'demand_spike' | 'inventory_discrepancy' | 'location_issue';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  affectedItems: string[];
  recommendedActions: string[];
}

// EDI Events
export interface EDIReceivedEvent extends InventoryDomainEvent {
  eventType: 'inventory.edi.received';
  ediType: '940' | '943' | '944' | '945' | '947';
  sender: string;
  documentId: string;
  processed: boolean;
  errors?: string[];
}

export interface EDISentEvent extends InventoryDomainEvent {
  eventType: 'inventory.edi.sent';
  ediType: '940' | '943' | '944' | '945' | '947';
  recipient: string;
  documentId: string;
  sentAt: Date;
}