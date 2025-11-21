import React, { useEffect, useState } from 'react';
import { View, StyleSheet, FlatList, RefreshControl } from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import { useNavigation } from '@react-navigation/native';
import {
  Text,
  Surface,
  Searchbar,
  FAB,
  useTheme,
  ActivityIndicator,
  Chip,
} from 'react-native-paper';
import { RootState } from '../../store';
import { fetchTasks } from '../../store/slices/tasksSlice';

export default function TasksScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const dispatch = useDispatch();
  const navigation = useNavigation();
  const theme = useTheme();

  const { items: tasks, loading, error } = useSelector(
    (state: RootState) => state.tasks
  );

  useEffect(() => {
    dispatch(fetchTasks({}));
  }, [dispatch]);

  const handleRefresh = () => {
    setRefreshing(true);
    dispatch(fetchTasks({})).finally(() => setRefreshing(false));
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    dispatch(fetchTasks({ search: query, status: statusFilter }));
  };

  const handleStatusFilter = (status: string | null) => {
    setStatusFilter(status);
    dispatch(fetchTasks({ search: searchQuery, status }));
  };

  const handleTaskPress = (taskId: string) => {
    navigation.navigate('TaskDetail' as never, { taskId } as never);
  };

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

  const renderTask = ({ item }: { item: any }) => (
    <Surface style={styles.taskCard} elevation={1}>
      <View style={styles.taskHeader}>
        <Text variant="titleMedium" style={styles.taskTitle} numberOfLines={1}>
          {item.title}
        </Text>
        <View style={styles.statusContainer}>
          <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(item.priority) }]}>
            <Text style={styles.priorityText}>{item.priority}</Text>
          </View>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
            <Text style={styles.statusText}>{item.status}</Text>
          </View>
        </View>
      </View>

      <Text variant="bodyMedium" style={styles.taskDescription} numberOfLines={2}>
        {item.description}
      </Text>

      <View style={styles.taskDetails}>
        <Text variant="bodySmall" style={styles.assignedTo}>
          Assigned: {item.assigned_to || 'Unassigned'}
        </Text>
        {item.due_date && (
          <Text variant="bodySmall" style={styles.dueDate}>
            Due: {new Date(item.due_date).toLocaleDateString()}
          </Text>
        )}
      </View>
    </Surface>
  );

  if (loading && tasks.length === 0) {
    return (
      <View style={[styles.centerContainer, { backgroundColor: theme.colors.background }]}>
        <ActivityIndicator size="large" />
        <Text style={{ marginTop: 16 }}>Loading tasks...</Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <Searchbar
        placeholder="Search tasks..."
        onChangeText={handleSearch}
        value={searchQuery}
        style={styles.searchBar}
      />

      <View style={styles.filterContainer}>
        <Chip
          selected={statusFilter === null}
          onPress={() => handleStatusFilter(null)}
          style={styles.filterChip}
        >
          All
        </Chip>
        <Chip
          selected={statusFilter === 'pending'}
          onPress={() => handleStatusFilter('pending')}
          style={styles.filterChip}
        >
          Pending
        </Chip>
        <Chip
          selected={statusFilter === 'in_progress'}
          onPress={() => handleStatusFilter('in_progress')}
          style={styles.filterChip}
        >
          In Progress
        </Chip>
        <Chip
          selected={statusFilter === 'completed'}
          onPress={() => handleStatusFilter('completed')}
          style={styles.filterChip}
        >
          Completed
        </Chip>
      </View>

      {error && (
        <Text style={[styles.errorText, { color: theme.colors.error }]}>
          {error}
        </Text>
      )}

      <FlatList
        data={tasks}
        renderItem={renderTask}
        keyExtractor={(item) => item.id}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text variant="bodyLarge" style={styles.emptyText}>
              No tasks found
            </Text>
          </View>
        }
        contentContainerStyle={tasks.length === 0 ? styles.emptyList : undefined}
      />

      <FAB
        icon="plus"
        style={[styles.fab, { backgroundColor: theme.colors.primary }]}
        onPress={() => navigation.navigate('TaskDetail' as never, { taskId: 'new' } as never)}
      />
    </View>
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
  searchBar: {
    margin: 16,
    marginBottom: 8,
  },
  filterContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    marginBottom: 8,
  },
  filterChip: {
    marginRight: 8,
  },
  taskCard: {
    marginHorizontal: 16,
    marginVertical: 4,
    padding: 16,
    borderRadius: 8,
  },
  taskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  taskTitle: {
    fontWeight: 'bold',
    flex: 1,
    marginRight: 8,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  priorityBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
    marginRight: 4,
  },
  priorityText: {
    color: 'white',
    fontSize: 10,
    fontWeight: 'bold',
  },
  statusBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
  },
  statusText: {
    color: 'white',
    fontSize: 10,
    fontWeight: 'bold',
  },
  taskDescription: {
    marginBottom: 8,
    opacity: 0.8,
  },
  taskDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  assignedTo: {
    opacity: 0.7,
  },
  dueDate: {
    opacity: 0.7,
  },
  errorText: {
    textAlign: 'center',
    margin: 16,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 64,
  },
  emptyText: {
    opacity: 0.6,
  },
  emptyList: {
    flexGrow: 1,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
});