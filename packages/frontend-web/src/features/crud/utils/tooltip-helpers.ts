/**
 * Tooltip Helper Functions
 * Utilities for field tooltips and help texts based on Odoo 19.0 German translations
 */

import { TFunction } from 'i18next';

/**
 * Get tooltip text for a field
 */
export function getFieldTooltip(
  t: TFunction,
  fieldName: string,
  fallback?: string
): string {
  const tooltipKey = `crud.tooltips.fields.${fieldName.toLowerCase()}`;
  const translated = t(tooltipKey, { defaultValue: '' });
  
  if (translated && translated !== tooltipKey) {
    return translated;
  }
  
  return fallback || '';
}

/**
 * Get placeholder text for a field
 */
export function getFieldPlaceholder(
  t: TFunction,
  fieldName: string,
  fallback?: string
): string {
  const placeholderKey = `crud.tooltips.placeholders.${fieldName.toLowerCase()}`;
  const translated = t(placeholderKey, { defaultValue: '' });
  
  if (translated && translated !== placeholderKey) {
    return translated;
  }
  
  return fallback || '';
}

/**
 * Get tooltip text for an action
 */
export function getActionTooltip(
  t: TFunction,
  action: string,
  fallback?: string
): string {
  const tooltipKey = `crud.tooltips.actions.${action.toLowerCase()}`;
  const translated = t(tooltipKey, { defaultValue: '' });
  
  if (translated && translated !== tooltipKey) {
    return translated;
  }
  
  return fallback || '';
}

