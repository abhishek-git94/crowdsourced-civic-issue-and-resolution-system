import React, { useState, useEffect } from 'react';
import {
  View, Text, StyleSheet, Switch, TouchableOpacity,
  ScrollView, Alert, Linking
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

const PREFS_KEY = 'jansuvidha_settings';

const LANGUAGES = ['English', 'हिंदी', 'मराठी', 'தமிழ்', 'తెలుగు'];

export default function SettingsScreen({ user, onLogout }) {
  const [pushNotifications, setPushNotifications] = useState(true);
  const [locationServices, setLocationServices]   = useState(true);
  const [soundEffects, setSoundEffects]           = useState(true);
  const [emailAlerts, setEmailAlerts]             = useState(false);
  const [selectedLanguage, setSelectedLanguage]   = useState('English');
  const [langMenuOpen, setLangMenuOpen]           = useState(false);
  const [prefsLoaded, setPrefsLoaded]             = useState(false);

  // Load saved prefs
  useEffect(() => {
    (async () => {
      try {
        const raw = await AsyncStorage.getItem(PREFS_KEY);
        if (raw) {
          const prefs = JSON.parse(raw);
          if (prefs.pushNotifications !== undefined) setPushNotifications(prefs.pushNotifications);
          if (prefs.locationServices  !== undefined) setLocationServices(prefs.locationServices);
          if (prefs.soundEffects      !== undefined) setSoundEffects(prefs.soundEffects);
          if (prefs.emailAlerts       !== undefined) setEmailAlerts(prefs.emailAlerts);
          if (prefs.selectedLanguage) setSelectedLanguage(prefs.selectedLanguage);
        }
      } catch (e) {
        console.log('Prefs load error:', e);
      }
      setPrefsLoaded(true);
    })();
  }, []);

  // Persist on any change
  const savePrefs = async (patch) => {
    try {
      const current = {
        pushNotifications, locationServices, soundEffects,
        emailAlerts, selectedLanguage, ...patch
      };
      await AsyncStorage.setItem(PREFS_KEY, JSON.stringify(current));
    } catch (e) {
      console.log('Prefs save error:', e);
    }
  };

  const toggle = (setter, key) => (val) => {
    setter(val);
    savePrefs({ [key]: val });
  };

  const toggleItems = [
    {
      icon: 'notifications', color: '#0d6efd', title: 'Push Notifications',
      sub:  'Get updates when your issue status changes',
      value: pushNotifications, onToggle: toggle(setPushNotifications, 'pushNotifications')
    },
    {
      icon: 'location', color: '#10b981', title: 'Location Services',
      sub:  'Auto-fill location when reporting issues',
      value: locationServices, onToggle: toggle(setLocationServices, 'locationServices')
    },
    {
      icon: 'volume-high', color: '#f59e0b', title: 'Sound Effects',
      sub:  'Play sounds for app interactions',
      value: soundEffects, onToggle: toggle(setSoundEffects, 'soundEffects')
    },
    {
      icon: 'mail', color: '#8b5cf6', title: 'Email Alerts',
      sub:  'Receive email updates for issue progress',
      value: emailAlerts, onToggle: toggle(setEmailAlerts, 'emailAlerts')
    },
  ];

  const aboutItems = [
    {
      icon: 'document-text', title: 'Terms of Service',
      onPress: () => Alert.alert('Terms of Service', 'By using Jan Suvidha, you agree to use the app responsibly for reporting civic issues. All reports must be genuine and location-accurate.')
    },
    {
      icon: 'shield-checkmark', title: 'Privacy Policy',
      onPress: () => Alert.alert('Privacy Policy', 'We collect only the data required to provide civic services.\n\n• Location: only during issue reporting\n• Photos: stored encrypted\n• Personal data: never shared with third parties')
    },
    {
      icon: 'star', title: 'Rate the App',
      onPress: () => Alert.alert('Rate Jan Suvidha', 'Thank you for using Jan Suvidha! Please rate us on the Play Store to help others find this app.')
    },
    {
      icon: 'mail', title: 'Contact Support',
      onPress: () => Linking.openURL('mailto:support@jansuvidha.gov.in').catch(() => Alert.alert('Email', 'support@jansuvidha.gov.in'))
    },
    {
      icon: 'logo-github', title: 'View on GitHub',
      onPress: () => Linking.openURL('https://github.com').catch(() => {})
    },
  ];

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Account info banner */}
      <View style={styles.accountBanner}>
        <View style={styles.accountAvatar}>
          <Text style={styles.accountAvatarText}>{(user?.name || 'U').charAt(0).toUpperCase()}</Text>
        </View>
        <View style={{ flex: 1 }}>
          <Text style={styles.accountName}>{user?.name || 'User'}</Text>
          <Text style={styles.accountEmail}>{user?.email || ''}</Text>
        </View>
        <View style={[styles.roleBadge, user?.role === 'admin' && styles.adminBadge]}>
          <Text style={[styles.roleText, user?.role === 'admin' && { color: 'white' }]}>
            {user?.role === 'admin' ? 'Admin' : 'Citizen'}
          </Text>
        </View>
      </View>

      {/* Preferences */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Preferences</Text>
        {toggleItems.map((item, i) => (
          <View key={i} style={[styles.settingItem, i < toggleItems.length - 1 && styles.settingBorder]}>
            <View style={[styles.iconBox, { backgroundColor: item.color + '15' }]}>
              <Ionicons name={item.icon} size={20} color={item.color} />
            </View>
            <View style={styles.settingTextGroup}>
              <Text style={styles.settingTitle}>{item.title}</Text>
              <Text style={styles.settingSubtitle}>{item.sub}</Text>
            </View>
            <Switch
              value={item.value}
              onValueChange={item.onToggle}
              trackColor={{ true: '#0d6efd', false: '#e5e7eb' }}
              thumbColor="white"
            />
          </View>
        ))}
      </View>

      {/* Language */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Language</Text>
        <TouchableOpacity
          style={styles.langSelector}
          onPress={() => setLangMenuOpen(!langMenuOpen)}
          activeOpacity={0.8}
        >
          <Ionicons name="language" size={20} color="#6366f1" />
          <Text style={styles.langSelected}>{selectedLanguage}</Text>
          <Ionicons name={langMenuOpen ? 'chevron-up' : 'chevron-down'} size={18} color="#9ca3af" />
        </TouchableOpacity>
        {langMenuOpen && (
          <View style={styles.langMenu}>
            {LANGUAGES.map(lang => (
              <TouchableOpacity
                key={lang}
                style={[styles.langOption, selectedLanguage === lang && styles.langOptionActive]}
                onPress={() => {
                  setSelectedLanguage(lang);
                  savePrefs({ selectedLanguage: lang });
                  setLangMenuOpen(false);
                  Alert.alert('Language', `Language set to ${lang}`);
                }}
                activeOpacity={0.8}
              >
                <Text style={[styles.langOptionText, selectedLanguage === lang && { color: '#0d6efd', fontWeight: '700' }]}>
                  {lang}
                </Text>
                {selectedLanguage === lang && (
                  <Ionicons name="checkmark" size={18} color="#0d6efd" />
                )}
              </TouchableOpacity>
            ))}
          </View>
        )}
      </View>

      {/* About */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About & Support</Text>
        {aboutItems.map((item, i) => (
          <TouchableOpacity
            key={i}
            style={[styles.aboutItem, i < aboutItems.length - 1 && styles.settingBorder]}
            onPress={item.onPress}
            activeOpacity={0.7}
          >
            <Ionicons name={item.icon} size={20} color="#6b7280" />
            <Text style={styles.aboutText}>{item.title}</Text>
            <Ionicons name="chevron-forward" size={18} color="#d1d5db" />
          </TouchableOpacity>
        ))}
      </View>

      {/* Version */}
      <View style={styles.section}>
        <View style={styles.versionRow}>
          <Text style={styles.versionLabel}>App Version</Text>
          <Text style={styles.versionValue}>v1.0.0</Text>
        </View>
        <View style={styles.versionRow}>
          <Text style={styles.versionLabel}>Build</Text>
          <Text style={styles.versionValue}>2024.05.09</Text>
        </View>
      </View>

      {/* Logout */}
      <TouchableOpacity style={styles.logoutButton} onPress={onLogout} activeOpacity={0.8}>
        <Ionicons name="log-out-outline" size={20} color="#dc2626" />
        <Text style={styles.logoutText}>Log Out</Text>
      </TouchableOpacity>

      <Text style={styles.footer}>© 2024 Jan Suvidha • Civic Issue Reporting System</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container:         { flex: 1, backgroundColor: '#f8faff' },
  accountBanner:     { flexDirection: 'row', alignItems: 'center', backgroundColor: 'white', marginHorizontal: 16, marginTop: 16, borderRadius: 14, padding: 16, gap: 12, elevation: 2 },
  accountAvatar:     { width: 48, height: 48, borderRadius: 24, backgroundColor: '#0d6efd', justifyContent: 'center', alignItems: 'center' },
  accountAvatarText: { color: 'white', fontSize: 20, fontWeight: '700' },
  accountName:       { fontSize: 16, fontWeight: '700', color: '#1f2937' },
  accountEmail:      { fontSize: 13, color: '#6b7280', marginTop: 2 },
  roleBadge:         { paddingHorizontal: 10, paddingVertical: 4, backgroundColor: '#f3f4f6', borderRadius: 12 },
  adminBadge:        { backgroundColor: '#0d6efd' },
  roleText:          { fontSize: 12, color: '#6b7280', fontWeight: '600' },
  section:           { backgroundColor: 'white', marginHorizontal: 16, marginTop: 14, borderRadius: 14, padding: 16 },
  sectionTitle:      { fontSize: 12, fontWeight: '700', color: '#9ca3af', marginBottom: 14, textTransform: 'uppercase', letterSpacing: 0.5 },
  settingItem:       { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, gap: 12 },
  settingBorder:     { borderBottomWidth: 1, borderBottomColor: '#f3f4f6' },
  iconBox:           { width: 38, height: 38, borderRadius: 10, justifyContent: 'center', alignItems: 'center' },
  settingTextGroup:  { flex: 1 },
  settingTitle:      { fontSize: 15, color: '#1f2937', fontWeight: '500' },
  settingSubtitle:   { fontSize: 12, color: '#9ca3af', marginTop: 2 },
  langSelector:      { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 8 },
  langSelected:      { flex: 1, fontSize: 15, color: '#374151', fontWeight: '500' },
  langMenu:          { borderTopWidth: 1, borderTopColor: '#f3f4f6', marginTop: 8, paddingTop: 8 },
  langOption:        { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingVertical: 11, paddingHorizontal: 4 },
  langOptionActive:  { backgroundColor: '#eff6ff', borderRadius: 10, paddingHorizontal: 10 },
  langOptionText:    { fontSize: 15, color: '#374151' },
  aboutItem:         { flexDirection: 'row', alignItems: 'center', paddingVertical: 13, gap: 12 },
  aboutText:         { flex: 1, fontSize: 15, color: '#374151' },
  versionRow:        { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 8 },
  versionLabel:      { fontSize: 14, color: '#6b7280' },
  versionValue:      { fontSize: 14, color: '#374151', fontWeight: '600' },
  logoutButton:      { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', marginHorizontal: 16, marginTop: 16, padding: 14, backgroundColor: '#fee2e2', borderRadius: 14 },
  logoutText:        { fontSize: 16, fontWeight: '600', color: '#dc2626', marginLeft: 8 },
  footer:            { textAlign: 'center', color: '#9ca3af', fontSize: 12, marginTop: 20, marginBottom: 40 },
});
