import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import * as SecureStore from 'expo-secure-store';
import * as LocalAuthentication from 'expo-local-authentication';

// Types
interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
  avatar?: string;
}

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  biometricEnabled: boolean;
  biometricSupported: boolean;
  loading: boolean;
  error: string | null;
}

// Initial state
const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  token: null,
  refreshToken: null,
  biometricEnabled: false,
  biometricSupported: false,
  loading: false,
  error: null,
};

// Async thunks
export const login = createAsyncThunk(
  'auth/login',
  async ({ email, password }: { email: string; password: string }) => {
    // API call to login endpoint
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    return data;
  }
);

export const refreshToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { getState }) => {
    const state = getState() as { auth: AuthState };
    const refreshToken = state.auth.refreshToken;

    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refreshToken }),
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    return data;
  }
);

export const checkBiometricSupport = createAsyncThunk(
  'auth/checkBiometricSupport',
  async () => {
    const compatible = await LocalAuthentication.hasHardwareAsync();
    const enrolled = await LocalAuthentication.isEnrolledAsync();
    return { supported: compatible && enrolled };
  }
);

export const authenticateWithBiometrics = createAsyncThunk(
  'auth/authenticateWithBiometrics',
  async () => {
    const result = await LocalAuthentication.authenticateAsync({
      promptMessage: 'Authenticate to access CRM',
      fallbackLabel: 'Use PIN',
    });

    if (!result.success) {
      throw new Error('Biometric authentication failed');
    }

    // Retrieve stored credentials
    const email = await SecureStore.getItemAsync('biometric_email');
    const password = await SecureStore.getItemAsync('biometric_password');

    if (!email || !password) {
      throw new Error('No stored credentials found');
    }

    return { email, password };
  }
);

// Slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.isAuthenticated = false;
      state.user = null;
      state.token = null;
      state.refreshToken = null;
      state.error = null;
      // Clear secure storage
      SecureStore.deleteItemAsync('auth_token');
      SecureStore.deleteItemAsync('refresh_token');
      SecureStore.deleteItemAsync('user_data');
    },
    clearError: (state) => {
      state.error = null;
    },
    setBiometricEnabled: (state, action: PayloadAction<boolean>) => {
      state.biometricEnabled = action.payload;
      SecureStore.setItemAsync('biometric_enabled', action.payload.toString());
    },
    updateUser: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
        SecureStore.setItemAsync('user_data', JSON.stringify(state.user));
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.refreshToken = action.payload.refreshToken;
        state.error = null;

        // Store in secure storage
        SecureStore.setItemAsync('auth_token', action.payload.token);
        SecureStore.setItemAsync('refresh_token', action.payload.refreshToken);
        SecureStore.setItemAsync('user_data', JSON.stringify(action.payload.user));
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Login failed';
      })

      // Token refresh
      .addCase(refreshToken.fulfilled, (state, action) => {
        state.token = action.payload.token;
        state.refreshToken = action.payload.refreshToken;
        SecureStore.setItemAsync('auth_token', action.payload.token);
        SecureStore.setItemAsync('refresh_token', action.payload.refreshToken);
      })

      // Biometric support check
      .addCase(checkBiometricSupport.fulfilled, (state, action) => {
        state.biometricSupported = action.payload.supported;
        const stored = SecureStore.getItemAsync('biometric_enabled');
        stored.then((enabled) => {
          state.biometricEnabled = enabled === 'true';
        });
      })

      // Biometric authentication
      .addCase(authenticateWithBiometrics.fulfilled, (state, action) => {
        // This will trigger the login thunk
        // The actual login logic is handled by the login thunk
      });
  },
});

export const { logout, clearError, setBiometricEnabled, updateUser } = authSlice.actions;
export default authSlice.reducer;