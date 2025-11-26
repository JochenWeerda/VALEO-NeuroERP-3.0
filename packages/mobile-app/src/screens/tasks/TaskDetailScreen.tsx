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
  ProgressBar,
} from 'react-native-paper';
import { RootState } from '../../store';
import { fetchTask } from '../../store/slices/tasksSlice';

interface RouteParams {
  taskId: string;
}

export default function TaskDetailScreen() {
  const route = useRoute();
  const navigation = useNavigation();
  const dispatch = useDispatch();
  const theme = useTheme();

  const { taskId } = route.params as RouteParams;
  const { currentTask: task, loading } = useSelector(
    (state: RootState) => state.tasks
  );

  useEffect(() => {
    if (taskId && taskId !== 'new') {
      dispatch(fetchTask(taskId));
    }
  }, [taskId, dispatch]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#4CAF50';
      case 'in_progress': return '#2196F3';
      case 'pending': return '#FF9800';
      case 'cancelled': return '#F44336';
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

  const getProgressValue = (status: string) => {
    switch (status) {
      case 'completed': return 1;
      case 'in_progress': return 0.6;
      case 'pending': return 0.1;
      case 'cancelled': return 0;
      default: return 0;
    }
  };

  if (loading) {
    return (
      <View style={[styles.centerContainer, { backgroundColor: theme.colors.background }]}>
        <ActivityIndicator size="large" />
        <Text style={{ marginTop: 16 }}>Loading task...</Text>
      </View>
    );
  }

  if (!task && taskId !== 'new') {
    return (
      <View style={[styles.centerContainer, { backgroundColor: theme.colors.background }]}>
        <Text>Task not found</Text>
        <Button onPress={() => navigation.goBack()}>Go Back</Button>
      </View>
    );
  }

  const displayTask = task || {
    id: '',
    title: '',
    description: '',
    status: 'pending',
    priority: 'medium',
    assigned_to: '',
    due_date: null,
    progress: 0,
  };

  return (
    <ScrollView style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <Surface style={styles.detailCard} elevation={2}>
        <Text variant="headlineMedium" style={styles.title}>
          {displayTask.title || 'New Task'}
        </Text>

        <View style={styles.statusContainer}>
          <Chip
            style={[styles.statusChip, { backgroundColor: getStatusColor(displayTask.status) }]}
            textStyle={{ color: 'white' }}
          >
            {displayTask.status.replace('_', ' ').toUpperCase()}
          </Chip>
          <Chip
            style={[styles.priorityChip, { backgroundColor: getPriorityColor(displayTask.priority) }]}
            textStyle={{ color: 'white' }}
          >
            {displayTask.priority.toUpperCase()}
          </Chip>
        </View>

        <View style={styles.progressContainer}>
          <Text variant="bodyMedium" style={styles.progressLabel}>
            Progress: {Math.round(getProgressValue(displayTask.status) * 100)}%
          </Text>
          <ProgressBar
            progress={getProgressValue(displayTask.status)}
            color={getStatusColor(displayTask.status)}
            style={styles.progressBar}
          />
        </View>

        <View style={styles.detailRow}>
          <Text variant="labelLarge" style={styles.label}>Assigned To:</Text>
          <Text variant="bodyLarge">{displayTask.assigned_to || 'Unassigned'}</Text>
        </View>

        {displayTask.due_date && (
          <View style={styles.detailRow}>
            <Text variant="labelLarge" style={styles.label}>Due Date:</Text>
            <Text variant="bodyLarge">
              {new Date(displayTask.due_date).toLocaleDateString()}
            </Text>
          </View>
        )}

        <View style={styles.descriptionContainer}>
          <Text variant="labelLarge" style={styles.label}>Description:</Text>
          <Text variant="bodyMedium" style={styles.description}>
            {displayTask.description || 'No description provided.'}
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
        {displayTask.status !== 'completed' && (
          <Button
            mode="contained"
            onPress={() => {/* TODO: Implement mark complete */}}
            style={[styles.button, { backgroundColor: '#4CAF50' }]}
          >
            Mark Complete
          </Button>
        )}
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
  progressContainer: {
    marginBottom: 16,
  },
  progressLabel: {
    marginBottom: 8,
    textAlign: 'center',
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
  },
  detailRow: {
    flexDirection: 'row',
    marginBottom: 12,
    alignItems: 'center',
  },
  label: {
    width: 100,
    fontWeight: 'bold',
  },
  descriptionContainer: {
    marginTop: 8,
  },
  description: {
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