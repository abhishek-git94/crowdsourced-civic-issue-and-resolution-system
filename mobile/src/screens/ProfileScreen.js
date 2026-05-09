import React, { useState, useEffect } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, ScrollView, Image,
  Alert, ActivityIndicator, Share, Modal, TextInput, KeyboardAvoidingView, Platform
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function ProfileScreen({ API_URL, user, onLogout, onUpdateUser, navigation }) {
  const [stats, setStats] = useState({ reported: 0, resolved: 0, pending: 0, upvotes: 0 });
  const [loading, setLoading] = useState(true);

  // Edit profile modal
  const [editVisible, setEditVisible] = useState(false);
  const [editName, setEditName] = useState(user?.name || '');
  const [editPhone, setEditPhone] = useState(user?.phone_number || '');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadUserStats();
  }, []);

  const loadUserStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/user/stats`, {
        headers: {
          'Accept': 'application/json',
          'X-User-ID': user?.id || user?._id || '',
        }
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

  const handleSaveProfile = async () => {
    if (!editName.trim()) {
      Alert.alert('Error', 'Name cannot be empty');
      return;
    }
    setSaving(true);
    try {
      const response = await fetch(`${API_URL}/auth/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': user?.id || user?._id || '',
        },
        body: JSON.stringify({ name: editName.trim(), phone_number: editPhone.trim() }),
      });
      const data = await response.json();
      if (data.success) {
        onUpdateUser && onUpdateUser(data.user);
        setEditVisible(false);
        Alert.alert('✅ Success', 'Profile updated successfully!');
      } else {
        Alert.alert('Error', data.message || 'Could not update profile');
      }
    } catch (e) {
      Alert.alert('Error', 'Cannot connect to server');
    }
    setSaving(false);
  };

  const handleShareProfile = async () => {
    try {
      await Share.share({
        message: `I'm using Jan Suvidha! I've reported ${stats.reported} civic issues and earned ${user?.points || 0} points. Join me in making our city better!`
      });
    } catch (e) {
      console.log(e);
    }
  };

  const menuItems = [
    {
      icon: 'person-circle', title: 'Edit Profile', color: '#0d6efd',
      onPress: () => {
        setEditName(user?.name || '');
        setEditPhone(user?.phone_number || '');
        setEditVisible(true);
      }
    },
    {
      icon: 'notifications', title: 'Notifications', color: '#f59e0b',
      onPress: () => navigation?.navigate('Notifications')
    },
    {
      icon: 'list', title: 'My Reports', color: '#ec4899',
      onPress: () => navigation?.navigate('MyIssues')
    },
    {
      icon: 'settings', title: 'Settings', color: '#8b5cf6',
      onPress: () => navigation?.navigate('Settings')
    },
    {
      icon: 'shield-checkmark', title: 'Privacy & Security', color: '#10b981',
      onPress: () => Alert.alert('Privacy', 'Your data is stored securely in our servers. We never share personal information with third parties.')
    },
    {
      icon: 'help-circle', title: 'Help & Support', color: '#6366f1',
      onPress: () => Alert.alert('Support', 'Email: support@jansuvidha.gov.in\nPhone: 1800-XXX-XXXX (Toll Free)\nHours: Mon–Sat 9AM–6PM')
    },
    {
      icon: 'share-social', title: 'Share App', color: '#059669',
      onPress: handleShareProfile
    },
  ];

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.avatarContainer}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>{(user?.name || 'U').charAt(0).toUpperCase()}</Text>
          </View>
          <TouchableOpacity
            style={styles.editBadge}
            onPress={() => {
              setEditName(user?.name || '');
              setEditPhone(user?.phone_number || '');
              setEditVisible(true);
            }}
          >
            <Ionicons name="pencil" size={14} color="white" />
          </TouchableOpacity>
        </View>

        <Text style={styles.name}>{user?.name || 'User'}</Text>
        <Text style={styles.email}>{user?.email || 'Not logged in'}</Text>
        {user?.phone_number ? <Text style={styles.phone}>{user.phone_number}</Text> : null}

        <View style={styles.badgeRow}>
          <View style={styles.badge}>
            <Ionicons name="star" size={14} color="#d97706" />
            <Text style={styles.badgeText}>{user?.points || 0} Points</Text>
          </View>
          {user?.role === 'admin' && (
            <View style={[styles.badge, styles.adminBadge]}>
              <Text style={[styles.badgeText, { color: 'white' }]}>Admin</Text>
            </View>
          )}
        </View>
      </View>

      {/* Stats */}
      {loading ? (
        <ActivityIndicator size="large" color="#0d6efd" style={{ marginTop: 20 }} />
      ) : (
        <View style={styles.statsContainer}>
          <View style={styles.statItem}>
            <Text style={[styles.statNumber, { color: '#0d6efd' }]}>{stats.reported}</Text>
            <Text style={styles.statLabel}>Reported</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={[styles.statNumber, { color: '#dc3545' }]}>{stats.pending}</Text>
            <Text style={styles.statLabel}>Pending</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={[styles.statNumber, { color: '#198754' }]}>{stats.resolved}</Text>
            <Text style={styles.statLabel}>Resolved</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={[styles.statNumber, { color: '#f59e0b' }]}>{stats.upvotes}</Text>
            <Text style={styles.statLabel}>Upvotes</Text>
          </View>
        </View>
      )}

      {/* Menu */}
      <View style={styles.menuContainer}>
        <Text style={styles.menuTitle}>Account</Text>
        {menuItems.map((item, index) => (
          <TouchableOpacity key={index} style={styles.menuItem} onPress={item.onPress} activeOpacity={0.7}>
            <View style={[styles.menuIcon, { backgroundColor: item.color + '20' }]}>
              <Ionicons name={item.icon} size={20} color={item.color} />
            </View>
            <Text style={styles.menuText}>{item.title}</Text>
            {item.badge && (
              <View style={styles.menuBadge}>
                <Text style={styles.menuBadgeText}>{item.badge}</Text>
              </View>
            )}
            <Ionicons name="chevron-forward" size={18} color="#9ca3af" />
          </TouchableOpacity>
        ))}
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={onLogout} activeOpacity={0.8}>
        <Ionicons name="log-out-outline" size={20} color="#dc2626" />
        <Text style={styles.logoutText}>Log Out</Text>
      </TouchableOpacity>

      <Text style={styles.version}>Jan Suvidha v1.0.0</Text>

      {/* ── Edit Profile Modal ── */}
      <Modal visible={editVisible} transparent animationType="slide">
        <KeyboardAvoidingView
          style={styles.modalOverlay}
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
          <View style={styles.modalContainer}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Edit Profile</Text>
              <TouchableOpacity onPress={() => setEditVisible(false)}>
                <Ionicons name="close" size={24} color="#374151" />
              </TouchableOpacity>
            </View>

            <Text style={styles.fieldLabel}>Full Name</Text>
            <TextInput
              style={styles.fieldInput}
              value={editName}
              onChangeText={setEditName}
              placeholder="Enter your name"
              placeholderTextColor="#9ca3af"
              autoCapitalize="words"
            />

            <Text style={styles.fieldLabel}>Phone Number</Text>
            <TextInput
              style={styles.fieldInput}
              value={editPhone}
              onChangeText={setEditPhone}
              placeholder="Enter phone number"
              placeholderTextColor="#9ca3af"
              keyboardType="phone-pad"
            />

            <TouchableOpacity
              style={[styles.saveButton, saving && { opacity: 0.6 }]}
              onPress={handleSaveProfile}
              disabled={saving}
              activeOpacity={0.8}
            >
              {saving ? (
                <ActivityIndicator color="white" />
              ) : (
                <>
                  <Ionicons name="checkmark-circle" size={20} color="white" />
                  <Text style={styles.saveButtonText}>Save Changes</Text>
                </>
              )}
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container:      { flex: 1, backgroundColor: '#f8faff' },
  header:         { backgroundColor: 'white', padding: 30, alignItems: 'center', borderBottomLeftRadius: 30, borderBottomRightRadius: 30, paddingTop: 60 },
  avatarContainer:{ position: 'relative' },
  avatar:         { width: 100, height: 100, borderRadius: 50, backgroundColor: '#0d6efd', justifyContent: 'center', alignItems: 'center' },
  avatarText:     { fontSize: 40, fontWeight: 'bold', color: 'white' },
  editBadge:      { position: 'absolute', bottom: 0, right: 0, backgroundColor: '#10b981', width: 32, height: 32, borderRadius: 16, justifyContent: 'center', alignItems: 'center', borderWidth: 3, borderColor: 'white' },
  name:           { fontSize: 26, fontWeight: 'bold', color: '#1f2937', marginTop: 15 },
  email:          { fontSize: 14, color: '#6b7280', marginTop: 5 },
  phone:          { fontSize: 13, color: '#9ca3af', marginTop: 3 },
  badgeRow:       { flexDirection: 'row', marginTop: 10, gap: 10 },
  badge:          { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fef3c7', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20 },
  adminBadge:     { backgroundColor: '#0d6efd' },
  badgeText:      { fontSize: 14, fontWeight: '600', color: '#d97706', marginLeft: 5 },
  statsContainer: { flexDirection: 'row', backgroundColor: 'white', marginHorizontal: 16, marginTop: 16, borderRadius: 16, padding: 16, justifyContent: 'space-around' },
  statItem:       { alignItems: 'center', flex: 1 },
  statNumber:     { fontSize: 24, fontWeight: 'bold' },
  statLabel:      { fontSize: 12, color: '#6b7280', marginTop: 4 },
  statDivider:    { width: 1, backgroundColor: '#e5e7eb' },
  menuContainer:  { backgroundColor: 'white', marginHorizontal: 16, marginTop: 16, borderRadius: 16, padding: 16 },
  menuTitle:      { fontSize: 16, fontWeight: '700', color: '#374151', marginBottom: 15 },
  menuItem:       { flexDirection: 'row', alignItems: 'center', paddingVertical: 14, borderBottomWidth: 1, borderBottomColor: '#f3f4f6' },
  menuIcon:       { width: 40, height: 40, borderRadius: 10, justifyContent: 'center', alignItems: 'center', marginRight: 12 },
  menuText:       { flex: 1, fontSize: 15, color: '#374151' },
  menuBadge:      { backgroundColor: '#dc2626', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 10, marginRight: 8 },
  menuBadgeText:  { color: 'white', fontSize: 11, fontWeight: '600' },
  logoutButton:   { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginHorizontal: 16, marginTop: 20, padding: 14, backgroundColor: '#fee2e2', borderRadius: 12 },
  logoutText:     { fontSize: 16, fontWeight: '600', color: '#dc2626', marginLeft: 8 },
  version:        { textAlign: 'center', color: '#9ca3af', fontSize: 12, marginTop: 20, marginBottom: 30 },

  // Modal
  modalOverlay:   { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  modalContainer: { backgroundColor: 'white', borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 24, paddingBottom: 40 },
  modalHeader:    { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 },
  modalTitle:     { fontSize: 20, fontWeight: '700', color: '#1f2937' },
  fieldLabel:     { fontSize: 14, fontWeight: '600', color: '#374151', marginBottom: 8 },
  fieldInput:     { borderWidth: 1.5, borderColor: '#e5e7eb', borderRadius: 12, paddingHorizontal: 16, paddingVertical: 12, fontSize: 15, color: '#1f2937', marginBottom: 16, backgroundColor: '#f9fafb' },
  saveButton:     { backgroundColor: '#0d6efd', borderRadius: 14, paddingVertical: 14, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, marginTop: 8 },
  saveButtonText: { color: 'white', fontSize: 16, fontWeight: '700' },
});
