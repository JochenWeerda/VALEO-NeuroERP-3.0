/** Agrar-Self-Service-Routen im Kundenportal — Terra-Theme (EMPFEHLUNG/TERRA). */
export const TERRA_AGRAR_PORTAL_PATHS = [
  '/portal/feldbuch',
  '/portal/naehrstoffbilanzen',
  '/portal/rationsoptimierung',
] as const

export function isTerraAgrarPortalPath(pathname: string): boolean {
  return TERRA_AGRAR_PORTAL_PATHS.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`),
  )
}
