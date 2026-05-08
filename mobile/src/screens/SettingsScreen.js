import React, { useState } from 'react';
import { View, Text, StyleSheet, Switch, TouchableOpacity, ScrollView, Alert, Linking } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function SettingsScreen({ user, onLogout }) {
  const [notifications, setNotifications] = useState(true);
  const [location, setLocation] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [sound, setSound] = useState(true);

  const settingItems = [
    { icon: 'notifications', title: 'Push Notifications', value: notifications, onToggle: setNotifications },
    { icon: 'location', title: 'Location Services', value: location, onToggle: setLocation },
    { icon: 'moon', title: 'Dark Mode', value: darkMode, onToggle: setDarkMode },
    { icon: 'volume-high', title: 'Sound Effects', value: sound, onToggle: setSound },
  ];

  const aboutItems = [
    { icon: 'document-text', title: 'Terms of Service', onPress: () => Alert.alert('Terms', 'By using Jan Suvidha, you agree to use the app responsibly for reporting civic issues in your community.') },
    { icon: 'shield-checkmark', title: 'Privacy Policy', onPress: () => Alert.alert('Privacy', 'We collect minimal data needed to provide civic services. Your location is used only for issue reporting.') },
    { icon: 'information-circle', title: 'App Version', onPress: () => Alert.alert('Version', 'Jan Suvidha v1.0.0') },
    { icon: 'mail', title: 'Contact Support', onPress: () => Linking.openURL('mailto:support@jansuvidha.gov.in') },
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>General Settings</Text>
        {settingItems.map((item, index) => (
          <View key={index} style={styles.settingItem}>
            <View style={styles.settingLeft}>
              <Ionicons name={item.icon} size={22} color="#0d6efd" />
              <Text style={styles.settingText}>{item.title}</Text>
            </View>
            <Switch value={item.value} onValueChange={item.onToggle} trackColor={{ true: '#0d6efd' }} />
          </View>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Language</Text>
        <TouchableOpacity style={styles.languageItem}>
          <Text style={styles.languageText}>English</Text>
          <Ionicons name="chevron-down" size={20} color="#9ca3af" />
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        {aboutItems.map((item, index) => (
          <TouchableOpacity key={index} style={styles.aboutItem} onPress={item.onPress}>
            <Ionicons name={item.icon} size={22} color="#6b7280" />
            <Text style={styles.aboutText}>{item.title}</Text>
            <Ionicons name="chevron-forward" size={20} color="#9ca3af" />
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Data</Text>
        <TouchableOpacity style={styles.dataItem} onPress={() => Alert.alert('Clear Cache', 'Cache cleared successfully')}>
          <Ionicons name="trash" size={22} color="#dc2626" />
          <Text style={[styles.aboutText, { color: '#dc2626' }]}>Clear Cache</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.dataItem} onPress={() => Alert.alert('Export Data', 'Your data will be exported')}>
          <Ionicons name="download" size={22} color="#0d6efd" />
          <Text style={styles.aboutText}>Export My Data</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={onLogout}>
        <Ionicons name="log-out" size={20} color="#dc2626" />
        <Text style={styles.logoutText}>Log Out</Text>
      </TouchableOpacity>

      <Text style={styles.footer}>© 2024 Jan Suvidha | Civic Issue Reporting System</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8faff', paddingTop: 50 },
  section: { backgroundColor: 'white', marginHorizontal: 16, marginBottom: 16, borderRadius: 12, padding: 16 },
  sectionTitle: { fontSize: 14, fontWeight: '700', color: '#9ca3af', marginBottom: 12, textTransform: 'uppercase' },
  settingItem: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: '#f3f4f6' },
  settingLeft: { flexDirection: 'row', alignItems: 'center' },
  settingText: { fontSize: 16, color: '#374151', marginLeft: 12 },
  languageItem: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: 12 },
  languageText: { fontSize: 16, color: '#374151' },
  aboutItem: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: '#f3f4f6' },
  aboutText: { flex: 1, fontSize: 16, color: '#374151', marginLeft: 12 },
  dataItem: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12 },
  logoutButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginHorizontal: 16, marginTop: 10, padding: 14, backgroundColor: '#fee2e2', borderRadius: 12 },
  logoutText: { fontSize: 16, fontWeight: '600', color: '#dc2626', marginLeft: 8 },
  footer: { textAlign: 'center', color: '#9ca3af', fontSize: 12, marginTop: 20, marginBottom: 40 },
});