# Entiendo: Document Understanding Assistant

## Overview
Entiendo is an AI-powered web application that helps users understand complex documents by providing plain-language explanations with verifiable citations. It leverages Anthropic's Claude API with Citations feature to ensure explanations are grounded in the source material.

## Core Features
1. Document Processing
   - PDF and text file upload support
   - Document segmentation for targeted analysis
   - Support for multiple document formats
   - Text extraction and preprocessing

2. AI Analysis
   - Integration with Claude 3.5 Sonnet
   - Citation-enabled responses
   - Plain language explanations
   - Source verification

3. User Interface
   - Split-screen document viewer
   - Interactive text selection
   - Real-time explanation generation
   - Citation highlighting
   - Responsive design

## Technical Architecture

### Backend (FastAPI)
```
src/
├── main.py              # Application entry point and API routes
├── services/
│   ├── anthropic.py     # Claude API integration
│   └── document.py      # Document processing logic
├── models/
│   ├── document.py      # Pydantic models
│   └── responses.py     # API response models
└── templates/
    └── index.html       # Main application template
```

### Frontend Components
1. Document Upload
   - Drag-and-drop interface
   - File type validation
   - Upload progress indicator
   - Error handling

2. Document Viewer
   - Original document display
   - Text segmentation
   - Interactive selection
   - Segment highlighting

3. Explanation Panel
   - AI-generated explanations
   - Citation display
   - Loading states
   - Error handling

### Technology Stack
- **Backend**
  - FastAPI (web framework)
  - Uvicorn (ASGI server)
  - Jinja2 (templating)
  - Anthropic SDK (AI integration)

- **Frontend**
  - Alpine.js (state management)
  - Alpine AJAX (form handling)
  - HTMX (dynamic updates)
  - Tailwind CSS (styling)
  - PDF.js (PDF rendering)

## API Routes

### Document Management
```python
POST /upload
- Accepts PDF/TXT files
- Returns document ID and metadata

GET /document/{id}
- Returns document content and segments

POST /analyze
- Accepts document segment
- Returns explanation with citations
```

## Data Flow

1. Document Upload
   ```
   Client -> /upload -> Process Document -> Store Segments -> Return ID
   ```

2. Analysis Request
   ```
   Client -> /analyze -> Claude API -> Process Response -> Return Explanation
   ```

## Implementation Details

### Document Processing
1. File Upload
   - Validate file type and size
   - Extract text content
   - Generate unique document ID
   - Store document metadata

2. Segmentation
   - Split document into logical segments
   - Preserve segment context
   - Generate segment IDs
   - Map segments to original document

3. Analysis
   - Prepare context for Claude
   - Enable citations
   - Process response
   - Match citations to segments

### UI/UX Considerations
1. Progressive Enhancement
   - Core functionality without JS
   - Enhanced features with JS
   - Fallback behaviors

2. Accessibility
   - Keyboard navigation
   - Screen reader support
   - ARIA attributes
   - Color contrast

3. Responsive Design
   - Mobile-first approach
   - Flexible layouts
   - Touch-friendly interactions

## Security Considerations

1. Input Validation
   - File type restrictions
   - Size limits
   - Content validation

2. API Security
   - Rate limiting
   - Authentication (future)
   - Input sanitization
   - Safe file handling

3. Data Privacy
   - Document storage policy
   - Data retention
   - User privacy

## Future Enhancements

1. Features
   - Document history
   - Export explanations
   - Batch processing
   - Document comparison

2. Technical
   - Caching layer
   - User accounts
   - Document persistence
   - API authentication

3. UI/UX
   - Dark mode
   - Custom themes
   - Keyboard shortcuts
   - Mobile app

## Development Setup

1. Prerequisites
   ```bash
   Python 3.11+
   Node.js (optional, for development)
   ```

2. Environment Setup
   ```bash
   # Install dependencies
   uv pip install -r pyproject.toml
   
   # Set environment variables
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

3. Running the Application
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

## Testing Strategy

1. Unit Tests
   - Document processing
   - API routes
   - UI components

2. Integration Tests
   - API integration
   - File handling
   - UI workflows

3. End-to-End Tests
   - User journeys
   - Error scenarios
   - Performance testing

## Deployment

1. Container Setup
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY . .
   RUN uv pip install -r pyproject.toml
   CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
   ```

2. Environment Variables
   ```
   ANTHROPIC_API_KEY=required
   DEBUG=optional
   PORT=optional
   ```

3. Resource Requirements
   - CPU: 1-2 cores
   - RAM: 512MB minimum
   - Storage: Based on document retention policy