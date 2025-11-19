"""
Base Extractor Class

Abstract base class for platform-specific website extractors.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, urljoin
import logging

from ..idf.schema import IDF, Page, Element, Asset, Theme, GlobalSettings


logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """
    Abstract base class for website extractors.

    Each platform (Wix, Squarespace, WordPress, etc.) should implement
    this interface to extract content into the IDF format.
    """

    def __init__(self, source_url: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the extractor.

        Args:
            source_url: The URL of the website to extract
            config: Optional configuration dictionary
        """
        self.source_url = source_url
        self.config = config or {}
        self.domain = urlparse(source_url).netloc
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

    @abstractmethod
    async def extract(self) -> IDF:
        """
        Extract the website and convert to IDF format.

        Returns:
            IDF: Complete website data in IDF format
        """
        pass

    @abstractmethod
    async def extract_pages(self) -> List[Page]:
        """
        Extract all pages from the website.

        Returns:
            List[Page]: List of pages in IDF format
        """
        pass

    @abstractmethod
    async def extract_theme(self) -> Theme:
        """
        Extract theme information (colors, fonts, etc.).

        Returns:
            Theme: Theme data in IDF format
        """
        pass

    @abstractmethod
    async def extract_assets(self) -> List[Asset]:
        """
        Extract all assets (images, videos, fonts, etc.).

        Returns:
            List[Asset]: List of assets in IDF format
        """
        pass

    @abstractmethod
    async def extract_settings(self) -> GlobalSettings:
        """
        Extract global site settings.

        Returns:
            GlobalSettings: Site settings in IDF format
        """
        pass

    def normalize_url(self, url: str) -> str:
        """
        Normalize a URL to absolute format.

        Args:
            url: The URL to normalize

        Returns:
            str: Absolute URL
        """
        if not url:
            return ""

        # Already absolute
        if url.startswith(('http://', 'https://')):
            return url

        # Protocol-relative
        if url.startswith('//'):
            return 'https:' + url

        # Relative URL
        return urljoin(self.source_url, url)

    def extract_domain_assets_only(self, url: str) -> bool:
        """
        Check if a URL belongs to the same domain.

        Args:
            url: URL to check

        Returns:
            bool: True if same domain
        """
        if not url:
            return False

        parsed = urlparse(url)
        return parsed.netloc == self.domain or not parsed.netloc

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a filename for safe storage.

        Args:
            filename: Original filename

        Returns:
            str: Sanitized filename
        """
        import re
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        if len(name) > 200:
            name = name[:200]
        return f"{name}.{ext}" if ext else name

    def generate_element_id(self, prefix: str = "elem") -> str:
        """
        Generate a unique element ID.

        Args:
            prefix: Prefix for the ID

        Returns:
            str: Unique element ID
        """
        import uuid
        return f"{prefix}_{uuid.uuid4().hex[:12]}"

    async def download_asset(self, url: str, asset_type: str) -> Optional[Asset]:
        """
        Download and create an Asset object.

        Args:
            url: URL of the asset
            asset_type: Type of asset (image, video, etc.)

        Returns:
            Optional[Asset]: Asset object or None if download fails
        """
        try:
            import aiohttp
            from pathlib import Path

            normalized_url = self.normalize_url(url)

            async with aiohttp.ClientSession() as session:
                async with session.get(normalized_url, timeout=30) as response:
                    if response.status != 200:
                        self.logger.warning(f"Failed to download asset: {normalized_url}")
                        return None

                    content = await response.read()
                    content_type = response.headers.get('Content-Type', '')

                    # Generate asset ID
                    asset_id = self.generate_element_id("asset")

                    # Create filename
                    filename = self.sanitize_filename(Path(urlparse(url).path).name)
                    if not filename:
                        ext = content_type.split('/')[-1] if '/' in content_type else 'bin'
                        filename = f"{asset_id}.{ext}"

                    return Asset(
                        id=asset_id,
                        type=asset_type,
                        original_url=normalized_url,
                        size=len(content),
                        mime_type=content_type,
                        metadata={
                            "filename": filename,
                            "content": content,  # This should be saved separately
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error downloading asset {url}: {str(e)}")
            return None

    def extract_styles_from_computed(self, computed_styles: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract and normalize styles from computed CSS styles.

        Args:
            computed_styles: Dictionary of computed CSS properties

        Returns:
            Dict[str, Any]: Normalized styles
        """
        # Map of CSS properties to extract
        important_props = [
            'color', 'background-color', 'font-family', 'font-size', 'font-weight',
            'margin', 'padding', 'border', 'width', 'height', 'display', 'position',
            'top', 'right', 'bottom', 'left', 'z-index', 'opacity', 'text-align',
            'line-height', 'letter-spacing', 'text-decoration', 'text-transform'
        ]

        styles = {}
        for prop in important_props:
            value = computed_styles.get(prop)
            if value and value != 'none' and value != 'auto':
                styles[prop] = value

        return styles

    async def detect_platform_specific_features(self) -> Dict[str, Any]:
        """
        Detect platform-specific features that need special handling.

        Returns:
            Dict[str, Any]: Platform-specific features detected
        """
        return {}

    def validate_extraction(self, idf: IDF) -> tuple[bool, List[str]]:
        """
        Validate the extracted IDF data.

        Args:
            idf: The IDF object to validate

        Returns:
            tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []

        if not idf.pages:
            errors.append("No pages extracted")

        if not idf.theme:
            errors.append("No theme information extracted")

        if not idf.get_homepage():
            errors.append("No homepage identified")

        # Check for broken asset references
        for page in idf.pages:
            for element in idf._get_all_elements(page.elements):
                for asset in element.assets:
                    if not asset.original_url:
                        errors.append(f"Asset {asset.id} missing original URL")

        return len(errors) == 0, errors
