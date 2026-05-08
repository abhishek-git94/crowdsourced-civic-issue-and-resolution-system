import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, Image } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function IssueDetailScreen({ route, API_URL }) {
  const { issueId } = route.params;
  const [issue, setIssue] = useState(null);

  useEffect(() => {
    fetchIssue();
  }, []);

  const fetchIssue = async () => {
    try {
      const response = await fetch(`${API_URL}/issues/view`);
      const data = await response.json();
      const found = (data.issues || []).find(i => i.id === issueId);
      setIssue(found);
    } catch (e) {
      console.log('Error:', e);
    }
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

  if (!issue) {
    return (
      <View style={styles.loadingContainer}>
        <Text>Loading...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Image */}
      {issue.file && (
        <Image source={{ uri: `${API_URL.replace('/api', '')}/static/${issue.file}` }} style={styles.image} />
      )}

      <View style={styles.content}>
        {/* Status Badge */}
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(issue.status) }]}>
          <Text style={styles.statusText}>{issue.status}</Text>
        </View>

        {/* Title */}
        <Text style={styles.title}>{issue.issue}</Text>

        {/* Location */}
        <View style={styles.infoRow}>
          <Ionicons name="location" size={20} color="#dc3545" />
          <Text style={styles.infoText}>{issue.location}</Text>
        </View>

        {/* Details Grid */}
        <View style={styles.grid}>
          <View style={styles.gridItem}>
            <Text style={styles.gridLabel}>Category</Text>
            <Text style={styles.gridValue}>{issue.category || 'General'}</Text>
          </View>
          <View style={styles.gridItem}>
            <Text style={styles.gridLabel}>Severity</Text>
            <Text style={[styles.gridValue, { color: getSeverityColor(issue.severity) }]}>
              {issue.severity || 'Low'}
            </Text>
          </View>
          <View style={styles.gridItem}>
            <Text style={styles.gridLabel}>Upvotes</Text>
            <Text style={styles.gridValue}>{issue.upvotes}</Text>
          </View>
          <View style={styles.gridItem}>
            <Text style={styles.gridLabel}>Assigned To</Text>
            <Text style={styles.gridValue}>{issue.assigned_to || 'Not assigned'}</Text>
          </View>
        </View>

        {/* Timeline */}
        <View style={styles.timeline}>
          <Text style={styles.sectionTitle}>Timeline</Text>
          
          <View style={styles.timelineItem}>
            <View style={[styles.timelineDot, { backgroundColor: '#198754' }]} />
            <View style={styles.timelineContent}>
              <Text style={styles.timelineTitle}>Reported</Text>
              <Text style={styles.timelineDate}>
                {issue.created_at ? new Date(issue.created_at).toLocaleDateString() : 'N/A'}
              </Text>
            </View>
          </View>

          {issue.status === 'In Progress' && (
            <View style={styles.timelineItem}>
              <View style={[styles.timelineDot, { backgroundColor: '#ffc107' }]} />
              <View style={styles.timelineContent}>
                <Text style={styles.timelineTitle}>Under Review</Text>
                <Text style={styles.timelineDate}>Assigned to {issue.assigned_to || 'Authority'}</Text>
              </View>
            </View>
          )}

          {issue.status.includes('Resolved') && (
            <View style={styles.timelineItem}>
              <View style={[styles.timelineDot, { backgroundColor: '#198754' }]} />
              <View style={styles.timelineContent}>
                <Text style={styles.timelineTitle}>Resolved</Text>
                <Text style={styles.timelineDate}>
                  {issue.resolved_at ? new Date(issue.resolved_at).toLocaleDateString() : 'Recently'}
                </Text>
              </View>
            </View>
          )}
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8faff' },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  image: { width: '100%', height: 250, resizeMode: 'cover' },
  content: { padding: 20 },
  statusBadge: { alignSelf: 'flex-start', paddingHorizontal: 15, paddingVertical: 6, borderRadius: 20, marginBottom: 15 },
  statusText: { color: 'white', fontWeight: '600' },
  title: { fontSize: 22, fontWeight: 'bold', color: '#333', marginBottom: 15 },
  infoRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  infoText: { marginLeft: 8, color: 'gray', flex: 1 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', backgroundColor: 'white', borderRadius: 16, padding: 15, marginBottom: 20 },
  gridItem: { width: '50%', paddingVertical: 10 },
  gridLabel: { fontSize: 12, color: 'gray' },
  gridValue: { fontSize: 16, fontWeight: '600', color: '#333' },
  timeline: { backgroundColor: 'white', borderRadius: 16, padding: 20 },
  sectionTitle: { fontSize: 16, fontWeight: 'bold', color: '#333', marginBottom: 15 },
  timelineItem: { flexDirection: 'row', marginBottom: 15 },
  timelineDot: { width: 12, height: 12, borderRadius: 6, marginTop: 4 },
  timelineContent: { marginLeft: 15 },
  timelineTitle: { fontSize: 14, fontWeight: '600', color: '#333' },
  timelineDate: { fontSize: 12, color: 'gray', marginTop: 2 },
});