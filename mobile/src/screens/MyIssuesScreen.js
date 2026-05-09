import React, { useState, useEffect } from 'react';
import {
  View, Text, FlatList, TouchableOpacity, StyleSheet,
  RefreshControl, ScrollView, Modal
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const SORT_OPTIONS = [
  { key: 'newest',   label: 'Newest',       icon: 'time-outline' },
  { key: 'upvotes',  label: 'Most Upvoted', icon: 'star-outline' },
  { key: 'severity', label: 'Severity',     icon: 'alert-circle-outline' },
  { key: 'oldest',   label: 'Oldest',       icon: 'calendar-outline' },
];
const SEVERITY_ORDER = { High: 3, Medium: 2, Low: 1 };

export default function MyIssuesScreen({ API_URL, user, navigation }) {
  const [issues, setIssues] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [activeFilter, setActiveFilter] = useState('All');
  const [sortKey, setSortKey] = useState('newest');
  const [sortModalVisible, setSortModalVisible] = useState(false);

  const filters = ['All', 'Pending', 'In Progress', 'Resolved'];

  useEffect(() => {
    fetchMyIssues();
  }, []);

  const fetchMyIssues = async () => {
    try {
      const response = await fetch(`${API_URL}/my`, {
        headers: {
          'Accept': 'application/json',
          'X-User-ID': user?.id || '',
          'Bypass-Tunnel-Reminder': 'true'
        }
      });
      const data = await response.json();
      setIssues(data.issues || data.my_issues || []);
    } catch (e) {
      console.log('Error fetching my issues:', e);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchMyIssues();
    setRefreshing(false);
  };

  // Filter
  let filtered = [...issues];
  if (activeFilter === 'Pending')       filtered = filtered.filter(i => i.status === 'Pending');
  else if (activeFilter === 'In Progress') filtered = filtered.filter(i => i.status === 'In Progress');
  else if (activeFilter === 'Resolved') filtered = filtered.filter(i => i.status?.includes('Resolved'));

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

  const pendingCount    = issues.filter(i => i.status === 'Pending').length;
  const inProgressCount = issues.filter(i => i.status === 'In Progress').length;
  const resolvedCount   = issues.filter(i => i.status?.includes('Resolved')).length;

  const currentSortLabel = SORT_OPTIONS.find(s => s.key === sortKey)?.label || 'Newest';

  const renderIssue = ({ item }) => (
    <TouchableOpacity
      style={styles.issueCard}
      onPress={() => navigation?.navigate('IssueDetail', { issue: item })}
      activeOpacity={0.82}
    >
      <View style={styles.issueHeader}>
        <Text style={styles.issueText} numberOfLines={2}>{item.issue || 'No description'}</Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
          <Text style={styles.statusText}>{item.status || 'Pending'}</Text>
        </View>
      </View>

      <View style={styles.issueDetails}>
        <Ionicons name="location" size={14} color="gray" />
        <Text style={styles.locationText}>{item.location || 'Unknown'}</Text>
      </View>

      <View style={styles.issueFooter}>
        <Text style={styles.dateText}>
          {item.created_at ? new Date(item.created_at).toLocaleDateString('en-IN') : 'N/A'}
        </Text>
        <View style={styles.upvoteContainer}>
          <Ionicons name="star" size={14} color="#ffc107" />
          <Text style={styles.upvoteText}>{item.upvotes || 0}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <View>
            <Text style={styles.platformName}>Jan Suvidha</Text>
            <Text style={styles.title}>My Issues</Text>
          </View>
          <View style={styles.headerRight}>
            <TouchableOpacity style={styles.sortBtn} onPress={() => setSortModalVisible(true)}>
              <Ionicons name="swap-vertical" size={16} color="#0d6efd" />
              <Text style={styles.sortBtnText}>{currentSortLabel}</Text>
            </TouchableOpacity>
            <View style={styles.aiBadge}>
              <Ionicons name="sparkles" size={12} color="#8b5cf6" />
              <Text style={styles.aiBadgeText}>AI Tracking</Text>
            </View>
          </View>
        </View>
        <Text style={styles.subtitle}>{issues.length} reported • {sorted.length} shown</Text>
      </View>

      {/* Stats cards */}
      <View style={styles.statsRow}>
        {[
          { label: 'Pending',     count: pendingCount,    color: '#dc3545', icon: 'alert-circle',    key: 'Pending' },
          { label: 'In Progress', count: inProgressCount, color: '#ffc107', icon: 'time',            key: 'In Progress' },
          { label: 'Resolved',    count: resolvedCount,   color: '#198754', icon: 'checkmark-circle', key: 'Resolved' },
        ].map(s => (
          <TouchableOpacity
            key={s.key}
            style={[styles.statCard, activeFilter === s.key && styles.statCardActive]}
            onPress={() => setActiveFilter(activeFilter === s.key ? 'All' : s.key)}
            activeOpacity={0.8}
          >
            <Ionicons name={s.icon} size={24} color={activeFilter === s.key ? 'white' : s.color} />
            <Text style={[styles.statNumber, activeFilter === s.key && styles.statNumberActive]}>{s.count}</Text>
            <Text style={[styles.statLabel, activeFilter === s.key && styles.statLabelActive]}>{s.label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Filter chips */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterRow} contentContainerStyle={{ paddingHorizontal: 16, paddingVertical: 8 }}>
        {filters.map(f => (
          <TouchableOpacity
            key={f}
            style={[styles.filterChip, activeFilter === f && styles.filterChipActive]}
            onPress={() => setActiveFilter(f)}
          >
            <Text style={[styles.filterChipText, activeFilter === f && styles.filterChipTextActive]}>{f}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <FlatList
        data={sorted}
        renderItem={renderIssue}
        keyExtractor={(item) => item.id || Math.random().toString()}
        contentContainerStyle={styles.list}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Ionicons name="document-text" size={60} color="lightgray" />
            <Text style={styles.emptyText}>
              {activeFilter === 'All' ? "You haven't reported any issues yet" : `No ${activeFilter.toLowerCase()} issues`}
            </Text>
            <TouchableOpacity style={styles.reportButton} onPress={() => navigation?.navigate('Report')}>
              <Ionicons name="add-circle" size={18} color="white" style={{ marginRight: 8 }} />
              <Text style={styles.reportButtonText}>Report an Issue</Text>
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
            <Text style={styles.sortModalTitle}>Sort My Issues</Text>
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
  header:             { padding: 20, paddingTop: 50, backgroundColor: 'white' },
  headerTop:          { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  platformName:       { fontSize: 14, color: '#8b5cf6', fontWeight: '600', marginBottom: 4 },
  title:              { fontSize: 28, fontWeight: 'bold', color: '#0d6efd' },
  headerRight:        { alignItems: 'flex-end', gap: 6 },
  sortBtn:            { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 12, paddingVertical: 6, backgroundColor: '#eff6ff', borderRadius: 16, borderWidth: 1, borderColor: '#bfdbfe' },
  sortBtnText:        { fontSize: 12, color: '#0d6efd', fontWeight: '600' },
  aiBadge:            { flexDirection: 'row', alignItems: 'center', backgroundColor: '#f3e8ff', paddingHorizontal: 10, paddingVertical: 5, borderRadius: 15 },
  aiBadgeText:        { fontSize: 11, color: '#8b5cf6', fontWeight: '600', marginLeft: 4 },
  subtitle:           { fontSize: 13, color: 'gray', marginTop: 5 },
  statsRow:           { flexDirection: 'row', paddingHorizontal: 16, paddingVertical: 12, gap: 10 },
  statCard:           { flex: 1, backgroundColor: 'white', borderRadius: 12, padding: 14, alignItems: 'center', borderWidth: 1, borderColor: '#e5e7eb' },
  statCardActive:     { backgroundColor: '#0d6efd', borderColor: '#0d6efd' },
  statNumber:         { fontSize: 22, fontWeight: 'bold', color: '#333', marginTop: 6 },
  statNumberActive:   { color: 'white' },
  statLabel:          { fontSize: 11, color: '#6b7280', marginTop: 3 },
  statLabelActive:    { color: 'white' },
  filterRow:          { backgroundColor: 'white' },
  filterChip:         { paddingHorizontal: 14, paddingVertical: 7, backgroundColor: '#f3f4f6', borderRadius: 18, marginRight: 8 },
  filterChipActive:   { backgroundColor: '#0d6efd' },
  filterChipText:     { fontSize: 13, color: '#6b7280', fontWeight: '500' },
  filterChipTextActive:{ color: 'white' },
  list:               { padding: 16 },
  issueCard:          { backgroundColor: 'white', borderRadius: 16, padding: 16, marginBottom: 12, elevation: 2, shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.07, shadowRadius: 3 },
  issueHeader:        { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  issueText:          { flex: 1, fontSize: 15, fontWeight: '600', color: '#333', marginRight: 10 },
  statusBadge:        { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 20 },
  statusText:         { color: 'white', fontSize: 12, fontWeight: '600' },
  issueDetails:       { flexDirection: 'row', alignItems: 'center', marginTop: 10 },
  locationText:       { color: 'gray', fontSize: 13, marginLeft: 5 },
  issueFooter:        { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 12 },
  dateText:           { fontSize: 12, color: '#9ca3af' },
  upvoteContainer:    { flexDirection: 'row', alignItems: 'center' },
  upvoteText:         { marginLeft: 5, fontWeight: '600', color: '#333' },
  empty:              { alignItems: 'center', paddingTop: 60 },
  emptyText:          { color: 'gray', fontSize: 16, marginTop: 10, marginBottom: 20, textAlign: 'center' },
  reportButton:       { backgroundColor: '#0d6efd', paddingHorizontal: 20, paddingVertical: 12, borderRadius: 25, flexDirection: 'row', alignItems: 'center' },
  reportButtonText:   { color: 'white', fontWeight: '600' },
  // Sort modal
  sortModalOverlay:   { flex: 1, backgroundColor: 'rgba(0,0,0,0.45)', justifyContent: 'flex-end' },
  sortModalContainer: { backgroundColor: 'white', borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 24, paddingBottom: 40 },
  sortModalTitle:     { fontSize: 18, fontWeight: '700', color: '#1f2937', marginBottom: 16 },
  sortOption:         { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 14, borderBottomWidth: 1, borderBottomColor: '#f3f4f6' },
  sortOptionActive:   { backgroundColor: '#eff6ff', borderRadius: 12, paddingHorizontal: 12 },
  sortOptionText:     { fontSize: 15, color: '#374151' },
});
