import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity, RefreshControl } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function ForumScreen({ API_URL, user }) {
  const [posts, setPosts] = useState([
    { id: '1', title: 'Best way to report water leakage?', author: 'Rahul S.', replies: 5, time: '2h ago', content: 'What is the fastest way to report water leakage? Should I call or use the app?' },
    { id: '2', title: 'Road repair update - Sector 15', author: 'Admin', replies: 12, time: '5h ago', content: 'Road repair work in Sector 15 will be completed by tomorrow.' },
    { id: '3', title: 'Garbage collection timing', author: 'Priya M.', replies: 3, time: '1d ago', content: 'The garbage truck came at 6 AM today. Can they come a bit later?' },
    { id: '4', title: 'Community cleanup event', author: 'Vikram J.', replies: 8, time: '2d ago', content: 'Join us this Saturday for a neighborhood cleanup drive!' },
  ]);
  const [refreshing, setRefreshing] = useState(false);
  const [newPost, setNewPost] = useState('');

  const onRefresh = () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 1000);
  };

  const submitPost = () => {
    if (!newPost.trim()) return;
    const post = {
      id: Date.now().toString(),
      title: newPost.length > 30 ? newPost.substring(0, 30) + '...' : newPost,
      author: user?.name || 'You',
      replies: 0,
      time: 'Just now',
      content: newPost
    };
    setPosts([post, ...posts]);
    setNewPost('');
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity style={styles.postCard}>
      <View style={styles.postHeader}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>{item.author.charAt(0)}</Text>
        </View>
        <View style={styles.postMeta}>
          <Text style={styles.authorName}>{item.author}</Text>
          <Text style={styles.postTime}>{item.time}</Text>
        </View>
        {item.author === 'Admin' && (
          <View style={styles.adminBadge}>
            <Ionicons name="checkmark-circle" size={14} color="#10b981" />
            <Text style={styles.adminText}>Official</Text>
          </View>
        )}
      </View>
      <Text style={styles.postTitle}>{item.title}</Text>
      <Text style={styles.postContent}>{item.content}</Text>
      <View style={styles.postFooter}>
        <TouchableOpacity style={styles.actionButton}>
          <Ionicons name="chatbubble-outline" size={18} color="#6b7280" />
          <Text style={styles.actionText}>{item.replies} replies</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton}>
          <Ionicons name="heart-outline" size={18} color="#6b7280" />
          <Text style={styles.actionText}>Like</Text>
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Community Forum</Text>
        <Text style={styles.headerSubtitle}>Discuss civic issues with your neighbors</Text>
      </View>

      <View style={styles.createPost}>
        <TextInput
          style={styles.input}
          placeholder="Start a discussion..."
          value={newPost}
          onChangeText={setNewPost}
          multiline
        />
        <TouchableOpacity 
          style={[styles.postButton, !newPost.trim() && styles.postButtonDisabled]} 
          onPress={submitPost}
          disabled={!newPost.trim()}
        >
          <Ionicons name="send" size={18} color="white" />
        </TouchableOpacity>
      </View>

      <FlatList
        data={posts}
        renderItem={renderItem}
        keyExtractor={item => item.id}
        contentContainerStyle={styles.list}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListHeaderComponent={<Text style={styles.sectionTitle}>Recent Discussions</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8faff' },
  header: { padding: 20, paddingTop: 50, backgroundColor: 'white', borderBottomLeftRadius: 24, borderBottomRightRadius: 24 },
  headerTitle: { fontSize: 28, fontWeight: 'bold', color: '#1f2937' },
  headerSubtitle: { fontSize: 14, color: '#6b7280', marginTop: 4 },
  createPost: { flexDirection: 'row', alignItems: 'center', backgroundColor: 'white', marginHorizontal: 16, marginTop: 16, borderRadius: 12, padding: 12 },
  input: { flex: 1, fontSize: 15, maxHeight: 80, paddingRight: 10 },
  postButton: { backgroundColor: '#0d6efd', width: 40, height: 40, borderRadius: 20, justifyContent: 'center', alignItems: 'center' },
  postButtonDisabled: { backgroundColor: '#9ca3af' },
  list: { padding: 16 },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#374151', marginBottom: 12 },
  postCard: { backgroundColor: 'white', borderRadius: 12, padding: 16, marginBottom: 12 },
  postHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  avatar: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#e5e7eb', justifyContent: 'center', alignItems: 'center' },
  avatarText: { fontSize: 16, fontWeight: '600', color: '#6b7280' },
  postMeta: { flex: 1, marginLeft: 10 },
  authorName: { fontSize: 14, fontWeight: '600', color: '#374151' },
  postTime: { fontSize: 12, color: '#9ca3af' },
  adminBadge: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#d1fae5', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 12 },
  adminText: { fontSize: 12, color: '#10b981', fontWeight: '600', marginLeft: 4 },
  postTitle: { fontSize: 16, fontWeight: '700', color: '#1f2937', marginBottom: 6 },
  postContent: { fontSize: 14, color: '#6b7280', lineHeight: 20, marginBottom: 12 },
  postFooter: { flexDirection: 'row', gap: 20, borderTopWidth: 1, borderTopColor: '#f3f4f6', paddingTop: 12 },
  actionButton: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  actionText: { fontSize: 13, color: '#6b7280' },
});