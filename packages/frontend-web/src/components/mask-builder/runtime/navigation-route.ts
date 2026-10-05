/** Resolves a ScreenDefinition navigationRoute. Missing placeholders stay unresolved. */
export function resolveNavigationRoute(
  template: string,
  values: { entityId?: string; businessPartnerId?: string },
): string | null {
  const entityId = (values.entityId ?? '').trim()
  const partnerId = (values.businessPartnerId ?? '').trim()
  if (template.includes('{business_partner_id}') && !partnerId) return null
  if (template.includes('{entity_id}') && !entityId) return null
  return template
    .replaceAll('{entity_id}', encodeURIComponent(entityId))
    .replaceAll('{business_partner_id}', encodeURIComponent(partnerId))
}
