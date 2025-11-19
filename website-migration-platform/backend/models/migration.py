"""
Database Models for Website Migration Platform

SQLAlchemy models for storing migration data, IDF, and metadata.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Boolean, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class MigrationStatus(str, enum.Enum):
    """Migration status enum"""
    PENDING = "pending"
    EXTRACTING = "extracting"
    ANALYZING = "analyzing"
    CONVERTING = "converting"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


class SourcePlatform(str, enum.Enum):
    """Supported source platforms"""
    WIX = "wix"
    SQUARESPACE = "squarespace"
    WEBFLOW = "webflow"
    WORDPRESS = "wordpress"
    CUSTOM_HTML = "custom_html"


class TargetPlatform(str, enum.Enum):
    """Supported target platforms"""
    WORDPRESS_ELEMENTOR = "wordpress_elementor"
    WORDPRESS = "wordpress"
    SQUARESPACE = "squarespace"
    DUDA = "duda"


class Migration(Base):
    """
    Main migration record.

    Tracks the entire migration lifecycle from extraction to deployment.
    """
    __tablename__ = "migrations"

    id = Column(String(36), primary_key=True)
    project_name = Column(String(255), nullable=False)

    # Source
    source_url = Column(String(1000), nullable=False)
    source_platform = Column(SQLEnum(SourcePlatform), nullable=False)

    # Target
    target_platform = Column(SQLEnum(TargetPlatform), nullable=False)

    # Status
    status = Column(SQLEnum(MigrationStatus), default=MigrationStatus.PENDING)
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    current_step = Column(String(100))

    # IDF Data (stored as JSON)
    idf_data = Column(JSON)

    # Converted Data
    converted_data = Column(JSON)

    # Similarity scores
    similarity_score = Column(Float)
    similarity_report = Column(JSON)

    # Screenshots (stored as URLs or base64)
    source_screenshot_url = Column(String(1000))
    target_screenshot_url = Column(String(1000))

    # Metadata
    extraction_metadata = Column(JSON)
    conversion_metadata = Column(JSON)

    # User/Client info
    client_id = Column(String(36))
    client_email = Column(String(255))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)

    # Deployment
    deployment_status = Column(String(50))
    deployment_url = Column(String(1000))
    hosting_provider = Column(String(100))

    # Error tracking
    error_message = Column(Text)
    error_details = Column(JSON)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "project_name": self.project_name,
            "source_url": self.source_url,
            "source_platform": self.source_platform.value if self.source_platform else None,
            "target_platform": self.target_platform.value if self.target_platform else None,
            "status": self.status.value if self.status else None,
            "progress": self.progress,
            "current_step": self.current_step,
            "similarity_score": self.similarity_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "deployment_url": self.deployment_url,
            "error_message": self.error_message,
        }


class Asset(Base):
    """
    Asset storage table for images, videos, fonts, etc.
    """
    __tablename__ = "assets"

    id = Column(String(36), primary_key=True)
    migration_id = Column(String(36), nullable=False)

    # Asset info
    type = Column(String(50), nullable=False)  # image, video, font, etc.
    original_url = Column(String(1000), nullable=False)
    local_path = Column(String(1000))
    s3_url = Column(String(1000))

    # Metadata
    filename = Column(String(500))
    mime_type = Column(String(100))
    size = Column(Integer)  # bytes
    width = Column(Integer)
    height = Column(Integer)
    alt_text = Column(Text)

    # Processing
    processed = Column(Boolean, default=False)
    processing_error = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    uploaded_at = Column(DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "migration_id": self.migration_id,
            "type": self.type,
            "original_url": self.original_url,
            "s3_url": self.s3_url,
            "filename": self.filename,
            "mime_type": self.mime_type,
            "size": self.size,
            "width": self.width,
            "height": self.height,
            "alt_text": self.alt_text,
            "processed": self.processed,
        }


class Page(Base):
    """
    Individual page records.
    """
    __tablename__ = "pages"

    id = Column(String(36), primary_key=True)
    migration_id = Column(String(36), nullable=False)

    # Page info
    title = Column(String(500), nullable=False)
    slug = Column(String(500), nullable=False)
    path = Column(String(1000), nullable=False)

    # Content (stored as JSON)
    elements = Column(JSON)
    seo_data = Column(JSON)

    # Status
    is_homepage = Column(Boolean, default=False)
    published = Column(Boolean, default=True)
    order = Column(Integer, default=0)

    # Screenshots
    screenshot_url = Column(String(1000))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "migration_id": self.migration_id,
            "title": self.title,
            "slug": self.slug,
            "path": self.path,
            "is_homepage": self.is_homepage,
            "published": self.published,
            "order": self.order,
        }


class AIAnalysis(Base):
    """
    AI analysis results for migrations.
    """
    __tablename__ = "ai_analyses"

    id = Column(String(36), primary_key=True)
    migration_id = Column(String(36), nullable=False)
    page_id = Column(String(36))

    # Analysis type
    analysis_type = Column(String(100), nullable=False)  # layout, similarity, etc.

    # Results
    result = Column(JSON)
    confidence_score = Column(Float)

    # Model info
    model_used = Column(String(100))
    model_version = Column(String(50))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "migration_id": self.migration_id,
            "page_id": self.page_id,
            "analysis_type": self.analysis_type,
            "result": self.result,
            "confidence_score": self.confidence_score,
            "model_used": self.model_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class User(Base):
    """
    User/client records.
    """
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))

    # Authentication
    password_hash = Column(String(255))
    api_key = Column(String(100), unique=True)

    # Subscription
    plan = Column(String(50), default="free")  # free, pro, enterprise
    migrations_limit = Column(Integer, default=3)
    migrations_used = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "plan": self.plan,
            "migrations_limit": self.migrations_limit,
            "migrations_used": self.migrations_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
