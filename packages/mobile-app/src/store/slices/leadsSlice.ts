import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiService from '../../services/api';

// Types
interface Lead {
  id: string;
  tenant_id: string;
  source: string;
  status: string;
  priority: string;
  estimated_value: number;
  company_name: string;
  contact_person: string;
  email?: string;
  phone?: string;
  assigned_to?: string;
  created_at: string;
  updated_at: string;
  converted_at?: string;
  converted_to_customer_id?: string;
  is_active: boolean;
  deleted_at?: string;
}

interface LeadsState {
  leads: Lead[];
  selectedLead: Lead | null;
  loading: boolean;
  error: string | null;
  total: number;
  page: number;
  size: number;
}

// Initial state
const initialState: LeadsState = {
  leads: [],
  selectedLead: null,
  loading: false,
  error: null,
  total: 0,
  page: 1,
  size: 50,
};

// Async thunks
export const fetchLeads = createAsyncThunk(
  'leads/fetchLeads',
  async (params: { skip?: number; limit?: number; status?: string; search?: string } = {}) => {
    const response = await apiService.getLeads(params);
    return response;
  }
);

export const fetchLead = createAsyncThunk(
  'leads/fetchLead',
  async (leadId: string) => {
    const response = await apiService.getLead(leadId);
    return response;
  }
);

export const createLead = createAsyncThunk(
  'leads/createLead',
  async (leadData: Partial<Lead>) => {
    const response = await apiService.createLead(leadData);
    return response;
  }
);

export const updateLead = createAsyncThunk(
  'leads/updateLead',
  async ({ id, data }: { id: string; data: Partial<Lead> }) => {
    const response = await apiService.updateLead(id, data);
    return response;
  }
);

// Slice
const leadsSlice = createSlice({
  name: 'leads',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setSelectedLead: (state, action: PayloadAction<Lead | null>) => {
      state.selectedLead = action.payload;
    },
    clearLeads: (state) => {
      state.leads = [];
      state.total = 0;
      state.page = 1;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch leads
      .addCase(fetchLeads.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchLeads.fulfilled, (state, action) => {
        state.loading = false;
        state.leads = action.payload.items || [];
        state.total = action.payload.total || 0;
        state.page = action.payload.page || 1;
        state.size = action.payload.size || 50;
      })
      .addCase(fetchLeads.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch leads';
      })

      // Fetch single lead
      .addCase(fetchLead.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchLead.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedLead = action.payload;
      })
      .addCase(fetchLead.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch lead';
      })

      // Create lead
      .addCase(createLead.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createLead.fulfilled, (state, action) => {
        state.loading = false;
        state.leads.unshift(action.payload);
        state.total += 1;
      })
      .addCase(createLead.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create lead';
      })

      // Update lead
      .addCase(updateLead.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateLead.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.leads.findIndex(l => l.id === action.payload.id);
        if (index !== -1) {
          state.leads[index] = action.payload;
        }
        if (state.selectedLead?.id === action.payload.id) {
          state.selectedLead = action.payload;
        }
      })
      .addCase(updateLead.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to update lead';
      });
  },
});

export const { clearError, setSelectedLead, clearLeads } = leadsSlice.actions;
export default leadsSlice.reducer;