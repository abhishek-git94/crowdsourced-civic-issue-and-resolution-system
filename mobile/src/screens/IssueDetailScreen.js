import React, { useState, useEffect } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  Image, Alert, Share, ActivityIndicator, Linking
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function IssueDetailScreen({ route, navigation, API_URL, user }) {
  const { issue } = route.params || {};
  const [issueData, setIssueData] = useState(issue);
  const [upvoting, setUpvoting]   = useState(false);
  const [upvoted, setUpvoted]     = useState(false);
  const [loading, setLoading]     = useState(!issue);

  useEffect(() => {
    if (!issue) fetchIssue();
  }, []);

  const fetchIssue = async () => {
    const issueId = route.params?.issueId;
    if (!issueId) return;
    setLoading(true);
    try {
      const r = await fetch(`${API_URL}/issue/${issueId}`, {
        headers: { 'Accept': 'application/json', 'X-User-ID': user?.id || '' }
      });
      const data = await r.json();
      if (data.success && data.issue) setIssueData(data.issue);
    } catch (e) { console.log('fetchIssue error:', e); }
    setLoading(false);
  };

  const handleUpvote = async () => {
    if (upvoting || !issueData || upvoted) return;
    setUpvoting(true);
    try {
      const r = await fetch(`${API_URL}/issue/${issueData.id}/upvote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User-ID': user?.id || '' }
      });
      if (r.ok) {
        const data = await r.json();
        setIssueData(prev => ({ ...prev, upvotes: data.upvotes ?? (prev.upvotes || 0) + 1 }));
        setUpvoted(true);
      } else {
        Alert.alert('Login Required', 'Please login to upvote this issue.');
      }
    } catch (e) {
      // Optimistic update on network failure
      setIssueData(prev => ({ ...prev, upvotes: (prev.upvotes || 0) + 1 }));
      setUpvoted(true);
    }
    setUpvoting(false);
  };

  const handleShare = async () => {
    if (!issueData) return;
    try {
      await Share.share({
        message: `🚨 Civic Issue via Jan Suvidha\n\n📌 ${issueData.issue}\n📍 ${issueData.location}\n🔴 Status: ${issueData.status || 'Pending'}\n⚠️ Severity: ${issueData.severity || 'Medium'}\n\nHelp us resolve this issue!`
      });
    } catch (e) { console.log(e); }
  };

  const openMap = () => {
    if (issueData?.latitude && issueData?.longitude) {
      const url = `https://maps.google.com/?q=${issueData.latitude},${issueData.longitude}`;
      Linking.openURL(url);
    } else if (issueData?.location) {
      const url = `https://maps.google.com/?q=${encodeURIComponent(issueData.location)}`;
      Linking.openURL(url);
    }
  };

  const getStatusColor = (s) => {
    if (s?.includes('Resolved')) return '#10b981';
    if (s === 'In Progress')     return '#f59e0b';
    return '#ef4444';
  };

  const getSeverityColor = (s) => {
    if (s === 'High')   return '#ef4444';
    if (s === 'Medium') return '#f59e0b';
    return '#10b981';
  };

  const getStatusIcon = (s) => {
    if (s?.includes('Resolved')) return 'checkmark-circle';
    if (s === 'In Progress')     return 'time';
    return 'alert-circle';
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#0d6efd" />
        <Text style={styles.loadingText}>Loading issue details...</Text>
      </View>
    );
  }

  if (!issueData) {
    return (
      <View style={styles.loadingContainer}>
        <Ionicons name="alert-circle-outline" size={60} color="#e5e7eb" />
        <Text style={{ color: '#6b7280', fontSize: 16, marginTop: 12 }}>Issue not found</Text>
      </View>
    );
  }

  const statusColor = getStatusColor(issueData.status);
  const sevColor    = getSeverityColor(issueData.severity);

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Cover Image or Gradient Banner */}
      {issueData.image_url ? (
        <View>
          <Image source={{ uri: issueData.image_url }} style={styles.coverImage} />
          <View style={styles.imageOverlay} />
        </View>
      ) : (
        <View style={[styles.bannerGradient, { backgroundColor: sevColor }]}>
          <Ionicons name={getStatusIcon(issueData.status)} size={60} color="rgba(255,255,255,0.3)" />
        </View>
      )}

      <View style={styles.content}>
        {/* Status + Severity badges */}
        <View style={styles.badgeRow}>
          <View style={[styles.statusBadge, { backgroundColor: statusColor }]}>
            <Ionicons name={getStatusIcon(issueData.status)} size={14} color="white" />
            <Text style={styles.badgeText}>{issueData.status || 'Pending'}</Text>
          </View>
          <View style={[styles.severityBadge, { borderColor: sevColor, backgroundColor: sevColor + '18' }]}>
            <Text style={[styles.sevText, { color: sevColor }]}>{issueData.severity || 'Low'} Severity</Text>
          </View>
          {issueData.priority && (
            <View style={styles.priorityBadge}>
              <Ionicons name="flash" size={12} color="#8b5cf6" />
              <Text style={styles.priorityText}>{issueData.priority}</Text>
            </View>
          )}
        </View>

        {/* Title */}
        <Text style={styles.title}>{issueData.issue || 'No description provided'}</Text>

        {/* Info cards */}
        <View style={styles.infoGrid}>
          <TouchableOpacity style={styles.infoCard} onPress={openMap} activeOpacity={0.8}>
            <Ionicons name="location" size={22} color="#0d6efd" />
            <View style={styles.infoCardText}>
              <Text style={styles.infoCardLabel}>Location</Text>
              <Text style={styles.infoCardValue} numberOfLines={2}>{issueData.location || 'Unknown'}</Text>
            </View>
            <Ionicons name="open-outline" size={16} color="#9ca3af" />
          </TouchableOpacity>

          <View style={styles.infoCard}>
            <Ionicons name="grid" size={22} color="#6366f1" />
            <View style={styles.infoCardText}>
              <Text style={styles.infoCardLabel}>Category</Text>
              <Text style={styles.infoCardValue}>{issueData.category || 'General'}</Text>
            </View>
          </View>

          {issueData.assigned_to && (
            <View style={styles.infoCard}>
              <Ionicons name="business" size={22} color="#059669" />
              <View style={styles.infoCardText}>
                <Text style={styles.infoCardLabel}>Assigned To</Text>
                <Text style={styles.infoCardValue}>{issueData.assigned_to}</Text>
              </View>
            </View>
          )}

          <View style={styles.infoCard}>
            <Ionicons name="calendar" size={22} color="#f59e0b" />
            <View style={styles.infoCardText}>
              <Text style={styles.infoCardLabel}>Reported On</Text>
              <Text style={styles.infoCardValue}>
                {issueData.created_at ? new Date(issueData.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' }) : 'N/A'}
              </Text>
            </View>
          </View>
        </View>

        {/* Stats row */}
        <View style={styles.statsRow}>
          <View style={styles.statItem}>
            <Ionicons name="star" size={26} color="#fbbf24" />
            <Text style={styles.statValue}>{issueData.upvotes || 0}</Text>
            <Text style={styles.statLabel}>Upvotes</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Ionicons name="people" size={26} color="#0d6efd" />
            <Text style={styles.statValue}>{(issueData.upvotes || 0) + 3}</Text>
            <Text style={styles.statLabel}>Affected</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Ionicons name="time" size={26} color="#8b5cf6" />
            <Text style={styles.statValue}>{issueData.predicted_resolution_days || 7}d</Text>
            <Text style={styles.statLabel}>Est. Fix</Text>
          </View>
        </View>

        {/* AI info if present */}
        {issueData.ai_category && (
          <View style={styles.aiCard}>
            <View style={styles.aiCardHeader}>
              <Ionicons name="sparkles" size={16} color="#8b5cf6" />
              <Text style={styles.aiCardTitle}>AI Analysis</Text>
            </View>
            <Text style={styles.aiCardText}>{issueData.description || issueData.ai_category}</Text>
          </View>
        )}

        {/* Actions */}
        <View style={styles.actions}>
          <TouchableOpacity
            style={[styles.upvoteBtn, upvoted && styles.upvoteBtnDone]}
            onPress={handleUpvote}
            disabled={upvoting || upvoted}
            activeOpacity={0.85}
          >
            {upvoting
              ? <ActivityIndicator color="white" size="small" />
              : <>
                  <Ionicons name={upvoted ? 'star' : 'star-outline'} size={20} color="white" />
                  <Text style={styles.actionBtnText}>{upvoted ? 'Upvoted!' : `Upvote (${issueData.upvotes || 0})`}</Text>
                </>
            }
          </TouchableOpacity>

          <TouchableOpacity style={styles.shareBtn} onPress={handleShare} activeOpacity={0.85}>
            <Ionicons name="share-social-outline" size={20} color="white" />
            <Text style={styles.actionBtnText}>Share</Text>
          </TouchableOpacity>
        </View>

        {/* Map button */}
        <TouchableOpacity style={styles.mapBtn} onPress={openMap} activeOpacity={0.85}>
          <Ionicons name="map" size={18} color="#0d6efd" />
          <Text style={styles.mapBtnText}>View on Map</Text>
          <Ionicons name="chevron-forward" size={16} color="#0d6efd" />
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container:       { flex: 1, backgroundColor: '#f8faff' },
  loadingContainer:{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f8faff' },
  loadingText:     { color: '#6b7280', marginTop: 12 },
  coverImage:      { width: '100%', height: 240, resizeMode: 'cover' },
  imageOverlay:    { position: 'absolute', bottom: 0, left: 0, right: 0, height: 60, backgroundColor: 'transparent' },
  bannerGradient:  { width: '100%', height: 160, justifyContent: 'center', alignItems: 'center', opacity: 0.85 },
  content:         { padding: 18 },
  badgeRow:        { flexDirection: 'row', gap: 8, marginBottom: 12, flexWrap: 'wrap' },
  statusBadge:     { flexDirection: 'row', alignItems: 'center', gap: 5, paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20 },
  badgeText:       { color: 'white', fontSize: 13, fontWeight: '700' },
  severityBadge:   { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, borderWidth: 1.5 },
  sevText:         { fontSize: 13, fontWeight: '700' },
  priorityBadge:   { flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: '#f3e8ff', paddingHorizontal: 10, paddingVertical: 6, borderRadius: 20 },
  priorityText:    { fontSize: 12, color: '#8b5cf6', fontWeight: '700' },
  title:           { fontSize: 20, fontWeight: '700', color: '#1f2937', marginBottom: 16, lineHeight: 28 },
  infoGrid:        { gap: 10, marginBottom: 16 },
  infoCard:        { flexDirection: 'row', alignItems: 'center', backgroundColor: 'white', borderRadius: 12, padding: 14, gap: 12, elevation: 1, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 3 },
  infoCardText:    { flex: 1 },
  infoCardLabel:   { fontSize: 11, color: '#9ca3af', fontWeight: '600', textTransform: 'uppercase', letterSpacing: 0.5 },
  infoCardValue:   { fontSize: 14, color: '#374151', fontWeight: '600', marginTop: 2 },
  statsRow:        { flexDirection: 'row', backgroundColor: 'white', borderRadius: 16, padding: 16, marginBottom: 14, elevation: 1 },
  statItem:        { flex: 1, alignItems: 'center', gap: 4 },
  statDivider:     { width: 1, backgroundColor: '#f3f4f6' },
  statValue:       { fontSize: 22, fontWeight: '800', color: '#1f2937' },
  statLabel:       { fontSize: 11, color: '#9ca3af', fontWeight: '500' },
  aiCard:          { backgroundColor: '#f3e8ff', borderRadius: 12, padding: 14, marginBottom: 14, borderLeftWidth: 4, borderLeftColor: '#8b5cf6' },
  aiCardHeader:    { flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 6 },
  aiCardTitle:     { fontSize: 13, fontWeight: '700', color: '#8b5cf6' },
  aiCardText:      { fontSize: 13, color: '#374151', lineHeight: 18 },
  actions:         { flexDirection: 'row', gap: 10, marginBottom: 12 },
  upvoteBtn:       { flex: 1, backgroundColor: '#0d6efd', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 14, borderRadius: 14 },
  upvoteBtnDone:   { backgroundColor: '#10b981' },
  shareBtn:        { flex: 1, backgroundColor: '#374151', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, padding: 14, borderRadius: 14 },
  actionBtnText:   { color: 'white', fontSize: 15, fontWeight: '700' },
  mapBtn:          { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, backgroundColor: '#eff6ff', padding: 14, borderRadius: 14, borderWidth: 1.5, borderColor: '#bfdbfe', marginBottom: 20 },
  mapBtnText:      { color: '#0d6efd', fontSize: 15, fontWeight: '600', flex: 1, textAlign: 'center' },
});
