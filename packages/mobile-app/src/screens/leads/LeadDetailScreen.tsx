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
  Chip,
} from 'react-native-paper';
import { RootState } from '../../store';
import { fetchLead } from '../../store/slices/leadsSlice';

interface RouteParams {
  leadId: string;
}

export default function LeadDetailScreen() {
  const route = useRoute();
  const navigation = useNavigation();
  const dispatch = useDispatch();
  const theme = useTheme();

  const { leadId } = route.params as RouteParams;
  const { currentLead: lead, loading } = useSelector(
    (state: RootState) => state.leads
  );

  useEffect(() => {
    if (leadId && leadId !== 'new') {
      dispatch(fetchLead(leadId));
    }
  }, [leadId, dispatch]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'qualified': return '#4CAF50';
      case 'contacted': return '#2196F3';
      case 'new': return '#FF9800';
      case 'lost': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#F44336';
      case 'medium': return '#FF9800';
      case 'low': return '#4CAF50';
      default: return '#9E9E9E';
    }
  };

  if (loading) {
    return (
      <View style={[styles.centerContainer, { backgroundColor: theme.colors.background }]}>
        <ActivityIndicator size="large" />
        <Text style={{ marginTop: 16 }}>Loading lead...</Text>
      </View>
    );
  }

  if (!lead && leadId !== 'new') {
    return (
      <View style={[styles.centerContainer, { backgroundColor: theme.colors.background }]}>
        <Text>Lead not found</Text>
        <Button onPress={() => navigation.goBack()}>Go Back</Button>
      </View>
    );
  }

  const displayLead = lead || {
    id: '',
    company_name: '',
    contact_person: '',
    email: '',
    phone: '',
    status: 'new',
    priority: 'medium',
    source: '',
    estimated_value: null,
    assigned_to: '',
    notes: '',
  };

  return (
    <ScrollView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <Surface style={styles.detailCard} elevation={2}>
        <Text variant="headlineMedium" style={styles.title}>
          {displayLead.company_name || 'New Lead'}
        </Text>

        <View style={styles.statusContainer}>
          <Chip
            style={[styles.statusChip, { backgroundColor: getStatusColor(displayLead.status) }]}
            textStyle={{ color: 'white' }}
          >
            {displayLead.status.toUpperCase()}
          </Chip>
          <Chip
            style={[styles.priorityChip, { backgroundColor: getPriorityColor(displayLead.priority) }]}
            textStyle={{ color: 'white' }}
          >
            {displayLead.priority.toUpperCase()}
          </Chip>
        </View>

        <View style={styles.detailRow}>
          <Text variant="labelLarge" style={styles.label}>Contact Person:</Text>
          <Text variant="bodyLarge">{displayLead.contact_person}</Text>
        </View>

        <View style={styles.detailRow}>
          <Text variant="labelLarge" style={styles.label}>Email:</Text>
          <Text variant="bodyLarge">{displayLead.email}</Text>
        </View>

        <View style={styles.detailRow}>
          <Text variant="labelLarge" style={styles.label}>Phone:</Text>
          <Text variant="bodyLarge">{displayLead.phone}</Text>
        </View>

        <View style={styles.detailRow}>
          <Text variant="labelLarge" style={styles.label}>Source:</Text>
          <Text variant="bodyLarge">{displayLead.source || 'Not specified'}</Text>
        </View>

        <View style={styles.detailRow}>
          <Text variant="labelLarge" style={styles.label}>Assigned To:</Text>
          <Text variant="bodyLarge">{displayLead.assigned_to || 'Unassigned'}</Text>
        </View>

        {displayLead.estimated_value && (
          <View style={styles.detailRow}>
            <Text variant="labelLarge" style={styles.label}>Estimated Value:</Text>
            <Text variant="bodyLarge" style={styles.value}>
              €{displayLead.estimated_value.toLocaleString()}
            </Text>
          </View>
        )}

        {displayLead.notes && (
          <View style={styles.notesContainer}>
            <Text variant="labelLarge" style={styles.label}>Notes:</Text>
            <Text variant="bodyMedium" style={styles.notes}>
              {displayLead.notes}
            </Text>
          </View>
        )}
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
        <Button
          mode="contained"
          onPress={() => {/* TODO: Implement convert to customer */}}
          style={[styles.button, { backgroundColor: '#4CAF50' }]}
        >
          Convert to Customer
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
  statusContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 16,
  },
  statusChip: {
    marginRight: 8,
  },
  priorityChip: {
    marginLeft: 8,
  },
  detailRow: {
    flexDirection: 'row',
    marginBottom: 12,
    alignItems: 'center',
  },
  label: {
    width: 120,
    fontWeight: 'bold',
  },
  value: {
    fontWeight: 'bold',
    color: '#4CAF50',
  },
  notesContainer: {
    marginTop: 8,
  },
  notes: {
    marginTop: 4,
    lineHeight: 20,
  },
  buttonContainer: {
    margin: 16,
  },
  button: {
    marginVertical: 4,
  },
});