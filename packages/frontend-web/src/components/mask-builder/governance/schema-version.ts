/** Kanonische Schema-Version. Eine neue Version ist eine Migration, kein zweites Format. */
export const SCREEN_SCHEMA_VERSION = 1 as const

export function assertSchemaVersion(version: number): string | null {
  if (version === SCREEN_SCHEMA_VERSION) return null
  return `schemaVersion must be ${SCREEN_SCHEMA_VERSION}`
}
