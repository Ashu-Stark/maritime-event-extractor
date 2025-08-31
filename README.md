# SoF Event Extractor - Laytime Intelligence System

A comprehensive AI-powered system for extracting maritime events from Statement of Facts (SoF) documents. This application uses advanced Natural Language Processing (NLP) and pattern matching to automatically identify and extract vessel operations, timestamps, locations, and other critical maritime data.

## Features

### Core Functionality
- **Universal File Processing**: Support for 59+ file formats across 10 categories with automatic detection
- **Document Processing**: Support for PDF, DOC, and DOCX formats with OCR capabilities
- **AI Event Extraction**: Advanced NLP and pattern matching for maritime event identification
- **Interactive Chat**: AI assistant for document queries and analysis
- **Data Export**: CSV and JSON export with configurable options
- **Real-time Processing**: Live status updates during document processing
- **Responsive Design**: Mobile-first design with desktop optimization

### Maritime Events Supported
- Vessel arrivals and departures
- Berthing and mooring operations
- Loading and discharging activities
- Pilot operations
- Weather delays and interruptions
- Port operations and logistics

### Technical Features
- **Universal File Handler**: Modular architecture supporting any file type automatically
- RESTful API architecture
- PostgreSQL database with SQLAlchemy ORM
- Redis caching and background task processing
- Docker containerization
- Nginx reverse proxy
- Comprehensive error handling and logging

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Nginx         │    │   Backend       │
│   (HTML/JS)     │◄──►│   (Reverse      │◄──►│   (Flask API)   │
│                 │    │    Proxy)       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────┐             │
                       │   PostgreSQL    │◄────────────┤
                       │   (Database)    │             │
                       └─────────────────┘             │
                                                        │
                       ┌─────────────────┐             │
                       │   Redis         │◄────────────┤
                       │   (Cache/Queue) │             │
                       └─────────────────┘             │
                                                        │
                       ┌─────────────────┐             │
                       │   Celery        │◄────────────┘
                       │   (Background)  │
                       └─────────────────┘
```

### Universal File Handler Architecture

The system now includes a modular Universal File Handler that can process any file type automatically:

```
┌─────────────────────────────────────────────────────────────┐
│                Universal File Handler                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ File Processor  │  │ Document        │  │ Media &     │ │
│  │ Core            │  │ Processor       │  │ Archive     │ │
│  │                 │  │ Enhanced        │  │ Processor   │ │
│  │ • Validation    │  │                 │  │             │ │
│  │ • Categorization│  │ • Spreadsheets  │  │ • Images    │ │
│  │ • File Info     │  │ • Presentations │  │ • Archives  │ │
│  │ • Hash Calc     │  │ • Code Files    │  │ • Media     │ │
│  └─────────────────┘  │ • Data Files    │  │ • CAD/3D    │ │
│                       └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Supported File Categories:**
- **Documents** (7 formats): PDF, DOC, DOCX, TXT, RTF, ODT, Pages
- **Images** (8 formats): JPG, PNG, GIF, BMP, TIFF, WebP, SVG
- **Archives** (6 formats): ZIP, RAR, 7Z, TAR, GZ, BZ2
- **Spreadsheets** (4 formats): XLS, XLSX, CSV, ODS
- **Presentations** (3 formats): PPT, PPTX, ODP
- **Code** (9 formats): PY, JS, HTML, CSS, Java, C++, C, PHP, SQL
- **Data** (7 formats): JSON, XML, YAML, INI, CFG, CONF
- **Media** (6 formats): MP3, MP4, AVI, MOV, WAV, FLAC
- **Design** (5 formats): DWG, DXF, SKP, Blend, 3DS
- **Databases** (4 formats): DB, SQLite, MDB, ACCDB

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- 4GB+ RAM recommended
- 2GB+ disk space

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sof-extractor
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost
   - API: http://localhost/api
   - Flower (Celery monitoring): http://localhost:5555

### Manual Installation (Development)

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **Database Setup**
   ```bash
   # Install PostgreSQL or use SQLite for development
   export DATABASE_URL="sqlite:///sof_extractor.db"
   python app.py  # This will create tables automatically
   ```

3. **Start Services**
   ```bash
   # Terminal 1: Flask API
   python app.py

   # Terminal 2: Redis (if using background tasks)
   redis-server

   # Terminal 3: Celery Worker (optional)
   celery -A app.celery worker --loglevel=info
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   # Serve with any HTTP server, e.g.:
   python -m http.server 8000
   # Or use Live Server in VS Code
   ```

## API Documentation

### Authentication
Currently, the API is open for development. In production, implement JWT or API key authentication.

### Endpoints

#### Document Management
```http
POST /api/upload
Content-Type: multipart/form-data

Upload a SoF document for processing.
```

```http
POST /api/process/{document_id}
Process an uploaded document and extract events.
```

```http
GET /api/documents/{document_id}/events?type={event_type}
Retrieve extracted events for a document.
```

#### AI Chat
```http
POST /api/chat
Content-Type: application/json

{
  "message": "What was the total loading time?",
  "document_id": "uuid"
}
```

#### Data Export
```http
GET /api/export/{document_id}/csv?confidence=true&remarks=true&metadata=false
Export events as CSV file.
```

```http
GET /api/export/{document_id}/json?confidence=true&remarks=true&metadata=false
Export events as JSON file.
```

#### System
```http
GET /api/health
Check system health status.
```

### Response Format
```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Error Handling
```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `DATABASE_URL` | Database connection string | `sqlite:///sof_extractor.db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `UPLOAD_FOLDER` | File upload directory | `./uploads` |
| `MAX_CONTENT_LENGTH` | Max file size (bytes) | `10485760` (10MB) |
| `SPACY_MODEL` | spaCy NLP model | `en_core_web_sm` |

### Docker Configuration

The application uses Docker Compose with the following services:
- **backend**: Flask API server
- **db**: PostgreSQL database
- **redis**: Redis cache and message broker
- **nginx**: Reverse proxy and static file server
- **celery-worker**: Background task processor
- **celery-beat**: Scheduled task scheduler
- **flower**: Celery monitoring dashboard

## 🧠 AI and NLP Features

## 🔧 Universal File Handler

The Universal File Handler is a revolutionary addition that extends the system's capabilities beyond maritime documents to handle any file type automatically.

### Key Features
- **Automatic File Detection**: Instantly identifies file type and category
- **Intelligent Processing**: Routes files to appropriate specialized processors
- **Content Extraction**: Extracts text, data, and metadata from any supported format
- **OCR Integration**: Built-in OCR for image-based documents and images
- **Archive Handling**: Processes compressed files and extracts contents
- **Media Analysis**: Analyzes audio, video, and design files
- **Database Processing**: Reads and analyzes database files

### Processing Capabilities
- **59+ File Formats** supported across 10 categories
- **Real-time Processing** with live status updates
- **Error Handling** with graceful fallbacks
- **Content Preview** for quick file assessment
- **Processing Suggestions** for optimal file handling

### Use Cases
- **Document Management**: Process any document type automatically
- **Content Analysis**: Extract text and data from diverse sources
- **File Conversion**: Convert between supported formats
- **Archive Management**: Handle compressed files and archives
- **Media Processing**: Analyze images, audio, and video files
- **Code Analysis**: Process and analyze source code files
- **Data Extraction**: Extract structured data from various formats

### Event Extraction Methods

1. **Pattern Matching**: Regex patterns for common maritime event formats
2. **NLP Analysis**: spaCy-based natural language processing
3. **Contextual Analysis**: Surrounding text analysis for better accuracy
4. **Confidence Scoring**: Each extracted event includes a confidence score

### Supported Event Types

| Event Type | Description | Example Patterns |
|------------|-------------|------------------|
| `arrival` | Vessel arrival at port/anchorage | "arrived at anchorage", "reached port" |
| `berthing` | Mooring and berthing operations | "all fast", "commenced berthing" |
| `loading` | Cargo loading operations | "loading commenced", "cargo operations" |
| `discharging` | Cargo discharge operations | "discharge started", "unloading" |
| `pilot` | Pilot boarding/disembarking | "pilot embarked", "pilot station" |
| `departure` | Vessel departure | "sailed", "departed", "cast off" |
| `weather` | Weather-related delays | "weather delay", "suspended due to rain" |

### AI Chat Capabilities

The AI assistant can answer questions about:
- Event timelines and durations
- Weather delays and interruptions
- Loading/discharging operations
- Pilot operations
- Laytime calculations
- Document summaries

## 📊 Data Models

### Document
```python
{
  "id": "uuid",
  "filename": "string",
  "original_filename": "string",
  "file_size": "integer",
  "status": "uploaded|processing|processed|failed",
  "created_at": "datetime",
  "processed_at": "datetime"
}
```

### Event
```python
{
  "id": "uuid",
  "document_id": "uuid",
  "event_type": "string",
  "event_name": "string",
  "start_time": "string",
  "end_time": "string",
  "duration": "string",
  "location": "string",
  "remarks": "string",
  "confidence": "float",
  "extraction_method": "string"
}
```

## 🔒 Security Considerations

### Development
- CORS enabled for local development
- File type validation
- File size limits
- Input sanitization

### Production Recommendations
- Enable HTTPS with SSL certificates
- Implement authentication (JWT/OAuth)
- Set up rate limiting
- Configure firewall rules
- Use environment variables for secrets
- Enable database encryption
- Set up monitoring and alerting

## 🧪 Testing

### Running Tests
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html
```

### Testing Universal File Handler
```bash
# Test the universal file handler capabilities
python test_universal_handler.py

# This will demonstrate:
# - Processing capabilities overview
# - Supported file formats
# - Sample file processing
# - Uploads folder scanning
```

### Test Categories
- Unit tests for individual components
- Integration tests for API endpoints
- Document processing tests
- AI extraction accuracy tests

### Sample Test Documents
Place test SoF documents in `backend/tests/fixtures/` for automated testing.

## 📈 Performance Optimization

### Backend Optimizations
- Database connection pooling
- Redis caching for frequent queries
- Background task processing with Celery
- Efficient file handling and streaming
- Database query optimization

### Frontend Optimizations
- Lazy loading of components
- Image optimization
- CSS and JS minification
- Browser caching strategies
- Mobile-first responsive design

## 🚀 Deployment

### Production Deployment

1. **Server Requirements**
   - 4+ CPU cores
   - 8GB+ RAM
   - 50GB+ storage
   - Ubuntu 20.04+ or similar

2. **Docker Production Setup**
   ```bash
   # Clone repository
   git clone <repository-url>
   cd sof-extractor
   
   # Set production environment
   cp .env.example .env
   # Edit .env for production settings
   
   # Deploy with Docker Compose
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

3. **SSL Configuration**
   - Obtain SSL certificates (Let's Encrypt recommended)
   - Update nginx.conf with SSL settings
   - Configure domain name and DNS

### Cloud Deployment Options

#### AWS
- EC2 for compute
- RDS for PostgreSQL
- ElastiCache for Redis
- S3 for file storage
- CloudFront for CDN

#### Google Cloud
- Compute Engine or Cloud Run
- Cloud SQL for PostgreSQL
- Memorystore for Redis
- Cloud Storage for files

#### Azure
- Container Instances or App Service
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Blob Storage for files

## 🛠️ Development

### Project Structure
```
sof-extractor/
├── backend/                 # Flask API backend
│   ├── app.py              # Main application
│   ├── config.py           # Configuration
│   ├── models/             # Database models
│   ├── services/           # Business logic
│   │   ├── document_processor.py           # Core document processing
│   │   ├── file_processor_core.py          # Universal file handler core
│   │   ├── document_processor_enhanced.py  # Enhanced document processing
│   │   ├── media_archive_processor.py      # Media & archive processing
│   │   ├── universal_file_handler.py       # Main universal coordinator
│   │   ├── event_extractor.py              # Maritime event extraction
│   │   └── ai_service.py                   # AI chat service
│   ├── utils/              # Utility functions
│   └── tests/              # Test suite
├── frontend/               # Frontend application
│   ├── index.html          # Main HTML file
│   └── static/             # CSS, JS, images
├── docker-compose.yml      # Docker services
├── Dockerfile             # Backend container
├── nginx.conf             # Nginx configuration
└── README.md              # This file
```

### Adding New Features

1. **Backend Development**
   - Add new API endpoints in `app.py`
   - Create services in `services/`
   - Add database models in `models/`
   - Write tests in `tests/`

2. **Frontend Development**
   - Update HTML in `frontend/index.html`
   - Add JavaScript in `frontend/static/js/app.js`
   - Style with Tailwind CSS classes

3. **AI/NLP Enhancements**
   - Extend patterns in `services/event_extractor.py`
   - Add new event types
   - Improve confidence scoring
   - Enhance chat responses in `services/ai_service.py`

### Code Style
- Python: Follow PEP 8, use Black formatter
- JavaScript: Use ESLint with standard configuration
- HTML/CSS: Use Prettier for formatting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Write tests for new features
- Update documentation
- Follow existing code style
- Add type hints for Python code
- Use meaningful commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues

**Q: Document processing fails**
A: Check file format (PDF/DOC/DOCX), file size (<10MB), and server logs

**Q: AI responses are inaccurate**
A: The system uses pattern matching and NLP. Accuracy depends on document quality and format

**Q: Upload fails**
A: Verify file size limits, network connectivity, and server status

### Getting Help
- Check the [Issues](../../issues) page for known problems
- Create a new issue with detailed description
- Include error logs and sample documents (if possible)

### Performance Monitoring
- Use Flower dashboard for Celery task monitoring
- Check application logs for errors
- Monitor database performance
- Use health check endpoint for system status

## 🔮 Roadmap

### Planned Features
- [x] **Universal File Handler** - Process any file type automatically ✅
- [ ] Advanced OCR for image-based PDFs
- [ ] Multi-language support
- [ ] Machine learning model training
- [ ] Real-time collaboration
- [ ] Advanced analytics dashboard
- [ ] Integration with maritime APIs
- [ ] Mobile application
- [ ] Blockchain integration for document verification

### Version History
- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Enhanced AI chat and export features
- **v1.2.0**: Docker containerization and deployment
- **v1.3.0**: Universal File Handler - Process any file type automatically ✅
- **v2.0.0**: Advanced NLP and ML integration (planned)

---

**Built with ❤️ for the Maritime Industry**

For more information, visit our [documentation](docs/) or contact the development team.
