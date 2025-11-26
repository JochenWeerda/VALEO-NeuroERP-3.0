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
import { fetchLeads } from '../../store/slices/leadsSlice';

export default function LeadsScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const dispatch = useDispatch();
  const navigation = useNavigation();
  const theme = useTheme();

  const { items: leads, loading, error } = useSelector(
    (state: RootState) => state.leads
  );

  useEffect(() => {
    dispatch(fetchLeads({}));
  }, [dispatch]);

  const handleRefresh = () => {
    setRefreshing(true);
    dispatch(fetchLeads({})).finally(() => setRefreshing(false));
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    dispatch(fetchLeads({ search: query, status: statusFilter }));
  };

  const handleStatusFilter = (status: string | null) => {
    setStatusFilter(status);
    dispatch(fetchLeads({ search: searchQuery, status }));
  };

  const handleLeadPress = (leadId: string) => {
    navigation.navigate('LeadDetail' as never, { leadId } as never);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'qualified': return '#4CAF50';
      case 'contacted': return '#2196F3';
      case 'new': return '#FF9800';
      case 'lost': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const renderLead = ({ item }: { item: any }) => (
    <Surface style={styles.leadCard} elevation={1}>
      <View style={styles.leadHeader}>
        <Text variant="titleMedium" style={styles.companyName}>
          {item.company_name}
        </Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
          <Text style={styles.statusText}>{item.status}</Text>
        </View>
      </View>

      <Text variant="bodyMedium" style={styles.contactPerson}>
        {item.contact_person}
      </Text>

      <View style={styles.leadDetails}>
        <Text variant="bodySmall" style={styles.email}>
          {item.email}
        </Text>
        <Text variant="bodySmall" style={styles.priority}>
          Priority: {item.priority}
        </Text>
      </View>

      {item.estimated_value && (
        <Text variant="bodySmall" style={styles.value}>
          Est. Value: €{item.estimated_value.toLocaleString()}
        </Text>
      )}
    </Surface>
  );

  if (loading && leads.length === 0) {
    return (
      <View style={[styles.centerContainer, { backgroundColor: theme.colors.background }]}>
        <ActivityIndicator size="large" />
        <Text style={{ marginTop: 16 }}>Loading leads...</Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <Searchbar
        placeholder="Search leads..."
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
          selected={statusFilter === 'new'}
          onPress={() => handleStatusFilter('new')}
          style={styles.filterChip}
        >
          New
        </Chip>
        <Chip
          selected={statusFilter === 'contacted'}
          onPress={() => handleStatusFilter('contacted')}
          style={styles.filterChip}
        >
          Contacted
        </Chip>
        <Chip
          selected={statusFilter === 'qualified'}
          onPress={() => handleStatusFilter('qualified')}
          style={styles.filterChip}
        >
          Qualified
        </Chip>
      </View>

      {error && (
        <Text style={[styles.errorText, { color: theme.colors.error }]}>
          {error}
        </Text>
      )}

      <FlatList
        data={leads}
        renderItem={renderLead}
        keyExtractor={(item) => item.id}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text variant="bodyLarge" style={styles.emptyText}>
              No leads found
            </Text>
          </View>
        }
        contentContainerStyle={leads.length === 0 ? styles.emptyList : undefined}
      />

      <FAB
        icon="plus"
        style={[styles.fab, { backgroundColor: theme.colors.primary }]}
        onPress={() => navigation.navigate('LeadDetail' as never, { leadId: 'new' } as never)}
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
  leadCard: {
    marginHorizontal: 16,
    marginVertical: 4,
    padding: 16,
    borderRadius: 8,
  },
  leadHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  companyName: {
    fontWeight: 'bold',
    flex: 1,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  contactPerson: {
    marginBottom: 4,
    opacity: 0.8,
  },
  leadDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  email: {
    flex: 1,
    opacity: 0.7,
  },
  priority: {
    opacity: 0.7,
  },
  value: {
    opacity: 0.8,
    fontWeight: '500',
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