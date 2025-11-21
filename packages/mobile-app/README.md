# VALEO CRM Mobile App

React Native mobile application for CRM access on iOS and Android devices.

## Features

- **Offline-First**: Full CRM functionality works offline with sync
- **Push Notifications**: Real-time alerts for leads, tasks, and opportunities
- **Biometric Authentication**: Face ID and Touch ID support
- **Camera Integration**: Scan business cards and documents
- **GPS Tracking**: Location-based customer visits and check-ins
- **Voice Recording**: Voice notes for customer interactions
- **Dashboard**: Personalized KPI dashboard with charts
- **Customer Management**: Full CRUD operations for customers and contacts
- **Lead Management**: Lead qualification and conversion on mobile
- **Task Management**: Create and manage sales activities and follow-ups
- **Calendar Integration**: Sync with device calendar for appointments

## Tech Stack

- **React Native**: Cross-platform mobile development
- **Expo**: Development platform and build service
- **Redux Toolkit**: State management
- **React Navigation**: Navigation and routing
- **Axios**: HTTP client for API communication
- **AsyncStorage**: Local data persistence
- **React Native Paper**: Material Design components
- **React Native Vector Icons**: Icon library
- **React Native Maps**: Location services
- **Expo Notifications**: Push notification handling

## Project Structure

```
packages/mobile-app/
├── assets/                 # Images, fonts, and other assets
├── components/             # Reusable UI components
│   ├── common/            # Shared components (Button, Input, etc.)
│   ├── crm/               # CRM-specific components
│   └── navigation/        # Navigation components
├── screens/                # Screen components
│   ├── auth/              # Authentication screens
│   ├── dashboard/         # Dashboard and home screens
│   ├── customers/         # Customer management screens
│   ├── leads/             # Lead management screens
│   ├── tasks/             # Task and activity screens
│   └── settings/          # Settings and configuration
├── services/               # API services and utilities
│   ├── api/               # API client and endpoints
│   ├── auth/              # Authentication services
│   ├── storage/           # Local storage utilities
│   └── sync/              # Data synchronization
├── store/                  # Redux store configuration
├── utils/                  # Utility functions
├── constants/              # App constants and configuration
├── hooks/                  # Custom React hooks
├── types/                  # TypeScript type definitions
└── App.tsx                 # Main app component
```

## Development Setup

### Prerequisites

- Node.js 18+
- npm or yarn
- Expo CLI
- iOS Simulator (macOS) or Android Emulator/Device

### Installation

```bash
# Install dependencies
npm install

# Install Expo CLI globally
npm install -g @expo/cli

# Start development server
npm start

# Run on iOS simulator
npm run ios

# Run on Android emulator
npm run android
```

### Environment Configuration

Create `.env` file in the mobile-app directory:

```env
API_BASE_URL=http://localhost:8000/api/v1
WEBSOCKET_URL=ws://localhost:8000/ws
TENANT_ID=00000000-0000-0000-0000-000000000001
APP_ENV=development
```

## Key Features Implementation

### Offline-First Architecture

- **Local Storage**: SQLite-based local database for offline data
- **Sync Engine**: Background synchronization with conflict resolution
- **Queue System**: Offline action queuing with retry logic
- **Data Versioning**: Optimistic updates with server reconciliation

### Authentication & Security

- **JWT Tokens**: Secure token storage and refresh
- **Biometric Auth**: Device biometric authentication
- **Certificate Pinning**: SSL certificate validation
- **Data Encryption**: Sensitive data encryption at rest

### Real-time Updates

- **WebSocket Connection**: Real-time data synchronization
- **Push Notifications**: Firebase/APNs integration
- **Background Sync**: Periodic data refresh
- **Live Updates**: Real-time dashboard updates

### Performance Optimization

- **Code Splitting**: Lazy loading of screens and components
- **Image Optimization**: Progressive image loading and caching
- **List Virtualization**: Efficient rendering of large lists
- **Memory Management**: Automatic cleanup and optimization

## API Integration

The mobile app integrates with all CRM microservices:

- **crm-core**: Customer and contact management
- **crm-sales**: Opportunities and quotes
- **crm-service**: Cases and support tickets
- **crm-communication**: Email and messaging
- **crm-ai**: Lead scoring and recommendations
- **crm-multichannel**: Social media and external integrations

## Build & Deployment

### Development Builds

```bash
# Build for development
expo build:ios
expo build:android
```

### Production Builds

```bash
# Build for production
expo build:ios --type archive
expo build:android --type app-bundle
```

### OTA Updates

```bash
# Publish OTA update
expo publish
```

## Testing

```bash
# Run unit tests
npm test

# Run integration tests
npm run test:e2e

# Run on device for testing
npm run ios:device
npm run android:device
```

## Contributing

1. Follow React Native and Expo best practices
2. Use TypeScript for all new code
3. Write tests for new features
4. Follow the established project structure
5. Use conventional commits for PRs

## Security Considerations

- **Data Encryption**: All sensitive data encrypted at rest
- **Network Security**: HTTPS-only communication with certificate pinning
- **Authentication**: Multi-factor authentication support
- **Permissions**: Minimal required device permissions
- **Code Obfuscation**: Production builds are obfuscated
- **Regular Updates**: Dependencies kept up-to-date with security patches