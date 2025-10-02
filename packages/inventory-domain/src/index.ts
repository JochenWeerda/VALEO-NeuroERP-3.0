// ===== VALEO NeuroERP 3.0 - INVENTORY DOMAIN PACKAGE =====
// Central exports for all inventory domain functionality

// Core entities and value objects
// export * from './core/entities/location'; // Commented out due to Location conflict
export * from './core/entities/lot';
export * from './core/entities/sku';

// Domain events
export * from './core/domain-events/inventory-domain-events';

// Services
// export * from './services/ai-assistance-service'; // Commented out due to SlottingRecommendation conflict
export * from './services/cycle-counting-service';
export * from './services/edi-service';
export * from './services/inventory-control-service';
export * from './services/packing-shipping-service';
export * from './services/picking-service';
export * from './services/putaway-slotting-service';
export * from './services/receiving-service';
export * from './services/returns-disposition-service';
export * from './services/traceability-service';
export * from './services/wcs-wes-adapter-service';

// Application services
export * from './application/services/inventory-domain-service';

// Infrastructure
export * from './infrastructure/event-bus/event-bus';
export * from './infrastructure/observability/metrics-service';
// export * from './infrastructure/observability/observability-service'; // Commented out - file deleted

// Presentation
// export * from './presentation/inventory-bff'; // Commented out - file deleted

// Bootstrap
export * from './bootstrap';

