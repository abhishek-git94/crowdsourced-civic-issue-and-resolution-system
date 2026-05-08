import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function MyIssuesScreen({ API_URL, user }) {
  const [issues, setIssues] = useState([]);

  useEffect(() => {
    fetchMyIssues();
  }, []);

  const fetchMyIssues = async () => {
    try {
      const response = await fetch(`${API_URL}/issues/my`);
      const data = await response.json();
      setIssues(data.my_issues || []);
    } catch (e) {
      console.log('Error:', e);
    }
  };

  const getStatusColor = (status) => {
    if (status.includes('Resolved')) return '#198754';
    if (status === 'In Progress') return '#ffc107';
    return '#dc3545';
  };

  const renderIssue = ({ item }) => (
    <TouchableOpacity style={styles.issueCard}>
      <View style={styles.issueHeader}>
        <Text style={styles.issueText} numberOfLines={2}>{item.issue}</Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
          <Text style={styles.statusText}>{item.status}</Text>
        </View>
      </View>
      
      <View style={styles.issueDetails}>
        <Ionicons name="location" size={14} color="gray" />
        <Text style={styles.locationText}>{item.location}</Text>
      </View>

      <View style={styles.issueFooter}>
        <Text style={styles.dateText}>
          {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'N/A'}
        </Text>
        <View style={styles.upvoteContainer}>
          <Ionicons name="star" size={16} color="#ffc107" />
          <Text style={styles.upvoteText}>{item.upvotes}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>My Issues</Text>
        <Text style={styles.subtitle}>{issues.length} issues you reported</Text>
      </View>

      <View style={styles.statsRow}>
        <View style={styles.statCard}>
          <Ionicons name="time" size={24} color="#ffc107" />
          <Text style={styles.statNumber}>{issues.filter(i => i.status === 'Pending').length}</Text>
          <Text style={styles.statLabel}>Pending</Text>
        </View>
        <View style={styles.statCard}>
          <Ionicons name="sync" size={24} color="#0d6efd" />
          <Text style={styles.statNumber}>{issues.filter(i => i.status === 'In Progress').length}</Text>
          <Text style={styles.statLabel}>In Progress</Text>
        </View>
        <View style={styles.statCard}>
          <Ionicons name="checkmark-circle" size={24} color="#198754" />
          <Text style={styles.statNumber}>{issues.filter(i => i.status.includes('Resolved')).length}</Text>
          <Text style={styles.statLabel}>Resolved</Text>
        </View>
      </View>

      <FlatList
        data={issues}
        renderItem={renderIssue}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Ionicons name="document-text" size={60} color="lightgray" />
            <Text style={styles.emptyText}>No issues reported yet</Text>
            <Text style={styles.emptySubtext}>Go to Report tab to create your first issue</Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8faff' },
  header: { padding: 20, paddingTop: 50, backgroundColor: 'white' },
  title: { fontSize: 28, fontWeight: 'bold', color: '#0d6efd' },
  subtitle: { fontSize: 14, color: 'gray', marginTop: 5 },
  statsRow: { flexDirection: 'row', padding: 15, gap: 10 },
  statCard: { flex: 1, backgroundColor: 'white', borderRadius: 12, padding: 15, alignItems: 'center', shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 2, elevation: 2 },
  statNumber: { fontSize: 24, fontWeight: 'bold', color: '#333', marginTop: 8 },
  statLabel: { fontSize: 12, color: 'gray', marginTop: 4 },
  list: { padding: 15 },
  issueCard: { backgroundColor: 'white', borderRadius: 16, padding: 16, marginBottom: 12, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 3 },
  issueHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  issueText: { flex: 1, fontSize: 16, fontWeight: '600', color: '#333', marginRight: 10 },
  statusBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 20 },
  statusText: { color: 'white', fontSize: 12, fontWeight: '600' },
  issueDetails: { flexDirection: 'row', alignItems: 'center', marginTop: 10 },
  locationText: { color: 'gray', fontSize: 13, marginLeft: 5 },
  issueFooter: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 12 },
  dateText: { color: 'gray', fontSize: 12 },
  upvoteContainer: { flexDirection: 'row', alignItems: 'center' },
  upvoteText: { marginLeft: 5, fontWeight: '600', color: '#333' },
  empty: { alignItems: 'center', paddingTop: 60 },
  emptyText: { color: 'gray', fontSize: 16, marginTop: 10 },
  emptySubtext: { color: 'lightgray', fontSize: 14, marginTop: 5 },
});