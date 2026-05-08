import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Image, Alert, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function ProfileScreen({ API_URL, user, onLogout }) {
  const [stats, setStats] = useState({ reported: 0, resolved: 0, pending: 0, upvotes: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUserStats();
  }, []);

  const loadUserStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/user/stats`, {
        headers: { 'Authorization': `Bearer ${user._id}` }
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (e) {
      console.log('Stats error:', e);
    }
    setLoading(false);
  };

  const menuItems = [
    { icon: 'person', title: 'Edit Profile', color: '#0d6efd', onPress: () => Alert.alert('Coming Soon', 'Profile editing will be available soon') },
    { icon: 'notifications', title: 'Notifications', color: '#f59e0b', onPress: () => Alert.alert('Coming Soon', 'Notifications screen coming soon') },
    { icon: 'shield-checkmark', title: 'Privacy & Security', color: '#10b981', onPress: () => Alert.alert('Privacy', 'Your data is secure') },
    { icon: 'help-circle', title: 'Help & Support', color: '#8b5cf6', onPress: () => Alert.alert('Help', 'Contact: support@jansuvidha.gov.in') },
    { icon: 'document-text', title: 'My Reports History', color: '#ec4899', onPress: () => Alert.alert('History', 'View all your reported issues') },
    { icon: 'heart', title: 'Saved Issues', color: '#ef4444', onPress: () => Alert.alert('Saved', 'Saved issues feature coming soon') },
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <View style={styles.avatarContainer}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>{user?.name?.charAt(0) || 'U'}</Text>
          </View>
          <TouchableOpacity style={styles.editBadge}>
            <Ionicons name="camera" size={16} color="white" />
          </TouchableOpacity>
        </View>
        <Text style={styles.name}>{user?.name || 'User'}</Text>
        <Text style={styles.email}>{user?.email || 'user@email.com'}</Text>
        <View style={styles.badge}>
          <Ionicons name="star" size={14} color="#f59e0b" />
          <Text style={styles.badgeText}>{user?.points || 0} Points</Text>
        </View>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{stats.reported}</Text>
          <Text style={styles.statLabel}>Reported</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{stats.pending}</Text>
          <Text style={styles.statLabel}>Pending</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{stats.resolved}</Text>
          <Text style={styles.statLabel}>Resolved</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{stats.upvotes}</Text>
          <Text style={styles.statLabel}>Upvotes</Text>
        </View>
      </View>

      <View style={styles.menuContainer}>
        <Text style={styles.menuTitle}>Account</Text>
        {menuItems.map((item, index) => (
          <TouchableOpacity key={index} style={styles.menuItem} onPress={item.onPress}>
            <View style={[styles.menuIcon, { backgroundColor: item.color + '20' }]}>
              <Ionicons name={item.icon} size={22} color={item.color} />
            </View>
            <Text style={styles.menuText}>{item.title}</Text>
            <Ionicons name="chevron-forward" size={20} color="#9ca3af" />
          </TouchableOpacity>
        ))}
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={onLogout}>
        <Ionicons name="log-out" size={20} color="#dc2626" />
        <Text style={styles.logoutText}>Log Out</Text>
      </TouchableOpacity>

      <Text style={styles.version}>Jan Suvidha v1.0.0 | Made with ❤️ for Citizens</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8faff' },
  header: { backgroundColor: 'white', padding: 30, alignItems: 'center', borderBottomLeftRadius: 30, borderBottomRightRadius: 30 },
  avatarContainer: { position: 'relative' },
  avatar: { width: 90, height: 90, borderRadius: 45, backgroundColor: '#0d6efd', justifyContent: 'center', alignItems: 'center' },
  avatarText: { fontSize: 36, fontWeight: 'bold', color: 'white' },
  editBadge: { position: 'absolute', bottom: 0, right: 0, backgroundColor: '#10b981', width: 30, height: 30, borderRadius: 15, justifyContent: 'center', alignItems: 'center', borderWidth: 3, borderColor: 'white' },
  name: { fontSize: 24, fontWeight: 'bold', color: '#1f2937', marginTop: 15 },
  email: { fontSize: 14, color: '#6b7280', marginTop: 5 },
  badge: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fef3c7', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, marginTop: 10 },
  badgeText: { fontSize: 14, fontWeight: '600', color: '#d97706', marginLeft: 5 },
  statsContainer: { flexDirection: 'row', backgroundColor: 'white', marginHorizontal: 16, marginTop: 16, borderRadius: 16, padding: 16, justifyContent: 'space-around' },
  statItem: { alignItems: 'center', flex: 1 },
  statNumber: { fontSize: 22, fontWeight: 'bold', color: '#0d6efd' },
  statLabel: { fontSize: 12, color: '#6b7280', marginTop: 4 },
  statDivider: { width: 1, backgroundColor: '#e5e7eb' },
  menuContainer: { backgroundColor: 'white', marginHorizontal: 16, marginTop: 16, borderRadius: 16, padding: 16 },
  menuTitle: { fontSize: 16, fontWeight: '700', color: '#374151', marginBottom: 15 },
  menuItem: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: '#f3f4f6' },
  menuIcon: { width: 40, height: 40, borderRadius: 10, justifyContent: 'center', alignItems: 'center', marginRight: 12 },
  menuText: { flex: 1, fontSize: 15, color: '#374151' },
  logoutButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginHorizontal: 16, marginTop: 20, padding: 14, backgroundColor: '#fee2e2', borderRadius: 12 },
  logoutText: { fontSize: 16, fontWeight: '600', color: '#dc2626', marginLeft: 8 },
  version: { textAlign: 'center', color: '#9ca3af', fontSize: 12, marginTop: 20, marginBottom: 30 },
});