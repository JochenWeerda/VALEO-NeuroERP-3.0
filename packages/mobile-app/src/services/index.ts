import * as Notifications from 'expo-notifications';
import * as SecureStore from 'expo-secure-store';
import NetInfo from '@react-native-community/netinfo';
import { store } from '../store';
import { checkBiometricSupport } from '../store/slices/authSlice';
import apiService from './api';

export const initializeServices = async () => {
  try {
    // Initialize API service
    console.log('Initializing API service...');

    // Check network connectivity
    const networkState = await NetInfo.fetch();
    console.log('Network state:', networkState);

    // Initialize biometric authentication
    store.dispatch(checkBiometricSupport());

    // Configure notifications
    await configureNotifications();

    // Load persisted auth state
    await loadPersistedAuthState();

    // Initialize offline queue processing
    setupOfflineQueueProcessing();

    // Initialize WebSocket connection for real-time updates
    initializeWebSocket();

    console.log('All services initialized successfully');
  } catch (error) {
    console.error('Error initializing services:', error);
    throw error;
  }
};

const configureNotifications = async () => {
  // Request permissions
  const { status } = await Notifications.requestPermissionsAsync();
  if (status !== 'granted') {
    console.warn('Notification permissions not granted');
    return;
  }

  // Configure notification channels
  await Notifications.setNotificationChannelAsync('leads', {
    name: 'New Leads',
    importance: Notifications.AndroidImportance.HIGH,
    vibrationPattern: [0, 250, 250, 250],
    lightColor: '#FF6B35',
    sound: 'default',
  });

  await Notifications.setNotificationChannelAsync('tasks', {
    name: 'Task Reminders',
    importance: Notifications.AndroidImportance.HIGH,
    vibrationPattern: [0, 250, 250, 250],
    lightColor: '#4ECDC4',
    sound: 'default',
  });

  await Notifications.setNotificationChannelAsync('opportunities', {
    name: 'Opportunities',
    importance: Notifications.AndroidImportance.DEFAULT,
    vibrationPattern: [0, 250, 250, 250],
    lightColor: '#45B7D1',
    sound: 'default',
  });

  // Set up notification handler
  Notifications.setNotificationHandler({
    handleNotification: async () => ({
      shouldShowAlert: true,
      shouldPlaySound: true,
      shouldSetBadge: true,
    }),
  });
};

const loadPersistedAuthState = async () => {
  try {
    const token = await SecureStore.getItemAsync('auth_token');
    const refreshToken = await SecureStore.getItemAsync('refresh_token');
    const userData = await SecureStore.getItemAsync('user_data');

    if (token && userData) {
      const user = JSON.parse(userData);
      // Dispatch action to restore auth state
      store.dispatch({
        type: 'auth/restoreAuthState',
        payload: { token, refreshToken, user },
      });
    }
  } catch (error) {
    console.error('Error loading persisted auth state:', error);
  }
};

const setupOfflineQueueProcessing = () => {
  // Process offline queue when network comes back online
  const unsubscribe = NetInfo.addEventListener(state => {
    if (state.isConnected) {
      apiService.processOfflineQueue();
    }
  });

  // Process queue on app start if online
  NetInfo.fetch().then(state => {
    if (state.isConnected) {
      apiService.processOfflineQueue();
    }
  });

  // Clean up on app close
  return unsubscribe;
};

const initializeWebSocket = () => {
  // WebSocket initialization for real-time updates
  // This would connect to the CRM WebSocket endpoint for live data
  console.log('WebSocket initialization placeholder');
  // TODO: Implement WebSocket connection for real-time CRM updates
};

// Notification listeners
Notifications.addNotificationReceivedListener(notification => {
  console.log('Notification received:', notification);
});

Notifications.addNotificationResponseReceivedListener(response => {
  console.log('Notification response:', response);
  // Handle notification tap - navigate to relevant screen
  const data = response.notification.request.content.data;
  if (data?.type === 'lead') {
    // Navigate to lead detail
  } else if (data?.type === 'task') {
    // Navigate to task detail
  }
});

// Background notification handler
Notifications.addNotificationReceivedListener(async notification => {
  const data = notification.request.content.data;

  // Handle background notifications
  if (data?.type === 'sync_complete') {
    // Refresh local data
    await apiService.processOfflineQueue();
  }
});