# UI Integration Guide - Product Feed Validator

**Last Updated:** 2026-01-06 12:53:45 UTC

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Component Structure](#component-structure)
4. [Integration Steps](#integration-steps)
5. [API Integration](#api-integration)
6. [State Management](#state-management)
7. [Error Handling](#error-handling)
8. [Testing Guidelines](#testing-guidelines)
9. [Deployment Considerations](#deployment-considerations)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The Product Feed Validator is a comprehensive web-based tool designed to validate product feeds against various standards and requirements. This guide provides complete instructions for integrating the UI components into your application.

### Key Features
- **Multi-format Support:** Validate feeds in CSV, XML, JSON formats
- **Real-time Validation:** Instant feedback on feed structure and content
- **Error Detection & Reporting:** Detailed error messages with severity levels
- **Data Visualization:** Charts and graphs for validation results
- **Batch Processing:** Handle multiple feeds simultaneously
- **Export Capabilities:** Download validation reports in multiple formats

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   UI Layer (React)                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Components (Validation, Dashboard, Reports)     │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              State Management (Redux/Context)           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Store, Actions, Reducers                        │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│              API Layer (HTTP/REST)                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Validation Endpoints, File Upload, Reports      │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│           Backend Services & Processors                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Feed Validation Engine, Database, Storage       │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Component Structure

### Core Components

#### 1. **ValidationContainer**
Main container component for the validator interface.

**Location:** `src/components/ValidationContainer.jsx`

**Props:**
```javascript
{
  onValidationComplete: Function,
  feedFormat: 'csv' | 'xml' | 'json',
  strictMode: Boolean,
  customRules: Array
}
```

**Usage:**
```jsx
<ValidationContainer
  feedFormat="csv"
  strictMode={false}
  onValidationComplete={handleValidationComplete}
/>
```

#### 2. **FeedUploadComponent**
Handles file uploads and feed input.

**Location:** `src/components/FeedUploadComponent.jsx`

**Props:**
```javascript
{
  supportedFormats: Array<string>,
  maxFileSize: Number (in MB),
  onFileSelect: Function,
  onUploadProgress: Function,
  allowUrl: Boolean
}
```

**Features:**
- Drag-and-drop file upload
- URL input for remote feeds
- File size validation
- Format detection

#### 3. **ValidationResultsPanel**
Displays detailed validation results.

**Location:** `src/components/ValidationResultsPanel.jsx`

**Props:**
```javascript
{
  results: ValidationResult,
  exportFormats: Array<'pdf' | 'json' | 'csv'>,
  onExport: Function,
  filterBySeverity: String
}
```

#### 4. **ErrorVisualization**
Interactive error list and statistics.

**Location:** `src/components/ErrorVisualization.jsx`

**Props:**
```javascript
{
  errors: Array<ValidationError>,
  warnings: Array<ValidationWarning>,
  groupBy: 'severity' | 'type' | 'row',
  onErrorClick: Function
}
```

#### 5. **DashboardComponent**
Overall statistics and metrics display.

**Location:** `src/components/DashboardComponent.jsx`

**Data Displayed:**
- Total items validated
- Error count and breakdown
- Validation success rate
- Performance metrics
- Recent validations

#### 6. **ReportGenerator**
Creates and exports validation reports.

**Location:** `src/components/ReportGenerator.jsx`

**Props:**
```javascript
{
  validationData: Object,
  reportTemplate: 'detailed' | 'summary' | 'executive',
  includeGraphics: Boolean,
  customBranding: Object
}
```

---

## Integration Steps

### Step 1: Prerequisites

Ensure your project has the following dependencies:

```json
{
  "react": "^18.0.0",
  "react-dom": "^18.0.0",
  "redux": "^4.2.0",
  "react-redux": "^8.0.0",
  "axios": "^1.3.0",
  "recharts": "^2.10.0",
  "react-icons": "^4.7.0"
}
```

Install with npm:
```bash
npm install react react-dom redux react-redux axios recharts react-icons
```

### Step 2: File Structure Setup

Create the following directory structure:

```
src/
├── components/
│   ├── ValidationContainer.jsx
│   ├── FeedUploadComponent.jsx
│   ├── ValidationResultsPanel.jsx
│   ├── ErrorVisualization.jsx
│   ├── DashboardComponent.jsx
│   └── ReportGenerator.jsx
├── store/
│   ├── validationSlice.js
│   ├── uiSlice.js
│   └── store.js
├── services/
│   ├── validationService.js
│   ├── apiClient.js
│   └── reportService.js
├── hooks/
│   ├── useValidation.js
│   ├── useResults.js
│   └── useExport.js
├── utils/
│   ├── validators.js
│   ├── formatters.js
│   └── constants.js
└── styles/
    ├── components.css
    └── theme.css
```

### Step 3: Redux Store Configuration

Create `src/store/store.js`:

```javascript
import { configureStore } from '@reduxjs/toolkit';
import validationReducer from './validationSlice';
import uiReducer from './uiSlice';

export const store = configureStore({
  reducer: {
    validation: validationReducer,
    ui: uiReducer,
  },
});

export default store;
```

### Step 4: Component Integration

Wrap your application with Redux Provider:

```jsx
import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import store from './store/store';
import App from './App';

ReactDOM.render(
  <Provider store={store}>
    <App />
  </Provider>,
  document.getElementById('root')
);
```

### Step 5: Import Main Component

In your main app file:

```jsx
import React from 'react';
import ValidationContainer from './components/ValidationContainer';

function App() {
  return (
    <div className="app">
      <header>
        <h1>Product Feed Validator</h1>
      </header>
      <main>
        <ValidationContainer
          feedFormat="csv"
          strictMode={false}
        />
      </main>
    </div>
  );
}

export default App;
```

---

## API Integration

### Base API Configuration

Create `src/services/apiClient.js`:

```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:3001/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Validation Endpoints

Create `src/services/validationService.js`:

```javascript
import apiClient from './apiClient';

const validationService = {
  // Validate a feed
  validateFeed: async (feedData, options = {}) => {
    try {
      const response = await apiClient.post('/validate', {
        feedData,
        ...options,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Upload file and validate
  uploadAndValidate: async (file, options = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    Object.keys(options).forEach(key => {
      formData.append(key, options[key]);
    });

    try {
      const response = await apiClient.post('/upload-validate', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: options.onProgress,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get validation history
  getValidationHistory: async (filters = {}) => {
    try {
      const response = await apiClient.get('/validations', { params: filters });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get validation details
  getValidationDetails: async (validationId) => {
    try {
      const response = await apiClient.get(`/validations/${validationId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Export validation report
  exportReport: async (validationId, format = 'pdf') => {
    try {
      const response = await apiClient.get(`/validations/${validationId}/export`, {
        params: { format },
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export default validationService;
```

### Custom Rules API

```javascript
// Get available validation rules
getRules: async () => {
  try {
    const response = await apiClient.get('/rules');
    return response.data;
  } catch (error) {
    throw error;
  }
},

// Create custom rule
createRule: async (ruleDefinition) => {
  try {
    const response = await apiClient.post('/rules', ruleDefinition);
    return response.data;
  } catch (error) {
    throw error;
  }
},
```

---

## State Management

### Redux Validation Slice

Create `src/store/validationSlice.js`:

```javascript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import validationService from '../services/validationService';

export const validateFeed = createAsyncThunk(
  'validation/validateFeed',
  async (payload, { rejectWithValue }) => {
    try {
      return await validationService.validateFeed(payload.data, payload.options);
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

export const uploadAndValidate = createAsyncThunk(
  'validation/uploadAndValidate',
  async (payload, { rejectWithValue }) => {
    try {
      return await validationService.uploadAndValidate(payload.file, payload.options);
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

const initialState = {
  results: null,
  loading: false,
  error: null,
  validationId: null,
  history: [],
  currentValidation: null,
  uploadProgress: 0,
};

const validationSlice = createSlice({
  name: 'validation',
  initialState,
  reducers: {
    clearResults: (state) => {
      state.results = null;
      state.error = null;
      state.validationId = null;
    },
    setUploadProgress: (state, action) => {
      state.uploadProgress = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Validate Feed
      .addCase(validateFeed.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(validateFeed.fulfilled, (state, action) => {
        state.loading = false;
        state.results = action.payload.results;
        state.validationId = action.payload.id;
      })
      .addCase(validateFeed.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Upload and Validate
      .addCase(uploadAndValidate.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.uploadProgress = 0;
      })
      .addCase(uploadAndValidate.fulfilled, (state, action) => {
        state.loading = false;
        state.results = action.payload.results;
        state.validationId = action.payload.id;
        state.uploadProgress = 100;
      })
      .addCase(uploadAndValidate.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearResults, setUploadProgress } = validationSlice.actions;
export default validationSlice.reducer;
```

### Custom Hooks

Create `src/hooks/useValidation.js`:

```javascript
import { useDispatch, useSelector } from 'react-redux';
import { validateFeed, uploadAndValidate, clearResults } from '../store/validationSlice';

export const useValidation = () => {
  const dispatch = useDispatch();
  const { results, loading, error, validationId } = useSelector(
    (state) => state.validation
  );

  const validate = async (data, options = {}) => {
    return dispatch(validateFeed({ data, options }));
  };

  const uploadAndValidateFile = async (file, options = {}) => {
    return dispatch(uploadAndValidate({ file, options }));
  };

  const reset = () => {
    dispatch(clearResults());
  };

  return {
    validate,
    uploadAndValidateFile,
    results,
    loading,
    error,
    validationId,
    reset,
  };
};

export default useValidation;
```

---

## Error Handling

### Error Boundaries

Create `src/components/ErrorBoundary.jsx`:

```javascript
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error tracking service
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <details>
            <summary>Error details</summary>
            <pre>{this.state.error?.message}</pre>
          </details>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

### Error Handling Best Practices

```javascript
// In components
try {
  const result = await validationService.validateFeed(data);
  // Handle success
} catch (error) {
  if (error.response?.status === 400) {
    // Handle validation errors
    setError('Invalid feed format');
  } else if (error.response?.status === 413) {
    // Handle file too large
    setError('File size exceeds limit');
  } else if (error.response?.status === 500) {
    // Handle server errors
    setError('Server error. Please try again later.');
  } else {
    // Handle network errors
    setError('Network error. Please check your connection.');
  }
}
```

---

## Testing Guidelines

### Unit Tests

Create `src/components/__tests__/ValidationContainer.test.js`:

```javascript
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import store from '../../store/store';
import ValidationContainer from '../ValidationContainer';

describe('ValidationContainer', () => {
  it('renders correctly', () => {
    render(
      <Provider store={store}>
        <ValidationContainer />
      </Provider>
    );
    expect(screen.getByText(/product feed validator/i)).toBeInTheDocument();
  });

  it('handles file upload', async () => {
    render(
      <Provider store={store}>
        <ValidationContainer />
      </Provider>
    );
    
    const file = new File(['test data'], 'test.csv', { type: 'text/csv' });
    const input = screen.getByLabelText(/upload/i);
    
    fireEvent.change(input, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(screen.getByText(/validating/i)).toBeInTheDocument();
    });
  });

  it('displays validation results', async () => {
    render(
      <Provider store={store}>
        <ValidationContainer />
      </Provider>
    );

    // Simulate validation completion
    // Assert results are displayed
    await waitFor(() => {
      expect(screen.getByText(/validation results/i)).toBeInTheDocument();
    });
  });
});
```

### Integration Tests

```javascript
describe('Validation Flow Integration', () => {
  it('completes full validation workflow', async () => {
    const { getByText, getByLabelText } = render(
      <Provider store={store}>
        <ValidationContainer />
      </Provider>
    );

    // 1. Upload file
    const file = new File(['test'], 'feed.csv', { type: 'text/csv' });
    fireEvent.change(getByLabelText(/upload/i), { target: { files: [file] } });

    // 2. Wait for validation
    await waitFor(() => {
      expect(getByText(/results/i)).toBeInTheDocument();
    });

    // 3. Check results
    expect(getByText(/errors/i)).toBeInTheDocument();

    // 4. Export report
    fireEvent.click(getByText(/export/i));
  });
});
```

---

## Deployment Considerations

### Environment Configuration

Create `.env` file:

```env
REACT_APP_API_BASE_URL=https://api.example.com/api
REACT_APP_ENV=production
REACT_APP_VERSION=1.0.0
REACT_APP_LOG_LEVEL=info
```

### Build Optimization

```bash
# Create optimized production build
npm run build

# Analyze bundle size
npm install --save-dev source-map-explorer
npm run analyze
```

### Performance Optimization

1. **Code Splitting:**
   ```javascript
   const ValidationContainer = React.lazy(() =>
     import('./components/ValidationContainer')
   );
   ```

2. **Memoization:**
   ```javascript
   const MemoizedResults = React.memo(ValidationResultsPanel);
   ```

3. **Lazy Loading:**
   ```javascript
   <Suspense fallback={<Spinner />}>
     <ValidationContainer />
   </Suspense>
   ```

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine
RUN npm install -g serve
WORKDIR /app
COPY --from=0 /app/build ./build

EXPOSE 3000
CMD ["serve", "-s", "build"]
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: "Module not found" errors

**Solution:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules
npm install
```

#### Issue: CORS errors during API calls

**Solution:**
Ensure backend has proper CORS configuration:
```javascript
// Backend (Express example)
app.use(cors({
  origin: 'http://localhost:3000',
  credentials: true,
}));
```

#### Issue: Redux state not updating

**Solution:**
- Check Redux DevTools to inspect state changes
- Ensure action payloads are being dispatched correctly
- Verify reducer is handling the action

#### Issue: Validation results not displaying

**Solution:**
```javascript
// Debug: Log results in component
useEffect(() => {
  console.log('Results updated:', results);
}, [results]);
```

#### Issue: Large file uploads timing out

**Solution:**
- Increase timeout in API client
- Implement chunked upload for large files
- Add progress indicators for user feedback

### Debug Mode

Enable debug logging:

```javascript
// In main App component
if (process.env.NODE_ENV === 'development') {
  window.DEBUG_MODE = true;
  // Expose store for debugging
  window.store = store;
}
```

### Performance Monitoring

Add performance monitoring:

```javascript
import { performanceMonitor } from './utils/monitoring';

performanceMonitor.startMeasure('validation');
// ... validation code ...
performanceMonitor.endMeasure('validation');
```

---

## Support and Resources

- **API Documentation:** [Link to API docs]
- **Component Storybook:** [Link to Storybook]
- **Issue Tracker:** [Link to GitHub issues]
- **Community Forum:** [Link to forum]
- **Email Support:** support@example.com

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-06 | Initial release - Complete UI integration guide |

---

## License

This integration guide and all associated code is provided under the MIT License.
