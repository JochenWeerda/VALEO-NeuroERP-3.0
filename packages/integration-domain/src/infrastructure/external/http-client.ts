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

export class HttpClient {
  private config: Required<HttpClientConfig>;

  constructor(config: HttpClientConfig = {}) {
    this.config = {
      baseUrl: '',
      timeout: 30000,
      retries: 3,
      retryDelay: 1000,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'VALEO-NeuroERP-Integration/3.0'
      },
      ...config
    };
  }

  async get<T = unknown>(url: string, headers?: Record<string, string>): Promise<HttpResponse<T>> {
    return this.request<T>('GET', url, { headers });
  }

  async post<T = unknown>(url: string, data?: unknown, headers?: Record<string, string>): Promise<HttpResponse<T>> {
    return this.request<T>('POST', url, { body: data, headers });
  }

  async put<T = unknown>(url: string, data?: unknown, headers?: Record<string, string>): Promise<HttpResponse<T>> {
    return this.request<T>('PUT', url, { body: data, headers });
  }

  async patch<T = unknown>(url: string, data?: unknown, headers?: Record<string, string>): Promise<HttpResponse<T>> {
    return this.request<T>('PATCH', url, { body: data, headers });
  }

  async delete<T = unknown>(url: string, headers?: Record<string, string>): Promise<HttpResponse<T>> {
    return this.request<T>('DELETE', url, { headers });
  }

  private async request<T>(
    method: string,
    url: string,
    options: {
      body?: unknown;
      headers?: Record<string, string>;
    } = {}
  ): Promise<HttpResponse<T>> {
    const fullUrl = this.buildUrl(url);
    const requestHeaders = this.buildHeaders(options.headers);

    // eslint-disable-next-line no-undef
    const requestOptions: RequestInit = {
      method,
      headers: requestHeaders,
      signal: AbortSignal.timeout(this.config.timeout)
    };

    if (options.body) {
      requestOptions.body = JSON.stringify(options.body);
    }

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.config.retries; attempt++) {
      try {
        const response = await fetch(fullUrl, requestOptions);
        
        if (!response.ok) {
          const errorData = await this.parseResponse(response);
          const error = new Error(`HTTP ${response.status}: ${response.statusText}`) as HttpError;
          error.status = response.status;
          error.response = {
            status: response.status,
            statusText: response.statusText,
            headers: this.parseHeaders(response.headers),
            data: errorData
          };
          throw error;
        }

        const data = await this.parseResponse<T>(response);
        
        return {
          status: response.status,
          statusText: response.statusText,
          headers: this.parseHeaders(response.headers),
          data
        };
      } catch (error) {
        lastError = error as Error;
        
        if (attempt < this.config.retries) {
          await this.delay(this.config.retryDelay * Math.pow(2, attempt));
        }
      }
    }

    throw lastError || new Error('Request failed');
  }

  private buildUrl(url: string): string {
    if (url.startsWith('http')) {
      return url;
    }
    return `${this.config.baseUrl}${url.startsWith('/') ? url : `/${url}`}`;
  }

  private buildHeaders(customHeaders?: Record<string, string>): Record<string, string> {
    return {
      ...this.config.headers,
      ...customHeaders
    };
  }

  private async parseResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type');
    
    if (contentType?.includes('application/json')) {
      return await response.json() as T;
    }
    
    const text = await response.text();
    
    try {
      return JSON.parse(text) as T;
    } catch {
      return text as unknown as T;
    }
  }

  private parseHeaders(headers: Headers): Record<string, string> {
    const result: Record<string, string> = {};
    headers.forEach((value, key) => {
      result[key] = value;
    });
    return result;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

/**
 * HTTP Client Factory
 */
export class HttpClientFactory {
  private static instances = new Map<string, HttpClient>();

  static create(name: string, config?: HttpClientConfig): HttpClient {
    if (!this.instances.has(name)) {
      this.instances.set(name, new HttpClient(config));
    }
    return this.instances.get(name)!;
  }

  static get(name: string): HttpClient | undefined {
    return this.instances.get(name);
  }

  static clear(): void {
    this.instances.clear();
  }
}
