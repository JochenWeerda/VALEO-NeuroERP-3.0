/**
 * Launcher-seitige Fassade auf die Adaptive-Workspace-Registry.
 * Implementierung liegt in `@/workspace` — hier nur der oeffentliche Importpfad.
 */
export {
  WORKSPACE_FACHAKTIONEN,
  getWorkspaceCatalog,
  mapAuthorizedFachaktionen,
  orderLaunchpadTileIds,
  rankWorkspaceItems,
  userContextFromPersonalization,
} from '@/workspace'
