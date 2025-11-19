"""
Wix Website Extractor

Specialized extractor for Wix websites that handles Wix-specific structure,
components, and rendering patterns.
"""

import json
import re
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
from datetime import datetime
import asyncio

from playwright.async_api import async_playwright, Page as PlaywrightPage, Browser
from bs4 import BeautifulSoup

from .base import BaseExtractor
from ..idf.schema import (
    IDF, Page, Element, ElementType, Asset, Theme, GlobalSettings,
    ColorPalette, Font, SEOData, ResponsiveStyles
)


class WixExtractor(BaseExtractor):
    """
    Extractor for Wix websites.

    Wix sites are heavily JavaScript-based with dynamic rendering,
    so we use Playwright for browser automation and content extraction.
    """

    def __init__(self, source_url: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(source_url, config)
        self.browser: Optional[Browser] = None
        self.wix_data: Dict[str, Any] = {}
        self.discovered_urls: set = set()

    async def extract(self) -> IDF:
        """
        Extract complete Wix website into IDF format.

        Returns:
            IDF: Complete website data
        """
        self.logger.info(f"Starting extraction of Wix site: {self.source_url}")

        async with async_playwright() as p:
            # Launch browser
            self.browser = await p.chromium.launch(
                headless=self.config.get('headless', True)
            )

            try:
                # Extract all components
                pages = await self.extract_pages()
                theme = await self.extract_theme()
                settings = await self.extract_settings()
                assets = await self.extract_assets()

                # Create IDF
                idf = IDF(
                    id=self.generate_element_id("idf"),
                    source_platform="wix",
                    source_url=self.source_url,
                    pages=pages,
                    theme=theme,
                    settings=settings,
                    assets=assets,
                    extraction_metadata={
                        "extractor": "WixExtractor",
                        "extractor_version": "1.0.0",
                        "extracted_at": datetime.utcnow().isoformat(),
                        "page_count": len(pages),
                        "asset_count": len(assets),
                        "wix_specific_data": self.wix_data,
                    }
                )

                # Validate
                is_valid, errors = self.validate_extraction(idf)
                if not is_valid:
                    self.logger.warning(f"Validation errors: {errors}")

                self.logger.info(f"Extraction complete: {len(pages)} pages, {len(assets)} assets")
                return idf

            finally:
                await self.browser.close()

    async def extract_pages(self) -> List[Page]:
        """
        Extract all pages from the Wix site.

        Returns:
            List[Page]: All pages in IDF format
        """
        self.logger.info("Extracting pages...")

        # Start with the homepage
        pages = []
        homepage = await self._extract_page(self.source_url, is_homepage=True)
        if homepage:
            pages.append(homepage)

        # Discover other pages from the navigation
        discovered_urls = await self._discover_pages(self.source_url)
        self.logger.info(f"Discovered {len(discovered_urls)} pages")

        # Extract each discovered page
        for i, url in enumerate(discovered_urls):
            if url != self.source_url:  # Skip homepage (already extracted)
                try:
                    page = await self._extract_page(url, is_homepage=False, order=i+1)
                    if page:
                        pages.append(page)
                except Exception as e:
                    self.logger.error(f"Failed to extract page {url}: {str(e)}")

        return pages

    async def _discover_pages(self, url: str) -> List[str]:
        """
        Discover all pages in the site by analyzing navigation.

        Args:
            url: Starting URL

        Returns:
            List[str]: List of discovered page URLs
        """
        context = await self.browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(2000)  # Wait for dynamic content

            # Extract all internal links
            links = await page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    return links.map(a => a.href);
                }
            """)

            # Filter to same-domain URLs
            discovered = set([url])  # Include the starting URL
            for link in links:
                parsed = urlparse(link)
                if parsed.netloc == self.domain:
                    # Remove query params and fragments for deduplication
                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    discovered.add(clean_url)

            return list(discovered)

        finally:
            await context.close()

    async def _extract_page(self, url: str, is_homepage: bool = False, order: int = 0) -> Optional[Page]:
        """
        Extract a single page.

        Args:
            url: Page URL
            is_homepage: Whether this is the homepage
            order: Page order

        Returns:
            Optional[Page]: Page in IDF format
        """
        self.logger.info(f"Extracting page: {url}")

        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page_handle = await context.new_page()

        try:
            # Navigate to page
            await page_handle.goto(url, wait_until='networkidle', timeout=30000)
            await page_handle.wait_for_timeout(3000)  # Wait for Wix to render

            # Extract page data
            page_data = await self._extract_page_data(page_handle)

            # Extract SEO data
            seo = await self._extract_seo_data(page_handle)

            # Extract elements
            elements = await self._extract_elements(page_handle)

            # Generate page ID and slug
            path = urlparse(url).path
            slug = path.strip('/') or 'home'
            page_id = self.generate_element_id("page")

            # Get page title
            title = await page_handle.title()

            page = Page(
                id=page_id,
                title=title or slug,
                slug=slug,
                path=path,
                elements=elements,
                seo=seo,
                is_homepage=is_homepage,
                order=order,
                platform_data={
                    "wix_page_data": page_data,
                    "url": url,
                }
            )

            return page

        except Exception as e:
            self.logger.error(f"Error extracting page {url}: {str(e)}")
            return None

        finally:
            await context.close()

    async def _extract_page_data(self, page: PlaywrightPage) -> Dict[str, Any]:
        """
        Extract Wix-specific page data.

        Args:
            page: Playwright page handle

        Returns:
            Dict: Wix page data
        """
        try:
            # Wix stores data in window objects
            wix_data = await page.evaluate("""
                () => {
                    const data = {};

                    // Try to extract Wix data model
                    if (window.clientSideRender) {
                        data.clientSideRender = true;
                    }

                    // Extract any Wix-specific variables
                    if (window.rendererModel) {
                        data.hasRendererModel = true;
                    }

                    return data;
                }
            """)

            return wix_data

        except Exception as e:
            self.logger.debug(f"Could not extract Wix page data: {str(e)}")
            return {}

    async def _extract_seo_data(self, page: PlaywrightPage) -> SEOData:
        """
        Extract SEO metadata from the page.

        Args:
            page: Playwright page handle

        Returns:
            SEOData: SEO metadata
        """
        seo_data = await page.evaluate("""
            () => {
                const data = {};

                // Title
                data.title = document.title;

                // Meta tags
                const metas = Array.from(document.querySelectorAll('meta'));
                metas.forEach(meta => {
                    const name = meta.getAttribute('name') || meta.getAttribute('property');
                    const content = meta.getAttribute('content');

                    if (name && content) {
                        data[name] = content;
                    }
                });

                // Canonical
                const canonical = document.querySelector('link[rel="canonical"]');
                if (canonical) {
                    data.canonical = canonical.href;
                }

                // Structured data
                const scripts = Array.from(document.querySelectorAll('script[type="application/ld+json"]'));
                data.structured_data = scripts.map(s => {
                    try {
                        return JSON.parse(s.textContent);
                    } catch (e) {
                        return null;
                    }
                }).filter(Boolean);

                return data;
            }
        """)

        return SEOData(
            title=seo_data.get('title'),
            description=seo_data.get('description'),
            keywords=seo_data.get('keywords', '').split(',') if seo_data.get('keywords') else [],
            canonical_url=seo_data.get('canonical'),
            og_title=seo_data.get('og:title'),
            og_description=seo_data.get('og:description'),
            og_image=seo_data.get('og:image'),
            og_type=seo_data.get('og:type'),
            twitter_card=seo_data.get('twitter:card'),
            twitter_title=seo_data.get('twitter:title'),
            twitter_description=seo_data.get('twitter:description'),
            twitter_image=seo_data.get('twitter:image'),
            structured_data=seo_data.get('structured_data', []),
        )

    async def _extract_elements(self, page: PlaywrightPage) -> List[Element]:
        """
        Extract all elements from the page in a hierarchical structure.

        Args:
            page: Playwright page handle

        Returns:
            List[Element]: Root-level elements
        """
        # Get the page structure
        structure = await page.evaluate("""
            () => {
                function extractElement(el, depth = 0) {
                    if (depth > 10) return null;  // Prevent infinite recursion

                    // Skip script, style, and other non-visual elements
                    const skipTags = ['SCRIPT', 'STYLE', 'NOSCRIPT', 'META', 'LINK'];
                    if (skipTags.includes(el.tagName)) return null;

                    // Get computed styles
                    const styles = window.getComputedStyle(el);

                    // Skip hidden elements
                    if (styles.display === 'none' || styles.visibility === 'hidden') {
                        return null;
                    }

                    const element = {
                        tag: el.tagName.toLowerCase(),
                        classes: Array.from(el.classList),
                        attributes: {},
                        content: null,
                        children: [],
                        styles: {}
                    };

                    // Extract important attributes
                    ['id', 'href', 'src', 'alt', 'title', 'data-testid'].forEach(attr => {
                        const value = el.getAttribute(attr);
                        if (value) element.attributes[attr] = value;
                    });

                    // Extract data attributes (Wix uses these extensively)
                    Array.from(el.attributes).forEach(attr => {
                        if (attr.name.startsWith('data-')) {
                            element.attributes[attr.name] = attr.value;
                        }
                    });

                    // Extract styles
                    const importantStyles = [
                        'color', 'backgroundColor', 'fontSize', 'fontFamily', 'fontWeight',
                        'margin', 'padding', 'border', 'width', 'height', 'display',
                        'position', 'top', 'left', 'right', 'bottom', 'zIndex',
                        'textAlign', 'lineHeight'
                    ];

                    importantStyles.forEach(prop => {
                        const value = styles[prop];
                        if (value && value !== 'none' && value !== 'auto') {
                            element.styles[prop] = value;
                        }
                    });

                    // Extract text content for leaf nodes
                    if (el.childNodes.length === 1 && el.childNodes[0].nodeType === Node.TEXT_NODE) {
                        element.content = el.textContent.trim();
                    }

                    // Recursively extract children
                    Array.from(el.children).forEach(child => {
                        const childElement = extractElement(child, depth + 1);
                        if (childElement) {
                            element.children.push(childElement);
                        }
                    });

                    return element;
                }

                // Start from body
                return extractElement(document.body);
            }
        """)

        # Convert to IDF Elements
        def convert_to_idf_element(raw_elem: Dict, parent_id: Optional[str] = None, order: int = 0) -> Optional[Element]:
            if not raw_elem:
                return None

            # Determine element type based on tag and classes
            elem_type = self._determine_element_type(raw_elem)

            element = Element(
                id=self.generate_element_id("elem"),
                type=elem_type,
                tag=raw_elem['tag'],
                content=raw_elem.get('content'),
                classes=raw_elem['classes'],
                styles=raw_elem['styles'],
                attributes=raw_elem['attributes'],
                parent_id=parent_id,
                order=order
            )

            # Process children
            for i, child_raw in enumerate(raw_elem.get('children', [])):
                child = convert_to_idf_element(child_raw, element.id, i)
                if child:
                    element.children.append(child)

            return element

        root_element = convert_to_idf_element(structure)
        return [root_element] if root_element else []

    def _determine_element_type(self, raw_elem: Dict) -> ElementType:
        """
        Determine the IDF element type from raw HTML element data.

        Args:
            raw_elem: Raw element data

        Returns:
            ElementType: IDF element type
        """
        tag = raw_elem['tag']
        classes = raw_elem['classes']
        attrs = raw_elem['attributes']

        # Common mappings
        if tag == 'header':
            return ElementType.HEADER
        elif tag == 'footer':
            return ElementType.FOOTER
        elif tag == 'nav':
            return ElementType.NAVIGATION
        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return ElementType.HEADING
        elif tag == 'p':
            return ElementType.PARAGRAPH
        elif tag == 'button':
            return ElementType.BUTTON
        elif tag == 'a':
            return ElementType.LINK
        elif tag == 'img':
            return ElementType.IMAGE
        elif tag == 'video':
            return ElementType.VIDEO
        elif tag == 'ul' or tag == 'ol':
            return ElementType.LIST
        elif tag == 'li':
            return ElementType.LIST_ITEM
        elif tag == 'section':
            return ElementType.SECTION
        elif tag == 'form':
            return ElementType.FORM
        elif tag == 'input':
            return ElementType.INPUT
        elif tag == 'textarea':
            return ElementType.TEXTAREA
        elif tag == 'select':
            return ElementType.SELECT
        elif tag == 'iframe':
            return ElementType.IFRAME

        # Check for Wix-specific classes
        class_str = ' '.join(classes).lower()
        if 'hero' in class_str:
            return ElementType.HERO
        elif 'gallery' in class_str:
            return ElementType.GALLERY
        elif 'slider' in class_str or 'carousel' in class_str:
            return ElementType.SLIDER
        elif 'card' in class_str:
            return ElementType.CARD

        # Default to container or section
        if tag == 'div':
            return ElementType.CONTAINER
        return ElementType.CONTAINER

    async def extract_theme(self) -> Theme:
        """
        Extract theme information from the Wix site.

        Returns:
            Theme: Theme data
        """
        self.logger.info("Extracting theme...")

        context = await self.browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(self.source_url, wait_until='networkidle')
            await page.wait_for_timeout(2000)

            # Extract colors and fonts
            theme_data = await page.evaluate("""
                () => {
                    const data = {
                        colors: new Set(),
                        fonts: new Set(),
                    };

                    // Analyze all elements
                    document.querySelectorAll('*').forEach(el => {
                        const styles = window.getComputedStyle(el);

                        // Colors
                        const color = styles.color;
                        const bgColor = styles.backgroundColor;
                        if (color && color !== 'rgba(0, 0, 0, 0)') data.colors.add(color);
                        if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)') data.colors.add(bgColor);

                        // Fonts
                        const fontFamily = styles.fontFamily;
                        if (fontFamily) data.fonts.add(fontFamily);
                    });

                    return {
                        colors: Array.from(data.colors),
                        fonts: Array.from(data.fonts),
                    };
                }
            """)

            # Parse colors
            colors = theme_data['colors'][:10]  # Top 10 colors
            primary_color = colors[0] if colors else '#000000'

            # Parse fonts
            font_families = theme_data['fonts'][:5]  # Top 5 fonts
            fonts = [
                Font(
                    id=self.generate_element_id("font"),
                    family=font.replace(/['"]/g, '').split(',')[0].strip(),
                    source="wix",
                )
                for font in font_families
            ]

            return Theme(
                name="wix-extracted",
                colors=ColorPalette(
                    primary=primary_color,
                    secondary=colors[1] if len(colors) > 1 else primary_color,
                    text=colors[2] if len(colors) > 2 else '#000000',
                    background='#ffffff',
                ),
                fonts=fonts,
            )

        finally:
            await context.close()

    async def extract_assets(self) -> List[Asset]:
        """
        Extract all assets from the Wix site.

        Returns:
            List[Asset]: All assets
        """
        self.logger.info("Extracting assets...")

        context = await self.browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(self.source_url, wait_until='networkidle')

            # Extract all asset URLs
            asset_urls = await page.evaluate("""
                () => {
                    const assets = {
                        images: [],
                        videos: [],
                        fonts: [],
                    };

                    // Images
                    document.querySelectorAll('img[src]').forEach(img => {
                        assets.images.push({
                            url: img.src,
                            alt: img.alt || '',
                            width: img.naturalWidth,
                            height: img.naturalHeight,
                        });
                    });

                    // Background images
                    document.querySelectorAll('*').forEach(el => {
                        const bg = window.getComputedStyle(el).backgroundImage;
                        const match = bg.match(/url\(["']?([^"')]+)["']?\)/);
                        if (match) {
                            assets.images.push({url: match[1], alt: '', width: 0, height: 0});
                        }
                    });

                    // Videos
                    document.querySelectorAll('video[src], source[src]').forEach(v => {
                        assets.videos.push({url: v.src});
                    });

                    return assets;
                }
            """)

            # Download and create Asset objects
            assets = []

            # Process images
            for img_data in asset_urls['images'][:50]:  # Limit to 50 images for now
                asset = await self.download_asset(img_data['url'], 'image')
                if asset:
                    asset.alt_text = img_data['alt']
                    asset.width = img_data['width']
                    asset.height = img_data['height']
                    assets.append(asset)

            # Process videos
            for video_data in asset_urls['videos'][:10]:  # Limit to 10 videos
                asset = await self.download_asset(video_data['url'], 'video')
                if asset:
                    assets.append(asset)

            self.logger.info(f"Extracted {len(assets)} assets")
            return assets

        finally:
            await context.close()

    async def extract_settings(self) -> GlobalSettings:
        """
        Extract global site settings.

        Returns:
            GlobalSettings: Site settings
        """
        self.logger.info("Extracting settings...")

        context = await self.browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(self.source_url, wait_until='networkidle')

            # Extract settings
            settings_data = await page.evaluate("""
                () => {
                    return {
                        title: document.title,
                        language: document.documentElement.lang || 'en',
                        favicon: document.querySelector('link[rel*="icon"]')?.href,
                    };
                }
            """)

            return GlobalSettings(
                site_name=settings_data['title'],
                site_url=self.source_url,
                language=settings_data['language'],
            )

        finally:
            await context.close()
