import React, { useState, useEffect } from 'react';
import {
  View, Text, FlatList, TouchableOpacity, StyleSheet,
  RefreshControl, TextInput, ScrollView, Image, Modal
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const SORT_OPTIONS = [
  { key: 'newest',   label: 'Newest',      icon: 'time-outline' },
  { key: 'upvotes',  label: 'Most Upvoted', icon: 'star-outline' },
  { key: 'severity', label: 'Severity',     icon: 'alert-circle-outline' },
  { key: 'oldest',   label: 'Oldest',       icon: 'calendar-outline' },
];

const SEVERITY_ORDER = { High: 3, Medium: 2, Low: 1 };

export default function HomeScreen({ API_URL, user, navigation }) {
  const [issues, setIssues] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('All');
  const [sortKey, setSortKey] = useState('newest');
  const [sortModalVisible, setSortModalVisible] = useState(false);

  const filters = ['All', 'Pending', 'In Progress', 'Resolved', 'High Severity'];

  const fetchIssues = async () => {
    try {
      const response = await fetch(`${API_URL}/view`, {
        headers: {
          'Accept': 'application/json',
          'X-User-ID': user?.id || '',
          'Bypass-Tunnel-Reminder': 'true'
        }
      });
      const data = await response.json();
      setIssues(data.issues || []);
    } catch (e) {
      console.log('Fetch issues error:', e);
    }
  };

  useEffect(() => {
    fetchIssues();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchIssues();
    setRefreshing(false);
  };

  // Filter
  let filtered = [...issues];
  if (activeFilter === 'Pending')       filtered = filtered.filter(i => i.status === 'Pending');
  else if (activeFilter === 'In Progress') filtered = filtered.filter(i => i.status === 'In Progress');
  else if (activeFilter === 'Resolved') filtered = filtered.filter(i => i.status?.includes('Resolved'));
  else if (activeFilter === 'High Severity') filtered = filtered.filter(i => i.severity === 'High');

  if (searchQuery.trim()) {
    const q = searchQuery.toLowerCase();
    filtered = filtered.filter(i =>
      (i.issue && i.issue.toLowerCase().includes(q)) ||
      (i.location && i.location.toLowerCase().includes(q)) ||
      (i.category && i.category.toLowerCase().includes(q))
    );
  }

  // Sort
  const sorted = [...filtered].sort((a, b) => {
    if (sortKey === 'newest')   return new Date(b.created_at) - new Date(a.created_at);
    if (sortKey === 'oldest')   return new Date(a.created_at) - new Date(b.created_at);
    if (sortKey === 'upvotes')  return (b.upvotes || 0) - (a.upvotes || 0);
    if (sortKey === 'severity') return (SEVERITY_ORDER[b.severity] || 0) - (SEVERITY_ORDER[a.severity] || 0);
    return 0;
  });

  const getStatusColor = (status) => {
    if (status?.includes('Resolved')) return '#198754';
    if (status === 'In Progress')     return '#ffc107';
    return '#dc3545';
  };

  const getSeverityColor = (severity) => {
    if (severity === 'High')   return '#dc3545';
    if (severity === 'Medium') return '#ffc107';
    return '#198754';
  };

  const getCategoryIcon = (cat) => {
    const icons = { roads: 'car', water: 'water', electricity: 'flash', sanitation: 'trash', traffic: 'navigate', parks: 'leaf', general: 'alert-circle' };
    return icons[cat?.toLowerCase()] || 'alert-circle-outline';
  };

  const getGreeting = () => {
    const h = new Date().getHours();
    if (h < 12) return 'Good Morning';
    if (h < 17) return 'Good Afternoon';
    return 'Good Evening';
  };

  const currentSortLabel = SORT_OPTIONS.find(s => s.key === sortKey)?.label || 'Newest';

  const renderIssue = ({ item }) => {
    const statusColor = getStatusColor(item.status);
    const sevColor    = getSeverityColor(item.severity);
    return (
      <TouchableOpacity
        style={[styles.issueCard, { borderLeftColor: sevColor, borderLeftWidth: 4 }]}
        onPress={() => navigation?.navigate('IssueDetail', { issue: item })}
        activeOpacity={0.82}
      >
        <View style={styles.issueHeader}>
          <View style={styles.issueHeaderLeft}>
            <View style={[styles.categoryIcon, { backgroundColor: sevColor + '20' }]}>
              <Ionicons name={getCategoryIcon(item.category)} size={16} color={sevColor} />
            </View>
            <Text style={styles.issueText} numberOfLines={2}>{item.issue || 'No description'}</Text>
          </View>
          <View style={[styles.statusBadge, { backgroundColor: statusColor }]}>
            <Text style={styles.statusText}>{item.status || 'Pending'}</Text>
          </View>
        </View>

        <View style={styles.issueDetails}>
          <Ionicons name="location" size={13} color="#9ca3af" />
          <Text style={styles.locationText} numberOfLines={1}>{item.location || 'Unknown location'}</Text>
        </View>

        <View style={styles.issueFooter}>
          <View style={[styles.severityBadge, { backgroundColor: sevColor + '18', borderColor: sevColor + '40', borderWidth: 1 }]}>
            <Text style={[styles.severityText, { color: sevColor }]}>{item.severity || 'Low'}</Text>
          </View>
          {item.category && (
            <View style={styles.categoryRow}>
              <Ionicons name="grid-outline" size={12} color="#9ca3af" />
              <Text style={styles.categoryText}>{item.category}</Text>
            </View>
          )}
          <View style={styles.upvoteContainer}>
            <Ionicons name="star" size={14} color="#fbbf24" />
            <Text style={styles.upvoteText}>{item.upvotes || 0}</Text>
          </View>
          {item.created_at && (
            <Text style={styles.dateText}>
              {new Date(item.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
            </Text>
          )}
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <View>
            <Text style={styles.greeting}>{getGreeting()}, {user?.name?.split(' ')[0] || 'User'} 👋</Text>
            <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 2 }}>
              <Image source={require('../../assets/logo.png')} style={{ width: 18, height: 18, marginRight: 6 }} resizeMode="contain" />
              <Text style={styles.platformName}>Jan Suvidha</Text>
            </View>
            <Text style={styles.title}>Civic Issues</Text>
          </View>
          <View style={styles.aiBadge}>
            <Ionicons name="sparkles" size={12} color="#8b5cf6" />
            <Text style={styles.aiBadgeText}>AI Powered</Text>
          </View>
        </View>
        <Text style={styles.subtitle}>{sorted.length} issues • sorted by {currentSortLabel.toLowerCase()}</Text>
      </View>

      {/* Search */}
      <View style={styles.searchContainer}>
        <Ionicons name="search" size={20} color="#9ca3af" />
        <TextInput
          style={styles.searchInput}
          placeholder="Search issues, location, category..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholderTextColor="#9ca3af"
        />
        {searchQuery.length > 0 && (
          <TouchableOpacity onPress={() => setSearchQuery('')}>
            <Ionicons name="close-circle" size={20} color="#9ca3af" />
          </TouchableOpacity>
        )}
      </View>

      {/* Filter chips + Sort button */}
      <View style={styles.controlRow}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ flex: 1 }}>
          {filters.map(filter => (
            <TouchableOpacity
              key={filter}
              style={[styles.filterChip, activeFilter === filter && styles.filterChipActive]}
              onPress={() => setActiveFilter(filter)}
            >
              <Text style={[styles.filterChipText, activeFilter === filter && styles.filterChipTextActive]}>
                {filter}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
        <TouchableOpacity style={styles.sortBtn} onPress={() => setSortModalVisible(true)}>
          <Ionicons name="swap-vertical" size={18} color="#0d6efd" />
          <Text style={styles.sortBtnText}>Sort</Text>
        </TouchableOpacity>
      </View>

      {/* Issue List */}
      <FlatList
        data={sorted}
        renderItem={renderIssue}
        keyExtractor={(item) => item.id || Math.random().toString()}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor="#0d6efd"
            colors={['#0d6efd']}
          />
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <View style={styles.emptyIcon}>
              <Ionicons name="search" size={36} color="#9ca3af" />
            </View>
            <Text style={styles.emptyText}>No issues found</Text>
            <Text style={styles.emptySubtext}>Try a different filter or search term</Text>
            <TouchableOpacity
              style={styles.emptyAction}
              onPress={() => { setActiveFilter('All'); setSearchQuery(''); }}
            >
              <Text style={styles.emptyActionText}>Clear Filters</Text>
            </TouchableOpacity>
          </View>
        }
      />

      {/* Sort Modal */}
      <Modal visible={sortModalVisible} transparent animationType="slide">
        <TouchableOpacity
          style={styles.sortModalOverlay}
          activeOpacity={1}
          onPress={() => setSortModalVisible(false)}
        >
          <View style={styles.sortModalContainer}>
            <Text style={styles.sortModalTitle}>Sort Issues</Text>
            {SORT_OPTIONS.map(opt => (
              <TouchableOpacity
                key={opt.key}
                style={[styles.sortOption, sortKey === opt.key && styles.sortOptionActive]}
                onPress={() => { setSortKey(opt.key); setSortModalVisible(false); }}
                activeOpacity={0.8}
              >
                <Ionicons name={opt.icon} size={20} color={sortKey === opt.key ? '#0d6efd' : '#6b7280'} />
                <Text style={[styles.sortOptionText, sortKey === opt.key && { color: '#0d6efd', fontWeight: '700' }]}>
                  {opt.label}
                </Text>
                {sortKey === opt.key && <Ionicons name="checkmark-circle" size={20} color="#0d6efd" style={{ marginLeft: 'auto' }} />}
              </TouchableOpacity>
            ))}
          </View>
        </TouchableOpacity>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container:          { flex: 1, backgroundColor: '#f8faff' },
  header:             { padding: 20, paddingTop: 50, backgroundColor: 'white', borderBottomWidth: 1, borderBottomColor: '#f3f4f6' },
  headerTop:          { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  greeting:           { fontSize: 12, color: '#9ca3af', fontWeight: '500', marginBottom: 2 },
  platformName:       { fontSize: 13, color: '#8b5cf6', fontWeight: '700' },
  title:              { fontSize: 26, fontWeight: '800', color: '#1f2937' },
  aiBadge:            { flexDirection: 'row', alignItems: 'center', backgroundColor: '#f3e8ff', paddingHorizontal: 10, paddingVertical: 5, borderRadius: 15, gap: 4 },
  aiBadgeText:        { fontSize: 11, color: '#8b5cf6', fontWeight: '700' },
  subtitle:           { fontSize: 12, color: '#9ca3af', marginTop: 5, fontWeight: '500' },
  searchContainer:    { flexDirection: 'row', alignItems: 'center', backgroundColor: 'white', marginHorizontal: 16, marginTop: 10, paddingHorizontal: 14, paddingVertical: 10, borderRadius: 14, borderWidth: 1.5, borderColor: '#e5e7eb', gap: 8 },
  searchInput:        { flex: 1, fontSize: 14, color: '#1f2937' },
  controlRow:         { flexDirection: 'row', alignItems: 'center', paddingLeft: 16, marginVertical: 10 },
  filterChip:         { paddingHorizontal: 14, paddingVertical: 8, backgroundColor: 'white', borderRadius: 20, marginRight: 8, borderWidth: 1.5, borderColor: '#e5e7eb' },
  filterChipActive:   { backgroundColor: '#0d6efd', borderColor: '#0d6efd' },
  filterChipText:     { fontSize: 13, color: '#6b7280', fontWeight: '600' },
  filterChipTextActive:{ color: 'white', fontWeight: '700' },
  sortBtn:            { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 14, paddingVertical: 8, backgroundColor: '#eff6ff', borderRadius: 20, marginRight: 16, borderWidth: 1.5, borderColor: '#bfdbfe' },
  sortBtnText:        { fontSize: 13, color: '#0d6efd', fontWeight: '700' },
  list:               { padding: 14, paddingBottom: 30 },
  issueCard:          { backgroundColor: 'white', borderRadius: 16, padding: 15, marginBottom: 12, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.07, shadowRadius: 6, elevation: 3, overflow: 'hidden' },
  issueHeader:        { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10, marginBottom: 8 },
  issueHeaderLeft:    { flex: 1, flexDirection: 'row', alignItems: 'flex-start', gap: 10 },
  categoryIcon:       { width: 32, height: 32, borderRadius: 8, justifyContent: 'center', alignItems: 'center', marginTop: 1 },
  issueText:          { flex: 1, fontSize: 15, fontWeight: '700', color: '#1f2937', lineHeight: 20 },
  statusBadge:        { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 20 },
  statusText:         { color: 'white', fontSize: 11, fontWeight: '700' },
  issueDetails:       { flexDirection: 'row', alignItems: 'center', gap: 5, marginBottom: 10 },
  locationText:       { color: '#9ca3af', fontSize: 12, flex: 1 },
  issueFooter:        { flexDirection: 'row', alignItems: 'center', gap: 8, flexWrap: 'wrap' },
  severityBadge:      { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 8 },
  severityText:       { fontSize: 11, fontWeight: '700' },
  upvoteContainer:    { flexDirection: 'row', alignItems: 'center', gap: 3, marginLeft: 'auto' },
  upvoteText:         { fontWeight: '700', color: '#374151', fontSize: 13 },
  categoryRow:        { flexDirection: 'row', alignItems: 'center', gap: 4 },
  categoryText:       { fontSize: 11, color: '#9ca3af', textTransform: 'capitalize', fontWeight: '500' },
  dateText:           { fontSize: 11, color: '#d1d5db', fontWeight: '500' },
  empty:              { alignItems: 'center', paddingTop: 60, paddingHorizontal: 30 },
  emptyIcon:          { width: 80, height: 80, borderRadius: 40, backgroundColor: '#f3f4f6', justifyContent: 'center', alignItems: 'center', marginBottom: 16 },
  emptyText:          { color: '#374151', fontSize: 18, fontWeight: '700', marginBottom: 6 },
  emptySubtext:       { color: '#9ca3af', fontSize: 14, textAlign: 'center' },
  emptyAction:        { marginTop: 20, backgroundColor: '#eff6ff', paddingHorizontal: 20, paddingVertical: 10, borderRadius: 20 },
  emptyActionText:    { color: '#0d6efd', fontWeight: '700', fontSize: 14 },
  // Sort modal
  sortModalOverlay:   { flex: 1, backgroundColor: 'rgba(0,0,0,0.45)', justifyContent: 'flex-end' },
  sortModalContainer: { backgroundColor: 'white', borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 24, paddingBottom: 40 },
  sortModalTitle:     { fontSize: 18, fontWeight: '700', color: '#1f2937', marginBottom: 16 },
  sortOption:         { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 14, borderBottomWidth: 1, borderBottomColor: '#f3f4f6' },
  sortOptionActive:   { backgroundColor: '#eff6ff', borderRadius: 12, paddingHorizontal: 12, marginHorizontal: -12 },
  sortOptionText:     { fontSize: 15, color: '#374151', fontWeight: '500' },
});
