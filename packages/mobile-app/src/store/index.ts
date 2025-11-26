import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { combineReducers } from 'redux';

// Reducers
import authReducer from './slices/authSlice';
import customersReducer from './slices/customersSlice';
import leadsReducer from './slices/leadsSlice';
import tasksReducer from './slices/tasksSlice';
import uiReducer from './slices/uiSlice';
import offlineReducer from './slices/offlineSlice';

const persistConfig = {
  key: 'root',
  storage: AsyncStorage,
  whitelist: ['auth', 'ui'], // Only persist auth and UI state
};

const rootReducer = combineReducers({
  auth: authReducer,
  customers: customersReducer,
  leads: leadsReducer,
  tasks: tasksReducer,
  ui: uiReducer,
  offline: offlineReducer,
});

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});

export const persistor = persistStore(store);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;