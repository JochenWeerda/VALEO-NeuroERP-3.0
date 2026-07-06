/**
 * UIX-052: BFF MCP-Tool für Masken-Actions.
 *
 * Proxied durch den BFF-Server: POST /api/mcp/v1/mask-actions/execute
 * Leitet an den FastAPI-Backend-CommandEndpoint weiter.
 *
 * Der Agent schickt: { screenId, entityId, actionKey, payload?, mode?, auditReason? }
 * Der BFF löst den commandEndpoint aus screen_definitions auf und proxied.
 */

const backendBaseUrl: string = process.env.BACKEND_URL ?? 'http://localhost:8000';
const devToken: string = process.env.API_DEV_TOKEN ?? 'dev-token';

interface ActionDef {
  key: string;
  commandEndpoint?: string;
  stubReason?: string;
  method?: string;
}

export interface MaskActionRequest {
  screenId: string;
  entityId: string;
  actionKey: string;
  payload?: Record<string, unknown>;
  mode?: 'dryRun' | 'execute' | 'propose' | 'validate';
  auditReason?: string;
  tenantId?: string;
}

export interface MaskActionResult {
  success: boolean;
  actionKey: string;
  entityId: string;
  mode: string;
  summary?: string;
  error?: string;
  proposedChanges?: unknown[];
}

function buildHeaders(tenantId: string): Record<string, string> {
  return {
    Authorization: `Bearer ${devToken}`,
    'X-Tenant-ID': tenantId,
  };
}

function failResult(req: MaskActionRequest, error: string): MaskActionResult {
  return {
    success: false,
    actionKey: req.actionKey,
    entityId: req.entityId,
    mode: req.mode ?? 'execute',
    error,
  };
}

async function resolveActionDef(req: MaskActionRequest, tenantId: string): Promise<ActionDef | MaskActionResult> {
  const schemaUrl = `${backendBaseUrl}/api/v1/masks/${encodeURIComponent(req.screenId)}/schema`;
  const schemaResp = await fetch(schemaUrl, { headers: buildHeaders(tenantId) });

  if (!schemaResp.ok) {
    return failResult(req, `ScreenDefinition '${req.screenId}' nicht abrufbar (${schemaResp.status}).`);
  }

  const schema = await schemaResp.json() as { actions?: ActionDef[] };
  const actionDef = schema.actions?.find((a) => a.key === req.actionKey);

  if (actionDef === undefined) {
    return failResult(req, `Aktion '${req.actionKey}' nicht in ScreenDefinition '${req.screenId}' gefunden.`);
  }

  const hasEndpoint = typeof actionDef.commandEndpoint === 'string' && actionDef.commandEndpoint.length > 0;
  const hasStub = typeof actionDef.stubReason === 'string' && actionDef.stubReason.length > 0;
  if (!hasEndpoint || hasStub) {
    return failResult(req, `Aktion '${req.actionKey}' hat noch keinen aktiven CommandEndpoint.`);
  }

  return actionDef;
}

async function dispatchAction(req: MaskActionRequest, actionDef: ActionDef, tenantId: string): Promise<MaskActionResult> {
  const endpoint = (actionDef.commandEndpoint ?? '')
    .replace('{entity_id}', req.entityId)
    .replace('{screen_id}', req.screenId);

  const body: Record<string, unknown> = { ...(req.payload ?? {}) };
  if (req.mode !== undefined && req.mode !== 'execute') {
    body._mode = req.mode;
  }
  if (req.auditReason !== undefined && req.auditReason.length > 0) {
    body._auditReason = req.auditReason;
  }

  const actionResp = await fetch(`${backendBaseUrl}${endpoint}`, {
    method: actionDef.method ?? 'POST',
    headers: { 'Content-Type': 'application/json', ...buildHeaders(tenantId) },
    body: JSON.stringify(body),
  });

  if (!actionResp.ok) {
    const text = await actionResp.text().catch(() => '');
    return failResult(req, `Backend-Fehler ${actionResp.status}: ${text}`);
  }

  const result = await actionResp.json() as MaskActionResult;
  return { ...result, mode: req.mode ?? 'execute' };
}

export async function executeMaskAction(req: MaskActionRequest): Promise<MaskActionResult> {
  const tenantId = req.tenantId ?? 'default';
  const resolved = await resolveActionDef(req, tenantId);

  if (!('key' in resolved)) {
    return resolved;
  }

  return dispatchAction(req, resolved, tenantId);
}
