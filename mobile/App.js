import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { View, Text, Image, ActivityIndicator } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import HomeScreen from './src/screens/HomeScreen';
import ReportScreen from './src/screens/ReportScreen';
import MapScreen from './src/screens/MapScreen';
import MyIssuesScreen from './src/screens/MyIssuesScreen';
import IssueDetailScreen from './src/screens/IssueDetailScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import ForumScreen from './src/screens/ForumScreen';
import NotificationsScreen from './src/screens/NotificationsScreen';
import SettingsScreen from './src/screens/SettingsScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// Use your computer's local IP address for same WiFi connection
const API_URL = 'http://192.168.29.159:5000';

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkUser();
  }, []);

  const checkUser = async () => {
    try {
      const userData = await AsyncStorage.getItem('user');
      if (userData) {
        setUser(JSON.parse(userData));
      }
    } catch (e) {
      console.log(e);
    }
    setLoading(false);
  };

  const login = async (email, password) => {
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Bypass-Tunnel-Reminder': 'true'
        },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      if (response.ok) {
        await AsyncStorage.setItem('user', JSON.stringify(data.user));
        setUser(data.user);
        return { success: true };
      }
      return { success: false, error: data.message };
    } catch (e) {
      return { success: false, error: 'Cannot connect to server' };
    }
  };

  const register = async (name, email, password) => {
    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Bypass-Tunnel-Reminder': 'true'
        },
        body: JSON.stringify({ name, email, password }),
      });
      const data = await response.json();
      if (response.ok) {
        return { success: true };
      }
      return { success: false, error: data.message };
    } catch (e) {
      return { success: false, error: 'Cannot connect to server' };
    }
  };

  const logout = async () => {
    await AsyncStorage.removeItem('user');
    setUser(null);
  };

  /** Called from ProfileScreen after a successful profile update */
  const updateUser = async (updatedUser) => {
    const merged = { ...user, ...updatedUser };
    await AsyncStorage.setItem('user', JSON.stringify(merged));
    setUser(merged);
  };

  function MainTabs() {
    return (
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused, color, size }) => {
            let iconName;
            if (route.name === 'Home')               iconName = focused ? 'home'               : 'home-outline';
            else if (route.name === 'Report')        iconName = focused ? 'add-circle'         : 'add-circle-outline';
            else if (route.name === 'Map')           iconName = focused ? 'map'                : 'map-outline';
            else if (route.name === 'Notifications') iconName = focused ? 'notifications'      : 'notifications-outline';
            else if (route.name === 'MyIssues')      iconName = focused ? 'list'               : 'list-outline';
            else if (route.name === 'Forum')         iconName = focused ? 'people'             : 'people-outline';
            else if (route.name === 'Profile')       iconName = focused ? 'person'             : 'person-outline';
            return <Ionicons name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: '#0d6efd',
          tabBarInactiveTintColor: '#9ca3af',
          headerShown: false,
          tabBarStyle: {
            backgroundColor: 'white',
            borderTopWidth: 1,
            borderTopColor: '#f3f4f6',
            height: 60,
            paddingBottom: 8,
            paddingTop: 6,
            elevation: 12,
            shadowColor: '#000',
            shadowOpacity: 0.08,
            shadowRadius: 8,
          },
          tabBarLabelStyle: { fontSize: 10, fontWeight: '600' },
        })}
      >
        <Tab.Screen name="Home">
          {(props) => <HomeScreen {...props} API_URL={API_URL} user={user} />}
        </Tab.Screen>
        <Tab.Screen name="Report">
          {(props) => <ReportScreen {...props} API_URL={API_URL} user={user} />}
        </Tab.Screen>
        <Tab.Screen name="Map">
          {(props) => <MapScreen {...props} API_URL={API_URL} user={user} />}
        </Tab.Screen>
        <Tab.Screen
          name="Notifications"
          options={{
            tabBarBadge: undefined, // set to number to show badge
          }}
        >
          {(props) => <NotificationsScreen {...props} API_URL={API_URL} user={user} />}
        </Tab.Screen>
        <Tab.Screen name="MyIssues" options={{ title: 'My Issues' }}>
          {(props) => <MyIssuesScreen {...props} API_URL={API_URL} user={user} />}
        </Tab.Screen>
        <Tab.Screen name="Forum">
          {(props) => <ForumScreen {...props} API_URL={API_URL} user={user} />}
        </Tab.Screen>
        <Tab.Screen name="Profile">
          {(props) => (
            <ProfileScreen
              {...props}
              API_URL={API_URL}
              user={user}
              onLogout={logout}
              onUpdateUser={updateUser}
            />
          )}
        </Tab.Screen>
      </Tab.Navigator>
    );
  }

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0d6efd' }}>
        <StatusBar style="light" />
        <View style={{ alignItems: 'center' }}>
          <View style={{ width: 90, height: 90, borderRadius: 22, backgroundColor: 'white', justifyContent: 'center', alignItems: 'center', marginBottom: 20, elevation: 10 }}>
            <Image
              source={require('./assets/logo.png')}
              style={{ width: 65, height: 65 }}
              resizeMode="contain"
            />
          </View>
          <Text style={{ fontSize: 36, fontWeight: 'bold', color: 'white', letterSpacing: 0.5 }}>Jan Suvidha</Text>
          <Text style={{ color: 'rgba(255,255,255,0.8)', marginTop: 8, fontSize: 14 }}>Civic Issue Reporting & Resolution</Text>
          <ActivityIndicator color="rgba(255,255,255,0.8)" style={{ marginTop: 30 }} size="large" />
          <Text style={{ color: 'rgba(255,255,255,0.6)', marginTop: 12, fontSize: 12 }}>Loading...</Text>
        </View>
      </View>
    );
  }

  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      {!user ? (
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          <Stack.Screen name="Login">
            {(props) => <LoginScreen {...props} onLogin={login} />}
          </Stack.Screen>
          <Stack.Screen name="Register">
            {(props) => <RegisterScreen {...props} onRegister={register} />}
          </Stack.Screen>
        </Stack.Navigator>
      ) : (
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          <Stack.Screen name="MainTabs" component={MainTabs} />
          <Stack.Screen name="IssueDetail" options={{ headerShown: true, title: 'Issue Details' }}>
            {(props) => <IssueDetailScreen {...props} API_URL={API_URL} user={user} />}
          </Stack.Screen>
          <Stack.Screen name="Settings" options={{ headerShown: true, title: 'Settings' }}>
            {(props) => <SettingsScreen {...props} API_URL={API_URL} user={user} onLogout={logout} />}
          </Stack.Screen>
        </Stack.Navigator>
      )}
    </NavigationContainer>
  );
}
