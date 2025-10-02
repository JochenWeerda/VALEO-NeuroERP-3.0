import { AnalyticsDomainService } from '../../services/analytics-domain-service';
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
export declare class AnalyticsApiController {
    private readonly service;
    constructor(service: AnalyticsDomainService);
    register(router: RouterLike): void;
    private handleListReports;
    private handleCreateReport;
    private handleUpdateReport;
    private handleListDashboards;
    private handleListPublicDashboards;
    private handleCreateDashboard;
    private handleUpdateDashboard;
}
//# sourceMappingURL=analytics-api-controller.d.ts.map