/**
 * Der Mandant der Anmeldung, gelesen aus dem Access-Token.
 *
 * Seit 12.10.2026 lehnt das Backend eine Anfrage ab, deren `X-Tenant-ID` nicht der Mandant des Tokens
 * ist. Die Oberflaeche nimmt den Mandanten deshalb aus dem Token, sobald es einen nennt — ein alter
 * Wert im Browser-Speicher wuerde sonst jede Anfrage mit 403 enden lassen.
 *
 * Das ist keine Pruefung: Die Signatur prueft das Backend. Hier wird nur gelesen, was mitgeschickt wird.
 */
const CLAIMS = ['tenant_id', 'mandanten_id'] as const

export function tenantFromToken(token: string | null | undefined): string | null {
  if (!token) return null
  const teile = token.split('.')
  if (teile.length !== 3) return null
  try {
    const base64 = teile[1].replace(/-/g, '+').replace(/_/g, '/')
    const json = decodeURIComponent(
      Array.from(atob(base64.padEnd(Math.ceil(base64.length / 4) * 4, '=')))
        .map((c) => `%${c.charCodeAt(0).toString(16).padStart(2, '0')}`)
        .join(''),
    )
    const claims = JSON.parse(json) as Record<string, unknown>
    const gefunden = new Set<string>()
    for (const name of CLAIMS) {
      const wert = claims[name]
      for (const einzel of Array.isArray(wert) ? wert : [wert]) {
        if (typeof einzel === 'string' && einzel.trim()) gefunden.add(einzel.trim())
      }
    }
    // Mehrdeutig ist wie nicht genannt: Das Backend lehnt ein solches Token ohnehin ab.
    return gefunden.size === 1 ? [...gefunden][0] : null
  } catch {
    // Kein lesbares JWT (z. B. der Dev-Token): Es gibt keinen Mandanten im Token.
    return null
  }
}
