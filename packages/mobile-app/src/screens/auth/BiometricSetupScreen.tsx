import React, { useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { useDispatch } from 'react-redux';
import {
  Text,
  Button,
  Surface,
  useTheme,
  Switch,
  List,
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import * as LocalAuthentication from 'expo-local-authentication';
import { setBiometricEnabled } from '../../store/slices/authSlice';

export default function BiometricSetupScreen() {
  const [biometricEnabled, setBiometricEnabled] = useState(false);
  const [loading, setLoading] = useState(false);
  const [biometricTypes, setBiometricTypes] = useState<LocalAuthentication.AuthenticationType[]>([]);

  const dispatch = useDispatch();
  const navigation = useNavigation();
  const theme = useTheme();

  React.useEffect(() => {
    checkBiometricSupport();
  }, []);

  const checkBiometricSupport = async () => {
    try {
      const compatible = await LocalAuthentication.hasHardwareAsync();
      const enrolled = await LocalAuthentication.isEnrolledAsync();
      const types = await LocalAuthentication.supportedAuthenticationTypesAsync();

      setBiometricTypes(types);
      setBiometricEnabled(enrolled && compatible);
    } catch (error) {
      console.error('Error checking biometric support:', error);
    }
  };

  const handleBiometricToggle = async (value: boolean) => {
    if (value) {
      await enableBiometricAuth();
    } else {
      await disableBiometricAuth();
    }
  };

  const enableBiometricAuth = async () => {
    setLoading(true);
    try {
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: 'Authenticate to enable biometric login',
        fallbackLabel: 'Use PIN',
      });

      if (result.success) {
        dispatch(setBiometricEnabled(true));
        setBiometricEnabled(true);
        Alert.alert(
          'Success',
          'Biometric authentication has been enabled.',
          [{ text: 'OK', onPress: () => navigation.goBack() }]
        );
      } else {
        Alert.alert('Authentication Failed', 'Please try again.');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to enable biometric authentication.');
    } finally {
      setLoading(false);
    }
  };

  const disableBiometricAuth = async () => {
    dispatch(setBiometricEnabled(false));
    setBiometricEnabled(false);
    Alert.alert(
      'Success',
      'Biometric authentication has been disabled.',
      [{ text: 'OK' }]
    );
  };

  const getBiometricTypeName = (type: LocalAuthentication.AuthenticationType) => {
    switch (type) {
      case LocalAuthentication.AuthenticationType.FINGERPRINT:
        return 'Fingerprint';
      case LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION:
        return 'Face ID';
      case LocalAuthentication.AuthenticationType.IRIS:
        return 'Iris';
      default:
        return 'Biometric';
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <Surface style={styles.setupCard} elevation={4}>
        <Text variant="headlineMedium" style={styles.title}>
          Biometric Setup
        </Text>
        <Text variant="bodyLarge" style={styles.subtitle}>
          Enable biometric authentication for quick login
        </Text>

        <List.Section>
          <List.Subheader>Available Biometric Methods</List.Subheader>
          {biometricTypes.map((type, index) => (
            <List.Item
              key={index}
              title={getBiometricTypeName(type)}
              left={(props) => <List.Icon {...props} icon="fingerprint" />}
            />
          ))}
          {biometricTypes.length === 0 && (
            <List.Item
              title="No biometric methods available"
              left={(props) => <List.Icon {...props} icon="lock" />}
            />
          )}
        </List.Section>

        <View style={styles.toggleContainer}>
          <Text variant="bodyLarge">Enable Biometric Login</Text>
          <Switch
            value={biometricEnabled}
            onValueChange={handleBiometricToggle}
            disabled={loading || biometricTypes.length === 0}
          />
        </View>

        <Button
          mode="outlined"
          onPress={() => navigation.goBack()}
          style={styles.backButton}
        >
          Back to Login
        </Button>
      </Surface>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
  },
  setupCard: {
    padding: 24,
    borderRadius: 12,
  },
  title: {
    textAlign: 'center',
    marginBottom: 8,
    fontWeight: 'bold',
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: 32,
    opacity: 0.7,
  },
  toggleContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 8,
    marginVertical: 16,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
  },
  backButton: {
    marginTop: 16,
  },
});