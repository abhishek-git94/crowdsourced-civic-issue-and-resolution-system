import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
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

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const API_URL = 'http://192.168.29.159:5000';

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;
          if (route.name === 'Home') iconName = focused ? 'home' : 'home-outline';
          else if (route.name === 'Report') iconName = focused ? 'add-circle' : 'add-circle-outline';
          else if (route.name === 'Map') iconName = focused ? 'map' : 'map-outline';
          else if (route.name === 'MyIssues') iconName = focused ? 'list' : 'list-outline';
          else if (route.name === 'Forum') iconName = focused ? 'people' : 'people-outline';
          else if (route.name === 'Profile') iconName = focused ? 'person' : 'person-outline';
          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#0d6efd',
        tabBarInactiveTintColor: 'gray',
        headerShown: false,
      })}
    >
      <Tab.Screen name="Home">
        {(props) => <HomeScreen {...props} API_URL={API_URL} />}
      </Tab.Screen>
      <Tab.Screen name="Report">
        {(props) => <ReportScreen {...props} API_URL={API_URL} />}
      </Tab.Screen>
      <Tab.Screen name="Map">
        {(props) => <MapScreen {...props} API_URL={API_URL} />}
      </Tab.Screen>
      <Tab.Screen name="MyIssues">
        {(props) => <MyIssuesScreen {...props} API_URL={API_URL} />}
      </Tab.Screen>
      <Tab.Screen name="Forum">
        {(props) => <ForumScreen {...props} API_URL={API_URL} />}
      </Tab.Screen>
      <Tab.Screen name="Profile">
        {(props) => <ProfileScreen {...props} API_URL={API_URL} />}
      </Tab.Screen>
    </Tab.Navigator>
  );
}

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
        headers: { 'Content-Type': 'application/json' },
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
        headers: { 'Content-Type': 'application/json' },
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

  if (loading) {
    return (
      <React.Fragment>
        <StatusBar style="auto" />
      </React.Fragment>
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
          <Stack.Screen name="IssueDetail" component={IssueDetailScreen} options={{ headerShown: true, title: 'Issue Details' }} />
        </Stack.Navigator>
      )}
    </NavigationContainer>
  );
}