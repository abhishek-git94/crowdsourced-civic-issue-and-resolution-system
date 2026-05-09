import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, TouchableOpacity } from 'react-native';
import MapView, { Marker, Callout } from 'react-native-maps';
import * as Location from 'expo-location';
import { Ionicons } from '@expo/vector-icons';

export default function MapScreen({ API_URL }) {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [myLocation, setMyLocation] = useState(null);
  const [myAddress, setMyAddress] = useState(null);

  useEffect(() => {
    fetchIssues();
    getMyLocation();
  }, []);

  const fetchIssues = async () => {
    try {
      const response = await fetch(`${API_URL}/view`, {
        headers: { 'Accept': 'application/json', 'Bypass-Tunnel-Reminder': 'true' }
      });
      const data = await response.json();
      setIssues(data.issues || []);
    } catch (e) {
      console.log('Error:', e);
    }
    setLoading(false);
  };

  // Get user's current location with Nominatim reverse geocoding
  const getMyLocation = async () => {
    try {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') return;

      let loc = await Location.getCurrentPositionAsync({});
      const { latitude, longitude } = loc.coords;
      
      setMyLocation({ latitude, longitude });
      
      // Reverse geocode using Nominatim
      try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`,
          { headers: { 'User-Agent': 'JanSuvidhaMobile/1.0' } }
        );
        const data = await response.json();
        
        if (data?.address) {
          const addr = data.address;
          const parts = [];
          if (addr.road) parts.push(addr.road);
          if (addr.city || addr.town) parts.push(addr.city || addr.town);
          setMyAddress(parts.join(', '));
        }
      } catch (e) {
        console.log('Geocode error:', e);
      }
    } catch (e) {
      console.log('Location error:', e);
    }
  };

  const getStatusColor = (status) => {
    if (status.includes('Resolved')) return 'green';
    if (status === 'In Progress') return 'orange';
    return 'red';
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#0d6efd" />
        <Text style={styles.loadingText}>Loading map...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <View style={styles.titleRow}>
            <View>
              <Text style={styles.platformName}>Jan Suvidha</Text>
              <Text style={styles.title}>Issue Map</Text>
            </View>
            <View style={styles.aiBadge}>
              <Ionicons name="sparkles" size={12} color="#fff" />
              <Text style={styles.aiBadgeText}>AI Hotspots</Text>
            </View>
          </View>
          <Text style={styles.subtitle}>{issues.length} issues • AI clustered by location</Text>
        </View>
        {myAddress && (
          <View style={styles.myLocationBadge}>
            <Ionicons name="location" size={14} color="#0d6efd" />
            <Text style={styles.myLocationText} numberOfLines={1}>{myAddress}</Text>
          </View>
        )}
      </View>

      <MapView
        style={styles.map}
        initialRegion={{
          latitude: 20.5937,
          longitude: 78.9629,
          latitudeDelta: 10,
          longitudeDelta: 10,
        }}
        customMapStyle={[]}
      >
        {/* User's current location marker */}
        {myLocation && (
          <Marker
            coordinate={myLocation}
            title="You are here"
            description={myAddress || 'Your current location'}
          >
            <View style={styles.myLocationMarker}>
              <Ionicons name="person" size={18} color="white" />
            </View>
          </Marker>
        )}

        {/* Issue markers */}
        {issues.map((issue) => (
          issue.latitude && issue.longitude ? (
            <Marker
              key={issue.id}
              coordinate={{
                latitude: issue.latitude,
                longitude: issue.longitude,
              }}
              pinColor={getStatusColor(issue.status)}
            >
              <Callout>
                <View style={styles.callout}>
                  <Text style={styles.calloutTitle} numberOfLines={2}>{issue.issue}</Text>
                  <Text style={styles.calloutLocation}>{issue.location}</Text>
                  <View style={[styles.calloutStatus, { backgroundColor: getStatusColor(issue.status) }]}>
                    <Text style={styles.calloutStatusText}>{issue.status}</Text>
                  </View>
                </View>
              </Callout>
            </Marker>
          ) : null
        ))}
      </MapView>

      {/* My Location Button */}
      <TouchableOpacity style={styles.myLocationButton} onPress={getMyLocation}>
        <Ionicons name="locate" size={24} color="#0d6efd" />
      </TouchableOpacity>

      <View style={styles.legend}>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: 'red' }]} />
          <Text style={styles.legendText}>Pending</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: 'orange' }]} />
          <Text style={styles.legendText}>In Progress</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: 'green' }]} />
          <Text style={styles.legendText}>Resolved</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8faff' },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { marginTop: 10, color: 'gray' },
  header: { padding: 20, paddingTop: 50, backgroundColor: 'white', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  headerContent: { flex: 1 },
  titleRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  platformName: { fontSize: 14, color: '#8b5cf6', fontWeight: '600', marginBottom: 4 },
  aiBadge: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#8b5cf6', paddingHorizontal: 10, paddingVertical: 5, borderRadius: 15, gap: 4 },
  aiBadgeText: { fontSize: 11, color: 'white', fontWeight: '600' },
  title: { fontSize: 28, fontWeight: 'bold', color: '#0d6efd' },
  subtitle: { fontSize: 14, color: 'gray', marginTop: 5 },
  myLocationBadge: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#e7f1ff', paddingHorizontal: 10, paddingVertical: 6, borderRadius: 20, maxWidth: 150 },
  myLocationText: { fontSize: 11, color: '#0d6efd', marginLeft: 4 },
  map: { flex: 1 },
  myLocationMarker: { width: 36, height: 36, borderRadius: 18, backgroundColor: '#0d6efd', justifyContent: 'center', alignItems: 'center', borderWidth: 3, borderColor: 'white' },
  callout: { width: 200, padding: 5 },
  calloutTitle: { fontSize: 14, fontWeight: 'bold', marginBottom: 5 },
  calloutLocation: { fontSize: 12, color: 'gray', marginBottom: 8 },
  calloutStatus: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 10, alignSelf: 'flex-start' },
  calloutStatusText: { color: 'white', fontSize: 10, fontWeight: '600' },
  myLocationButton: { position: 'absolute', top: 130, right: 20, backgroundColor: 'white', width: 50, height: 50, borderRadius: 25, justifyContent: 'center', alignItems: 'center', shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 4, elevation: 5 },
  legend: { position: 'absolute', bottom: 30, left: 20, right: 20, backgroundColor: 'white', borderRadius: 12, padding: 15, flexDirection: 'row', justifyContent: 'space-around', shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 4, elevation: 3 },
  legendItem: { flexDirection: 'row', alignItems: 'center' },
  legendDot: { width: 12, height: 12, borderRadius: 6, marginRight: 6 },
  legendText: { fontSize: 12, color: '#333' },
});
