# Getting Started with Website Migration Platform

Welcome! This guide will help you set up and run the Website Migration Platform on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker & Docker Compose** (recommended) - [Install Docker](https://docs.docker.com/get-docker/)
- **OR** Manual setup requirements:
  - Python 3.11+
  - Node.js 18+
  - PostgreSQL 14+
  - Redis 7+

## Quick Start with Docker (Recommended)

### 1. Clone and Configure

```bash
# Navigate to the project directory
cd website-migration-platform

# Copy environment variables
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Required API Keys:**
- `OPENAI_API_KEY` - For GPT-4 Vision analysis (get from https://platform.openai.com/)
- `ANTHROPIC_API_KEY` - Optional, for Claude AI features

### 2. Start All Services

```bash
# Build and start all containers
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 3. Initialize the Database

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head
```

### 4. Access the Platform

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MinIO Console** (Storage): http://localhost:9001

### 5. Create Your First Migration

1. Open http://localhost:3000
2. Click "New Migration"
3. Enter:
   - Project name
   - Source website URL (Wix site)
   - Target platform (WordPress + Elementor)
4. Click "Start Migration"
5. Monitor progress in real-time

## Manual Setup (Without Docker)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Set up environment variables
cp ../.env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start Celery Worker (Separate Terminal)

```bash
cd backend
source venv/bin/activate

# Start Celery worker for background tasks
celery -A core.celery_app worker --loglevel=info
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Database & Redis

Ensure PostgreSQL and Redis are running:

```bash
# PostgreSQL
createdb migration_db

# Redis
redis-server
```

## Configuration

### Environment Variables

Key environment variables to configure:

```bash
# API Keys (Required)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here  # Optional

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/migration_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Storage (Optional - defaults to local storage)
S3_BUCKET=migration-assets
S3_ACCESS_KEY=your-key
S3_SECRET_KEY=your-secret
```

## Platform Features

### 1. Multi-Platform Migration

**Supported Source Platforms:**
- ✅ Wix
- 🚧 Squarespace (coming soon)
- 🚧 Webflow (coming soon)
- 🚧 WordPress (coming soon)
- 🚧 Custom HTML (coming soon)

**Supported Target Platforms:**
- ✅ WordPress + Elementor
- 🚧 WordPress (vanilla)
- 🚧 Squarespace
- 🚧 Duda

### 2. AI-Powered Features

- **Layout Analysis**: GPT-4 Vision analyzes page structure
- **Similarity Checking**: 90%+ fidelity validation
- **Smart Conversion**: Intelligent widget mapping
- **AI Editing**: Natural language modifications (coming soon)

### 3. Quality Assurance

The platform ensures high-fidelity migrations through:

- **Visual Similarity**: Screenshot comparison using SSIM
- **Structural Similarity**: DOM tree analysis
- **Content Similarity**: Text and asset verification
- **Semantic Similarity**: AI-powered understanding

Target: **90%+ overall similarity score**

## Usage Examples

### API Examples

#### 1. Create a Migration

```bash
curl -X POST http://localhost:8000/api/v1/migrations \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "My Awesome Site",
    "source_url": "https://example.wixsite.com/mysite",
    "source_platform": "wix",
    "target_platform": "wordpress_elementor",
    "client_email": "client@example.com"
  }'
```

#### 2. Check Migration Status

```bash
curl http://localhost:8000/api/v1/migrations/{migration_id}
```

#### 3. Get Similarity Report

```bash
curl http://localhost:8000/api/v1/migrations/{migration_id}/similarity
```

#### 4. Deploy to Hosting

```bash
curl -X POST http://localhost:8000/api/v1/migrations/{migration_id}/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "hosting_provider": "digitalocean",
    "domain": "mynewsite.com"
  }'
```

## Troubleshooting

### Common Issues

#### 1. Playwright Browser Issues

```bash
# Reinstall Playwright browsers
docker-compose exec backend playwright install chromium

# Or manually:
cd backend
playwright install chromium
```

#### 2. Database Connection Errors

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

#### 3. API Key Errors

Ensure your `.env` file contains valid API keys:

```bash
# Test OpenAI API
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

#### 4. Port Conflicts

If ports are already in use, edit `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Change 8000 to 8001
```

### Reset Everything

```bash
# Stop and remove all containers
docker-compose down -v

# Remove all data (WARNING: This deletes all migrations)
docker volume prune

# Start fresh
docker-compose up -d
```

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=.

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd backend
black .
flake8 .
mypy .

# Frontend linting
cd frontend
npm run lint
npm run type-check
```

### Database Migrations

```bash
# Create a new migration
cd backend
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Production Deployment

### Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start in production mode
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables for Production

```bash
APP_ENV=production
APP_DEBUG=false
SECRET_KEY=use-a-strong-random-key
DATABASE_URL=postgresql://user:pass@prod-db:5432/migration_db
REDIS_URL=redis://prod-redis:6379/0
```

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Check all services
docker-compose ps
```

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f frontend
```

## Support

### Documentation

- [Architecture Overview](docs/architecture.md)
- [API Reference](http://localhost:8000/docs)
- [IDF Schema](docs/idf-schema.md)

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs: `docker-compose logs -f`
3. Open an issue on GitHub (if applicable)
4. Contact support: support@migrationplatform.com

## Next Steps

1. **Explore the Dashboard**: Navigate through the UI
2. **Run a Test Migration**: Try migrating a sample Wix site
3. **Review AI Analysis**: Check the similarity reports
4. **Customize Settings**: Adjust .env variables for your needs
5. **Integrate Hosting**: Set up deployment credentials

## Performance Tips

1. **Use Redis**: Always run Redis for background tasks
2. **Scale Workers**: Run multiple Celery workers for parallel processing
3. **Optimize Database**: Ensure PostgreSQL is properly indexed
4. **CDN for Assets**: Use S3/CloudFront for asset storage
5. **API Rate Limiting**: Respect OpenAI API rate limits

## Security Considerations

1. **Change Default Secrets**: Update all keys in `.env`
2. **Use HTTPS**: Enable SSL in production
3. **Secure Database**: Use strong passwords and restrict access
4. **API Authentication**: Implement JWT tokens for production
5. **Environment Isolation**: Never commit `.env` files

---

**Ready to migrate websites with 90%+ fidelity!** 🚀

For questions or feedback, contact: support@migrationplatform.com
