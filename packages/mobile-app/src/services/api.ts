import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import * as SecureStore from 'expo-secure-store';
import NetInfo from '@react-native-community/netinfo';

// Configuration
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api/v1';
const WEBSOCKET_URL = process.env.WEBSOCKET_URL || 'ws://localhost:8000/ws';

class ApiService {
  private axiosInstance: AxiosInstance;
  private refreshPromise: Promise<any> | null = null;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private async setupInterceptors() {
    // Request interceptor
    this.axiosInstance.interceptors.request.use(
      async (config) => {
        // Add auth token
        const token = await SecureStore.getItemAsync('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Add tenant ID
        config.headers['X-Tenant-ID'] = process.env.TENANT_ID || '00000000-0000-0000-0000-000000000001';

        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            // Try to refresh token
            const newToken = await this.refreshToken();
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return this.axiosInstance(originalRequest);
          } catch (refreshError) {
            // Refresh failed, logout user
            await this.logout();
            throw refreshError;
          }
        }

        return Promise.reject(error);
      }
    );
  }

  private async refreshToken(): Promise<string> {
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = (async () => {
      try {
        const refreshToken = await SecureStore.getItemAsync('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token');
        }

        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refreshToken,
        });

        const { token, refreshToken: newRefreshToken } = response.data;

        await SecureStore.setItemAsync('auth_token', token);
        await SecureStore.setItemAsync('refresh_token', newRefreshToken);

        return token;
      } finally {
        this.refreshPromise = null;
      }
    })();

    return this.refreshPromise;
  }

  private async logout() {
    await SecureStore.deleteItemAsync('auth_token');
    await SecureStore.deleteItemAsync('refresh_token');
    await SecureStore.deleteItemAsync('user_data');
    // Dispatch logout action would be handled by Redux
  }

  // Generic request methods
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.get(url, config);
    return response.data;
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.post(url, data, config);
    return response.data;
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.put(url, data, config);
    return response.data;
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.patch(url, data, config);
    return response.data;
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.delete(url, config);
    return response.data;
  }

  // CRM-specific methods
  async getCustomers(params?: { skip?: number; limit?: number; search?: string }) {
    return this.get('/crm/customers', { params });
  }

  async getCustomer(id: string) {
    return this.get(`/crm/customers/${id}`);
  }

  async createCustomer(data: any) {
    return this.post('/crm/customers', data);
  }

  async updateCustomer(id: string, data: any) {
    return this.patch(`/crm/customers/${id}`, data);
  }

  async getLeads(params?: { skip?: number; limit?: number; status?: string; search?: string }) {
    return this.get('/crm/leads', { params });
  }

  async getLead(id: string) {
    return this.get(`/crm/leads/${id}`);
  }

  async createLead(data: any) {
    return this.post('/crm/leads', data);
  }

  async updateLead(id: string, data: any) {
    return this.patch(`/crm/leads/${id}`, data);
  }

  async getTasks(params?: { skip?: number; limit?: number; status?: string; assigned_to?: string }) {
    return this.get('/crm/tasks', { params });
  }

  async getTask(id: string) {
    return this.get(`/crm/tasks/${id}`);
  }

  async createTask(data: any) {
    return this.post('/crm/tasks', data);
  }

  async updateTask(id: string, data: any) {
    return this.patch(`/crm/tasks/${id}`, data);
  }

  // AI features
  async scoreLead(leadId: string, features: any) {
    return this.post('/crm/ai/lead-score', { lead_id: leadId, features });
  }

  async predictChurn(customerId: string, features: any) {
    return this.post('/crm/ai/predict/churn', { customer_id: customerId, features });
  }

  async getNextActions(entityId: string, entityType: string, context: any) {
    return this.post('/crm/ai/recommend/actions', {
      customer_id: entityType === 'customer' ? entityId : undefined,
      lead_id: entityType === 'lead' ? entityId : undefined,
      context,
    });
  }

  // Offline queue management
  private offlineQueue: Array<{
    id: string;
    method: string;
    url: string;
    data?: any;
    resolve: Function;
    reject: Function;
  }> = [];

  async queueOfflineRequest(method: string, url: string, data?: any): Promise<any> {
    const networkState = await NetInfo.fetch();

    if (networkState.isConnected) {
      // Online, execute immediately
      const result = await this.axiosInstance.request({ method, url, data });
      return result.data;
    } else {
      // Offline, queue for later
      const requestId = `req_${Date.now()}_${Math.random()}`;
      this.offlineQueue.push({
        id: requestId,
        method,
        url,
        data,
        resolve: () => {},
        reject: () => {},
      });

      // Store in persistent queue
      await this.storeOfflineRequest(requestId, { method, url, data });

      // Return a promise that resolves when the request is processed
      return new Promise((resolve, reject) => {
        // In offline mode, we don't resolve immediately
        // The request will be processed when connection is restored
        resolve({ queued: true, requestId });
      });
    }
  }

  private async storeOfflineRequest(id: string, request: any) {
    const stored = await SecureStore.getItemAsync('offline_queue');
    const queue = stored ? JSON.parse(stored) : [];
    queue.push({ id, request, timestamp: Date.now() });
    await SecureStore.setItemAsync('offline_queue', JSON.stringify(queue));
  }

  async processOfflineQueue() {
    const networkState = await NetInfo.fetch();
    if (!networkState.isConnected) return;

    const stored = await SecureStore.getItemAsync('offline_queue');
    if (!stored) return;

    const queue = JSON.parse(stored);
    const processedIds: string[] = [];

    for (const item of queue) {
      try {
        const result = await this.axiosInstance.request({
          method: item.request.method,
          url: item.request.url,
          data: item.request.data,
        });
        processedIds.push(item.id);
      } catch (error) {
        // Keep failed requests in queue for retry
        console.warn('Offline request failed:', error);
      }
    }

    // Remove processed requests
    const remaining = queue.filter((item: any) => !processedIds.includes(item.id));
    await SecureStore.setItemAsync('offline_queue', JSON.stringify(remaining));
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;