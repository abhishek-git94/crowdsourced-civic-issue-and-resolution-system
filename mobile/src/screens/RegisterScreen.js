import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  Alert, Image, ActivityIndicator, KeyboardAvoidingView,
  Platform, ScrollView
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function RegisterScreen({ navigation, onRegister }) {
  const [name, setName]             = useState('');
  const [email, setEmail]           = useState('');
  const [password, setPassword]     = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword]       = useState(false);
  const [showConfirm, setShowConfirm]         = useState(false);
  const [loading, setLoading]       = useState(false);
  const [focused, setFocused]       = useState('');

  const getPasswordStrength = (p) => {
    if (p.length === 0) return { label: '', color: '#e5e7eb', width: 0 };
    if (p.length < 6)   return { label: 'Weak',   color: '#ef4444', width: 0.33 };
    if (p.length < 10)  return { label: 'Medium', color: '#f59e0b', width: 0.66 };
    return                     { label: 'Strong', color: '#10b981', width: 1.0 };
  };

  const strength = getPasswordStrength(password);

  const handleRegister = async () => {
    if (!name.trim())     { Alert.alert('Error', 'Please enter your full name'); return; }
    if (!email.trim())    { Alert.alert('Error', 'Please enter your email'); return; }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) { Alert.alert('Error', 'Please enter a valid email address'); return; }
    if (password.length < 6) { Alert.alert('Error', 'Password must be at least 6 characters'); return; }
    if (password !== confirmPassword) { Alert.alert('Error', 'Passwords do not match'); return; }

    setLoading(true);
    const result = await onRegister(name.trim(), email.trim().toLowerCase(), password);
    setLoading(false);
    if (!result.success) {
      Alert.alert('Registration Failed', result.error || 'Something went wrong. Please try again.');
    } else {
      Alert.alert('Account Created!', 'Please login with your new credentials.', [
        { text: 'Login Now', onPress: () => navigation.navigate('Login') }
      ]);
    }
  };

  const inputStyle = (field) => [styles.inputWrap, focused === field && styles.inputWrapFocused];

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        {/* Header */}
        <View style={styles.hero}>
          <View style={styles.logoWrapper}>
            <Image source={require('../../assets/logo.png')} style={styles.logo} resizeMode="contain" />
          </View>
          <Text style={styles.title}>Jan Suvidha</Text>
          <Text style={styles.tagline}>Join the movement for a better city</Text>
        </View>

        {/* Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Create Account</Text>
          <Text style={styles.cardSubtitle}>Be a voice for your community</Text>

          {/* Benefits */}
          <View style={styles.benefitsRow}>
            {[['📍','Report Issues'],['🔔','Get Updates'],['⭐','Earn Points']].map(([emoji, label]) => (
              <View key={label} style={styles.benefit}>
                <Text style={styles.benefitEmoji}>{emoji}</Text>
                <Text style={styles.benefitLabel}>{label}</Text>
              </View>
            ))}
          </View>

          {/* Name */}
          <View style={inputStyle('name')}>
            <Ionicons name="person-outline" size={20} color={focused === 'name' ? '#0d6efd' : '#9ca3af'} />
            <TextInput
              style={styles.input}
              placeholder="Full name"
              placeholderTextColor="#9ca3af"
              value={name}
              onChangeText={setName}
              autoCapitalize="words"
              onFocus={() => setFocused('name')}
              onBlur={() => setFocused('')}
              returnKeyType="next"
            />
          </View>

          {/* Email */}
          <View style={inputStyle('email')}>
            <Ionicons name="mail-outline" size={20} color={focused === 'email' ? '#0d6efd' : '#9ca3af'} />
            <TextInput
              style={styles.input}
              placeholder="Email address"
              placeholderTextColor="#9ca3af"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
              onFocus={() => setFocused('email')}
              onBlur={() => setFocused('')}
              returnKeyType="next"
            />
          </View>

          {/* Password */}
          <View style={inputStyle('password')}>
            <Ionicons name="lock-closed-outline" size={20} color={focused === 'password' ? '#0d6efd' : '#9ca3af'} />
            <TextInput
              style={styles.input}
              placeholder="Create password (min 6 chars)"
              placeholderTextColor="#9ca3af"
              value={password}
              onChangeText={setPassword}
              secureTextEntry={!showPassword}
              onFocus={() => setFocused('password')}
              onBlur={() => setFocused('')}
              returnKeyType="next"
            />
            <TouchableOpacity onPress={() => setShowPassword(!showPassword)} activeOpacity={0.7}>
              <Ionicons name={showPassword ? 'eye-off-outline' : 'eye-outline'} size={20} color="#9ca3af" />
            </TouchableOpacity>
          </View>

          {/* Password strength */}
          {password.length > 0 && (
            <View style={styles.strengthRow}>
              <View style={styles.strengthBar}>
                <View style={[styles.strengthFill, { width: `${strength.width * 100}%`, backgroundColor: strength.color }]} />
              </View>
              <Text style={[styles.strengthLabel, { color: strength.color }]}>{strength.label}</Text>
            </View>
          )}

          {/* Confirm Password */}
          <View style={inputStyle('confirm')}>
            <Ionicons name="shield-checkmark-outline" size={20} color={focused === 'confirm' ? '#0d6efd' : '#9ca3af'} />
            <TextInput
              style={styles.input}
              placeholder="Confirm password"
              placeholderTextColor="#9ca3af"
              value={confirmPassword}
              onChangeText={setConfirmPassword}
              secureTextEntry={!showConfirm}
              onFocus={() => setFocused('confirm')}
              onBlur={() => setFocused('')}
              returnKeyType="done"
              onSubmitEditing={handleRegister}
            />
            <TouchableOpacity onPress={() => setShowConfirm(!showConfirm)} activeOpacity={0.7}>
              <Ionicons name={showConfirm ? 'eye-off-outline' : 'eye-outline'} size={20} color="#9ca3af" />
            </TouchableOpacity>
            {confirmPassword.length > 0 && (
              <Ionicons
                name={password === confirmPassword ? 'checkmark-circle' : 'close-circle'}
                size={20}
                color={password === confirmPassword ? '#10b981' : '#ef4444'}
              />
            )}
          </View>

          {/* Register Button */}
          <TouchableOpacity
            style={[styles.btn, loading && styles.btnDisabled]}
            onPress={handleRegister}
            disabled={loading}
            activeOpacity={0.85}
          >
            {loading
              ? <ActivityIndicator color="white" />
              : <>
                  <Ionicons name="person-add-outline" size={20} color="white" />
                  <Text style={styles.btnText}>Create Account</Text>
                </>
            }
          </TouchableOpacity>

          <View style={styles.footer}>
            <Text style={styles.footerText}>Already have an account? </Text>
            <TouchableOpacity onPress={() => navigation.navigate('Login')} activeOpacity={0.7}>
              <Text style={styles.link}>Sign In</Text>
            </TouchableOpacity>
          </View>
        </View>

        <Text style={styles.bottomNote}>By registering, you agree to report genuine civic issues</Text>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container:      { flex: 1, backgroundColor: '#6366f1' },
  scroll:         { flexGrow: 1, paddingBottom: 30 },
  hero:           { alignItems: 'center', paddingTop: 50, paddingBottom: 24, paddingHorizontal: 20 },
  logoWrapper:    { width: 80, height: 80, borderRadius: 20, backgroundColor: 'white', justifyContent: 'center', alignItems: 'center', shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 10, elevation: 8, marginBottom: 12 },
  logo:           { width: 55, height: 55 },
  title:          { fontSize: 30, fontWeight: 'bold', color: 'white' },
  tagline:        { fontSize: 13, color: 'rgba(255,255,255,0.8)', marginTop: 5 },
  card:           { backgroundColor: 'white', marginHorizontal: 16, borderRadius: 24, padding: 24, shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 20, elevation: 8 },
  cardTitle:      { fontSize: 22, fontWeight: '700', color: '#1f2937', marginBottom: 4 },
  cardSubtitle:   { fontSize: 14, color: '#6b7280', marginBottom: 16 },
  benefitsRow:    { flexDirection: 'row', justifyContent: 'space-around', backgroundColor: '#f8faff', borderRadius: 12, paddingVertical: 12, marginBottom: 18 },
  benefit:        { alignItems: 'center' },
  benefitEmoji:   { fontSize: 20 },
  benefitLabel:   { fontSize: 11, color: '#6b7280', marginTop: 4, fontWeight: '500' },
  inputWrap:      { flexDirection: 'row', alignItems: 'center', backgroundColor: '#f9fafb', borderRadius: 12, paddingHorizontal: 14, paddingVertical: 4, borderWidth: 1.5, borderColor: '#e5e7eb', marginBottom: 12, gap: 10 },
  inputWrapFocused: { borderColor: '#6366f1', backgroundColor: '#eef2ff' },
  input:          { flex: 1, fontSize: 15, color: '#1f2937', paddingVertical: 12 },
  strengthRow:    { flexDirection: 'row', alignItems: 'center', marginBottom: 12, gap: 10 },
  strengthBar:    { flex: 1, height: 4, backgroundColor: '#e5e7eb', borderRadius: 2, overflow: 'hidden' },
  strengthFill:   { height: '100%', borderRadius: 2 },
  strengthLabel:  { fontSize: 12, fontWeight: '600', minWidth: 50 },
  btn:            { backgroundColor: '#6366f1', padding: 16, borderRadius: 12, alignItems: 'center', justifyContent: 'center', flexDirection: 'row', gap: 8, marginTop: 6 },
  btnDisabled:    { backgroundColor: '#a5b4fc' },
  btnText:        { color: 'white', fontSize: 17, fontWeight: '700' },
  footer:         { flexDirection: 'row', justifyContent: 'center', marginTop: 20 },
  footerText:     { color: '#6b7280', fontSize: 14 },
  link:           { color: '#6366f1', fontWeight: '700', fontSize: 14 },
  bottomNote:     { textAlign: 'center', color: 'rgba(255,255,255,0.65)', fontSize: 12, marginTop: 18, paddingHorizontal: 30 },
});
