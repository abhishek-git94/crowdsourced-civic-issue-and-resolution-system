import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  Alert, Image, ActivityIndicator, KeyboardAvoidingView,
  Platform, ScrollView
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function LoginScreen({ navigation, onLogin }) {
  const [email, setEmail]           = useState('');
  const [password, setPassword]     = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading]       = useState(false);
  const [emailFocused, setEmailFocused]     = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);

  const handleLogin = async () => {
    if (!email.trim()) { Alert.alert('Missing Email', 'Please enter your email address.'); return; }
    if (!password.trim()) { Alert.alert('Missing Password', 'Please enter your password.'); return; }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) { Alert.alert('Invalid Email', 'Please enter a valid email address.'); return; }

    setLoading(true);
    const result = await onLogin(email.trim().toLowerCase(), password.trim());
    setLoading(false);
    if (!result.success) {
      Alert.alert('Login Failed', result.error || 'Invalid credentials. Please try again.');
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        {/* Hero */}
        <View style={styles.hero}>
          <View style={styles.logoWrapper}>
            <Image source={require('../../assets/logo.png')} style={styles.logo} resizeMode="contain" />
          </View>
          <Text style={styles.title}>Jan Suvidha</Text>
          <Text style={styles.tagline}>Civic Issue Reporting & Resolution</Text>
          <View style={styles.statRow}>
            {[['10K+','Citizens'],['500+','Issues Solved'],['Pan','India']].map(([v,l]) => (
              <View key={l} style={styles.statItem}>
                <Text style={styles.statVal}>{v}</Text>
                <Text style={styles.statLbl}>{l}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Welcome Back</Text>
          <Text style={styles.cardSubtitle}>Sign in to your account</Text>

          {/* Email */}
          <View style={[styles.inputWrap, emailFocused && styles.inputWrapFocused]}>
            <Ionicons name="mail-outline" size={20} color={emailFocused ? '#0d6efd' : '#9ca3af'} />
            <TextInput
              style={styles.input}
              placeholder="Email address"
              placeholderTextColor="#9ca3af"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
              onFocus={() => setEmailFocused(true)}
              onBlur={() => setEmailFocused(false)}
              returnKeyType="next"
            />
          </View>

          {/* Password */}
          <View style={[styles.inputWrap, passwordFocused && styles.inputWrapFocused]}>
            <Ionicons name="lock-closed-outline" size={20} color={passwordFocused ? '#0d6efd' : '#9ca3af'} />
            <TextInput
              style={styles.input}
              placeholder="Password"
              placeholderTextColor="#9ca3af"
              value={password}
              onChangeText={setPassword}
              secureTextEntry={!showPassword}
              onFocus={() => setPasswordFocused(true)}
              onBlur={() => setPasswordFocused(false)}
              returnKeyType="done"
              onSubmitEditing={handleLogin}
            />
            <TouchableOpacity onPress={() => setShowPassword(!showPassword)} activeOpacity={0.7}>
              <Ionicons name={showPassword ? 'eye-off-outline' : 'eye-outline'} size={20} color="#9ca3af" />
            </TouchableOpacity>
          </View>

          {/* Login Button */}
          <TouchableOpacity
            style={[styles.btn, loading && styles.btnDisabled]}
            onPress={handleLogin}
            disabled={loading}
            activeOpacity={0.85}
          >
            {loading
              ? <ActivityIndicator color="white" />
              : <>
                  <Ionicons name="log-in-outline" size={20} color="white" />
                  <Text style={styles.btnText}>Sign In</Text>
                </>
            }
          </TouchableOpacity>

          {/* Register Link */}
          <View style={styles.footer}>
            <Text style={styles.footerText}>New to Jan Suvidha? </Text>
            <TouchableOpacity onPress={() => navigation.navigate('Register')} activeOpacity={0.7}>
              <Text style={styles.link}>Create Account</Text>
            </TouchableOpacity>
          </View>
        </View>

        <Text style={styles.bottomNote}>🔒 Your data is secure & encrypted</Text>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container:     { flex: 1, backgroundColor: '#0d6efd' },
  scroll:        { flexGrow: 1, paddingBottom: 30 },
  hero:          { alignItems: 'center', paddingTop: 60, paddingBottom: 30, paddingHorizontal: 20 },
  logoWrapper:   { width: 90, height: 90, borderRadius: 22, backgroundColor: 'white', justifyContent: 'center', alignItems: 'center', shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 12, elevation: 8, marginBottom: 14 },
  logo:          { width: 65, height: 65 },
  title:         { fontSize: 34, fontWeight: 'bold', color: 'white', letterSpacing: 0.5 },
  tagline:       { fontSize: 14, color: 'rgba(255,255,255,0.8)', marginTop: 6, marginBottom: 20 },
  statRow:       { flexDirection: 'row', gap: 24 },
  statItem:      { alignItems: 'center' },
  statVal:       { fontSize: 18, fontWeight: '800', color: 'white' },
  statLbl:       { fontSize: 11, color: 'rgba(255,255,255,0.75)', marginTop: 2 },
  card:          { backgroundColor: 'white', marginHorizontal: 16, borderRadius: 24, padding: 24, shadowColor: '#000', shadowOpacity: 0.12, shadowRadius: 20, elevation: 8 },
  cardTitle:     { fontSize: 24, fontWeight: '700', color: '#1f2937', marginBottom: 4 },
  cardSubtitle:  { fontSize: 14, color: '#6b7280', marginBottom: 20 },
  inputWrap:     { flexDirection: 'row', alignItems: 'center', backgroundColor: '#f9fafb', borderRadius: 12, paddingHorizontal: 14, paddingVertical: 4, borderWidth: 1.5, borderColor: '#e5e7eb', marginBottom: 14, gap: 10 },
  inputWrapFocused: { borderColor: '#0d6efd', backgroundColor: '#eff6ff' },
  input:         { flex: 1, fontSize: 15, color: '#1f2937', paddingVertical: 12 },
  btn:           { backgroundColor: '#0d6efd', padding: 16, borderRadius: 12, alignItems: 'center', justifyContent: 'center', flexDirection: 'row', gap: 8, marginTop: 6 },
  btnDisabled:   { backgroundColor: '#93c5fd' },
  btnText:       { color: 'white', fontSize: 17, fontWeight: '700' },
  footer:        { flexDirection: 'row', justifyContent: 'center', marginTop: 20 },
  footerText:    { color: '#6b7280', fontSize: 14 },
  link:          { color: '#0d6efd', fontWeight: '700', fontSize: 14 },
  bottomNote:    { textAlign: 'center', color: 'rgba(255,255,255,0.7)', fontSize: 12, marginTop: 20 },
});
