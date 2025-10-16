/**
 * AI-Powered Autocomplete API Service
 * Frontend service for communicating with AI autocomplete endpoints
 */

export interface AutocompleteSuggestion {
  text: string;
  confidence: number;
  category: string;
  metadata?: Record<string, any>;
}

export interface AutocompleteRequest {
  query: string;
  context: string;
  domain: string;
  max_suggestions?: number;
}

export interface AutocompleteResponse {
  suggestions: AutocompleteSuggestion[];
  query: string;
  context: string;
  domain: string;
  processing_time_ms: number;
}

class AutocompleteAPIService {
  private baseURL: string;

  constructor(baseURL: string = '/api/v1/autocomplete') {
    this.baseURL = baseURL;
  }

  /**
   * Get autocomplete suggestions from AI service
   */
  async getSuggestions(request: AutocompleteRequest): Promise<AutocompleteResponse> {
    try {
      const response = await fetch(`${this.baseURL}/suggest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: AutocompleteResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to fetch autocomplete suggestions:', error);
      // Return empty suggestions on error
      return {
        suggestions: [],
        query: request.query,
        context: request.context,
        domain: request.domain,
        processing_time_ms: 0,
      };
    }
  }

  /**
   * Get supported autocomplete domains
   */
  async getDomains(): Promise<{ domains: Array<{ id: string; name: string; description: string }> }> {
    try {
      const response = await fetch(`${this.baseURL}/domains`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch autocomplete domains:', error);
      // Return default domains on error
      return {
        domains: [
          {
            id: 'general',
            name: 'Allgemein',
            description: 'Allgemeine ERP-Funktionen',
          },
        ],
      };
    }
  }

  /**
   * Create a debounced version of getSuggestions
   */
  createDebouncedSuggestions(debounceMs: number = 300) {
    let timeoutId: NodeJS.Timeout;

    return (request: AutocompleteRequest): Promise<AutocompleteResponse> => {
      return new Promise((resolve) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(async () => {
          const result = await this.getSuggestions(request);
          resolve(result);
        }, debounceMs);
      });
    };
  }
}

// Export singleton instance
export const autocompleteAPI = new AutocompleteAPIService();