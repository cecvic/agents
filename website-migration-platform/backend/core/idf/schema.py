"""
Intermediate Data Format (IDF) Schema

This module defines the platform-agnostic schema for storing website structure,
content, and styling. The IDF enables conversion to any target platform.
"""

from typing import List, Dict, Optional, Any, Union, Literal
from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from enum import Enum


class ElementType(str, Enum):
    """Supported element types in the IDF"""
    # Layout
    CONTAINER = "container"
    SECTION = "section"
    ROW = "row"
    COLUMN = "column"

    # Navigation
    HEADER = "header"
    FOOTER = "footer"
    NAVIGATION = "navigation"
    MENU = "menu"
    MENU_ITEM = "menu_item"

    # Content
    TEXT = "text"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    LIST_ITEM = "list_item"

    # Media
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    GALLERY = "gallery"
    SLIDER = "slider"

    # Interactive
    BUTTON = "button"
    LINK = "link"
    FORM = "form"
    INPUT = "input"
    TEXTAREA = "textarea"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"

    # Advanced
    HERO = "hero"
    CARD = "card"
    ACCORDION = "accordion"
    TAB = "tab"
    MODAL = "modal"
    ICON = "icon"
    SPACER = "spacer"
    DIVIDER = "divider"

    # Embedded
    IFRAME = "iframe"
    EMBED = "embed"
    HTML = "html"
    SCRIPT = "script"


class ResponsiveUnit(str, Enum):
    """CSS units for responsive design"""
    PX = "px"
    EM = "em"
    REM = "rem"
    PERCENT = "%"
    VW = "vw"
    VH = "vh"
    AUTO = "auto"


class StyleProperty(BaseModel):
    """Individual style property with responsive values"""
    value: Union[str, int, float]
    unit: Optional[ResponsiveUnit] = None
    important: bool = False


class ResponsiveStyles(BaseModel):
    """Responsive styling for different breakpoints"""
    desktop: Dict[str, Any] = Field(default_factory=dict)
    tablet: Dict[str, Any] = Field(default_factory=dict)
    mobile: Dict[str, Any] = Field(default_factory=dict)


class Animation(BaseModel):
    """Animation definition"""
    name: str
    duration: float = 1.0  # seconds
    delay: float = 0.0
    timing_function: str = "ease"
    iteration_count: Union[int, str] = 1  # or "infinite"
    direction: str = "normal"
    fill_mode: str = "none"


class Interaction(BaseModel):
    """User interaction definition"""
    event: str  # click, hover, scroll, etc.
    action: str  # navigate, toggle, animate, etc.
    target: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class Asset(BaseModel):
    """Asset reference (image, font, video, etc.)"""
    id: str
    type: str  # image, video, font, etc.
    original_url: HttpUrl
    local_path: Optional[str] = None
    s3_url: Optional[HttpUrl] = None
    width: Optional[int] = None
    height: Optional[int] = None
    size: Optional[int] = None  # bytes
    mime_type: Optional[str] = None
    alt_text: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SEOData(BaseModel):
    """SEO metadata for a page"""
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    canonical_url: Optional[HttpUrl] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[HttpUrl] = None
    og_type: Optional[str] = "website"
    twitter_card: Optional[str] = None
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[HttpUrl] = None
    structured_data: List[Dict[str, Any]] = Field(default_factory=list)
    robots: Optional[str] = "index, follow"


class Element(BaseModel):
    """Base element in the IDF tree"""
    id: str
    type: ElementType
    tag: Optional[str] = None  # HTML tag if applicable

    # Content
    content: Optional[str] = None
    html: Optional[str] = None

    # Styling
    classes: List[str] = Field(default_factory=list)
    styles: Dict[str, Any] = Field(default_factory=dict)
    responsive_styles: Optional[ResponsiveStyles] = None

    # Layout
    children: List['Element'] = Field(default_factory=list)
    parent_id: Optional[str] = None
    order: int = 0

    # Attributes
    attributes: Dict[str, Any] = Field(default_factory=dict)

    # Assets
    assets: List[Asset] = Field(default_factory=list)

    # Interactions
    animations: List[Animation] = Field(default_factory=list)
    interactions: List[Interaction] = Field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Platform-specific data
    platform_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


# Enable forward references for recursive Element model
Element.model_rebuild()


class Font(BaseModel):
    """Font definition"""
    id: str
    family: str
    variants: List[str] = Field(default_factory=list)  # e.g., ["400", "700", "400italic"]
    source: str  # google, custom, system
    url: Optional[HttpUrl] = None
    local_path: Optional[str] = None


class ColorPalette(BaseModel):
    """Color palette for the site"""
    primary: str
    secondary: Optional[str] = None
    accent: Optional[str] = None
    background: str = "#ffffff"
    text: str = "#000000"
    custom_colors: Dict[str, str] = Field(default_factory=dict)


class Theme(BaseModel):
    """Site theme definition"""
    name: str = "default"
    colors: ColorPalette
    fonts: List[Font] = Field(default_factory=list)
    spacing: Dict[str, int] = Field(default_factory=dict)  # e.g., {"small": 8, "medium": 16, ...}
    breakpoints: Dict[str, int] = Field(
        default_factory=lambda: {"mobile": 768, "tablet": 1024, "desktop": 1440}
    )
    custom_css: Optional[str] = None


class Page(BaseModel):
    """Individual page in the website"""
    id: str
    title: str
    slug: str
    path: str

    # Content
    elements: List[Element] = Field(default_factory=list)

    # SEO
    seo: SEOData = Field(default_factory=SEOData)

    # Metadata
    is_homepage: bool = False
    template: Optional[str] = None
    parent_page_id: Optional[str] = None
    order: int = 0

    # Status
    published: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Platform-specific
    platform_data: Dict[str, Any] = Field(default_factory=dict)


class GlobalSettings(BaseModel):
    """Global website settings"""
    site_name: str
    site_url: HttpUrl
    language: str = "en"
    favicon: Optional[Asset] = None
    logo: Optional[Asset] = None

    # Analytics
    google_analytics_id: Optional[str] = None
    google_tag_manager_id: Optional[str] = None
    facebook_pixel_id: Optional[str] = None

    # Social
    social_links: Dict[str, HttpUrl] = Field(default_factory=dict)

    # Contact
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

    # Custom
    custom_head_code: Optional[str] = None
    custom_footer_code: Optional[str] = None


class IDF(BaseModel):
    """
    Complete Intermediate Data Format (IDF) representation of a website.

    This is the core schema that stores all website information in a
    platform-agnostic format, enabling conversion to any target platform.
    """
    # Metadata
    id: str
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Source
    source_platform: str  # wix, squarespace, wordpress, etc.
    source_url: HttpUrl

    # Content
    pages: List[Page] = Field(default_factory=list)
    theme: Theme
    settings: GlobalSettings

    # Assets
    assets: List[Asset] = Field(default_factory=list)

    # Navigation
    navigation: Dict[str, Any] = Field(default_factory=dict)

    # Metadata
    extraction_metadata: Dict[str, Any] = Field(default_factory=dict)
    similarity_scores: Dict[str, float] = Field(default_factory=dict)

    # Platform-specific preservation
    platform_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def get_page_by_id(self, page_id: str) -> Optional[Page]:
        """Get a page by its ID"""
        for page in self.pages:
            if page.id == page_id:
                return page
        return None

    def get_homepage(self) -> Optional[Page]:
        """Get the homepage"""
        for page in self.pages:
            if page.is_homepage:
                return page
        return self.pages[0] if self.pages else None

    def get_all_assets(self) -> List[Asset]:
        """Get all assets from the entire site"""
        all_assets = list(self.assets)

        for page in self.pages:
            for element in self._get_all_elements(page.elements):
                all_assets.extend(element.assets)

        return all_assets

    def _get_all_elements(self, elements: List[Element]) -> List[Element]:
        """Recursively get all elements"""
        all_elements = []
        for element in elements:
            all_elements.append(element)
            if element.children:
                all_elements.extend(self._get_all_elements(element.children))
        return all_elements

    def validate_integrity(self) -> bool:
        """Validate the integrity of the IDF structure"""
        # Check that all page IDs are unique
        page_ids = [page.id for page in self.pages]
        if len(page_ids) != len(set(page_ids)):
            return False

        # Check that all element IDs within a page are unique
        for page in self.pages:
            element_ids = [elem.id for elem in self._get_all_elements(page.elements)]
            if len(element_ids) != len(set(element_ids)):
                return False

        return True


class IDFExportFormat(BaseModel):
    """Export configuration for converting IDF to target platform"""
    target_platform: str
    include_assets: bool = True
    include_seo: bool = True
    include_analytics: bool = True
    custom_mapping: Dict[str, Any] = Field(default_factory=dict)
    options: Dict[str, Any] = Field(default_factory=dict)
