import { PsmDto } from '@/schemas/psm';

// API Client für PSM
class PsmService {
  private baseUrl = '/api/v1/agrar/psm';

  // CRUD Operations
  async getPsm(id: string): Promise<PsmDto> {
    const response = await fetch(`${this.baseUrl}/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch PSM: ${response.statusText}`);
    }
    return response.json();
  }

  async createPsm(psm: Omit<PsmDto, 'id'>): Promise<PsmDto> {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(psm),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create PSM');
    }

    return response.json();
  }

  async updatePsm(id: string, psm: Partial<PsmDto>): Promise<PsmDto> {
    const response = await fetch(`${this.baseUrl}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(psm),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update PSM');
    }

    return response.json();
  }

  async deletePsm(id: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/${id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`Failed to delete PSM: ${response.statusText}`);
    }
  }

  // Search & List
  async searchPsm(query: string, limit = 10): Promise<PsmDto[]> {
    const params = new URLSearchParams({ q: query, limit: limit.toString() });
    const response = await fetch(`${this.baseUrl}/search?${String(params)}`);

    if (!response.ok) {
      throw new Error(`Failed to search PSM: ${response.statusText}`);
    }

    return response.json();
  }

  async listPsm(filters: {
    search?: string;
    mittel_typ?: string;
    wirkstoff?: string;
    kultur?: string;
    bienenschutz?: boolean;
    wasserschutz_gebiet?: boolean;
    ist_aktiv?: boolean;
    skip?: number;
    limit?: number;
  } = {}): Promise<{ items: PsmDto[]; total: number; page: number; pages: number }> {
    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await fetch(`${this.baseUrl}?${String(params)}`);

    if (!response.ok) {
      throw new Error(`Failed to list PSM: ${response.statusText}`);
    }

    return response.json();
  }

  // BVL Sync
  async syncFromBvl(bvlPsmId: string): Promise<{
    current: PsmDto;
    bvl: PsmDto;
    diff: Record<string, { current: any; bvl: any }>;
  }> {
    const response = await fetch(`${this.baseUrl}/bvl-sync`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ bvl_psm_id: bvlPsmId }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to sync from BVL');
    }

    return response.json();
  }

  async applyBvlSync(id: string, bvlData: Partial<PsmDto>): Promise<PsmDto> {
    const updateData: Partial<PsmDto> = {
      ...bvlData,
      datenquelle: `BVL PSM-API (${new Date().toISOString().split('T')[0]})`,
    };

    if (bvlData.zulassung) {
      updateData.zulassung = {
        ...bvlData.zulassung,
        letztePruefung: new Date().toISOString(),
      };
    }

    return this.updatePsm(id, updateData);
  }

  // Codelisten
  async getCodelists(): Promise<{
    ghs: Array<{ code: string; label: string; icon: string }>;
    h_saetze: Array<{ code: string; text: string }>;
    p_saetze: Array<{ code: string; text: string }>;
    euh_saetze: Array<{ code: string; text: string }>;
    auflagen: Array<{ code: string; kategorie: string; text: string; version: string }>;
    bbch: Record<string, Array<{ code: string; description: string }>>;
    kulturen: Array<{ code: string; name: string }>;
  }> {
    const response = await fetch(`${this.baseUrl}/codelists`);

    if (!response.ok) {
      throw new Error(`Failed to fetch codelists: ${response.statusText}`);
    }

    return response.json();
  }

  // Statistics
  async getStats(): Promise<{
    total_psm: number;
    by_type: Record<string, number>;
    by_safety: Record<string, number>;
    approval_warnings: {
      expiring_soon: number;
      already_expired: number;
    };
    stock_summary: {
      total_stock: number;
      avg_price: number;
    };
  }> {
    const response = await fetch(`${this.baseUrl}/stats/overview`);

    if (!response.ok) {
      throw new Error(`Failed to fetch stats: ${response.statusText}`);
    }

    return response.json();
  }

  // BBCH Validation
  async validateBbch(kulturCode: string, bbchVon: string, bbchBis: string): Promise<{
    valid: boolean;
    errors: string[];
    suggestions?: Array<{ code: string; description: string }>;
  }> {
    const response = await fetch(`${this.baseUrl}/validate-bbch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ kultur_code: kulturCode, bbch_von: bbchVon, bbch_bis: bbchBis }),
    });

    if (!response.ok) {
      throw new Error(`Failed to validate BBCH: ${response.statusText}`);
    }

    return response.json();
  }

  // Export
  async exportLabel(id: string, format: 'pdf' | 'png' = 'pdf'): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/${id}/export-label?format=${format}`);

    if (!response.ok) {
      throw new Error(`Failed to export label: ${response.statusText}`);
    }

    return response.blob();
  }

  async exportSafetyDataSheet(id: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/${id}/export-sds`);

    if (!response.ok) {
      throw new Error(`Failed to export SDS: ${response.statusText}`);
    }

    return response.blob();
  }
}

// Singleton instance
export const psmService = new PsmService();
export default psmService;