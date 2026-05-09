import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  RefreshControl, Alert
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function NotificationsScreen({ API_URL, user }) {
  const [notifications, setNotifications] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    loadNotifications();
  }, []);

  useEffect(() => {
    setUnreadCount(notifications.filter(n => !n.read).length);
  }, [notifications]);

  const loadNotifications = async () => {
    try {
      const response = await fetch(`${API_URL}/api/notifications`, {
        headers: {
          'Accept': 'application/json',
          'X-User-ID': user?.id || user?._id || '',
        }
      });
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
        return;
      }
    } catch (e) {
      console.log('Notifications fetch error:', e);
    }
    // Demo fallback
    setNotifications([
      { id: 'demo-1', type: 'status', title: 'Issue Status Updated', message: 'Your reported pothole on Main Road has been marked as In Progress', time: '2 hours ago', read: false },
      { id: 'demo-2', type: 'system', title: 'Welcome to Jan Suvidha', message: 'Thank you for joining! Start reporting civic issues in your area.', time: '1 day ago', read: true },
      { id: 'demo-3', type: 'alert', title: 'New Issue Near You', message: 'A garbage dump has been reported in your neighborhood', time: '2 days ago', read: true },
      { id: 'demo-4', type: 'success', title: 'Issue Resolved', message: 'The water leak you reported has been fixed!', time: '3 days ago', read: true },
    ]);
  };

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadNotifications();
    setRefreshing(false);
  }, []);

  const markAsRead = async (notifId) => {
    // Optimistic update
    setNotifications(prev =>
      prev.map(n => n.id === notifId ? { ...n, read: true } : n)
    );
    try {
      await fetch(`${API_URL}/api/notifications/${notifId}/read`, {
        method: 'POST',
        headers: { 'X-User-ID': user?.id || user?._id || '' }
      });
    } catch (e) {
      console.log('Mark read error:', e);
    }
  };

  const markAllRead = async () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    try {
      await fetch(`${API_URL}/api/notifications/read-all`, {
        method: 'POST',
        headers: { 'X-User-ID': user?.id || user?._id || '' }
      });
    } catch (e) {
      console.log('Mark all read error:', e);
    }
    Alert.alert('Done', 'All notifications marked as read');
  };

  const getIcon = (type) => {
    switch (type) {
      case 'status':  return 'sync';
      case 'alert':   return 'alert-circle';
      case 'success': return 'checkmark-circle';
      case 'system':  return 'information-circle';
      default:        return 'notifications';
    }
  };

  const getColor = (type) => {
    switch (type) {
      case 'status':  return '#0d6efd';
      case 'alert':   return '#f59e0b';
      case 'success': return '#10b981';
      case 'system':  return '#8b5cf6';
      default:        return '#6b7280';
    }
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity
      style={[styles.notificationItem, !item.read && styles.unread]}
      onPress={() => !item.read && markAsRead(item.id)}
      activeOpacity={0.75}
    >
      <View style={[styles.iconContainer, { backgroundColor: getColor(item.type) + '20' }]}>
        <Ionicons name={getIcon(item.type)} size={24} color={getColor(item.type)} />
      </View>
      <View style={styles.content}>
        <Text style={[styles.notifTitle, !item.read && styles.unreadText]}>{item.title}</Text>
        <Text style={styles.message}>{item.message}</Text>
        <Text style={styles.time}>{item.time}</Text>
      </View>
      {!item.read && <View style={styles.unreadDot} />}
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.platformName}>Jan Suvidha</Text>
          <Text style={styles.headerTitle}>Notifications</Text>
        </View>
        <View style={styles.headerRight}>
          {unreadCount > 0 && (
            <TouchableOpacity style={styles.markAllBtn} onPress={markAllRead} activeOpacity={0.8}>
              <Ionicons name="checkmark-done" size={16} color="#0d6efd" />
              <Text style={styles.markAllText}>Mark all read</Text>
            </TouchableOpacity>
          )}
          <View style={styles.aiBadge}>
            <Ionicons name="sparkles" size={12} color="#8b5cf6" />
            <Text style={styles.aiBadgeText}>AI Smart</Text>
          </View>
        </View>
      </View>

      {unreadCount > 0 && (
        <View style={styles.unreadBanner}>
          <Ionicons name="ellipse" size={8} color="#0d6efd" />
          <Text style={styles.unreadBannerText}>{unreadCount} unread notification{unreadCount > 1 ? 's' : ''} – tap to mark as read</Text>
        </View>
      )}

      <FlatList
        data={notifications}
        renderItem={renderItem}
        keyExtractor={item => item.id}
        contentContainerStyle={styles.list}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="notifications-off-outline" size={80} color="#e5e7eb" />
            <Text style={styles.emptyText}>No notifications yet</Text>
            <Text style={styles.emptySubtext}>We'll notify you when something important happens</Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container:         { flex: 1, backgroundColor: '#f8faff', paddingTop: 50 },
  header:            { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', paddingHorizontal: 20, paddingBottom: 12 },
  platformName:      { fontSize: 13, color: '#8b5cf6', fontWeight: '600', marginBottom: 2 },
  headerTitle:       { fontSize: 28, fontWeight: 'bold', color: '#1f2937' },
  headerRight:       { alignItems: 'flex-end', gap: 8 },
  markAllBtn:        { flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: '#eff6ff', paddingHorizontal: 10, paddingVertical: 6, borderRadius: 12 },
  markAllText:       { fontSize: 12, color: '#0d6efd', fontWeight: '600' },
  aiBadge:           { flexDirection: 'row', alignItems: 'center', backgroundColor: '#f3e8ff', paddingHorizontal: 10, paddingVertical: 5, borderRadius: 15 },
  aiBadgeText:       { fontSize: 11, color: '#8b5cf6', fontWeight: '600', marginLeft: 4 },
  unreadBanner:      { flexDirection: 'row', alignItems: 'center', gap: 6, backgroundColor: '#eff6ff', paddingHorizontal: 20, paddingVertical: 8, marginHorizontal: 16, borderRadius: 10, marginBottom: 4 },
  unreadBannerText:  { fontSize: 12, color: '#3b82f6' },
  list:              { paddingHorizontal: 16, paddingTop: 8 },
  notificationItem:  { flexDirection: 'row', backgroundColor: 'white', padding: 16, borderRadius: 14, marginBottom: 10, alignItems: 'center' },
  unread:            { backgroundColor: '#f0f9ff', borderLeftWidth: 4, borderLeftColor: '#0d6efd' },
  iconContainer:     { width: 44, height: 44, borderRadius: 22, justifyContent: 'center', alignItems: 'center', marginRight: 12 },
  content:           { flex: 1 },
  notifTitle:        { fontSize: 15, fontWeight: '600', color: '#374151', marginBottom: 4 },
  unreadText:        { color: '#1f2937' },
  message:           { fontSize: 13, color: '#6b7280', marginBottom: 6, lineHeight: 18 },
  time:              { fontSize: 12, color: '#9ca3af' },
  unreadDot:         { width: 10, height: 10, borderRadius: 5, backgroundColor: '#0d6efd', marginLeft: 8 },
  emptyContainer:    { alignItems: 'center', paddingTop: 80 },
  emptyText:         { fontSize: 18, fontWeight: '600', color: '#6b7280', marginTop: 16 },
  emptySubtext:      { fontSize: 14, color: '#9ca3af', marginTop: 8, textAlign: 'center', paddingHorizontal: 30 },
});
