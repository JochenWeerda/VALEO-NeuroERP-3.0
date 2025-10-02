/**
 * HTTP Client for External Services
 */
export class HttpClient {
    config;
    constructor(config = {}) {
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
    async get(url, headers) {
        return this.request('GET', url, { headers });
    }
    async post(url, data, headers) {
        return this.request('POST', url, { body: data, headers });
    }
    async put(url, data, headers) {
        return this.request('PUT', url, { body: data, headers });
    }
    async patch(url, data, headers) {
        return this.request('PATCH', url, { body: data, headers });
    }
    async delete(url, headers) {
        return this.request('DELETE', url, { headers });
    }
    async request(method, url, options = {}) {
        const fullUrl = this.buildUrl(url);
        const requestHeaders = this.buildHeaders(options.headers);
        const requestOptions = {
            method,
            headers: requestHeaders,
            signal: AbortSignal.timeout(this.config.timeout)
        };
        if (options.body) {
            requestOptions.body = JSON.stringify(options.body);
        }
        let lastError = null;
        for (let attempt = 0; attempt <= this.config.retries; attempt++) {
            try {
                const response = await fetch(fullUrl, requestOptions);
                if (!response.ok) {
                    const errorData = await this.parseResponse(response);
                    const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
                    error.status = response.status;
                    error.response = {
                        status: response.status,
                        statusText: response.statusText,
                        headers: this.parseHeaders(response.headers),
                        data: errorData
                    };
                    throw error;
                }
                const data = await this.parseResponse(response);
                return {
                    status: response.status,
                    statusText: response.statusText,
                    headers: this.parseHeaders(response.headers),
                    data
                };
            }
            catch (error) {
                lastError = error;
                if (attempt < this.config.retries) {
                    await this.delay(this.config.retryDelay * Math.pow(2, attempt));
                }
            }
        }
        throw lastError || new Error('Request failed');
    }
    buildUrl(url) {
        if (url.startsWith('http')) {
            return url;
        }
        return `${this.config.baseUrl}${url.startsWith('/') ? url : `/${url}`}`;
    }
    buildHeaders(customHeaders) {
        return {
            ...this.config.headers,
            ...customHeaders
        };
    }
    async parseResponse(response) {
        const contentType = response.headers.get('content-type');
        if (contentType?.includes('application/json')) {
            return await response.json();
        }
        const text = await response.text();
        try {
            return JSON.parse(text);
        }
        catch {
            return text;
        }
    }
    parseHeaders(headers) {
        const result = {};
        headers.forEach((value, key) => {
            result[key] = value;
        });
        return result;
    }
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
/**
 * HTTP Client Factory
 */
export class HttpClientFactory {
    static instances = new Map();
    static create(name, config) {
        if (!this.instances.has(name)) {
            this.instances.set(name, new HttpClient(config));
        }
        return this.instances.get(name);
    }
    static get(name) {
        return this.instances.get(name);
    }
    static clear() {
        this.instances.clear();
    }
}
//# sourceMappingURL=http-client.js.map