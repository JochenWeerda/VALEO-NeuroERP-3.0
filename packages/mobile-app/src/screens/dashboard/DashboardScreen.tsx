import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  RefreshControl,
  StyleSheet,
  Dimensions,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import { Card, Title, Paragraph, FAB, Chip } from 'react-native-paper';
import { MaterialIcons } from '@expo/vector-icons';

import { RootState } from '../../store';
import apiService from '../../services/api';

const { width } = Dimensions.get('window');

interface DashboardStats {
  totalCustomers: number;
  totalLeads: number;
  activeTasks: number;
  monthlyRevenue: number;
  conversionRate: number;
  avgResponseTime: number;
}

interface RecentActivity {
  id: string;
  type: 'lead' | 'task' | 'customer' | 'opportunity';
  title: string;
  description: string;
  timestamp: string;
  priority?: 'low' | 'medium' | 'high';
}

export default function DashboardScreen({ navigation }: any) {
  const [stats, setStats] = useState<DashboardStats>({
    totalCustomers: 0,
    totalLeads: 0,
    activeTasks: 0,
    monthlyRevenue: 0,
    conversionRate: 0,
    avgResponseTime: 0,
  });
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const user = useSelector((state: RootState) => state.auth.user);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Load dashboard statistics
      const [customersRes, leadsRes, tasksRes] = await Promise.all([
        apiService.getCustomers({ limit: 1 }),
        apiService.getLeads({ limit: 1 }),
        apiService.getTasks({ limit: 1 }),
      ]);

      setStats({
        totalCustomers: customersRes.total || 0,
        totalLeads: leadsRes.total || 0,
        activeTasks: tasksRes.total || 0,
        monthlyRevenue: 125000, // Mock data
        conversionRate: 23.5, // Mock data
        avgResponseTime: 2.3, // Mock data
      });

      // Load recent activities (mock data for now)
      setRecentActivities([
        {
          id: '1',
          type: 'lead',
          title: 'New Lead: TechCorp GmbH',
          description: 'High-priority lead from website form',
          timestamp: '2025-11-15T10:30:00Z',
          priority: 'high',
        },
        {
          id: '2',
          type: 'task',
          title: 'Follow-up Call',
          description: 'Call John Smith about proposal',
          timestamp: '2025-11-15T09:15:00Z',
          priority: 'medium',
        },
        {
          id: '3',
          type: 'customer',
          title: 'Customer Updated',
          description: 'ABC Corp updated contact information',
          timestamp: '2025-11-15T08:45:00Z',
        },
      ]);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'lead':
        return 'person-add';
      case 'task':
        return 'assignment';
      case 'customer':
        return 'business';
      case 'opportunity':
        return 'trending-up';
      default:
        return 'info';
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'lead':
        return '#FF6B35';
      case 'task':
        return '#4ECDC4';
      case 'customer':
        return '#45B7D1';
      case 'opportunity':
        return '#96CEB4';
      default:
        return '#666';
    }
  };

  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case 'high':
        return '#FF4444';
      case 'medium':
        return '#FFAA00';
      case 'low':
        return '#44AA44';
      default:
        return '#666';
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Welcome Header */}
        <View style={styles.header}>
          <Text style={styles.welcomeText}>
            Welcome back, {user?.firstName || 'User'}!
          </Text>
          <Text style={styles.dateText}>
            {new Date().toLocaleDateString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </Text>
        </View>

        {/* Stats Cards */}
        <View style={styles.statsContainer}>
          <View style={styles.statsRow}>
            <Card style={[styles.statCard, { backgroundColor: '#E3F2FD' }]}>
              <Card.Content>
                <MaterialIcons name="business" size={24} color="#1976D2" />
                <Title style={styles.statNumber}>{stats.totalCustomers}</Title>
                <Paragraph style={styles.statLabel}>Customers</Paragraph>
              </Card.Content>
            </Card>

            <Card style={[styles.statCard, { backgroundColor: '#F3E5F5' }]}>
              <Card.Content>
                <MaterialIcons name="person-add" size={24} color="#7B1FA2" />
                <Title style={styles.statNumber}>{stats.totalLeads}</Title>
                <Paragraph style={styles.statLabel}>Active Leads</Paragraph>
              </Card.Content>
            </Card>
          </View>

          <View style={styles.statsRow}>
            <Card style={[styles.statCard, { backgroundColor: '#E8F5E8' }]}>
              <Card.Content>
                <MaterialIcons name="assignment" size={24} color="#388E3C" />
                <Title style={styles.statNumber}>{stats.activeTasks}</Title>
                <Paragraph style={styles.statLabel}>Active Tasks</Paragraph>
              </Card.Content>
            </Card>

            <Card style={[styles.statCard, { backgroundColor: '#FFF3E0' }]}>
              <Card.Content>
                <MaterialIcons name="trending-up" size={24} color="#F57C00" />
                <Title style={styles.statNumber}>{stats.conversionRate}%</Title>
                <Paragraph style={styles.statLabel}>Conversion</Paragraph>
              </Card.Content>
            </Card>
          </View>
        </View>

        {/* Recent Activity */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Activity</Text>
          {recentActivities.map((activity) => (
            <Card key={activity.id} style={styles.activityCard}>
              <Card.Content style={styles.activityContent}>
                <View style={styles.activityIcon}>
                  <MaterialIcons
                    name={getActivityIcon(activity.type)}
                    size={20}
                    color={getActivityColor(activity.type)}
                  />
                </View>
                <View style={styles.activityDetails}>
                  <Text style={styles.activityTitle}>{activity.title}</Text>
                  <Text style={styles.activityDescription}>{activity.description}</Text>
                  <View style={styles.activityMeta}>
                    <Text style={styles.activityTime}>
                      {new Date(activity.timestamp).toLocaleTimeString('en-US', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </Text>
                    {activity.priority && (
                      <Chip
                        mode="outlined"
                        style={[
                          styles.priorityChip,
                          { borderColor: getPriorityColor(activity.priority) },
                        ]}
                        textStyle={{ color: getPriorityColor(activity.priority), fontSize: 10 }}
                      >
                        {activity.priority.toUpperCase()}
                      </Chip>
                    )}
                  </View>
                </View>
              </Card.Content>
            </Card>
          ))}
        </View>
      </ScrollView>

      {/* Quick Actions FAB */}
      <FAB.Group
        open={false}
        icon="plus"
        actions={[
          {
            icon: 'person-add',
            label: 'New Lead',
            onPress: () => navigation.navigate('Leads'),
          },
          {
            icon: 'business',
            label: 'New Customer',
            onPress: () => navigation.navigate('Customers'),
          },
          {
            icon: 'assignment',
            label: 'New Task',
            onPress: () => navigation.navigate('Tasks'),
          },
        ]}
        onStateChange={() => {}}
        onPress={() => {}}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    padding: 20,
    backgroundColor: '#007AFF',
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  dateText: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  statsContainer: {
    padding: 16,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  statCard: {
    flex: 1,
    marginHorizontal: 4,
    elevation: 2,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginTop: 8,
  },
  statLabel: {
    textAlign: 'center',
    color: '#666',
    marginTop: 4,
  },
  section: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#333',
  },
  activityCard: {
    marginBottom: 8,
    elevation: 1,
  },
  activityContent: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  activityIcon: {
    marginRight: 12,
    marginTop: 2,
  },
  activityDetails: {
    flex: 1,
  },
  activityTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  activityDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  activityMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  activityTime: {
    fontSize: 12,
    color: '#999',
  },
  priorityChip: {
    height: 20,
    borderWidth: 1,
  },
});