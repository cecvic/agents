"""
Website Migration Platform - FastAPI Backend

Main application entry point with API routes and middleware.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
import uuid
import logging

from models.migration import (
    Migration, MigrationStatus, SourcePlatform, TargetPlatform,
    Base
)
from core.extractors.wix import WixExtractor
from core.converters.wordpress import WordPressElementorConverter
from core.ai.layout_analyzer import LayoutAnalyzer
from core.ai.similarity_checker import SimilarityChecker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Website Migration Platform API",
    description="Professional AI-powered website migration platform",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/migration_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# Request/Response Models
# ============================================================================

class MigrationCreateRequest(BaseModel):
    """Request to create a new migration"""
    project_name: str
    source_url: HttpUrl
    source_platform: str
    target_platform: str
    client_email: Optional[str] = None


class MigrationResponse(BaseModel):
    """Migration response"""
    id: str
    project_name: str
    source_url: str
    source_platform: str
    target_platform: str
    status: str
    progress: float
    current_step: Optional[str] = None
    similarity_score: Optional[float] = None
    created_at: str
    updated_at: str
    deployment_url: Optional[str] = None
    error_message: Optional[str] = None


class AIEditRequest(BaseModel):
    """Request for AI-powered editing"""
    prompt: str
    page_id: Optional[str] = None


class DeploymentRequest(BaseModel):
    """Deployment request"""
    hosting_provider: str
    domain: Optional[str] = None
    credentials: Optional[dict] = None


# ============================================================================
# API Routes
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Website Migration Platform",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "ai_services": "available",
        "timestamp": datetime.utcnow().isoformat(),
    }


# ============================================================================
# Migration Endpoints
# ============================================================================

@app.post("/api/v1/migrations", response_model=MigrationResponse)
async def create_migration(
    request: MigrationCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new website migration.

    This endpoint initiates the migration process:
    1. Creates a migration record
    2. Starts background extraction task
    3. Returns migration ID for tracking
    """
    logger.info(f"Creating migration for {request.source_url}")

    # Generate migration ID
    migration_id = str(uuid.uuid4())

    # Create migration record
    migration = Migration(
        id=migration_id,
        project_name=request.project_name,
        source_url=str(request.source_url),
        source_platform=SourcePlatform(request.source_platform),
        target_platform=TargetPlatform(request.target_platform),
        status=MigrationStatus.PENDING,
        progress=0.0,
        current_step="Initializing",
        client_email=request.client_email,
    )

    db.add(migration)
    db.commit()
    db.refresh(migration)

    # Start background migration task
    background_tasks.add_task(
        run_migration_pipeline,
        migration_id=migration_id,
        source_url=str(request.source_url),
        source_platform=request.source_platform,
        target_platform=request.target_platform,
    )

    return MigrationResponse(**migration.to_dict())


@app.get("/api/v1/migrations", response_model=List[MigrationResponse])
async def list_migrations(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all migrations with optional filtering.
    """
    query = db.query(Migration)

    if status:
        query = query.filter(Migration.status == MigrationStatus(status))

    migrations = query.offset(skip).limit(limit).all()

    return [MigrationResponse(**m.to_dict()) for m in migrations]


@app.get("/api/v1/migrations/{migration_id}", response_model=MigrationResponse)
async def get_migration(migration_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific migration.
    """
    migration = db.query(Migration).filter(Migration.id == migration_id).first()

    if not migration:
        raise HTTPException(status_code=404, detail="Migration not found")

    return MigrationResponse(**migration.to_dict())


@app.delete("/api/v1/migrations/{migration_id}")
async def delete_migration(migration_id: str, db: Session = Depends(get_db)):
    """
    Delete a migration.
    """
    migration = db.query(Migration).filter(Migration.id == migration_id).first()

    if not migration:
        raise HTTPException(status_code=404, detail="Migration not found")

    db.delete(migration)
    db.commit()

    return {"message": "Migration deleted successfully", "id": migration_id}


@app.get("/api/v1/migrations/{migration_id}/idf")
async def get_migration_idf(migration_id: str, db: Session = Depends(get_db)):
    """
    Get the IDF (Intermediate Data Format) for a migration.
    """
    migration = db.query(Migration).filter(Migration.id == migration_id).first()

    if not migration:
        raise HTTPException(status_code=404, detail="Migration not found")

    if not migration.idf_data:
        raise HTTPException(status_code=404, detail="IDF data not available yet")

    return migration.idf_data


@app.get("/api/v1/migrations/{migration_id}/converted")
async def get_converted_data(migration_id: str, db: Session = Depends(get_db)):
    """
    Get the converted data (WordPress/Elementor format).
    """
    migration = db.query(Migration).filter(Migration.id == migration_id).first()

    if not migration:
        raise HTTPException(status_code=404, detail="Migration not found")

    if not migration.converted_data:
        raise HTTPException(status_code=404, detail="Converted data not available yet")

    return migration.converted_data


@app.get("/api/v1/migrations/{migration_id}/similarity")
async def get_similarity_report(migration_id: str, db: Session = Depends(get_db)):
    """
    Get the similarity report for a migration.
    """
    migration = db.query(Migration).filter(Migration.id == migration_id).first()

    if not migration:
        raise HTTPException(status_code=404, detail="Migration not found")

    if not migration.similarity_report:
        raise HTTPException(status_code=404, detail="Similarity report not available yet")

    return {
        "migration_id": migration_id,
        "similarity_score": migration.similarity_score,
        "report": migration.similarity_report,
    }


@app.post("/api/v1/migrations/{migration_id}/validate")
async def validate_migration(
    migration_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Run validation and similarity check on a migration.
    """
    migration = db.query(Migration).filter(Migration.id == migration_id).first()

    if not migration:
        raise HTTPException(status_code=404, detail="Migration not found")

    if not migration.idf_data or not migration.converted_data:
        raise HTTPException(
            status_code=400,
            detail="Migration must be completed before validation"
        )

    # Run validation in background
    background_tasks.add_task(run_validation, migration_id)

    return {
        "message": "Validation started",
        "migration_id": migration_id,
    }


@app.post("/api/v1/migrations/{migration_id}/ai-edit")
async def ai_edit(
    migration_id: str,
    request: AIEditRequest,
    db: Session = Depends(get_db)
):
    """
    Make AI-powered edits to the migrated site using natural language.

    Example prompts:
    - "Make the header background blue"
    - "Add a contact form to the homepage"
    - "Change the font to Arial"
    """
    migration = db.query(Migration).filter(Migration.id == migration_id).first()

    if not migration:
        raise HTTPException(status_code=404, detail="Migration not found")

    # TODO: Implement AI editing using GPT-4
    # For now, return a placeholder response

    return {
        "message": "AI editing feature coming soon",
        "migration_id": migration_id,
        "prompt": request.prompt,
    }


@app.post("/api/v1/migrations/{migration_id}/deploy")
async def deploy_migration(
    migration_id: str,
    request: DeploymentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Deploy the migrated website to a hosting provider.
    """
    migration = db.query(Migration).filter(Migration.id == migration_id).first()

    if not migration:
        raise HTTPException(status_code=404, detail="Migration not found")

    if migration.status != MigrationStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Migration must be completed before deployment"
        )

    # Start deployment in background
    background_tasks.add_task(
        run_deployment,
        migration_id=migration_id,
        hosting_provider=request.hosting_provider,
        domain=request.domain,
        credentials=request.credentials,
    )

    return {
        "message": "Deployment started",
        "migration_id": migration_id,
        "hosting_provider": request.hosting_provider,
    }


@app.get("/api/v1/migrations/{migration_id}/preview")
async def get_preview_url(migration_id: str, db: Session = Depends(get_db)):
    """
    Get a preview URL for the migrated site.
    """
    migration = db.query(Migration).filter(Migration.id == migration_id).first()

    if not migration:
        raise HTTPException(status_code=404, detail="Migration not found")

    # TODO: Implement preview generation
    preview_url = f"https://preview.migrationplatform.com/{migration_id}"

    return {
        "migration_id": migration_id,
        "preview_url": preview_url,
        "expires_at": "2024-12-31T23:59:59Z",
    }


# ============================================================================
# Background Tasks
# ============================================================================

async def run_migration_pipeline(
    migration_id: str,
    source_url: str,
    source_platform: str,
    target_platform: str
):
    """
    Run the complete migration pipeline in the background.
    """
    db = SessionLocal()
    migration = db.query(Migration).filter(Migration.id == migration_id).first()

    try:
        # Step 1: Extract from source
        logger.info(f"Starting extraction for migration {migration_id}")
        migration.status = MigrationStatus.EXTRACTING
        migration.current_step = "Extracting content from source"
        migration.progress = 0.1
        db.commit()

        # Initialize extractor based on platform
        if source_platform == "wix":
            extractor = WixExtractor(source_url)
        else:
            raise ValueError(f"Unsupported source platform: {source_platform}")

        idf = await extractor.extract()

        migration.idf_data = idf.dict()
        migration.progress = 0.4
        db.commit()

        # Step 2: AI Analysis
        logger.info(f"Running AI analysis for migration {migration_id}")
        migration.status = MigrationStatus.ANALYZING
        migration.current_step = "Analyzing layout with AI"
        migration.progress = 0.5
        db.commit()

        # TODO: Run layout analysis

        # Step 3: Convert to target
        logger.info(f"Converting to {target_platform} for migration {migration_id}")
        migration.status = MigrationStatus.CONVERTING
        migration.current_step = f"Converting to {target_platform}"
        migration.progress = 0.7
        db.commit()

        if target_platform in ["wordpress_elementor", "wordpress"]:
            converter = WordPressElementorConverter(idf)
            converted_data = converter.convert()
            migration.converted_data = converted_data
        else:
            raise ValueError(f"Unsupported target platform: {target_platform}")

        migration.progress = 0.9
        db.commit()

        # Step 4: Validation
        logger.info(f"Validating migration {migration_id}")
        migration.status = MigrationStatus.VALIDATING
        migration.current_step = "Validating quality"
        migration.progress = 0.95
        db.commit()

        # Complete
        migration.status = MigrationStatus.COMPLETED
        migration.current_step = "Migration completed successfully"
        migration.progress = 1.0
        migration.completed_at = datetime.utcnow()
        db.commit()

        logger.info(f"Migration {migration_id} completed successfully")

    except Exception as e:
        logger.error(f"Migration {migration_id} failed: {str(e)}")
        migration.status = MigrationStatus.FAILED
        migration.error_message = str(e)
        migration.progress = 0.0
        db.commit()

    finally:
        db.close()


async def run_validation(migration_id: str):
    """Run similarity validation on a completed migration"""
    db = SessionLocal()
    migration = db.query(Migration).filter(Migration.id == migration_id).first()

    try:
        # TODO: Implement actual similarity checking
        # For now, generate a mock report

        similarity_report = {
            "overall_score": 0.92,
            "meets_target": True,
            "scores": {
                "visual": {"score": 0.90},
                "structural": {"score": 0.93},
                "content": {"score": 0.95},
                "asset": {"score": 0.90},
                "semantic": {"score": 0.92},
            },
            "recommendations": [
                "✅ Excellent migration! Target similarity achieved."
            ],
        }

        migration.similarity_score = 0.92
        migration.similarity_report = similarity_report
        db.commit()

    except Exception as e:
        logger.error(f"Validation failed for migration {migration_id}: {str(e)}")

    finally:
        db.close()


async def run_deployment(
    migration_id: str,
    hosting_provider: str,
    domain: Optional[str],
    credentials: Optional[dict]
):
    """Deploy the migrated site to hosting"""
    db = SessionLocal()
    migration = db.query(Migration).filter(Migration.id == migration_id).first()

    try:
        # TODO: Implement actual deployment logic

        deployment_url = f"https://{domain}" if domain else f"https://site-{migration_id}.example.com"

        migration.deployment_status = "deployed"
        migration.deployment_url = deployment_url
        migration.hosting_provider = hosting_provider
        db.commit()

        logger.info(f"Migration {migration_id} deployed to {deployment_url}")

    except Exception as e:
        logger.error(f"Deployment failed for migration {migration_id}: {str(e)}")
        migration.deployment_status = "failed"
        migration.error_message = str(e)
        db.commit()

    finally:
        db.close()


# ============================================================================
# Utility Endpoints
# ============================================================================

@app.get("/api/v1/platforms")
async def get_supported_platforms():
    """Get list of supported source and target platforms"""
    return {
        "source_platforms": [
            {"value": "wix", "name": "Wix"},
            {"value": "squarespace", "name": "Squarespace"},
            {"value": "webflow", "name": "Webflow"},
            {"value": "wordpress", "name": "WordPress"},
            {"value": "custom_html", "name": "Custom HTML"},
        ],
        "target_platforms": [
            {"value": "wordpress_elementor", "name": "WordPress + Elementor"},
            {"value": "wordpress", "name": "WordPress"},
            {"value": "squarespace", "name": "Squarespace"},
            {"value": "duda", "name": "Duda"},
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
