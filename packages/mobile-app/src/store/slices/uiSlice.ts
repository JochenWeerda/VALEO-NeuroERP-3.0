import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// Types
interface UiState {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  sidebarCollapsed: boolean;
  notificationsEnabled: boolean;
  hapticFeedbackEnabled: boolean;
  loading: boolean;
  modal: {
    visible: boolean;
    type: string | null;
    data: any;
  };
  toast: {
    visible: boolean;
    message: string;
    type: 'success' | 'error' | 'info' | 'warning';
  };
}

// Initial state
const initialState: UiState = {
  theme: 'auto',
  language: 'en',
  sidebarCollapsed: false,
  notificationsEnabled: true,
  hapticFeedbackEnabled: true,
  loading: false,
  modal: {
    visible: false,
    type: null,
    data: null,
  },
  toast: {
    visible: false,
    message: '',
    type: 'info',
  },
};

// Slice
const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<'light' | 'dark' | 'auto'>) => {
      state.theme = action.payload;
    },
    setLanguage: (state, action: PayloadAction<string>) => {
      state.language = action.payload;
    },
    toggleSidebar: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed;
    },
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.sidebarCollapsed = action.payload;
    },
    setNotificationsEnabled: (state, action: PayloadAction<boolean>) => {
      state.notificationsEnabled = action.payload;
    },
    setHapticFeedbackEnabled: (state, action: PayloadAction<boolean>) => {
      state.hapticFeedbackEnabled = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    showModal: (state, action: PayloadAction<{ type: string; data?: any }>) => {
      state.modal.visible = true;
      state.modal.type = action.payload.type;
      state.modal.data = action.payload.data || null;
    },
    hideModal: (state) => {
      state.modal.visible = false;
      state.modal.type = null;
      state.modal.data = null;
    },
    showToast: (state, action: PayloadAction<{ message: string; type?: 'success' | 'error' | 'info' | 'warning' }>) => {
      state.toast.visible = true;
      state.toast.message = action.payload.message;
      state.toast.type = action.payload.type || 'info';
    },
    hideToast: (state) => {
      state.toast.visible = false;
      state.toast.message = '';
    },
  },
});

export const {
  setTheme,
  setLanguage,
  toggleSidebar,
  setSidebarCollapsed,
  setNotificationsEnabled,
  setHapticFeedbackEnabled,
  setLoading,
  showModal,
  hideModal,
  showToast,
  hideToast,
} = uiSlice.actions;

export default uiSlice.reducer;