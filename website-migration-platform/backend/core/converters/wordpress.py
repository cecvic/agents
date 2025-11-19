"""
WordPress/Elementor Converter

Converts IDF format to WordPress with Elementor page builder support.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ..idf.schema import (
    IDF, Page, Element, ElementType, Asset, Theme,
    ColorPalette, Font
)


logger = logging.getLogger(__name__)


class WordPressElementorConverter:
    """
    Converts IDF to WordPress with Elementor page builder.

    Generates:
    - WordPress XML export file
    - Elementor JSON structures for pages
    - Theme configuration (colors, fonts)
    - Media library imports
    """

    def __init__(self, idf: IDF, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the converter.

        Args:
            idf: The IDF data to convert
            config: Optional configuration
        """
        self.idf = idf
        self.config = config or {}
        self.elementor_data = {}
        self.wp_posts = []
        self.wp_pages = []
        self.media_items = []

    def convert(self) -> Dict[str, Any]:
        """
        Convert IDF to WordPress/Elementor format.

        Returns:
            Dict containing:
                - wp_export_xml: WordPress XML export
                - elementor_data: Elementor page data
                - theme_config: Theme configuration
                - media_library: Media items to import
        """
        logger.info("Converting IDF to WordPress/Elementor format")

        # Convert pages
        for page in self.idf.pages:
            wp_page = self._convert_page(page)
            self.wp_pages.append(wp_page)

        # Convert theme
        theme_config = self._convert_theme(self.idf.theme)

        # Convert assets
        media_library = self._convert_assets(self.idf.assets)

        # Generate WordPress XML
        wp_xml = self._generate_wordpress_xml()

        return {
            "wordpress_xml": wp_xml,
            "elementor_data": self.elementor_data,
            "theme_config": theme_config,
            "media_library": media_library,
            "pages": self.wp_pages,
        }

    def _convert_page(self, page: Page) -> Dict[str, Any]:
        """
        Convert a single page to WordPress format.

        Args:
            page: IDF Page object

        Returns:
            Dict: WordPress page data
        """
        logger.info(f"Converting page: {page.title}")

        # Convert elements to Elementor format
        elementor_content = self._convert_elements_to_elementor(page.elements)

        wp_page = {
            "id": page.id,
            "title": page.title,
            "slug": page.slug,
            "status": "publish" if page.published else "draft",
            "type": "page",
            "content": "",  # Elementor handles content
            "elementor_data": elementor_content,
            "meta": {
                "_elementor_edit_mode": "builder",
                "_elementor_template_type": "wp-page",
                "_elementor_version": "3.18.0",
                "_elementor_data": json.dumps(elementor_content),
            },
            "seo": {
                "title": page.seo.title,
                "description": page.seo.description,
                "keywords": page.seo.keywords,
                "og_image": page.seo.og_image,
            },
            "is_homepage": page.is_homepage,
        }

        # Store elementor data
        self.elementor_data[page.id] = elementor_content

        return wp_page

    def _convert_elements_to_elementor(self, elements: List[Element]) -> List[Dict[str, Any]]:
        """
        Convert IDF elements to Elementor JSON structure.

        Args:
            elements: List of IDF elements

        Returns:
            List[Dict]: Elementor-formatted elements
        """
        elementor_elements = []

        for element in elements:
            elementor_elem = self._convert_single_element_to_elementor(element)
            if elementor_elem:
                elementor_elements.append(elementor_elem)

        return elementor_elements

    def _convert_single_element_to_elementor(self, element: Element) -> Optional[Dict[str, Any]]:
        """
        Convert a single IDF element to Elementor widget format.

        Args:
            element: IDF Element

        Returns:
            Optional[Dict]: Elementor widget data
        """
        # Map IDF element types to Elementor widgets
        elementor_mapping = {
            ElementType.SECTION: self._create_elementor_section,
            ElementType.CONTAINER: self._create_elementor_container,
            ElementType.HEADING: self._create_elementor_heading,
            ElementType.PARAGRAPH: self._create_elementor_text,
            ElementType.TEXT: self._create_elementor_text,
            ElementType.BUTTON: self._create_elementor_button,
            ElementType.IMAGE: self._create_elementor_image,
            ElementType.VIDEO: self._create_elementor_video,
            ElementType.GALLERY: self._create_elementor_gallery,
            ElementType.SLIDER: self._create_elementor_slider,
            ElementType.FORM: self._create_elementor_form,
            ElementType.ICON: self._create_elementor_icon,
            ElementType.SPACER: self._create_elementor_spacer,
            ElementType.DIVIDER: self._create_elementor_divider,
        }

        converter_func = elementor_mapping.get(element.type)
        if converter_func:
            return converter_func(element)
        else:
            # Default to container
            return self._create_elementor_container(element)

    def _create_elementor_section(self, element: Element) -> Dict[str, Any]:
        """Create Elementor section"""
        return {
            "id": element.id,
            "elType": "section",
            "settings": {
                **self._extract_elementor_settings(element),
            },
            "elements": [
                {
                    "id": f"{element.id}_column",
                    "elType": "column",
                    "settings": {"_column_size": 100},
                    "elements": self._convert_elements_to_elementor(element.children),
                }
            ],
        }

    def _create_elementor_container(self, element: Element) -> Dict[str, Any]:
        """Create Elementor container"""
        return {
            "id": element.id,
            "elType": "container",
            "settings": {
                "content_width": "full",
                **self._extract_elementor_settings(element),
            },
            "elements": self._convert_elements_to_elementor(element.children),
        }

    def _create_elementor_heading(self, element: Element) -> Dict[str, Any]:
        """Create Elementor heading widget"""
        # Determine heading level from tag
        header_size = "h2"
        if element.tag and element.tag.startswith('h'):
            header_size = element.tag

        return {
            "id": element.id,
            "elType": "widget",
            "widgetType": "heading",
            "settings": {
                "title": element.content or "",
                "header_size": header_size,
                **self._extract_typography_settings(element),
                **self._extract_elementor_settings(element),
            },
        }

    def _create_elementor_text(self, element: Element) -> Dict[str, Any]:
        """Create Elementor text editor widget"""
        content = element.content or element.html or ""

        return {
            "id": element.id,
            "elType": "widget",
            "widgetType": "text-editor",
            "settings": {
                "editor": content,
                **self._extract_typography_settings(element),
                **self._extract_elementor_settings(element),
            },
        }

    def _create_elementor_button(self, element: Element) -> Dict[str, Any]:
        """Create Elementor button widget"""
        return {
            "id": element.id,
            "elType": "widget",
            "widgetType": "button",
            "settings": {
                "text": element.content or "Click Here",
                "link": {
                    "url": element.attributes.get('href', '#'),
                    "is_external": False,
                },
                "button_type": "primary",
                **self._extract_elementor_settings(element),
            },
        }

    def _create_elementor_image(self, element: Element) -> Dict[str, Any]:
        """Create Elementor image widget"""
        image_asset = element.assets[0] if element.assets else None
        image_url = image_asset.original_url if image_asset else element.attributes.get('src', '')

        return {
            "id": element.id,
            "elType": "widget",
            "widgetType": "image",
            "settings": {
                "image": {
                    "url": str(image_url),
                    "id": image_asset.id if image_asset else "",
                },
                "alt": element.attributes.get('alt', ''),
                "link_to": "none",
                **self._extract_elementor_settings(element),
            },
        }

    def _create_elementor_video(self, element: Element) -> Dict[str, Any]:
        """Create Elementor video widget"""
        video_asset = element.assets[0] if element.assets else None
        video_url = video_asset.original_url if video_asset else element.attributes.get('src', '')

        return {
            "id": element.id,
            "elType": "widget",
            "widgetType": "video",
            "settings": {
                "video_type": "hosted",
                "hosted_url": {
                    "url": str(video_url),
                },
                **self._extract_elementor_settings(element),
            },
        }

    def _create_elementor_gallery(self, element: Element) -> Dict[str, Any]:
        """Create Elementor gallery widget"""
        gallery_images = [
            {
                "id": asset.id,
                "url": str(asset.original_url),
            }
            for asset in element.assets if asset.type == "image"
        ]

        return {
            "id": element.id,
            "elType": "widget",
            "widgetType": "gallery",
            "settings": {
                "gallery": gallery_images,
                "gallery_layout": "grid",
                **self._extract_elementor_settings(element),
            },
        }

    def _create_elementor_slider(self, element: Element) -> Dict[str, Any]:
        """Create Elementor image carousel widget"""
        slides = [
            {
                "id": asset.id,
                "url": str(asset.original_url),
            }
            for asset in element.assets if asset.type == "image"
        ]

        return {
            "id": element.id,
            "elType": "widget",
            "widgetType": "image-carousel",
            "settings": {
                "slides": slides,
                "autoplay": "yes",
                **self._extract_elementor_settings(element),
            },
        }

    def _create_elementor_form(self, element: Element) -> Dict[str, Any]:
        """Create Elementor form widget"""
        # Extract form fields from children
        fields = []
        for child in element.children:
            if child.type in [ElementType.INPUT, ElementType.TEXTAREA, ElementType.SELECT]:
                field_type = "text"
                if child.type == ElementType.TEXTAREA:
                    field_type = "textarea"
                elif child.type == ElementType.SELECT:
                    field_type = "select"

                fields.append({
                    "custom_id": child.id,
                    "field_type": field_type,
                    "field_label": child.attributes.get('placeholder', 'Field'),
                    "required": child.attributes.get('required', False),
                })

        return {
            "id": element.id,
            "elType": "widget",
            "widgetType": "form",
            "settings": {
                "form_fields": fields,
                "submit_button_text": "Submit",
                **self._extract_elementor_settings(element),
            },
        }

    def _create_elementor_icon(self, element: Element) -> Dict[str, Any]:
        """Create Elementor icon widget"""
        return {
            "id": element.id,
            "elType": "widget",
            "widgetType": "icon",
            "settings": {
                "icon": {"value": "fas fa-star"},
                **self._extract_elementor_settings(element),
            },
        }

    def _create_elementor_spacer(self, element: Element) -> Dict[str, Any]:
        """Create Elementor spacer widget"""
        height = element.styles.get('height', '50px')

        return {
            "id": element.id,
            "elType": "widget",
            "widgetType": "spacer",
            "settings": {
                "space": {"size": int(height.replace('px', '')) if 'px' in height else 50},
            },
        }

    def _create_elementor_divider(self, element: Element) -> Dict[str, Any]:
        """Create Elementor divider widget"""
        return {
            "id": element.id,
            "elType": "widget",
            "widgetType": "divider",
            "settings": {
                **self._extract_elementor_settings(element),
            },
        }

    def _extract_elementor_settings(self, element: Element) -> Dict[str, Any]:
        """
        Extract common Elementor settings from element styles.

        Args:
            element: IDF Element

        Returns:
            Dict: Elementor settings
        """
        settings = {}
        styles = element.styles

        # Background color
        if 'backgroundColor' in styles or 'background-color' in styles:
            bg_color = styles.get('backgroundColor') or styles.get('background-color')
            settings['background_background'] = 'classic'
            settings['background_color'] = bg_color

        # Padding
        if 'padding' in styles:
            settings['padding'] = self._parse_spacing(styles['padding'])

        # Margin
        if 'margin' in styles:
            settings['margin'] = self._parse_spacing(styles['margin'])

        # Border
        if 'border' in styles:
            settings['border_border'] = 'solid'
            settings['border_width'] = {'top': '1', 'right': '1', 'bottom': '1', 'left': '1'}

        # Width
        if 'width' in styles:
            settings['width'] = self._parse_dimension(styles['width'])

        return settings

    def _extract_typography_settings(self, element: Element) -> Dict[str, Any]:
        """
        Extract typography settings from element styles.

        Args:
            element: IDF Element

        Returns:
            Dict: Typography settings
        """
        settings = {}
        styles = element.styles

        if 'fontFamily' in styles or 'font-family' in styles:
            font = styles.get('fontFamily') or styles.get('font-family')
            settings['typography_font_family'] = font

        if 'fontSize' in styles or 'font-size' in styles:
            size = styles.get('fontSize') or styles.get('font-size')
            settings['typography_font_size'] = self._parse_dimension(size)

        if 'fontWeight' in styles or 'font-weight' in styles:
            weight = styles.get('fontWeight') or styles.get('font-weight')
            settings['typography_font_weight'] = weight

        if 'color' in styles:
            settings['text_color'] = styles['color']

        if 'textAlign' in styles or 'text-align' in styles:
            align = styles.get('textAlign') or styles.get('text-align')
            settings['align'] = align

        if 'lineHeight' in styles or 'line-height' in styles:
            height = styles.get('lineHeight') or styles.get('line-height')
            settings['typography_line_height'] = self._parse_dimension(height)

        return settings

    def _parse_spacing(self, spacing: str) -> Dict[str, str]:
        """Parse CSS spacing (margin/padding) into Elementor format"""
        parts = spacing.split()
        if len(parts) == 1:
            return {'top': parts[0], 'right': parts[0], 'bottom': parts[0], 'left': parts[0]}
        elif len(parts) == 2:
            return {'top': parts[0], 'right': parts[1], 'bottom': parts[0], 'left': parts[1]}
        elif len(parts) == 4:
            return {'top': parts[0], 'right': parts[1], 'bottom': parts[2], 'left': parts[3]}
        return {'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}

    def _parse_dimension(self, dimension: str) -> Dict[str, Any]:
        """Parse CSS dimension into Elementor format"""
        import re
        match = re.match(r'(\d+(?:\.\d+)?)(px|em|rem|%)?', str(dimension))
        if match:
            value, unit = match.groups()
            return {'size': float(value), 'unit': unit or 'px'}
        return {'size': 0, 'unit': 'px'}

    def _convert_theme(self, theme: Theme) -> Dict[str, Any]:
        """
        Convert IDF theme to WordPress theme configuration.

        Args:
            theme: IDF Theme object

        Returns:
            Dict: WordPress theme config
        """
        return {
            "colors": {
                "primary": theme.colors.primary,
                "secondary": theme.colors.secondary,
                "accent": theme.colors.accent,
                "text": theme.colors.text,
                "background": theme.colors.background,
            },
            "fonts": [
                {
                    "family": font.family,
                    "variants": font.variants,
                }
                for font in theme.fonts
            ],
            "elementor_global_colors": {
                "primary": theme.colors.primary,
                "secondary": theme.colors.secondary,
                "text": theme.colors.text,
                "accent": theme.colors.accent,
            },
            "elementor_global_fonts": {
                "primary": theme.fonts[0].family if theme.fonts else "Arial",
                "secondary": theme.fonts[1].family if len(theme.fonts) > 1 else "Arial",
            }
        }

    def _convert_assets(self, assets: List[Asset]) -> List[Dict[str, Any]]:
        """
        Convert IDF assets to WordPress media library format.

        Args:
            assets: List of IDF Asset objects

        Returns:
            List[Dict]: WordPress media items
        """
        media_items = []

        for asset in assets:
            media_item = {
                "id": asset.id,
                "type": asset.type,
                "url": str(asset.original_url),
                "filename": asset.metadata.get('filename', f"{asset.id}.jpg"),
                "mime_type": asset.mime_type,
                "alt_text": asset.alt_text,
                "width": asset.width,
                "height": asset.height,
                "size": asset.size,
            }
            media_items.append(media_item)

        return media_items

    def _generate_wordpress_xml(self) -> str:
        """
        Generate WordPress XML export file.

        Returns:
            str: WordPress XML content
        """
        from xml.etree.ElementTree import Element as XMLElement, SubElement, tostring
        from xml.dom import minidom

        # Create root RSS element
        rss = XMLElement('rss')
        rss.set('version', '2.0')
        rss.set('xmlns:excerpt', 'http://wordpress.org/export/1.2/excerpt/')
        rss.set('xmlns:content', 'http://purl.org/rss/1.0/modules/content/')
        rss.set('xmlns:wp', 'http://wordpress.org/export/1.2/')

        channel = SubElement(rss, 'channel')

        # Add site info
        SubElement(channel, 'title').text = self.idf.settings.site_name
        SubElement(channel, 'link').text = str(self.idf.settings.site_url)
        SubElement(channel, 'language').text = self.idf.settings.language

        # Add pages
        for wp_page in self.wp_pages:
            item = SubElement(channel, 'item')
            SubElement(item, 'title').text = wp_page['title']
            SubElement(item, 'wp:post_type').text = 'page'
            SubElement(item, 'wp:status').text = wp_page['status']
            SubElement(item, 'wp:post_name').text = wp_page['slug']

            # Add meta fields for Elementor
            for meta_key, meta_value in wp_page['meta'].items():
                meta = SubElement(item, 'wp:postmeta')
                SubElement(meta, 'wp:meta_key').text = meta_key
                SubElement(meta, 'wp:meta_value').text = str(meta_value)

        # Pretty print XML
        xml_string = tostring(rss, encoding='unicode')
        dom = minidom.parseString(xml_string)
        return dom.toprettyxml(indent='  ')

    def export_to_files(self, output_dir: str) -> Dict[str, str]:
        """
        Export converted data to files.

        Args:
            output_dir: Directory to save files

        Returns:
            Dict: Paths to generated files
        """
        import os
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        converted_data = self.convert()

        files = {}

        # Save WordPress XML
        xml_path = output_path / "wordpress_export.xml"
        xml_path.write_text(converted_data['wordpress_xml'])
        files['wordpress_xml'] = str(xml_path)

        # Save Elementor data
        elementor_path = output_path / "elementor_data.json"
        elementor_path.write_text(json.dumps(converted_data['elementor_data'], indent=2))
        files['elementor_data'] = str(elementor_path)

        # Save theme config
        theme_path = output_path / "theme_config.json"
        theme_path.write_text(json.dumps(converted_data['theme_config'], indent=2))
        files['theme_config'] = str(theme_path)

        # Save media library
        media_path = output_path / "media_library.json"
        media_path.write_text(json.dumps(converted_data['media_library'], indent=2))
        files['media_library'] = str(media_path)

        logger.info(f"Exported files to {output_dir}")
        return files
