import React, { useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { useDispatch } from 'react-redux';
import {
  Text,
  TextInput,
  Button,
  Surface,
  useTheme,
  HelperText,
} from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { login } from '../../store/slices/authSlice';
import { apiService } from '../../services/api';

export default function LoginScreen() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ username?: string; password?: string }>({});

  const dispatch = useDispatch();
  const navigation = useNavigation();
  const theme = useTheme();

  const validateForm = () => {
    const newErrors: { username?: string; password?: string } = {};

    if (!username.trim()) {
      newErrors.username = 'Username is required';
    }

    if (!password.trim()) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleLogin = async () => {
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      // For demo purposes, we'll simulate a login
      // In a real app, this would call the actual authentication API
      const response = await apiService.post('/auth/login', {
        username: username.trim(),
        password,
      });

      if (response.token) {
        dispatch(login({
          token: response.token,
          refreshToken: response.refreshToken,
          user: response.user,
        }));
      }
    } catch (error) {
      Alert.alert(
        'Login Failed',
        'Invalid username or password. Please try again.',
        [{ text: 'OK' }]
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <Surface style={styles.loginCard} elevation={4}>
        <Text variant="headlineMedium" style={styles.title}>
          VALEO CRM
        </Text>
        <Text variant="bodyLarge" style={styles.subtitle}>
          Mobile Login
        </Text>

        <TextInput
          label="Username"
          value={username}
          onChangeText={(text) => {
            setUsername(text);
            if (errors.username) {
              setErrors({ ...errors, username: undefined });
            }
          }}
          mode="outlined"
          autoCapitalize="none"
          autoCorrect={false}
          error={!!errors.username}
          style={styles.input}
        />
        <HelperText type="error" visible={!!errors.username}>
          {errors.username}
        </HelperText>

        <TextInput
          label="Password"
          value={password}
          onChangeText={(text) => {
            setPassword(text);
            if (errors.password) {
              setErrors({ ...errors, password: undefined });
            }
          }}
          mode="outlined"
          secureTextEntry
          error={!!errors.password}
          style={styles.input}
        />
        <HelperText type="error" visible={!!errors.password}>
          {errors.password}
        </HelperText>

        <Button
          mode="contained"
          onPress={handleLogin}
          loading={loading}
          disabled={loading}
          style={styles.loginButton}
        >
          {loading ? 'Signing In...' : 'Sign In'}
        </Button>

        <Button
          mode="text"
          onPress={() => navigation.navigate('BiometricSetup' as never)}
          style={styles.biometricButton}
        >
          Setup Biometric Login
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
  loginCard: {
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
  input: {
    marginBottom: 4,
  },
  loginButton: {
    marginTop: 16,
    marginBottom: 16,
  },
  biometricButton: {
    marginTop: 8,
  },
});