# Mewayz v2 - Technical Implementation Guide

## Overview
This document provides detailed technical specifications for implementing the screens and pages defined in the Screen Documentation, including component hierarchies, state management, API integration patterns, and platform-specific considerations.

---

## 🏗️ **COMPONENT ARCHITECTURE**

### **React Component Structure**
```
src/
├── components/
│   ├── common/
│   │   ├── Layout/
│   │   ├── Navigation/
│   │   ├── Forms/
│   │   ├── Cards/
│   │   ├── Modals/
│   │   └── Loading/
│   ├── auth/
│   ├── dashboard/
│   ├── booking/
│   ├── escrow/
│   ├── website/
│   ├── templates/
│   ├── linkinbio/
│   ├── courses/
│   ├── marketplace/
│   ├── financial/
│   ├── social/
│   ├── crm/
│   ├── email/
│   ├── ai/
│   ├── pwa/
│   ├── visual/
│   ├── mobile/
│   └── workflow/
├── screens/
├── hooks/
├── services/
├── utils/
└── styles/
```

### **React Native Component Structure**
```
src/
├── components/
│   ├── common/
│   ├── navigation/
│   └── [feature-specific]/
├── screens/
├── hooks/
├── services/
├── utils/
└── styles/
```

---

## 🔧 **STATE MANAGEMENT**

### **Context Structure**
```javascript
// Global Contexts
- AuthContext
- UserContext
- WorkspaceContext
- ThemeContext
- NotificationContext

// Feature Contexts
- BookingContext
- EscrowContext
- WebsiteContext
- SocialContext
- CRMContext
- FinancialContext
```

### **State Management Patterns**
```javascript
// useAuth Hook
const useAuth = () => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const login = async (credentials) => {
    try {
      const response = await authService.login(credentials);
      setUser(response.user);
      setToken(response.access_token);
      localStorage.setItem('token', response.access_token);
    } catch (error) {
      throw error;
    }
  };
  
  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
  };
  
  return { user, token, login, logout, loading };
};

// useAPI Hook
const useAPI = (endpoint, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await apiService.get(endpoint, options);
      setData(response.data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchData();
  }, [endpoint]);
  
  return { data, loading, error, refetch: fetchData };
};
```

---

## 🌐 **API INTEGRATION PATTERNS**

### **Service Layer Structure**
```javascript
// Base API Service
class APIService {
  constructor() {
    this.baseURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }
  
  setAuthToken(token) {
    this.defaultHeaders.Authorization = `Bearer ${token}`;
  }
  
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: { ...this.defaultHeaders, ...options.headers },
      ...options,
    };
    
    try {
      const response = await fetch(url, config);
      if (!response.ok) throw new Error(response.statusText);
      return await response.json();
    } catch (error) {
      throw error;
    }
  }
  
  get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`${endpoint}${queryString ? `?${queryString}` : ''}`);
  }
  
  post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
  
  put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }
  
  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

// Feature-specific Services
class BookingService extends APIService {
  async getBookings(params = {}) {
    return this.get('/api/booking/', params);
  }
  
  async createBooking(bookingData) {
    return this.post('/api/booking/', bookingData);
  }
  
  async updateBooking(id, bookingData) {
    return this.put(`/api/booking/${id}`, bookingData);
  }
  
  async deleteBooking(id) {
    return this.delete(`/api/booking/${id}`);
  }
  
  async getBookingStats() {
    return this.get('/api/booking/stats');
  }
}

// PWA Service
class PWAService extends APIService {
  async createConfig(configData) {
    return this.post('/api/pwa/configs', configData);
  }
  
  async getConfig(configId) {
    return this.get(`/api/pwa/configs/${configId}`);
  }
  
  async updateConfig(configId, configData) {
    return this.put(`/api/pwa/configs/${configId}`, configData);
  }
  
  async generateManifest(configId) {
    return this.post(`/api/pwa/manifest/generate/${configId}`);
  }
  
  async trackInstallation(installData) {
    return this.post('/api/pwa/install/track', installData);
  }
}

// Visual Builder Service
class VisualBuilderService extends APIService {
  async createProject(projectData) {
    return this.post('/api/visual-builder/projects', projectData);
  }
  
  async getProject(projectId) {
    return this.get(`/api/visual-builder/projects/${projectId}`);
  }
  
  async updateProject(projectId, projectData) {
    return this.put(`/api/visual-builder/projects/${projectId}`, projectData);
  }
  
  async publishProject(projectId) {
    return this.post(`/api/visual-builder/projects/${projectId}/publish`);
  }
  
  async getComponentLibrary() {
    return this.get('/api/visual-builder/components');
  }
}
```

---

## 📱 **SCREEN IMPLEMENTATIONS**

### **Authentication Flow**
```javascript
// Login Screen Component
const LoginScreen = () => {
  const [credentials, setCredentials] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { login } = useAuth();
  const navigation = useNavigation();
  
  const handleLogin = async () => {
    setLoading(true);
    setError(null);
    
    try {
      await login(credentials);
      navigation.navigate('Dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.form}>
        <Text style={styles.title}>Welcome Back</Text>
        
        <TextInput
          style={styles.input}
          placeholder="Email"
          value={credentials.email}
          onChangeText={(text) => setCredentials({...credentials, email: text})}
          keyboardType="email-address"
          autoCapitalize="none"
        />
        
        <TextInput
          style={styles.input}
          placeholder="Password"
          value={credentials.password}
          onChangeText={(text) => setCredentials({...credentials, password: text})}
          secureTextEntry
        />
        
        {error && <Text style={styles.error}>{error}</Text>}
        
        <TouchableOpacity 
          style={styles.loginButton} 
          onPress={handleLogin}
          disabled={loading}
        >
          <Text style={styles.loginButtonText}>
            {loading ? 'Logging in...' : 'Login'}
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity onPress={() => navigation.navigate('Register')}>
          <Text style={styles.linkText}>Don't have an account? Sign up</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};
```

### **Dashboard Implementation**
```javascript
// Dashboard Screen Component
const DashboardScreen = () => {
  const { user } = useAuth();
  const { data: dashboardData, loading, error } = useAPI('/api/dashboard/');
  const [refreshing, setRefreshing] = useState(false);
  
  const onRefresh = async () => {
    setRefreshing(true);
    // Refresh data logic
    setRefreshing(false);
  };
  
  if (loading) return <LoadingScreen />;
  if (error) return <ErrorScreen error={error} />;
  
  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <Header>
        <Text style={styles.greeting}>Good morning, {user.name}!</Text>
        <NotificationBell />
      </Header>
      
      <StatsGrid stats={dashboardData.stats} />
      
      <RecentActivity activities={dashboardData.activities} />
      
      <QuickActions />
      
      <RevenueChart data={dashboardData.revenue} />
    </ScrollView>
  );
};

// Stats Grid Component
const StatsGrid = ({ stats }) => {
  return (
    <View style={styles.statsGrid}>
      {stats.map((stat, index) => (
        <StatCard key={index} stat={stat} />
      ))}
    </View>
  );
};

// Stat Card Component
const StatCard = ({ stat }) => {
  return (
    <View style={styles.statCard}>
      <Text style={styles.statValue}>{stat.value}</Text>
      <Text style={styles.statLabel}>{stat.label}</Text>
      <Text style={[styles.statChange, stat.change > 0 ? styles.positive : styles.negative]}>
        {stat.change > 0 ? '+' : ''}{stat.change}%
      </Text>
    </View>
  );
};
```

### **Booking System Implementation**
```javascript
// Booking Calendar Component
const BookingCalendar = () => {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [viewMode, setViewMode] = useState('month');
  const { data: bookings, loading } = useAPI('/api/booking/', {
    date: selectedDate.toISOString(),
    view: viewMode
  });
  
  const renderBookingCard = (booking) => (
    <TouchableOpacity 
      key={booking.id}
      style={styles.bookingCard}
      onPress={() => navigation.navigate('BookingDetails', { id: booking.id })}
    >
      <Text style={styles.bookingTime}>{booking.time}</Text>
      <Text style={styles.bookingClient}>{booking.client_name}</Text>
      <Text style={styles.bookingService}>{booking.service}</Text>
      <StatusBadge status={booking.status} />
    </TouchableOpacity>
  );
  
  return (
    <View style={styles.container}>
      <CalendarHeader 
        selectedDate={selectedDate}
        onDateChange={setSelectedDate}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
      />
      
      <Calendar
        selectedDate={selectedDate}
        onDateSelect={setSelectedDate}
        bookings={bookings}
        viewMode={viewMode}
      />
      
      <BookingsList bookings={bookings} renderItem={renderBookingCard} />
      
      <FloatingActionButton 
        onPress={() => navigation.navigate('CreateBooking')}
        icon="plus"
      />
    </View>
  );
};

// Create Booking Form
const CreateBookingScreen = () => {
  const [bookingData, setBookingData] = useState({
    client_id: '',
    service: '',
    date: '',
    time: '',
    duration: 60,
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const bookingService = new BookingService();
  
  const handleSubmit = async () => {
    setLoading(true);
    try {
      await bookingService.createBooking(bookingData);
      navigation.goBack();
    } catch (error) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <ScrollView style={styles.container}>
      <Form>
        <ClientSelector
          value={bookingData.client_id}
          onSelect={(client_id) => setBookingData({...bookingData, client_id})}
        />
        
        <ServiceSelector
          value={bookingData.service}
          onSelect={(service) => setBookingData({...bookingData, service})}
        />
        
        <DateTimePicker
          date={bookingData.date}
          time={bookingData.time}
          onDateChange={(date) => setBookingData({...bookingData, date})}
          onTimeChange={(time) => setBookingData({...bookingData, time})}
        />
        
        <DurationSelector
          value={bookingData.duration}
          onChange={(duration) => setBookingData({...bookingData, duration})}
        />
        
        <TextInput
          style={styles.notesInput}
          placeholder="Notes"
          value={bookingData.notes}
          onChangeText={(notes) => setBookingData({...bookingData, notes})}
          multiline
        />
        
        <Button 
          title="Create Booking"
          onPress={handleSubmit}
          loading={loading}
        />
      </Form>
    </ScrollView>
  );
};
```

### **PWA Management Implementation**
```javascript
// PWA Configuration Screen
const PWAConfigScreen = () => {
  const [config, setConfig] = useState({
    app_name: '',
    short_name: '',
    description: '',
    theme_color: '#007AFF',
    background_color: '#ffffff',
    display: 'standalone',
    orientation: 'portrait-primary'
  });
  const [loading, setLoading] = useState(false);
  const pwaService = new PWAService();
  
  const handleSave = async () => {
    setLoading(true);
    try {
      const response = await pwaService.createConfig(config);
      Alert.alert('Success', 'PWA configuration saved successfully');
    } catch (error) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <ScrollView style={styles.container}>
      <Form>
        <TextInput
          style={styles.input}
          placeholder="App Name"
          value={config.app_name}
          onChangeText={(text) => setConfig({...config, app_name: text})}
        />
        
        <TextInput
          style={styles.input}
          placeholder="Short Name"
          value={config.short_name}
          onChangeText={(text) => setConfig({...config, short_name: text})}
        />
        
        <TextInput
          style={styles.input}
          placeholder="Description"
          value={config.description}
          onChangeText={(text) => setConfig({...config, description: text})}
          multiline
        />
        
        <ColorPicker
          label="Theme Color"
          value={config.theme_color}
          onSelect={(color) => setConfig({...config, theme_color: color})}
        />
        
        <ColorPicker
          label="Background Color"
          value={config.background_color}
          onSelect={(color) => setConfig({...config, background_color: color})}
        />
        
        <Picker
          selectedValue={config.display}
          onValueChange={(value) => setConfig({...config, display: value})}
        >
          <Picker.Item label="Standalone" value="standalone" />
          <Picker.Item label="Fullscreen" value="fullscreen" />
          <Picker.Item label="Minimal UI" value="minimal-ui" />
          <Picker.Item label="Browser" value="browser" />
        </Picker>
        
        <IconUploader
          onUpload={(icons) => setConfig({...config, icons})}
        />
        
        <Button 
          title="Save Configuration"
          onPress={handleSave}
          loading={loading}
        />
      </Form>
    </ScrollView>
  );
};
```

### **Visual Builder Implementation**
```javascript
// Visual Builder Component
const VisualBuilderScreen = () => {
  const { projectId } = useRoute().params;
  const [project, setProject] = useState(null);
  const [selectedComponent, setSelectedComponent] = useState(null);
  const [showComponentLibrary, setShowComponentLibrary] = useState(false);
  const visualBuilderService = new VisualBuilderService();
  
  useEffect(() => {
    loadProject();
  }, [projectId]);
  
  const loadProject = async () => {
    try {
      const response = await visualBuilderService.getProject(projectId);
      setProject(response.data);
    } catch (error) {
      Alert.alert('Error', error.message);
    }
  };
  
  const handleComponentDrop = (component, position) => {
    const updatedProject = {
      ...project,
      canvas_data: {
        ...project.canvas_data,
        components: [...project.canvas_data.components, {
          ...component,
          id: generateUniqueId(),
          position
        }]
      }
    };
    setProject(updatedProject);
    saveProject(updatedProject);
  };
  
  const saveProject = async (projectData) => {
    try {
      await visualBuilderService.updateProject(projectId, projectData);
    } catch (error) {
      Alert.alert('Error', error.message);
    }
  };
  
  return (
    <View style={styles.container}>
      <Toolbar>
        <ToolbarButton 
          icon="components"
          onPress={() => setShowComponentLibrary(!showComponentLibrary)}
        />
        <ToolbarButton 
          icon="preview"
          onPress={() => navigation.navigate('Preview', { project })}
        />
        <ToolbarButton 
          icon="save"
          onPress={() => saveProject(project)}
        />
        <ToolbarButton 
          icon="publish"
          onPress={() => publishProject()}
        />
      </Toolbar>
      
      <View style={styles.editorContainer}>
        {showComponentLibrary && (
          <ComponentLibrary
            onComponentSelect={handleComponentDrop}
            onClose={() => setShowComponentLibrary(false)}
          />
        )}
        
        <Canvas
          project={project}
          onComponentSelect={setSelectedComponent}
          onComponentMove={handleComponentMove}
          onComponentResize={handleComponentResize}
        />
        
        {selectedComponent && (
          <PropertiesPanel
            component={selectedComponent}
            onPropertyChange={handlePropertyChange}
          />
        )}
      </View>
    </View>
  );
};

// Component Library
const ComponentLibrary = ({ onComponentSelect, onClose }) => {
  const { data: components } = useAPI('/api/visual-builder/components');
  const [selectedCategory, setSelectedCategory] = useState('layout');
  
  const categories = ['layout', 'content', 'forms', 'media'];
  
  return (
    <Modal visible={true} animationType="slide">
      <View style={styles.libraryContainer}>
        <View style={styles.libraryHeader}>
          <Text style={styles.libraryTitle}>Component Library</Text>
          <TouchableOpacity onPress={onClose}>
            <Text style={styles.closeButton}>×</Text>
          </TouchableOpacity>
        </View>
        
        <View style={styles.categoryTabs}>
          {categories.map(category => (
            <TouchableOpacity
              key={category}
              style={[
                styles.categoryTab,
                selectedCategory === category && styles.activeTab
              ]}
              onPress={() => setSelectedCategory(category)}
            >
              <Text style={styles.categoryText}>{category}</Text>
            </TouchableOpacity>
          ))}
        </View>
        
        <ScrollView style={styles.componentGrid}>
          {components?.[selectedCategory]?.map(component => (
            <TouchableOpacity
              key={component.id}
              style={styles.componentCard}
              onPress={() => onComponentSelect(component)}
            >
              <Text style={styles.componentIcon}>{component.icon}</Text>
              <Text style={styles.componentName}>{component.name}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>
    </Modal>
  );
};
```

---

## 🎨 **STYLING SYSTEM**

### **Theme Configuration**
```javascript
// Theme System
const lightTheme = {
  colors: {
    primary: '#007AFF',
    secondary: '#5856D6',
    background: '#FFFFFF',
    surface: '#F2F2F7',
    text: '#000000',
    textSecondary: '#666666',
    border: '#E5E5E5',
    error: '#FF3B30',
    success: '#34C759',
    warning: '#FF9500'
  },
  fonts: {
    regular: 'System',
    medium: 'System-Medium',
    bold: 'System-Bold'
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32
  },
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 16,
    xl: 24
  }
};

const darkTheme = {
  ...lightTheme,
  colors: {
    ...lightTheme.colors,
    background: '#000000',
    surface: '#1C1C1E',
    text: '#FFFFFF',
    textSecondary: '#8E8E93',
    border: '#38383A'
  }
};
```

### **Responsive Design System**
```javascript
// Responsive Utilities
const breakpoints = {
  mobile: 0,
  tablet: 768,
  desktop: 1024,
  large: 1440
};

const useResponsive = () => {
  const [windowWidth, setWindowWidth] = useState(Dimensions.get('window').width);
  
  useEffect(() => {
    const subscription = Dimensions.addEventListener('change', ({window}) => {
      setWindowWidth(window.width);
    });
    
    return () => subscription?.remove();
  }, []);
  
  return {
    isMobile: windowWidth < breakpoints.tablet,
    isTablet: windowWidth >= breakpoints.tablet && windowWidth < breakpoints.desktop,
    isDesktop: windowWidth >= breakpoints.desktop,
    windowWidth
  };
};

// Responsive Styles
const createResponsiveStyles = (theme) => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
    padding: theme.spacing.md
  },
  // Mobile styles
  ...(Platform.OS === 'ios' || Platform.OS === 'android' ? {
    mobileContainer: {
      paddingHorizontal: theme.spacing.sm
    }
  } : {}),
  // Web styles
  ...(Platform.OS === 'web' ? {
    webContainer: {
      maxWidth: 1200,
      marginHorizontal: 'auto'
    }
  } : {})
});
```

---

## 🔄 **REAL-TIME FEATURES**

### **WebSocket Integration**
```javascript
// WebSocket Service
class WebSocketService {
  constructor() {
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }
  
  connect(token) {
    this.socket = new WebSocket(`ws://localhost:8001/ws?token=${token}`);
    
    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };
    
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
    
    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.reconnect();
    };
    
    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }
  
  handleMessage(data) {
    // Handle different message types
    switch (data.type) {
      case 'booking_update':
        EventBus.emit('booking_updated', data.payload);
        break;
      case 'notification':
        EventBus.emit('notification', data.payload);
        break;
      case 'user_activity':
        EventBus.emit('user_activity', data.payload);
        break;
    }
  }
  
  send(message) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    }
  }
  
  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        this.connect();
      }, 1000 * Math.pow(2, this.reconnectAttempts));
    }
  }
}

// Real-time Hook
const useRealTime = (eventType, handler) => {
  useEffect(() => {
    EventBus.on(eventType, handler);
    return () => EventBus.off(eventType, handler);
  }, [eventType, handler]);
};
```

### **Push Notifications**
```javascript
// Push Notification Service
class PushNotificationService {
  async requestPermission() {
    if (Platform.OS === 'ios') {
      const permission = await messaging().requestPermission();
      return permission === messaging.AuthorizationStatus.AUTHORIZED;
    }
    return true;
  }
  
  async getToken() {
    const token = await messaging().getToken();
    return token;
  }
  
  async registerToken(token) {
    const nativeMobileService = new NativeMobileService();
    await nativeMobileService.registerPushToken({
      push_token: token,
      platform: Platform.OS,
      device_id: await DeviceInfo.getUniqueId(),
      app_version: await DeviceInfo.getVersion()
    });
  }
  
  setupNotificationHandlers() {
    messaging().onMessage(async (remoteMessage) => {
      // Handle foreground notifications
      this.showLocalNotification(remoteMessage);
    });
    
    messaging().onNotificationOpenedApp((remoteMessage) => {
      // Handle notification tap when app is in background
      this.handleNotificationTap(remoteMessage);
    });
    
    messaging().getInitialNotification().then((remoteMessage) => {
      // Handle notification tap when app is closed
      if (remoteMessage) {
        this.handleNotificationTap(remoteMessage);
      }
    });
  }
}
```

---

## 📊 **PERFORMANCE OPTIMIZATION**

### **Lazy Loading**
```javascript
// Lazy Loading Components
const LazyDashboard = React.lazy(() => import('./screens/Dashboard'));
const LazyBookings = React.lazy(() => import('./screens/Bookings'));
const LazyVisualBuilder = React.lazy(() => import('./screens/VisualBuilder'));

// Lazy Loading with Suspense
const App = () => (
  <Router>
    <Suspense fallback={<LoadingScreen />}>
      <Routes>
        <Route path="/dashboard" element={<LazyDashboard />} />
        <Route path="/bookings" element={<LazyBookings />} />
        <Route path="/builder" element={<LazyVisualBuilder />} />
      </Routes>
    </Suspense>
  </Router>
);
```

### **Image Optimization**
```javascript
// Optimized Image Component
const OptimizedImage = ({ source, style, ...props }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  
  const handleLoad = () => setLoading(false);
  const handleError = () => {
    setLoading(false);
    setError(true);
  };
  
  return (
    <View style={[style, styles.imageContainer]}>
      {loading && <ActivityIndicator style={styles.loader} />}
      {error ? (
        <View style={styles.errorContainer}>
          <Text>Failed to load image</Text>
        </View>
      ) : (
        <Image
          source={source}
          style={[style, { opacity: loading ? 0 : 1 }]}
          onLoad={handleLoad}
          onError={handleError}
          {...props}
        />
      )}
    </View>
  );
};
```

### **Data Caching**
```javascript
// Cache Service
class CacheService {
  constructor() {
    this.cache = new Map();
    this.expirationTimes = new Map();
  }
  
  set(key, value, ttl = 300000) { // 5 minutes default
    this.cache.set(key, value);
    this.expirationTimes.set(key, Date.now() + ttl);
  }
  
  get(key) {
    const expiration = this.expirationTimes.get(key);
    if (expiration && Date.now() > expiration) {
      this.cache.delete(key);
      this.expirationTimes.delete(key);
      return null;
    }
    return this.cache.get(key);
  }
  
  clear() {
    this.cache.clear();
    this.expirationTimes.clear();
  }
}

// Cached API Hook
const useCachedAPI = (endpoint, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const cache = new CacheService();
  
  const fetchData = async (useCache = true) => {
    if (useCache) {
      const cachedData = cache.get(endpoint);
      if (cachedData) {
        setData(cachedData);
        return;
      }
    }
    
    setLoading(true);
    try {
      const response = await apiService.get(endpoint, options);
      setData(response.data);
      cache.set(endpoint, response.data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchData();
  }, [endpoint]);
  
  return { data, loading, error, refetch: () => fetchData(false) };
};
```

---

## 🔐 **SECURITY IMPLEMENTATION**

### **Authentication Guard**
```javascript
// Authentication HOC
const withAuth = (WrappedComponent) => {
  return (props) => {
    const { user, token } = useAuth();
    const navigation = useNavigation();
    
    useEffect(() => {
      if (!user || !token) {
        navigation.navigate('Login');
      }
    }, [user, token]);
    
    if (!user || !token) {
      return <LoadingScreen />;
    }
    
    return <WrappedComponent {...props} />;
  };
};

// Protected Route Component
const ProtectedRoute = ({ children, requiredRole }) => {
  const { user } = useAuth();
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  if (requiredRole && user.role !== requiredRole) {
    return <AccessDenied />;
  }
  
  return children;
};
```

### **Permission System**
```javascript
// Permission Hook
const usePermissions = () => {
  const { user } = useAuth();
  
  const hasPermission = (permission) => {
    return user?.permissions?.includes(permission) || false;
  };
  
  const hasRole = (role) => {
    return user?.role === role || false;
  };
  
  const canAccess = (resource, action) => {
    return hasPermission(`${resource}:${action}`);
  };
  
  return { hasPermission, hasRole, canAccess };
};

// Permission-based Component
const PermissionGate = ({ permission, children, fallback = null }) => {
  const { hasPermission } = usePermissions();
  
  if (!hasPermission(permission)) {
    return fallback;
  }
  
  return children;
};
```

---

## 🧪 **TESTING STRATEGIES**

### **Unit Testing**
```javascript
// Component Testing
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { LoginScreen } from '../screens/Login';

describe('LoginScreen', () => {
  it('should submit login form with correct credentials', async () => {
    const mockLogin = jest.fn();
    const { getByPlaceholderText, getByText } = render(
      <LoginScreen onLogin={mockLogin} />
    );
    
    fireEvent.changeText(getByPlaceholderText('Email'), 'test@example.com');
    fireEvent.changeText(getByPlaceholderText('Password'), 'password123');
    fireEvent.press(getByText('Login'));
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123'
      });
    });
  });
});
```

### **Integration Testing**
```javascript
// API Integration Testing
describe('BookingService', () => {
  let bookingService;
  
  beforeEach(() => {
    bookingService = new BookingService();
  });
  
  it('should create booking successfully', async () => {
    const bookingData = {
      client_id: 'test-client',
      service: 'Test Service',
      date: '2024-01-01',
      time: '10:00'
    };
    
    const response = await bookingService.createBooking(bookingData);
    
    expect(response.success).toBe(true);
    expect(response.data.id).toBeDefined();
  });
});
```

---

## 🚀 **DEPLOYMENT CONSIDERATIONS**

### **Environment Configuration**
```javascript
// Environment Variables
const config = {
  API_URL: process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001',
  WS_URL: process.env.REACT_APP_WS_URL || 'ws://localhost:8001',
  SENTRY_DSN: process.env.REACT_APP_SENTRY_DSN,
  GOOGLE_MAPS_API_KEY: process.env.REACT_APP_GOOGLE_MAPS_API_KEY,
  STRIPE_PUBLISHABLE_KEY: process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY,
  FIREBASE_CONFIG: {
    apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
    authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
    // ... other Firebase config
  }
};
```

### **Build Optimization**
```javascript
// Webpack Configuration (for web)
const path = require('path');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = {
  // ... other config
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          enforce: true,
        },
      },
    },
  },
  plugins: [
    // ... other plugins
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      openAnalyzer: false,
    }),
  ],
};
```

---

This technical implementation guide provides the foundation for building robust, scalable, and maintainable applications that fully utilize the comprehensive backend API system we've developed. Each component is designed with performance, security, and user experience in mind while maintaining consistency across both mobile and web platforms.