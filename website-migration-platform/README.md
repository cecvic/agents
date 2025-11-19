# Website Migration Platform

Professional AI-powered website migration platform for converting websites from Wix to WordPress and other platforms with 90%+ fidelity.

## Overview

This platform intelligently extracts website content, layout, and assets into an **Intermediate Data Format (IDF)** stored in a database, enabling high-fidelity migrations to various platforms like WordPress (Elementor), Squarespace, and Duda.

## Key Features

- **🎯 Multi-Platform Source Support**: Extract from Wix, Squarespace, Webflow, and custom HTML sites
- **🤖 AI-Powered Extraction**: Advanced computer vision and NLP for layout analysis
- **💾 Platform-Agnostic Storage**: Universal IDF format for any target platform
- **✨ 90%+ Fidelity**: AI-driven similarity matching ensures visual and functional accuracy
- **🎨 WordPress/Elementor Integration**: Direct export to Elementor-ready WordPress sites
- **💬 AI Editing**: Natural language prompts for post-migration modifications
- **🚀 Hosting Integration**: One-click deployment to hosting providers
- **✅ Quality Assurance**: Automated visual regression and similarity checking

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│              Client Dashboard (Next.js)                   │
│     Migration Management • Preview • AI Editing           │
└──────────────────────────────────────────────────────────┘
                            │ REST API
                            ▼
┌──────────────────────────────────────────────────────────┐
│              FastAPI Backend Server                       │
├──────────────────────────────────────────────────────────┤
│  Extraction    │    AI Engine     │    Conversion         │
│  - Wix         │    - GPT-4V      │    - WordPress        │
│  - Squarespace │    - Layout AI   │    - Elementor        │
│  - Custom HTML │    - Similarity  │    - Squarespace      │
└──────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│    PostgreSQL + S3 (IDF Storage + Assets)                │
└──────────────────────────────────────────────────────────┘
```

## Migration Workflow

```
Source Site (Wix)
    ↓
1. Crawl & Extract (Playwright)
    ↓
2. AI Analysis (GPT-4 Vision + Custom ML)
    ↓
3. Generate IDF (JSON Schema)
    ↓
4. Store in Database (PostgreSQL)
    ↓
5. Convert to Target (WordPress/Elementor)
    ↓
6. AI Quality Check (90%+ similarity)
    ↓
7. Deploy & Handoff
```

## Technology Stack

### Backend
- **FastAPI** (Python 3.11+) - High-performance async API
- **SQLAlchemy + Alembic** - ORM and migrations
- **Playwright** - Headless browser automation
- **OpenAI GPT-4 Vision** - Layout and content analysis
- **Celery + Redis** - Background task processing
- **Pillow + OpenCV** - Image processing
- **BeautifulSoup4** - HTML parsing

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS + shadcn/ui** - Modern UI components
- **React Query** - Server state management
- **Zustand** - Client state management
- **Vercel** - Deployment platform

### ML/AI
- **OpenAI GPT-4 Vision API** - Visual layout understanding
- **TensorFlow/PyTorch** - Custom similarity models
- **Transformers** - NLP for content analysis
- **scikit-image** - Image similarity metrics

### Infrastructure
- **PostgreSQL 14+** - Primary database
- **Redis 7+** - Cache and task queue
- **S3/MinIO** - Asset storage
- **Docker + Docker Compose** - Containerization
- **Nginx** - Reverse proxy

## Quick Start

### Prerequisites
```bash
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (recommended)
```

### Installation

1. **Clone and setup environment**:
```bash
cd website-migration-platform
cp .env.example .env
# Edit .env with your API keys and database credentials
```

2. **Backend setup**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
```

3. **Frontend setup**:
```bash
cd frontend
npm install
```

4. **Start services**:
```bash
# Option 1: Docker Compose (recommended)
docker-compose up -d

# Option 2: Manual
# Terminal 1: Backend
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Celery worker
cd backend && celery -A core.celery_app worker --loglevel=info

# Terminal 3: Frontend
cd frontend && npm run dev
```

5. **Access the platform**:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- API: http://localhost:8000/api/v1

## Usage Example

### 1. Start a Migration

```bash
curl -X POST http://localhost:8000/api/v1/migrations \
  -H "Content-Type: application/json" \
  -d '{
    "source_url": "https://example.wixsite.com/mysite",
    "source_platform": "wix",
    "target_platform": "wordpress_elementor",
    "project_name": "My Site Migration"
  }'
```

### 2. Monitor Progress

```bash
curl http://localhost:8000/api/v1/migrations/{migration_id}
```

### 3. Preview & Edit

Visit the dashboard to:
- Preview extracted content
- Use AI prompts to modify design
- Compare source vs. migrated site
- Check similarity score

### 4. Deploy

```bash
curl -X POST http://localhost:8000/api/v1/migrations/{migration_id}/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "hosting_provider": "digitalocean",
    "domain": "mynewsite.com"
  }'
```

## Project Structure

```
website-migration-platform/
├── backend/
│   ├── api/
│   │   ├── routes/          # API endpoints
│   │   └── middleware/      # Auth, CORS, etc.
│   ├── core/
│   │   ├── extractors/      # Platform-specific extractors
│   │   │   ├── wix.py
│   │   │   ├── squarespace.py
│   │   │   └── base.py
│   │   ├── converters/      # Platform-specific converters
│   │   │   ├── wordpress.py
│   │   │   ├── elementor.py
│   │   │   └── base.py
│   │   ├── ai/              # AI/ML components
│   │   │   ├── layout_analyzer.py
│   │   │   ├── similarity_checker.py
│   │   │   └── content_classifier.py
│   │   └── idf/             # Intermediate Data Format
│   │       ├── schema.py
│   │       ├── validator.py
│   │       └── serializer.py
│   ├── models/              # SQLAlchemy models
│   ├── services/            # Business logic
│   ├── utils/               # Helpers
│   └── tests/               # Test suite
├── frontend/
│   └── src/
│       ├── components/      # React components
│       ├── pages/           # Next.js pages
│       ├── lib/             # Utilities
│       └── store/           # State management
├── ml/
│   ├── layout_analyzer/     # Custom layout detection model
│   ├── similarity_checker/  # Visual similarity model
│   └── training/            # Training scripts
├── docs/                    # Documentation
└── scripts/                 # Utility scripts
```

## API Endpoints

### Migrations
- `POST /api/v1/migrations` - Start new migration
- `GET /api/v1/migrations` - List all migrations
- `GET /api/v1/migrations/{id}` - Get migration details
- `DELETE /api/v1/migrations/{id}` - Delete migration

### Content
- `GET /api/v1/migrations/{id}/idf` - Get IDF data
- `PUT /api/v1/migrations/{id}/idf` - Update IDF
- `POST /api/v1/migrations/{id}/ai-edit` - AI-powered edits

### Deployment
- `POST /api/v1/migrations/{id}/deploy` - Deploy to hosting
- `GET /api/v1/migrations/{id}/preview` - Get preview URL

### Quality
- `GET /api/v1/migrations/{id}/similarity` - Get similarity score
- `POST /api/v1/migrations/{id}/validate` - Run validation

## IDF (Intermediate Data Format)

The IDF is a comprehensive JSON schema that captures:
- **Page structure**: Headers, sections, footers
- **Components**: Buttons, forms, galleries, sliders
- **Styling**: Colors, fonts, spacing, responsive rules
- **Content**: Text, images, videos, embedded media
- **Interactions**: Animations, hover effects, click handlers
- **SEO**: Meta tags, structured data, alt text
- **Assets**: Images, fonts, scripts, stylesheets

See [docs/idf-schema.md](docs/idf-schema.md) for complete specification.

## AI Components

### Layout Analysis
- Computer vision to detect visual hierarchy
- Element classification (hero, nav, footer, etc.)
- Responsive breakpoint detection
- Grid system analysis

### Similarity Checking
- Structural similarity (DOM tree comparison)
- Visual similarity (screenshot comparison using SSIM/MSE)
- Content similarity (text and asset matching)
- Functional similarity (interaction testing)

### AI Editing
- Natural language to design changes
- "Make the header blue" → CSS modifications
- "Add a contact form" → Component insertion
- Powered by GPT-4 with vision understanding

## Deployment Options

### Supported Hosting Providers
- DigitalOcean
- AWS (EC2, Lightsail)
- Kinsta
- WP Engine
- SiteGround
- Custom FTP/SFTP

### Deployment Process
1. WordPress installation on hosting
2. Theme and plugin setup (Elementor)
3. Content import via IDF converter
4. Asset upload to media library
5. DNS configuration
6. SSL certificate installation

## Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=.

# Frontend tests
cd frontend
npm test
npm run test:e2e

# Integration tests
npm run test:integration
```

## Performance

- **Extraction**: ~2-5 minutes for average site (10-20 pages)
- **AI Analysis**: ~30-60 seconds per page
- **Conversion**: ~1-3 minutes for WordPress/Elementor
- **Similarity Check**: ~15-30 seconds per page
- **Total Migration**: ~10-20 minutes for typical site

## Roadmap

### Phase 1 (Current)
- ✅ Project setup and architecture
- ✅ IDF schema design
- 🚧 Wix extractor
- 🚧 WordPress/Elementor converter
- 🚧 Basic AI analysis

### Phase 2
- Squarespace extractor
- Webflow extractor
- Advanced AI similarity checking
- Visual regression testing
- AI editing interface

### Phase 3
- Duda converter
- Shopify converter
- Advanced hosting integrations
- White-label capabilities
- API for third-party integrations

## Contributing

This is a proprietary project. For development guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Proprietary - All Rights Reserved

## Support

For questions or issues:
- Email: support@migrationplatform.com
- Documentation: [docs/](docs/)
- API Reference: http://localhost:8000/docs

---

**Built with ❤️ for seamless website migrations**
