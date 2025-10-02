/**
 * HTTP Client for External Services
 */
export interface HttpClientConfig {
    baseUrl?: string;
    timeout?: number;
    retries?: number;
    retryDelay?: number;
    headers?: Record<string, string>;
}
export interface HttpResponse<T = unknown> {
    status: number;
    statusText: string;
    headers: Record<string, string>;
    data: T;
}
export interface HttpError extends Error {
    status?: number;
    response?: HttpResponse;
}
export declare class HttpClient {
    private config;
    constructor(config?: HttpClientConfig);
    get<T = unknown>(url: string, headers?: Record<string, string>): Promise<HttpResponse<T>>;
    post<T = unknown>(url: string, data?: unknown, headers?: Record<string, string>): Promise<HttpResponse<T>>;
    put<T = unknown>(url: string, data?: unknown, headers?: Record<string, string>): Promise<HttpResponse<T>>;
    patch<T = unknown>(url: string, data?: unknown, headers?: Record<string, string>): Promise<HttpResponse<T>>;
    delete<T = unknown>(url: string, headers?: Record<string, string>): Promise<HttpResponse<T>>;
    private request;
    private buildUrl;
    private buildHeaders;
    private parseResponse;
    private parseHeaders;
    private delay;
}
/**
 * HTTP Client Factory
 */
export declare class HttpClientFactory {
    private static instances;
    static create(name: string, config?: HttpClientConfig): HttpClient;
    static get(name: string): HttpClient | undefined;
    static clear(): void;
}
//# sourceMappingURL=http-client.d.ts.map