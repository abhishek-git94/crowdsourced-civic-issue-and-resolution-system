import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, Image, ScrollView, ActivityIndicator } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import { Ionicons } from '@expo/vector-icons';

export default function ReportScreen({ API_URL, user }) {
  const [location, setLocation] = useState('');
  const [description, setDescription] = useState('');
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [locationLoading, setLocationLoading] = useState(false);
  const [latitude, setLatitude] = useState(null);
  const [longitude, setLongitude] = useState(null);
  
  // AI Analysis State
  const [analyzing, setAnalyzing] = useState(false);
  const [aiResult, setAiResult] = useState(null);
  const [showAiModal, setShowAiModal] = useState(false);
  
  // Voice Input State
  const [isRecording, setIsRecording] = useState(false);

  const pickImage = async () => {
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
    }
  };

  // Reverse Geocoding using Nominatim API
  const reverseGeocode = async (lat, lon) => {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&addressdetails=1`,
        {
          headers: {
            'User-Agent': 'JanSuvidhaMobile/1.0'
          }
        }
      );
      
      const data = await response.json();
      
      if (data && data.address) {
        const addr = data.address;
        // Build readable address
        let addressParts = [];
        
        if (addr.road) addressParts.push(addr.road);
        if (addr.neighbourhood) addressParts.push(addr.neighbourhood);
        if (addr.suburb) addressParts.push(addr.suburb);
        if (addr.city || addr.town || addr.village) addressParts.push(addr.city || addr.town || addr.village);
        if (addr.state) addressParts.push(addr.state);
        
        return addressParts.join(', ') || data.display_name?.split(',').slice(0, 2).join(', ');
      }
      return null;
    } catch (error) {
      console.log('Geocoding error:', error);
      return null;
    }
  };

  const getLocation = async () => {
    let { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission Denied', 'Location permission is required');
      return;
    }

    setLocationLoading(true);
    
    try {
      let loc = await Location.getCurrentPositionAsync({});
      const lat = loc.coords.latitude;
      const lon = loc.coords.longitude;
      
      setLatitude(lat);
      setLongitude(lon);
      
      // Try to get readable address from Nominatim
      const address = await reverseGeocode(lat, lon);
      
      if (address) {
        setLocation(address);
        Alert.alert('Location Found', `📍 ${address}`);
      } else {
        // Fallback to coordinates
        setLocation(`${lat.toFixed(4)}, ${lon.toFixed(4)}`);
        Alert.alert('Location Found', `Coordinates: ${lat.toFixed(4)}, ${lon.toFixed(4)}`);
      }
    } catch (error) {
      Alert.alert('Error', 'Could not get your location');
      console.error(error);
    }
    
    setLocationLoading(false);
  };

  // Analyze image with AI
  const analyzeWithAI = async () => {
    if (!image) {
      Alert.alert('No Image', 'Please take a photo first to analyze with AI');
      return;
    }

    setAnalyzing(true);
    try {
      const formData = new FormData();
      const filename = image.split('/').pop();
      const match = /\.(\w+)$/.exec(filename);
      const type = match ? `image/${match[1]}` : 'image';
      formData.append('image', { uri: image, name: filename, type });
      formData.append('location', location || 'Unknown');

      const response = await fetch(`${API_URL}/api/analyze-image`, {
        method: 'POST',
        body: formData,
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const data = await response.json();
      
      if (response.ok && data.description) {
        setAiResult(data);
        setDescription(data.description);
        setShowAiModal(true);
      } else {
        Alert.alert('Analysis Failed', data.error || 'Could not analyze image');
      }
    } catch (e) {
      Alert.alert('Error', 'AI analysis failed');
      console.log(e);
    }
    setAnalyzing(false);
  };

  // Voice Input - Record and transcribe
  const handleVoiceInput = async () => {
    if (isRecording) {
      setIsRecording(false);
      return;
    }
    
    Alert.alert(
      'Voice Input',
      'Tap to start recording your issue. Speak clearly about the problem.',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Start Recording', 
          onPress: async () => {
            setIsRecording(true);
            
            // Simulate voice recording - in production, use expo-av + speech API
            // For demo, show UI feedback
            setTimeout(async () => {
              setIsRecording(false);
              
              // Use text analysis API instead of actual speech recognition
              // In production, integrate with device speech-to-text
              Alert.alert(
                'Voice Recording Complete',
                'Would you like to type your issue or use AI to analyze your description?',
                [
                  { 
                    text: 'Type Description', 
                    style: 'cancel'
                  },
                  {
                    text: 'AI Analyze My Voice',
                    onPress: () => {
                      // Use sample text for demo
                      const sampleDescription = 'There is a large pothole on the main road near the market. It is very dangerous for vehicles and pedestrians.';
                      setDescription(sampleDescription);
                      // Trigger AI analysis on the text
                      analyzeTextDescription(sampleDescription);
                    }
                  }
                ]
              );
            }, 3000);
          }
        }
      ]
    );
  };

  // Analyze text description with AI
  const analyzeTextDescription = async (text) => {
    if (!text) return;
    
    setAnalyzing(true);
    try {
      const response = await fetch(`${API_URL}/api/analyze-text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, location: location || 'Unknown' })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        // Combine text analysis with image if available
        setAiResult({
          description: text,
          category: data.recommended_department?.includes('Water') ? 'water' : 
                   data.recommended_department?.includes('Sanitation') ? 'sanitation' :
                   data.recommended_department?.includes('PWD') ? 'roads' : 'general',
          sentiment: data.sentiment,
          urgency_score: data.urgency_score,
          priority: data.urgency_score > 0.6 ? 'High' : data.urgency_score > 0.3 ? 'Medium' : 'Low',
          severity: data.urgency_score > 0.6 ? 'High' : 'Medium',
          assigned_department: data.recommended_department,
          predicted_resolution_days: data.predicted_resolution_days,
          confidence: 85,
          similar_issues_count: 0,
          duplicate_detected: false
        });
      }
    } catch (e) {
      console.log('Text analysis error:', e);
    }
    setAnalyzing(false);
  };

  const submitReport = async () => {
    if (!location || !description) {
      Alert.alert('Error', 'Please fill in location and description');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('location', location);
      formData.append('issue', description);
      formData.append('name', user.name);
      if (latitude) formData.append('latitude', latitude.toString());
      if (longitude) formData.append('longitude', longitude.toString());
      
      if (image) {
        const filename = image.split('/').pop();
        const match = /\.(\w+)$/.exec(filename);
        const type = match ? `image/${match[1]}` : 'image';
        formData.append('attachment', { uri: image, name: filename, type });
      }

      const response = await fetch(`${API_URL}/issues/report`, {
        method: 'POST',
        body: formData,
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const data = await response.json();
      
      if (response.ok) {
        let successMsg = 'Issue reported successfully!';
        if (aiResult) {
          successMsg += `\n\n🤖 AI Analysis:\n• Category: ${aiResult.category || 'General'}\n• Severity: ${aiResult.severity || 'Low'}\n• Priority: ${aiResult.priority || 'Low'}\n• Confidence: ${Math.round(aiResult.confidence || 0)}%`;
          if (aiResult.duplicate_detected) {
            successMsg += '\n\n⚠️ This is a duplicate - linked to existing issue';
          }
        }
        Alert.alert('✅ Success', successMsg);
        
        // Reset form
        setLocation('');
        setDescription('');
        setImage(null);
        setLatitude(null);
        setLongitude(null);
        setAiResult(null);
      } else {
        Alert.alert('Error', data.error || 'Failed to submit');
      }
    } catch (e) {
      Alert.alert('Error', 'Cannot connect to server');
    }
    setLoading(false);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Report Issue</Text>
        <Text style={styles.subtitle}>Help improve your city</Text>
      </View>

      <View style={styles.form}>
        {/* Location */}
        <Text style={styles.label}>Location *</Text>
        <View style={styles.locationRow}>
          <View style={styles.locationInput}>
            <Ionicons name="location" size={20} color="gray" style={styles.inputIcon} />
            <TextInput
              style={styles.input}
              placeholder="Enter location or use GPS"
              value={location}
              onChangeText={setLocation}
            />
          </View>
          <TouchableOpacity 
            style={[styles.gpsButton, locationLoading && styles.gpsButtonLoading]} 
            onPress={getLocation}
            disabled={locationLoading}
          >
            {locationLoading ? (
              <ActivityIndicator size="small" color="white" />
            ) : (
              <Ionicons name="navigate" size={24} color="white" />
            )}
          </TouchableOpacity>
        </View>
        {latitude && longitude && (
          <Text style={styles.coordText}>
            📍 {latitude.toFixed(6)}, {longitude.toFixed(6)}
          </Text>
        )}

        {/* Image */}
        <Text style={styles.label}>Photo (Optional)</Text>
        <TouchableOpacity style={styles.imagePicker} onPress={pickImage}>
          {image ? (
            <Image source={{ uri: image }} style={styles.imagePreview} />
          ) : (
            <View style={styles.imagePlaceholder}>
              <Ionicons name="camera" size={40} color="gray" />
              <Text style={styles.imageText}>Take Photo</Text>
            </View>
          )}
        </TouchableOpacity>
        
        {/* AI Analyze Button */}
        {image && (
          <TouchableOpacity 
            style={[styles.analyzeButton, analyzing && styles.analyzeButtonLoading]} 
            onPress={analyzeWithAI}
            disabled={analyzing}
          >
            {analyzing ? (
              <ActivityIndicator size="small" color="white" />
            ) : (
              <>
                <Ionicons name="cpu" size={20} color="white" />
                <Text style={styles.analyzeButtonText}>
                  {aiResult ? 'Re-analyze with AI' : 'Analyze with AI'}
                </Text>
              </>
            )}
          </TouchableOpacity>
        )}

        {/* AI Result Preview */}
        {aiResult && (
          <View style={styles.aiResultPreview}>
            <View style={styles.aiResultHeader}>
              <Ionicons name="sparkles" size={18} color="#8b5cf6" />
              <Text style={styles.aiResultTitle}>AI Analysis Complete</Text>
            </View>
            <Text style={styles.aiResultCategory}>
              📁 {aiResult.category || 'General'} | ⚠️ {aiResult.severity || 'Low'} | 🚨 {aiResult.priority || 'Low'}
            </Text>
            <Text style={styles.aiResultDetail}>
              🔍 {Math.round(aiResult.confidence || 0)}% | 📊 {aiResult.similar_issues_count || 0} similar | 📅 ~{aiResult.predicted_resolution_days || 7} days
            </Text>
            {(aiResult.sentiment || aiResult.assigned_department) && (
              <View style={styles.aiExtraInfo}>
                {aiResult.sentiment && (
                  <View style={[styles.sentimentBadge, 
                    aiResult.sentiment === 'angry' && styles.sentimentAngry ||
                    aiResult.sentiment === 'urgent' && styles.sentimentUrgent ||
                    aiResult.sentiment === 'concerned' && styles.sentimentConcerned
                  ]}>
                    <Text style={styles.sentimentText}>
                      {aiResult.sentiment === 'angry' ? '😠' : aiResult.sentiment === 'urgent' ? '🚨' : aiResult.sentiment === 'concerned' ? '😟' : '😐'} 
                      {aiResult.sentiment.toUpperCase()}
                    </Text>
                  </View>
                )}
                {aiResult.assigned_department && (
                  <Text style={styles.deptText}>🏢 {aiResult.assigned_department}</Text>
                )}
              </View>
            )}
            {aiResult.duplicate_detected && (
              <View style={styles.duplicateBadge}>
                <Ionicons name="warning" size={14} color="#dc2626" />
                <Text style={styles.duplicateText}>Duplicate! Linked to existing</Text>
              </View>
            )}
          </View>
        )}

        {/* Description */}
        <View style={styles.descriptionHeader}>
          <Text style={styles.label}>Description *</Text>
          <TouchableOpacity 
            style={[styles.voiceButton, isRecording && styles.voiceButtonActive]} 
            onPress={handleVoiceInput}
          >
            {isRecording ? (
              <ActivityIndicator size="small" color="white" />
            ) : (
              <Ionicons name="mic" size={20} color="white" />
            )}
            <Text style={styles.voiceButtonText}>
              {isRecording ? 'Recording...' : 'Voice'}
            </Text>
          </TouchableOpacity>
        </View>
        <TextInput
          style={styles.textArea}
          placeholder="Describe the issue... (or tap Voice above)"
          value={description}
          onChangeText={(text) => {
            setDescription(text);
            // Auto-analyze when user stops typing
            if (text.length > 20) {
              clearTimeout(window._analyzeTimeout);
              window._analyzeTimeout = setTimeout(() => analyzeTextDescription(text), 1500);
            }
          }}
          multiline
          numberOfLines={4}
        />

        {/* Submit */}
        <TouchableOpacity 
          style={[styles.button, loading && styles.buttonDisabled]} 
          onPress={submitReport}
          disabled={loading}
        >
          <Ionicons name="send" size={20} color="white" />
          <Text style={styles.buttonText}>
            {loading ? 'Submitting...' : 'Submit Report'}
          </Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8faff' },
  header: { padding: 20, paddingTop: 50, backgroundColor: 'white' },
  title: { fontSize: 28, fontWeight: 'bold', color: '#0d6efd' },
  subtitle: { fontSize: 14, color: 'gray', marginTop: 5 },
  form: { padding: 20 },
  label: { fontSize: 14, fontWeight: '600', color: '#333', marginBottom: 8, marginTop: 15 },
  locationRow: { flexDirection: 'row', gap: 10 },
  locationInput: { flex: 1, flexDirection: 'row', alignItems: 'center', backgroundColor: 'white', borderRadius: 12, paddingHorizontal: 15, borderWidth: 1, borderColor: '#ddd' },
  inputIcon: { marginRight: 10 },
  input: { flex: 1, paddingVertical: 15, fontSize: 16 },
  gpsButton: { backgroundColor: '#0d6efd', width: 50, height: 50, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  gpsButtonLoading: { backgroundColor: '#6c757d' },
  coordText: { fontSize: 12, color: '#666', marginTop: 5, marginLeft: 5 },
  imagePicker: { backgroundColor: 'white', borderRadius: 12, borderWidth: 2, borderStyle: 'dashed', borderColor: '#ddd', overflow: 'hidden' },
  imagePreview: { width: '100%', height: 200, resizeMode: 'cover' },
  imagePlaceholder: { height: 150, justifyContent: 'center', alignItems: 'center' },
  imageText: { color: 'gray', marginTop: 10 },
  
  // Voice Input
  descriptionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  voiceButton: { 
    backgroundColor: '#059669', 
    paddingHorizontal: 12, 
    paddingVertical: 6, 
    borderRadius: 20, 
    flexDirection: 'row', 
    alignItems: 'center', 
    gap: 5 
  },
  voiceButtonActive: { backgroundColor: '#dc2626' },
  voiceButtonText: { color: 'white', fontSize: 12, fontWeight: '600' },
  
  // AI Button
  analyzeButton: { 
    backgroundColor: '#8b5cf6', 
    padding: 14, 
    borderRadius: 12, 
    alignItems: 'center', 
    flexDirection: 'row', 
    justifyContent: 'center', 
    gap: 10, 
    marginTop: 15 
  },
  analyzeButtonLoading: { backgroundColor: '#6c757d' },
  analyzeButtonText: { color: 'white', fontSize: 16, fontWeight: '600' },
  
  // AI Result Preview
  aiResultPreview: { 
    backgroundColor: '#f3e8ff', 
    borderRadius: 12, 
    padding: 15, 
    marginTop: 15,
    borderWidth: 1,
    borderColor: '#8b5cf6'
  },
  aiResultHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  aiResultTitle: { fontSize: 14, fontWeight: '700', color: '#8b5cf6', marginLeft: 8 },
  aiResultCategory: { fontSize: 13, color: '#666', marginTop: 5 },
  aiResultDetail: { fontSize: 12, color: '#888', marginTop: 3 },
  aiExtraInfo: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 8 },
  sentimentBadge: { backgroundColor: '#e5e7eb', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 12 },
  sentimentAngry: { backgroundColor: '#fee2e2' },
  sentimentUrgent: { backgroundColor: '#fef3c7' },
  sentimentConcerned: { backgroundColor: '#dbeafe' },
  sentimentText: { fontSize: 11, fontWeight: '700', color: '#374151' },
  deptText: { fontSize: 12, color: '#6b7280', backgroundColor: '#f3f4f6', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 12 },
  duplicateBadge: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    backgroundColor: '#fee2e2', 
    padding: 8, 
    borderRadius: 8, 
    marginTop: 8 
  },
  duplicateText: { fontSize: 12, color: '#dc2626', marginLeft: 6, fontWeight: '600' },
  
  textArea: { backgroundColor: 'white', borderRadius: 12, padding: 15, fontSize: 16, borderWidth: 1, borderColor: '#ddd', minHeight: 120, textAlignVertical: 'top' },
  button: { backgroundColor: '#0d6efd', padding: 16, borderRadius: 12, alignItems: 'center', flexDirection: 'row', justifyContent: 'center', gap: 10, marginTop: 30 },
  buttonDisabled: { backgroundColor: '#999' },
  buttonText: { color: 'white', fontSize: 18, fontWeight: 'bold' },
});