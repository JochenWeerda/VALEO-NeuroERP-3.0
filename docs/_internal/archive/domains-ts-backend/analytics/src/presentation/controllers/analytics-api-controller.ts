import { createDashboardId, createReportId } from '@packages/data-models';
import { AnalyticsDomainService } from '../../services/analytics-domain-service';
import type { CreateReportInput, UpdateReportInput } from '../../core/entities/report';
import type { CreateDashboardInput, UpdateDashboardInput } from '../../core/entities/dashboard';

export interface HttpRequest<TBody = unknown> {
  params: Record<string, string>;
  query: Record<string, string | string[] | undefined>;
  body?: TBody;
}

export interface HttpResponse<TBody = unknown> {
  status: number;
  body?: TBody;
}

export type RouteHandler = (request: HttpRequest) => Promise<HttpResponse>;

export interface RouterLike {
  get(path: string, handler: RouteHandler): void;
  post(path: string, handler: RouteHandler): void;
  put(path: string, handler: RouteHandler): void;
}

export class AnalyticsApiController {
  constructor(private readonly service: AnalyticsDomainService) {}

  register(router: RouterLike): void {
    router.get('/analytics/reports', (request) => this.handleListReports(request));
    router.post('/analytics/reports', (request) => this.handleCreateReport(request));
    router.put('/analytics/reports/:id', (request) => this.handleUpdateReport(request));

    router.get('/analytics/dashboards', (request) => this.handleListDashboards(request));
    router.get('/analytics/dashboards/public', (request) => this.handleListPublicDashboards(request));
    router.post('/analytics/dashboards', (request) => this.handleCreateDashboard(request));
    router.put('/analytics/dashboards/:id', (request) => this.handleUpdateDashboard(request));
  }

  private async handleListReports(request: HttpRequest): Promise<HttpResponse> {
    const tenantId = asString(request.query.tenantId);
    if (!tenantId) {
      return { status: 400, body: { message: 'tenantId query parameter is required' } };
    }

    const reports = await this.service.listReports(tenantId);
    return { status: 200, body: reports };
  }

  private async handleCreateReport(request: HttpRequest): Promise<HttpResponse> {
    const body = request.body as CreateReportInput | undefined;
    if (!body) {
      return { status: 400, body: { message: 'Request body is required' } };
    }

    try {
      const created = await this.service.createReport(body);
      return { status: 201, body: created };
    } catch (error) {
      return toHttpError(error);
    }
  }

  private async handleUpdateReport(request: HttpRequest): Promise<HttpResponse> {
    const id = request.params.id;
    if (!id) {
      return { status: 400, body: { message: 'Report id missing' } };
    }

    const body = request.body as UpdateReportInput | undefined;
    if (!body) {
      return { status: 400, body: { message: 'Request body is required' } };
    }

    try {
      const updated = await this.service.updateReport(createReportId(id), body);
      return { status: 200, body: updated };
    } catch (error) {
      return toHttpError(error);
    }
  }

  private async handleListDashboards(request: HttpRequest): Promise<HttpResponse> {
    const tenantId = asString(request.query.tenantId);
    if (!tenantId) {
      return { status: 400, body: { message: 'tenantId query parameter is required' } };
    }

    const dashboards = await this.service.listDashboards(tenantId);
    return { status: 200, body: dashboards };
  }

  private async handleListPublicDashboards(request: HttpRequest): Promise<HttpResponse> {
    const tenantId = asString(request.query.tenantId);
    if (!tenantId) {
      return { status: 400, body: { message: 'tenantId query parameter is required' } };
    }

    const dashboards = await this.service.listPublicDashboards(tenantId);
    return { status: 200, body: dashboards };
  }

  private async handleCreateDashboard(request: HttpRequest): Promise<HttpResponse> {
    const body = request.body as CreateDashboardInput | undefined;
    if (!body) {
      return { status: 400, body: { message: 'Request body is required' } };
    }

    try {
      const created = await this.service.createDashboard(body);
      return { status: 201, body: created };
    } catch (error) {
      return toHttpError(error);
    }
  }

  private async handleUpdateDashboard(request: HttpRequest): Promise<HttpResponse> {
    const id = request.params.id;
    if (!id) {
      return { status: 400, body: { message: 'Dashboard id missing' } };
    }

    const body = request.body as UpdateDashboardInput | undefined;
    if (!body) {
      return { status: 400, body: { message: 'Request body is required' } };
    }

    try {
      const updated = await this.service.updateDashboard(createDashboardId(id), body);
      return { status: 200, body: updated };
    } catch (error) {
      return toHttpError(error);
    }
  }
}

function asString(value: string | string[] | undefined): string | undefined {
  if (Array.isArray(value)) {
    return value[0];
  }
  return value;
}

function toHttpError(error: unknown): HttpResponse<{ message: string }> {
  if (error instanceof Error) {
    const message = error.message;
    if (message.toLowerCase().includes('not found')) {
      return { status: 404, body: { message } };
    }
    return { status: 400, body: { message } };
  }
  return { status: 500, body: { message: 'Unknown error' } };
}
