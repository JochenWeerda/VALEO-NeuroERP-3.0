import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// Types
interface OfflineRequest {
  id: string;
  method: string;
  url: string;
  data?: any;
  timestamp: number;
  retryCount: number;
}

interface OfflineState {
  isOnline: boolean;
  pendingRequests: OfflineRequest[];
  syncInProgress: boolean;
  lastSyncTime: number | null;
  syncErrors: string[];
}

// Initial state
const initialState: OfflineState = {
  isOnline: true,
  pendingRequests: [],
  syncInProgress: false,
  lastSyncTime: null,
  syncErrors: [],
};

// Slice
const offlineSlice = createSlice({
  name: 'offline',
  initialState,
  reducers: {
    setOnline: (state, action: PayloadAction<boolean>) => {
      state.isOnline = action.payload;
    },
    addPendingRequest: (state, action: PayloadAction<Omit<OfflineRequest, 'timestamp' | 'retryCount'>>) => {
      const request: OfflineRequest = {
        ...action.payload,
        timestamp: Date.now(),
        retryCount: 0,
      };
      state.pendingRequests.push(request);
    },
    removePendingRequest: (state, action: PayloadAction<string>) => {
      state.pendingRequests = state.pendingRequests.filter(req => req.id !== action.payload);
    },
    incrementRetryCount: (state, action: PayloadAction<string>) => {
      const request = state.pendingRequests.find(req => req.id === action.payload);
      if (request) {
        request.retryCount += 1;
      }
    },
    setSyncInProgress: (state, action: PayloadAction<boolean>) => {
      state.syncInProgress = action.payload;
    },
    setLastSyncTime: (state, action: PayloadAction<number>) => {
      state.lastSyncTime = action.payload;
    },
    addSyncError: (state, action: PayloadAction<string>) => {
      state.syncErrors.push(action.payload);
      // Keep only last 10 errors
      if (state.syncErrors.length > 10) {
        state.syncErrors = state.syncErrors.slice(-10);
      }
    },
    clearSyncErrors: (state) => {
      state.syncErrors = [];
    },
    clearPendingRequests: (state) => {
      state.pendingRequests = [];
    },
  },
});

export const {
  setOnline,
  addPendingRequest,
  removePendingRequest,
  incrementRetryCount,
  setSyncInProgress,
  setLastSyncTime,
  addSyncError,
  clearSyncErrors,
  clearPendingRequests,
} = offlineSlice.actions;

export default offlineSlice.reducer;