import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function NotificationsScreen({ API_URL, user }) {
  const [notifications, setNotifications] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      const response = await fetch(`${API_URL}/api/notifications`, {
        headers: { 'Authorization': `Bearer ${user._id}` }
      });
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
      }
    } catch (e) {
      // Demo data
      setNotifications([
        { id: '1', type: 'status', title: 'Issue Status Updated', message: 'Your reported pothole on Main Road has been marked as In Progress', time: '2 hours ago', read: false },
        { id: '2', type: 'system', title: 'Welcome to Jan Suvidha', message: 'Thank you for joining! Start reporting civic issues in your area.', time: '1 day ago', read: true },
        { id: '3', type: 'alert', title: 'New Issue Near You', message: 'A garbage dump has been reported in your neighborhood', time: '2 days ago', read: true },
        { id: '4', type: 'success', title: 'Issue Resolved', message: 'The water leak you reported has been fixed!', time: '3 days ago', read: true },
      ]);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadNotifications();
    setRefreshing(false);
  };

  const getIcon = (type) => {
    switch(type) {
      case 'status': return 'sync';
      case 'alert': return 'alert-circle';
      case 'success': return 'checkmark-circle';
      case 'system': return 'information-circle';
      default: return 'notifications';
    }
  };

  const getColor = (type) => {
    switch(type) {
      case 'status': return '#0d6efd';
      case 'alert': return '#f59e0b';
      case 'success': return '#10b981';
      case 'system': return '#8b5cf6';
      default: return '#6b7280';
    }
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity style={[styles.notificationItem, !item.read && styles.unread]}>
      <View style={[styles.iconContainer, { backgroundColor: getColor(item.type) + '20' }]}>
        <Ionicons name={getIcon(item.type)} size={22} color={getColor(item.type)} />
      </View>
      <View style={styles.content}>
        <Text style={[styles.title, !item.read && styles.unreadText]}>{item.title}</Text>
        <Text style={styles.message}>{item.message}</Text>
        <Text style={styles.time}>{item.time}</Text>
      </View>
      {!item.read && <View style={styles.unreadDot} />}
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Notifications</Text>
        <TouchableOpacity onPress={() => setNotifications([])}>
          <Text style={styles.clearAll}>Clear All</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={notifications}
        renderItem={renderItem}
        keyExtractor={item => item.id}
        contentContainerStyle={styles.list}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="notifications-off" size={60} color="#d1d5db" />
            <Text style={styles.emptyText}>No notifications yet</Text>
            <Text style={styles.emptySubtext}>We'll notify you when something important happens</Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8faff', paddingTop: 50 },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 20, paddingBottom: 15 },
  headerTitle: { fontSize: 28, fontWeight: 'bold', color: '#1f2937' },
  clearAll: { fontSize: 14, color: '#0d6efd', fontWeight: '600' },
  list: { paddingHorizontal: 16 },
  notificationItem: { flexDirection: 'row', backgroundColor: 'white', padding: 16, borderRadius: 12, marginBottom: 10 },
  unread: { backgroundColor: '#f0f9ff', borderLeftWidth: 4, borderLeftColor: '#0d6efd' },
  iconContainer: { width: 44, height: 44, borderRadius: 22, justifyContent: 'center', alignItems: 'center', marginRight: 12 },
  content: { flex: 1 },
  title: { fontSize: 15, fontWeight: '600', color: '#374151', marginBottom: 4 },
  unreadText: { color: '#1f2937' },
  message: { fontSize: 13, color: '#6b7280', marginBottom: 6, lineHeight: 18 },
  time: { fontSize: 12, color: '#9ca3af' },
  unreadDot: { width: 10, height: 10, borderRadius: 5, backgroundColor: '#0d6efd', marginLeft: 8 },
  emptyContainer: { alignItems: 'center', paddingTop: 80 },
  emptyText: { fontSize: 18, fontWeight: '600', color: '#6b7280', marginTop: 16 },
  emptySubtext: { fontSize: 14, color: '#9ca3af', marginTop: 8, textAlign: 'center' },
});