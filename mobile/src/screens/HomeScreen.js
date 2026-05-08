import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, RefreshControl, TextInput } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function HomeScreen({ API_URL, navigation }) {
  const [issues, setIssues] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredIssues, setFilteredIssues] = useState([]);

  const fetchIssues = async () => {
    try {
      const response = await fetch(`${API_URL}/issues/view`);
      const data = await response.json();
      setIssues(data.issues || []);
      setFilteredIssues(data.issues || []);
    } catch (e) {
      console.log('Error:', e);
    }
  };

  useEffect(() => {
    fetchIssues();
  }, []);

  useEffect(() => {
    if (searchQuery.trim()) {
      const filtered = issues.filter(i => 
        (i.issue || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (i.location || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
        (i.category || '').toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredIssues(filtered);
    } else {
      setFilteredIssues(issues);
    }
  }, [searchQuery, issues]);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchIssues();
    setRefreshing(false);
  };

  const getStatusColor = (status) => {
    if (status.includes('Resolved')) return '#198754';
    if (status === 'In Progress') return '#ffc107';
    return '#dc3545';
  };

  const getSeverityColor = (severity) => {
    if (severity === 'High') return '#dc3545';
    if (severity === 'Medium') return '#ffc107';
    return '#198754';
  };

  const renderIssue = ({ item }) => (
    <TouchableOpacity style={styles.issueCard} onPress={() => navigation?.navigate('IssueDetail', { issue: item })}>
      <View style={styles.issueHeader}>
        <Text style={styles.issueText} numberOfLines={2}>{item.issue}</Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
          <Text style={styles.statusText}>{item.status}</Text>
        </View>
      </View>
      
      <View style={styles.issueDetails}>
        <Ionicons name="location" size={14} color="gray" />
        <Text style={styles.locationText} numberOfLines={1}>{item.location}</Text>
      </View>

      <View style={styles.issueFooter}>
        <View style={[styles.severityBadge, { backgroundColor: getSeverityColor(item.severity) + '20' }]}>
          <Text style={[styles.severityText, { color: getSeverityColor(item.severity) }]}>
            {item.severity || 'Low'} Severity
          </Text>
        </View>
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
        <Text style={styles.title}>Civic Issues</Text>
        <Text style={styles.subtitle}>{filteredIssues.length} issues found</Text>
      </View>

      <View style={styles.searchContainer}>
        <Ionicons name="search" size={20} color="#9ca3af" />
        <TextInput
          style={styles.searchInput}
          placeholder="Search issues, locations, categories..."
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
        {searchQuery.length > 0 && (
          <TouchableOpacity onPress={() => setSearchQuery('')}>
            <Ionicons name="close-circle" size={20} color="#9ca3af" />
          </TouchableOpacity>
        )}
      </View>

      <FlatList
        data={filteredIssues}
        renderItem={renderIssue}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Ionicons name="inbox" size={60} color="lightgray" />
            <Text style={styles.emptyText}>{searchQuery ? 'No matching issues' : 'No issues found'}</Text>
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
  searchContainer: { flexDirection: 'row', alignItems: 'center', backgroundColor: 'white', marginHorizontal: 16, marginTop: -10, paddingHorizontal: 12, paddingVertical: 10, borderRadius: 12, borderWidth: 1, borderColor: '#e5e7eb' },
  searchInput: { flex: 1, fontSize: 15, marginLeft: 8, paddingVertical: 0 },
  list: { padding: 15 },
  issueCard: { backgroundColor: 'white', borderRadius: 16, padding: 16, marginBottom: 12, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 3 },
  issueHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  issueText: { flex: 1, fontSize: 16, fontWeight: '600', color: '#333', marginRight: 10 },
  statusBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 20 },
  statusText: { color: 'white', fontSize: 12, fontWeight: '600' },
  issueDetails: { flexDirection: 'row', alignItems: 'center', marginTop: 10 },
  locationText: { color: 'gray', fontSize: 13, marginLeft: 5 },
  issueFooter: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 12 },
  severityBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8 },
  severityText: { fontSize: 12, fontWeight: '600' },
  upvoteContainer: { flexDirection: 'row', alignItems: 'center' },
  upvoteText: { marginLeft: 5, fontWeight: '600', color: '#333' },
  empty: { alignItems: 'center', paddingTop: 60 },
  emptyText: { color: 'gray', fontSize: 16, marginTop: 10 },
});