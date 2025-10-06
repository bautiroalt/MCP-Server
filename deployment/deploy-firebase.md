# Firebase Deployment Guide for NEW MCP Server

## 🚀 Quick Deployment Steps

### 1. Install Firebase CLI
```bash
npm install -g firebase-tools
```

### 2. Login to Firebase
```bash
firebase login
```

### 3. Initialize Firebase Project
```bash
cd "NEW MCP"
firebase init
```

When prompted, select:
- ✅ **Hosting: Configure files for Firebase Hosting**
- ✅ **Functions: Configure a Cloud Functions directory**
- ✅ **Storage: Configure a security rules file for Cloud Storage**

### 4. Configure Project ID
Edit `.firebaserc` and replace `your-project-id` with your actual Firebase project ID:
```json
{
  "projects": {
    "default": "your-actual-project-id"
  }
}
```

### 5. Build Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

### 6. Deploy Everything
```bash
# Deploy hosting (frontend)
firebase deploy --only hosting

# Deploy functions (backend)
firebase deploy --only functions

# Deploy storage rules
firebase deploy --only storage

# Deploy everything at once
firebase deploy
```

## 🌐 Access Your Deployed App

After deployment, you'll get URLs like:
- **Frontend**: `https://your-project-id.web.app`
- **Backend API**: `https://your-project-id.web.app/api`
- **MCP API**: `https://your-project-id.web.app/mcp/api/v1`

## 🔧 Environment Configuration

### 1. Set Environment Variables
```bash
# Set Firebase environment variables
firebase functions:config:set \
  jwt.secret_key="your-secret-key" \
  api.key="your-api-key" \
  cors.origins="https://your-project-id.web.app"

# View current config
firebase functions:config:get
```

### 2. Update Firebase Function
Edit `functions/main.py` to use environment variables:
```python
import os

# Get Firebase config
from firebase_functions import https_fn
from firebase_admin import initialize_app

# Initialize with config
initialize_app()

# Access config in your function
@https_fn.on_request()
def new_mcp_server(req: https_fn.Request):
    secret_key = os.environ.get('JWT_SECRET_KEY')
    api_key = os.environ.get('API_KEY')
    # ... rest of your function
```

## 📁 File Structure After Deployment

```
Firebase Project
├── Hosting (Frontend)
│   └── https://your-project-id.web.app
├── Functions (Backend)
│   └── https://your-project-id.web.app/api
├── Storage (Files)
│   └── Firebase Storage bucket
└── Firestore (Database)
    └── User data and context
```

## 🔒 Security Configuration

### 1. Storage Rules
The `storage.rules` file is already configured for:
- Authenticated user access
- Public read access to specific directories
- User-specific file access

### 2. CORS Configuration
Update your backend to allow Firebase domains:
```python
# In your FastAPI app
CORS_ORIGINS = [
    "https://your-project-id.web.app",
    "https://your-project-id.firebaseapp.com"
]
```

## 🚀 Advanced Deployment Options

### Option 1: Frontend Only (Recommended for MVP)
```bash
# Deploy only the React frontend
firebase deploy --only hosting
```

### Option 2: Full Stack with Functions
```bash
# Deploy both frontend and backend
firebase deploy
```

### Option 3: Custom Domain
1. Go to Firebase Console → Hosting
2. Click "Add custom domain"
3. Follow the verification steps
4. Update your CORS settings

## 🔧 Troubleshooting

### Common Issues:

#### 1. Build Errors
```bash
# Clear cache and rebuild
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### 2. Function Deployment Errors
```bash
# Check function logs
firebase functions:log

# Test function locally
firebase emulators:start --only functions
```

#### 3. CORS Issues
Update your backend CORS settings:
```python
CORS_ORIGINS = [
    "https://your-project-id.web.app",
    "https://your-project-id.firebaseapp.com",
    "http://localhost:3000"  # For development
]
```

## 📊 Monitoring

### 1. Firebase Console
- Go to [Firebase Console](https://console.firebase.google.com)
- Select your project
- Monitor:
  - **Hosting**: Page views, performance
  - **Functions**: Invocations, errors
  - **Storage**: Usage, requests

### 2. Analytics
```bash
# Install Firebase Analytics
npm install firebase

# Add to your React app
import { initializeApp } from 'firebase/app';
import { getAnalytics } from 'firebase/analytics';

const firebaseConfig = {
  // Your config from Firebase Console
};

const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
```

## 🎯 Production Checklist

- [ ] Set up custom domain
- [ ] Configure environment variables
- [ ] Set up monitoring and alerts
- [ ] Configure security rules
- [ ] Set up backup and recovery
- [ ] Test all endpoints
- [ ] Configure SSL/TLS
- [ ] Set up CDN for static assets

## 🆘 Support

If you encounter issues:
1. Check Firebase Console for errors
2. Review function logs: `firebase functions:log`
3. Test locally: `firebase emulators:start`
4. Check Firebase documentation
5. Review this deployment guide

---

**Your NEW MCP Server is now live on Firebase! 🚀**
