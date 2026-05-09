import React, { useState, useEffect, useCallback } from 'react';
import {
  View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity,
  RefreshControl, Alert, KeyboardAvoidingView, Platform, ActivityIndicator
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function ForumScreen({ API_URL, user }) {
  const [posts, setPosts] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [newPostTitle, setNewPostTitle] = useState('');
  const [posting, setPosting] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadPosts = async () => {
    try {
      const response = await fetch(`${API_URL}/api/forum/posts`, {
        headers: {
          'Accept': 'application/json',
          'X-User-ID': user?.id || user?._id || '',
        }
      });
      if (response.ok) {
        const data = await response.json();
        setPosts(data.posts || []);
      }
    } catch (e) {
      console.log('Forum fetch error:', e);
      // Demo fallback
      setPosts([
        { id: 'f1', title: 'Best way to report water leakage?', author: 'Community', replies: 5, time: '2h ago' },
        { id: 'f2', title: 'Road repair update - Main Road', author: 'Admin', replies: 12, time: '5h ago' },
        { id: 'f3', title: 'Garbage collection timing issue', author: 'Community', replies: 3, time: '1d ago' },
      ]);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadPosts();
  }, []);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadPosts();
    setRefreshing(false);
  }, []);

  const submitPost = async () => {
    if (!newPostTitle.trim()) return;
    if (!user) {
      Alert.alert('Login Required', 'Please login to post in the forum');
      return;
    }
    setPosting(true);
    try {
      const response = await fetch(`${API_URL}/api/forum/posts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-ID': user?.id || user?._id || '',
        },
        body: JSON.stringify({ title: newPostTitle.trim(), content: newPostTitle.trim() })
      });
      const data = await response.json();
      if (data.success && data.post) {
        setPosts(prev => [data.post, ...prev]);
        setNewPostTitle('');
      } else {
        Alert.alert('Error', data.error || 'Could not post. Please try again.');
      }
    } catch (e) {
      // Optimistic local add on network error
      const localPost = {
        id: Date.now().toString(),
        title: newPostTitle.trim(),
        author: user?.name || 'You',
        replies: 0,
        time: 'Just now'
      };
      setPosts(prev => [localPost, ...prev]);
      setNewPostTitle('');
    }
    setPosting(false);
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity style={styles.postCard} activeOpacity={0.8}>
      <View style={styles.postHeader}>
        <View style={[styles.avatar, { backgroundColor: item.author === 'Admin' ? '#10b981' : '#6366f1' }]}>
          <Text style={styles.avatarText}>{(item.author || '?').charAt(0).toUpperCase()}</Text>
        </View>
        <View style={styles.postMeta}>
          <Text style={styles.authorName}>{item.author}</Text>
          <Text style={styles.postTime}>{item.time}</Text>
        </View>
        {item.author === 'Admin' && (
          <View style={styles.adminBadge}>
            <Ionicons name="shield-checkmark" size={12} color="#10b981" />
            <Text style={styles.adminText}>Official</Text>
          </View>
        )}
      </View>

      <Text style={styles.postTitle}>{item.title}</Text>

      <View style={styles.postFooter}>
        <View style={styles.actionButton}>
          <Ionicons name="chatbubble-outline" size={16} color="#6b7280" />
          <Text style={styles.actionText}>{item.replies || 0} replies</Text>
        </View>
        <View style={styles.actionButton}>
          <Ionicons name="time-outline" size={16} color="#6b7280" />
          <Text style={styles.actionText}>{item.time}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.platformName}>Jan Suvidha</Text>
          <Text style={styles.headerTitle}>Community Forum</Text>
        </View>
        <View style={styles.aiBadge}>
          <Ionicons name="people" size={12} color="#059669" />
          <Text style={styles.aiBadgeText}>Community</Text>
        </View>
      </View>

      {/* Compose box */}
      <View style={styles.createPost}>
        <View style={styles.composeAvatar}>
          <Text style={styles.composeAvatarText}>{(user?.name || 'U').charAt(0).toUpperCase()}</Text>
        </View>
        <TextInput
          style={styles.input}
          placeholder="Start a discussion about a civic issue..."
          value={newPostTitle}
          onChangeText={setNewPostTitle}
          multiline
          maxLength={200}
          placeholderTextColor="#9ca3af"
        />
        <TouchableOpacity
          style={[styles.postButton, (!newPostTitle.trim() || posting) && styles.postButtonDisabled]}
          onPress={submitPost}
          disabled={!newPostTitle.trim() || posting}
          activeOpacity={0.8}
        >
          {posting
            ? <ActivityIndicator color="white" size="small" />
            : <Ionicons name="send" size={18} color="white" />
          }
        </TouchableOpacity>
      </View>

      {/* Posts list */}
      {loading ? (
        <ActivityIndicator size="large" color="#0d6efd" style={{ marginTop: 40 }} />
      ) : (
        <FlatList
          data={posts}
          renderItem={renderItem}
          keyExtractor={item => item.id}
          contentContainerStyle={styles.list}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
          ListHeaderComponent={
            <Text style={styles.sectionTitle}>Recent Discussions ({posts.length})</Text>
          }
          ListEmptyComponent={
            <View style={styles.empty}>
              <Ionicons name="chatbubbles-outline" size={60} color="#e5e7eb" />
              <Text style={styles.emptyText}>No discussions yet</Text>
              <Text style={styles.emptySubtext}>Be the first to start a conversation!</Text>
            </View>
          }
        />
      )}
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container:        { flex: 1, backgroundColor: '#f8faff' },
  header:           { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 20, paddingTop: 50, backgroundColor: 'white', borderBottomLeftRadius: 20, borderBottomRightRadius: 20 },
  platformName:     { fontSize: 13, color: '#8b5cf6', fontWeight: '600', marginBottom: 2 },
  headerTitle:      { fontSize: 24, fontWeight: 'bold', color: '#1f2937' },
  aiBadge:          { flexDirection: 'row', alignItems: 'center', backgroundColor: '#d1fae5', paddingHorizontal: 10, paddingVertical: 5, borderRadius: 15 },
  aiBadgeText:      { fontSize: 11, color: '#059669', fontWeight: '600', marginLeft: 4 },
  createPost:       { flexDirection: 'row', alignItems: 'flex-start', backgroundColor: 'white', marginHorizontal: 16, marginTop: 12, borderRadius: 14, padding: 14, elevation: 2, shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.08, shadowRadius: 3, gap: 10 },
  composeAvatar:    { width: 36, height: 36, borderRadius: 18, backgroundColor: '#0d6efd', justifyContent: 'center', alignItems: 'center' },
  composeAvatarText:{ color: 'white', fontWeight: '700', fontSize: 14 },
  input:            { flex: 1, fontSize: 14, maxHeight: 80, color: '#1f2937', paddingTop: 0 },
  postButton:       { backgroundColor: '#0d6efd', width: 38, height: 38, borderRadius: 19, justifyContent: 'center', alignItems: 'center' },
  postButtonDisabled:{ backgroundColor: '#c7d2fe' },
  list:             { padding: 16 },
  sectionTitle:     { fontSize: 15, fontWeight: '700', color: '#374151', marginBottom: 12 },
  postCard:         { backgroundColor: 'white', borderRadius: 14, padding: 16, marginBottom: 12, elevation: 1, shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.06, shadowRadius: 2 },
  postHeader:       { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  avatar:           { width: 38, height: 38, borderRadius: 19, justifyContent: 'center', alignItems: 'center' },
  avatarText:       { fontSize: 15, fontWeight: '700', color: 'white' },
  postMeta:         { flex: 1, marginLeft: 10 },
  authorName:       { fontSize: 14, fontWeight: '600', color: '#374151' },
  postTime:         { fontSize: 12, color: '#9ca3af' },
  adminBadge:       { flexDirection: 'row', alignItems: 'center', backgroundColor: '#d1fae5', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 12 },
  adminText:        { fontSize: 11, color: '#10b981', fontWeight: '600', marginLeft: 3 },
  postTitle:        { fontSize: 15, fontWeight: '700', color: '#1f2937', marginBottom: 12 },
  postFooter:       { flexDirection: 'row', gap: 20, borderTopWidth: 1, borderTopColor: '#f3f4f6', paddingTop: 10 },
  actionButton:     { flexDirection: 'row', alignItems: 'center', gap: 5 },
  actionText:       { fontSize: 13, color: '#6b7280' },
  empty:            { alignItems: 'center', paddingTop: 40 },
  emptyText:        { fontSize: 17, fontWeight: '600', color: '#6b7280', marginTop: 12 },
  emptySubtext:     { fontSize: 13, color: '#9ca3af', marginTop: 6 },
});
