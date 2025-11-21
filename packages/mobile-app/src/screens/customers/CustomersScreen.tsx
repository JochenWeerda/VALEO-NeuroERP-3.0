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
} from 'react-native-paper';
import { RootState } from '../../store';
import { fetchCustomers } from '../../store/slices/customersSlice';

export default function CustomersScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const dispatch = useDispatch();
  const navigation = useNavigation();
  const theme = useTheme();

  const { items: customers, loading, error } = useSelector(
    (state: RootState) => state.customers
  );

  useEffect(() => {
    dispatch(fetchCustomers({}));
  }, [dispatch]);

  const handleRefresh = () => {
    setRefreshing(true);
    dispatch(fetchCustomers({})).finally(() => setRefreshing(false));
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    dispatch(fetchCustomers({ search: query }));
  };

  const handleCustomerPress = (customerId: string) => {
    navigation.navigate('CustomerDetail' as never, { customerId } as never);
  };

  const renderCustomer = ({ item }: { item: any }) => (
    <Surface style={styles.customerCard} elevation={1}>
      <Text variant="titleMedium" style={styles.customerName}>
        {item.company_name || item.name}
      </Text>
      <Text variant="bodyMedium" style={styles.customerEmail}>
        {item.email}
      </Text>
      <Text variant="bodySmall" style={styles.customerStatus}>
        Status: {item.status}
      </Text>
    </Surface>
  );

  if (loading && customers.length === 0) {
    return (
      <View style={[styles.centerContainer, { backgroundColor: theme.colors.background }]}>
        <ActivityIndicator size="large" />
        <Text style={{ marginTop: 16 }}>Loading customers...</Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <Searchbar
        placeholder="Search customers..."
        onChangeText={handleSearch}
        value={searchQuery}
        style={styles.searchBar}
      />

      {error && (
        <Text style={[styles.errorText, { color: theme.colors.error }]}>
          {error}
        </Text>
      )}

      <FlatList
        data={customers}
        renderItem={renderCustomer}
        keyExtractor={(item) => item.id}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text variant="bodyLarge" style={styles.emptyText}>
              No customers found
            </Text>
          </View>
        }
        contentContainerStyle={customers.length === 0 ? styles.emptyList : undefined}
      />

      <FAB
        icon="plus"
        style={[styles.fab, { backgroundColor: theme.colors.primary }]}
        onPress={() => navigation.navigate('CustomerDetail' as never, { customerId: 'new' } as never)}
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
  customerCard: {
    marginHorizontal: 16,
    marginVertical: 4,
    padding: 16,
    borderRadius: 8,
  },
  customerName: {
    fontWeight: 'bold',
    marginBottom: 4,
  },
  customerEmail: {
    marginBottom: 2,
    opacity: 0.8,
  },
  customerStatus: {
    opacity: 0.6,
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