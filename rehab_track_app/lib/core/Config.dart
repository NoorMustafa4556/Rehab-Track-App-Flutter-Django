class Config {
  // --------------------------------------------------------
  // CHANGE THIS IP ADDRESS TO MATCH YOUR DJANGO SERVER IP
  // --------------------------------------------------------
  // If running on Android Emulator connecting to local Django: 'http://10.0.2.2:8000'
  // If testing on a physical device, use your PC's local IP (e.g., 'http://192.168.1.5:8000')
  static const String serverUrl = 'http://192.168.143.9:8000';
  
  static const String apiBaseUrl = '$serverUrl/api/v1';
}
