/**
 * i18n Helper Functions
 * Utilities for entity labels and dynamic translations
 */

import { TFunction } from 'i18next';

/**
 * Get translated entity type name
 */
export function getEntityTypeLabel(
  t: TFunction,
  entityType: string,
  fallback?: string
): string {
  // Try to get from crud.entities namespace
  const entityKey = entityType.toLowerCase();
  const translated = t(`crud.entities.${entityKey}`, { defaultValue: '' });
  
  if (translated && translated !== entityKey) {
    return translated;
  }
  
  // Fallback to provided fallback or original entityType
  return fallback || entityType;
}

/**
 * Get translated field label
 */
export function getFieldLabel(
  t: TFunction,
  fieldName: string,
  fallback?: string
): string {
  const fieldKey = fieldName.toLowerCase();
  const translated = t(`crud.fields.${fieldKey}`, { defaultValue: '' });
  
  if (translated && translated !== fieldKey) {
    return translated;
  }
  
  // Fallback to provided fallback or formatted fieldName
  return fallback || formatFieldName(fieldName);
}

/**
 * Format field name (camelCase to Title Case)
 */
function formatFieldName(fieldName: string): string {
  return fieldName
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (str) => str.toUpperCase())
    .trim();
}

/**
 * Get translated action label
 */
export function getActionLabel(
  t: TFunction,
  action: string,
  fallback?: string
): string {
  const actionKey = action.toLowerCase();
  const translated = t(`crud.actions.${actionKey}`, { defaultValue: '' });
  
  if (translated && translated !== actionKey) {
    return translated;
  }
  
  return fallback || action;
}

/**
 * Get translated status label
 */
export function getStatusLabel(
  t: TFunction,
  status: string,
  fallback?: string
): string {
  const statusKey = status.toLowerCase();
  const translated = t(`status.${statusKey}`, { defaultValue: '' });
  
  if (translated && translated !== statusKey) {
    return translated;
  }
  
  return fallback || status;
}

/**
 * Get success message for CRUD operation
 */
export function getSuccessMessage(
  t: TFunction,
  operation: 'create' | 'update' | 'delete' | 'cancel' | 'restore',
  entityType: string
): string {
  const entityTypeTranslated = getEntityTypeLabel(t, entityType);
  const messageKey = `crud.messages.${operation}Success`;
  
  return t(messageKey, { entityType: entityTypeTranslated });
}

/**
 * Get error message for CRUD operation
 */
export function getErrorMessage(
  t: TFunction,
  operation: 'create' | 'update' | 'delete' | 'cancel',
  entityType: string
): string {
  const entityTypeTranslated = getEntityTypeLabel(t, entityType);
  const messageKey = `crud.messages.${operation}Error`;
  
  return t(messageKey, { entityType: entityTypeTranslated });
}

/**
 * Get translated list title
 */
export function getListTitle(
  t: TFunction,
  entityType: string
): string {
  const entityTypeTranslated = getEntityTypeLabel(t, entityType);
  return t('crud.list.title', { entityType: entityTypeTranslated });
}

/**
 * Get translated detail title
 */
export function getDetailTitle(
  t: TFunction,
  entityType: string,
  entityName: string
): string {
  const entityTypeTranslated = getEntityTypeLabel(t, entityType);
  return t('crud.detail.title', {
    entityType: entityTypeTranslated,
    entityName,
  });
}

/**
 * Entity type mappings for common entities
 */
export const ENTITY_TYPE_MAPPINGS: Record<string, string> = {
  farmer: 'farmer',
  batch: 'batch',
  contract: 'contract',
  task: 'task',
  fieldServiceTask: 'fieldServiceTask',
  commodityContract: 'commodityContract',
  qualityCertificate: 'qualityCertificate',
  amendment: 'amendment',
  purchaseOrder: 'purchaseOrder',
  salesOrder: 'salesOrder',
  invoice: 'invoice',
  delivery: 'delivery',
  warehouse: 'warehouse',
  location: 'location',
  product: 'product',
  customer: 'customer',
  supplier: 'supplier',
};

/**
 * Get entity type key from entity object or string
 */
export function getEntityTypeKey(entity: any | string): string {
  if (typeof entity === 'string') {
    return entity.toLowerCase();
  }
  
  // Try to infer from entity properties
  if (entity?.entityType) {
    return entity.entityType.toLowerCase();
  }
  
  // Try common entity type fields
  const typeFields = ['type', 'entityType', 'kind', 'category'];
  for (const field of typeFields) {
    if (entity?.[field]) {
      return String(entity[field]).toLowerCase();
    }
  }
  
  return 'entity';
}

