export const translations = {
  en: {
    // Platform
    platformName: 'Jan Suvidha',
    aiPowered: 'AI Powered',
    
    // Common
    search: 'Search',
    filter: 'Filter',
    all: 'All',
    pending: 'Pending',
    inProgress: 'In Progress',
    resolved: 'Resolved',
    highSeverity: 'High Severity',
    low: 'Low',
    medium: 'Medium',
    high: 'High',
    critical: 'Critical',
    
    // Home
    civicIssues: 'Civic Issues',
    issuesFound: 'issues found',
    
    // Report
    reportIssue: 'Report Issue',
    helpImprove: 'Help improve your city',
    location: 'Location',
    enterLocation: 'Enter location or use GPS',
    photo: 'Photo (Optional)',
    takePhoto: 'Take Photo',
    analyzeWithAI: 'Analyze with AI',
    description: 'Description',
    describeIssue: 'Describe the issue...',
    submit: 'Submit Report',
    
    // My Issues
    myIssues: 'My Issues',
    youReported: 'You have reported',
    
    // Map
    issueMap: 'Issue Map',
    issuesShown: 'issues shown',
    aiHotspots: 'AI Hotspots',
    
    // Notifications
    notifications: 'Notifications',
    aiSmart: 'AI Smart',
    
    // Profile
    profile: 'Profile',
    editProfile: 'Edit Profile',
    reported: 'Reported',
    upvotes: 'Upvotes',
    logout: 'Logout',
    
    // Settings
    settings: 'Settings',
    language: 'Language',
    notifications: 'Notifications',
    darkMode: 'Dark Mode',
    about: 'About',
    version: 'Version',
    
    // AI
    aiAnalysis: 'AI Analysis',
    confidence: 'Confidence',
    category: 'Category',
    severity: 'Severity',
    priority: 'Priority',
    department: 'Department',
    predictedDays: 'Predicted Days',
    similarIssues: 'Similar Issues',
    sentiment: 'Sentiment',
  },
  hi: {
    // Platform
    platformName: 'जन सुफला',
    aiPowered: 'AI संचालित',
    
    // Common
    search: 'खोजें',
    filter: 'फ़िल्टर',
    all: 'सभी',
    pending: 'लंबित',
    inProgress: 'प्रगति में',
    resolved: 'हल की गई',
    highSeverity: 'उच्च गंभीरता',
    low: 'कम',
    medium: 'मध्यम',
    high: 'उच्च',
    critical: 'गंभीर',
    
    // Home
    civicIssues: 'नागरिक शिकायतें',
    issuesFound: 'शिकायतें मिलीं',
    
    // Report
    reportIssue: 'शिकायत दर्ज करें',
    helpImprove: 'शहर को बेहतर बनाने में मदद करें',
    location: 'स्थान',
    enterLocation: 'स्थान दर्ज करें या GPS का उपयोग करें',
    photo: 'फोटो (वैकल्पिक)',
    takePhoto: 'फोटो लें',
    analyzeWithAI: 'AI से विश्लेषण करें',
    description: 'विवरण',
    describeIssue: 'शिकायत का वर्णन करें...',
    submit: 'सबमिट करें',
    
    // My Issues
    myIssues: 'मेरी शिकायतें',
    youReported: 'आपने दर्ज की हैं',
    
    // Map
    issueMap: 'शिकायत नक्शा',
    issuesShown: 'शिकायतें दिखाई जा रही हैं',
    aiHotspots: 'AI हॉटस्पॉट',
    
    // Notifications
    notifications: 'सूचनाएं',
    aiSmart: 'AI स्मार्ट',
    
    // Profile
    profile: 'प्रोफ़ाइल',
    editProfile: 'प्रोफ़ाइल संपादित करें',
    reported: 'दर्ज की गई',
    upvotes: 'अपवोट',
    logout: 'लॉग आउट',
    
    // Settings
    settings: 'सेटिंग्स',
    language: 'भाषा',
    notifications: 'सूचनाएं',
    darkMode: 'डार्क मोड',
    about: 'के बारे में',
    version: 'संस्करण',
    
    // AI
    aiAnalysis: 'AI विश्लेषण',
    confidence: 'विश्वास',
    category: 'श्रेणी',
    severity: 'गंभीरता',
    priority: 'प्राथमिकता',
    department: 'विभाग',
    predictedDays: 'अनुमानित दिन',
    similarIssues: 'समान शिकायतें',
    sentiment: 'भावना',
  }
};

export const getTranslation = (lang, key) => {
  return translations[lang]?.[key] || translations['en'][key] || key;
};