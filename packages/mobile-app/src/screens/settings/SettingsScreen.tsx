import React from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import {
  Text,
  Surface,
  List,
  Switch,
  Button,
  useTheme,
  Divider,
} from 'react-native-paper';
import { RootState } from '../../store';
import { setBiometricEnabled } from '../../store/slices/authSlice';
import { clearOfflineData } from '../../store/slices/offlineSlice';

export default function SettingsScreen() {
  const dispatch = useDispatch();
  const theme = useTheme();

  const { biometricEnabled, biometricSupported } = useSelector(
    (state: RootState) => state.auth
  );
  const { syncEnabled, lastSync } = useSelector(
    (state: RootState) => state.offline
  );

  const handleBiometricToggle = (value: boolean) => {
    dispatch(setBiometricEnabled(value));
  };

  const handleClearOfflineData = () => {
    Alert.alert(
      'Clear Offline Data',
      'This will remove all locally stored data. Are you sure?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: () => dispatch(clearOfflineData()),
        },
      ]
    );
  };

  const handleSyncNow = () => {
    // TODO: Implement manual sync
    Alert.alert('Sync', 'Manual sync not yet implemented');
  };

  return (
    <ScrollView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <Surface style={styles.section} elevation={1}>
        <Text variant="titleLarge" style={styles.sectionTitle}>
          Account Settings
        </Text>

        <List.Item
          title="Biometric Authentication"
          description={biometricSupported ? "Enable fingerprint/face unlock" : "Not available on this device"}
          left={(props) => <List.Icon {...props} icon="fingerprint" />}
          right={() => (
            <Switch
              value={biometricEnabled}
              onValueChange={handleBiometricToggle}
              disabled={!biometricSupported}
            />
          )}
        />

        <Divider />

        <List.Item
          title="Change Password"
          description="Update your account password"
          left={(props) => <List.Icon {...props} icon="lock" />}
          onPress={() => Alert.alert('Feature', 'Password change not yet implemented')}
        />
      </Surface>

      <Surface style={styles.section} elevation={1}>
        <Text variant="titleLarge" style={styles.sectionTitle}>
          Data & Sync
        </Text>

        <List.Item
          title="Offline Mode"
          description={syncEnabled ? "Data sync enabled" : "Working offline only"}
          left={(props) => <List.Icon {...props} icon="sync" />}
          right={() => (
            <Switch
              value={syncEnabled}
              onValueChange={() => {/* TODO: Toggle sync */}}
            />
          )}
        />

        <Divider />

        <List.Item
          title="Last Sync"
          description={lastSync ? new Date(lastSync).toLocaleString() : "Never synced"}
          left={(props) => <List.Icon {...props} icon="clock-outline" />}
        />

        <Divider />

        <List.Item
          title="Sync Now"
          description="Manually sync data with server"
          left={(props) => <List.Icon {...props} icon="refresh" />}
          onPress={handleSyncNow}
        />

        <Divider />

        <List.Item
          title="Clear Offline Data"
          description="Remove all locally stored data"
          left={(props) => <List.Icon {...props} icon="delete-outline" />}
          onPress={handleClearOfflineData}
        />
      </Surface>

      <Surface style={styles.section} elevation={1}>
        <Text variant="titleLarge" style={styles.sectionTitle}>
          Notifications
        </Text>

        <List.Item
          title="Push Notifications"
          description="Receive alerts for new leads and tasks"
          left={(props) => <List.Icon {...props} icon="bell" />}
          right={() => (
            <Switch
              value={true} // TODO: Connect to actual setting
              onValueChange={() => {/* TODO: Toggle notifications */}}
            />
          )}
        />

        <Divider />

        <List.Item
          title="Task Reminders"
          description="Get notified about upcoming tasks"
          left={(props) => <List.Icon {...props} icon="calendar-check" />}
          right={() => (
            <Switch
              value={true} // TODO: Connect to actual setting
              onValueChange={() => {/* TODO: Toggle task reminders */}}
            />
          )}
        />
      </Surface>

      <Surface style={styles.section} elevation={1}>
        <Text variant="titleLarge" style={styles.sectionTitle}>
          App Information
        </Text>

        <List.Item
          title="Version"
          description="1.0.0"
          left={(props) => <List.Icon {...props} icon="information" />}
        />

        <Divider />

        <List.Item
          title="Privacy Policy"
          description="View our privacy policy"
          left={(props) => <List.Icon {...props} icon="shield-account" />}
          onPress={() => Alert.alert('Feature', 'Privacy policy not yet implemented')}
        />

        <Divider />

        <List.Item
          title="Terms of Service"
          description="View terms and conditions"
          left={(props) => <List.Icon {...props} icon="file-document" />}
          onPress={() => Alert.alert('Feature', 'Terms of service not yet implemented')}
        />
      </Surface>

      <View style={styles.logoutContainer}>
        <Button
          mode="outlined"
          onPress={() => {/* TODO: Implement logout */}}
          style={styles.logoutButton}
          textColor={theme.colors.error}
        >
          Logout
        </Button>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  section: {
    margin: 16,
    marginBottom: 8,
    borderRadius: 8,
  },
  sectionTitle: {
    padding: 16,
    paddingBottom: 8,
    fontWeight: 'bold',
  },
  logoutContainer: {
    margin: 16,
    marginTop: 8,
  },
  logoutButton: {
    borderColor: '#F44336',
  },
});