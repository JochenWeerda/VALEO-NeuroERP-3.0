import { DashboardId, createDashboardId } from '@valero-neuroerp/data-models';

export interface DashboardWidget {
  id: string;
  type: 'chart' | 'table' | 'metric' | 'text';
  title: string;
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  definition: Record<string, unknown>;
  refreshIntervalMs?: number;
}

export interface Dashboard {
  readonly id: DashboardId;
  readonly tenantId: string;
  name: string;
  description?: string;
  isPublic: boolean;
  widgets: DashboardWidget[];
  tags: string[];
  readonly createdAt: Date;
  updatedAt: Date;
}

export interface CreateDashboardInput {
  tenantId: string;
  name: string;
  widgets?: DashboardWidget[];
  description?: string;
  isPublic?: boolean;
  tags?: string[];
}

export interface UpdateDashboardInput {
  name?: string;
  description?: string;
  isPublic?: boolean;
  widgets?: DashboardWidget[];
  tags?: string[];
}

export function createDashboard(input: CreateDashboardInput): Dashboard {
  if (!input.tenantId) {
    throw new Error('tenantId is required');
  }
  if (!input.name) {
    throw new Error('name is required');
  }

  const now = new Date();

  return {
    id: createDashboardId(globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`),
    tenantId: input.tenantId,
    name: input.name.trim(),
    description: input.description?.trim(),
    isPublic: input.isPublic ?? false,
    widgets: sanitizeWidgets(input.widgets ?? []),
    tags: normalizeTags(input.tags),
    createdAt: now,
    updatedAt: now,
  };
}

export function applyDashboardUpdate(dashboard: Dashboard, update: UpdateDashboardInput): Dashboard {
  return {
    ...dashboard,
    name: update.name ? update.name.trim() : dashboard.name,
    description: update.description?.trim() ?? dashboard.description,
    isPublic: update.isPublic ?? dashboard.isPublic,
    widgets: update.widgets ? sanitizeWidgets(update.widgets) : dashboard.widgets,
    tags: update.tags ? normalizeTags(update.tags) : dashboard.tags,
    updatedAt: new Date(),
  };
}

function sanitizeWidgets(widgets: DashboardWidget[]): DashboardWidget[] {
  return widgets.map((widget) => ({
    ...widget,
    id: widget.id || `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    title: widget.title.trim(),
    position: { ...widget.position },
    definition: { ...widget.definition },
  }));
}

function normalizeTags(tags?: string[]): string[] {
  return tags ? [...new Set(tags.map((tag) => tag.trim()).filter(Boolean))] : [];
}
