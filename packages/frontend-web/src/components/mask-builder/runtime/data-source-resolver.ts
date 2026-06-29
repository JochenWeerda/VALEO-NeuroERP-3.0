/** Substitutes {entity_id}, {tenant_id}, {q} etc. in endpoint templates */
export function resolveEndpoint(
  template: string,
  vars: Record<string, string>,
): string {
  return template.replace(/\{(\w+)\}/g, (_, k: string) => vars[k] ?? '')
}
