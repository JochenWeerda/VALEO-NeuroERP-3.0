import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import { useRoute, useNavigation } from '@react-navigation/native';
import {
  Text,
  Surface,
  Button,
  useTheme,
  ActivityIndicator,
} from 'react-native-paper';
import { RootState } from '../../store';
import { fetchCustomer } from '../../store/slices/customersSlice';

interface RouteParams {
  customerId: string;
}

export default function CustomerDetailScreen() {
  const route = useRoute();
  const navigation = useNavigation();
  const dispatch = useDispatch();
  const theme = useTheme();

  const { customerId } = route.params as RouteParams;
  const { currentCustomer: customer, loading } = useSelector(
    (state: RootState) => state.customers
  );

  useEffect(() => {
    if (customerId && customerId !== 'new') {
      dispatch(fetchCustomer(customerId));
    }
  }, [customerId, dispatch]);

  if (loading) {
    return (
      <View style={[styles.centerContainer, { backgroundColor: theme.colors.background }]}>
        <ActivityIndicator size="large" />
        <Text style={{ marginTop: 16 }}>Loading customer...</Text>
      </View>
    );
  }

  if (!customer && customerId !== 'new') {
    return (
      <View style={[styles.centerContainer, { backgroundColor: theme.colors.background }]}>
        <Text>Customer not found</Text>
        <Button onPress={() => navigation.goBack()}>Go Back</Button>
      </View>
    );
  }

  const displayCustomer = customer || {
    id: '',
    company_name: '',
    name: '',
    contact_person: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    status: 'prospect',
  };

  return (
    <ScrollView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <Surface style={styles.detailCard} elevation={2}>
        <Text variant="headlineMedium" style={styles.title}>
          {displayCustomer.company_name || displayCustomer.name || 'New Customer'}
        </Text>

        <View style={styles.detailRow}>
          <Text variant="labelLarge" style={styles.label}>Status:</Text>
          <Text variant="bodyLarge">{displayCustomer.status}</Text>
        </View>

        <View style={styles.detailRow}>
          <Text variant="labelLarge" style={styles.label}>Contact:</Text>
          <Text variant="bodyLarge">{displayCustomer.contact_person}</Text>
        </View>

        <View style={styles.detailRow}>
          <Text variant="labelLarge" style={styles.label}>Email:</Text>
          <Text variant="bodyLarge">{displayCustomer.email}</Text>
        </View>

        <View style={styles.detailRow}>
          <Text variant="labelLarge" style={styles.label}>Phone:</Text>
          <Text variant="bodyLarge">{displayCustomer.phone}</Text>
        </View>

        <View style={styles.detailRow}>
          <Text variant="labelLarge" style={styles.label}>Address:</Text>
          <Text variant="bodyLarge">
            {[displayCustomer.address, displayCustomer.city].filter(Boolean).join(', ')}
          </Text>
        </View>
      </Surface>

      <View style={styles.buttonContainer}>
        <Button
          mode="outlined"
          onPress={() => navigation.goBack()}
          style={styles.button}
        >
          Back
        </Button>
        <Button
          mode="contained"
          onPress={() => {/* TODO: Implement edit */}}
          style={styles.button}
        >
          Edit
        </Button>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  detailCard: {
    margin: 16,
    padding: 16,
    borderRadius: 8,
  },
  title: {
    marginBottom: 16,
    textAlign: 'center',
  },
  detailRow: {
    flexDirection: 'row',
    marginBottom: 12,
    alignItems: 'center',
  },
  label: {
    width: 80,
    fontWeight: 'bold',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    margin: 16,
  },
  button: {
    flex: 1,
    marginHorizontal: 4,
  },
});