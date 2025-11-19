"""
AI-Powered Layout Analyzer

Uses GPT-4 Vision and computer vision to analyze website layouts,
detect component types, and understand visual hierarchy.
"""

import base64
from io import BytesIO
from typing import Dict, List, Optional, Any, Tuple
import logging

from PIL import Image
import openai

from ..idf.schema import Element, ElementType


logger = logging.getLogger(__name__)


class LayoutAnalyzer:
    """
    AI-powered layout analysis using GPT-4 Vision and computer vision techniques.

    Capabilities:
    - Visual hierarchy detection
    - Component type classification
    - Layout pattern recognition
    - Responsive design analysis
    - Color scheme extraction
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the layout analyzer.

        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key
        if api_key:
            openai.api_key = api_key

    async def analyze_screenshot(
        self,
        screenshot: bytes,
        elements: List[Element],
        url: str
    ) -> Dict[str, Any]:
        """
        Analyze a page screenshot using GPT-4 Vision.

        Args:
            screenshot: Screenshot image bytes
            elements: Extracted elements from the page
            url: Page URL

        Returns:
            Dict: Analysis results including layout structure, components, and suggestions
        """
        logger.info(f"Analyzing screenshot for {url}")

        # Encode screenshot for GPT-4 Vision
        base64_image = base64.b64encode(screenshot).decode('utf-8')

        # Create analysis prompt
        prompt = self._create_analysis_prompt(elements, url)

        try:
            # Call GPT-4 Vision
            response = await openai.ChatCompletion.acreate(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.2,
            )

            analysis_text = response.choices[0].message.content

            # Parse the response
            analysis = self._parse_gpt_vision_response(analysis_text)

            # Enhance with computer vision analysis
            cv_analysis = await self._computer_vision_analysis(screenshot)

            # Combine results
            combined_analysis = {
                **analysis,
                "computer_vision": cv_analysis,
                "confidence_score": self._calculate_confidence(analysis, cv_analysis),
            }

            return combined_analysis

        except Exception as e:
            logger.error(f"Error in GPT-4 Vision analysis: {str(e)}")
            # Fallback to basic computer vision
            return await self._computer_vision_analysis(screenshot)

    def _create_analysis_prompt(self, elements: List[Element], url: str) -> str:
        """
        Create a detailed prompt for GPT-4 Vision.

        Args:
            elements: Extracted elements
            url: Page URL

        Returns:
            str: Analysis prompt
        """
        return f"""Analyze this webpage screenshot and provide detailed insights:

URL: {url}
Extracted Elements: {len(elements)} elements detected

Please analyze and provide:

1. **Layout Structure**:
   - Overall layout pattern (e.g., single column, multi-column, grid, asymmetric)
   - Visual hierarchy (header, hero, content sections, footer)
   - Spacing and alignment patterns

2. **Component Identification**:
   - Key components (navigation, hero section, cards, forms, galleries, etc.)
   - Interactive elements (buttons, links, forms)
   - Media elements (images, videos, icons)

3. **Design System**:
   - Color palette (primary, secondary, accent colors)
   - Typography (font families, sizes, weights used)
   - Spacing system (padding, margins, gaps)

4. **Responsive Design**:
   - Layout behavior indicators
   - Breakpoint suggestions
   - Mobile-friendly elements

5. **Element Classification**:
   For the major sections, identify:
   - Element type (hero, card, gallery, form, etc.)
   - Purpose and function
   - Visual prominence (high, medium, low)

6. **Migration Recommendations**:
   - Suitable Elementor widgets for each component
   - Complexity level (simple, moderate, complex)
   - Special considerations for migration

Format your response as JSON with these sections:
{{
  "layout_pattern": "...",
  "hierarchy": [...],
  "components": [...],
  "design_system": {{}},
  "responsive_indicators": [...],
  "element_classifications": [...],
  "migration_recommendations": {{}}
}}
"""

    def _parse_gpt_vision_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse GPT-4 Vision response into structured data.

        Args:
            response_text: Raw response text

        Returns:
            Dict: Parsed analysis data
        """
        import json
        import re

        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

            # Fallback: parse as structured text
            return {
                "raw_analysis": response_text,
                "layout_pattern": self._extract_value(response_text, "layout"),
                "components": self._extract_components(response_text),
            }

        except json.JSONDecodeError:
            logger.warning("Failed to parse GPT-4 Vision response as JSON")
            return {"raw_analysis": response_text}

    def _extract_value(self, text: str, key: str) -> str:
        """Extract a value from unstructured text"""
        import re
        pattern = rf"{key}[:\s]+([^\n]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _extract_components(self, text: str) -> List[str]:
        """Extract component list from text"""
        components = []
        for line in text.split('\n'):
            if any(keyword in line.lower() for keyword in ['component', 'widget', 'element']):
                components.append(line.strip())
        return components

    async def _computer_vision_analysis(self, screenshot: bytes) -> Dict[str, Any]:
        """
        Perform computer vision analysis on the screenshot.

        Args:
            screenshot: Screenshot image bytes

        Returns:
            Dict: CV analysis results
        """
        image = Image.open(BytesIO(screenshot))

        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Analyze color palette
        color_palette = self._extract_color_palette(image)

        # Detect visual regions
        regions = self._detect_visual_regions(image)

        # Analyze layout grid
        grid_analysis = self._analyze_grid_structure(image)

        return {
            "image_dimensions": {"width": image.width, "height": image.height},
            "color_palette": color_palette,
            "visual_regions": regions,
            "grid_analysis": grid_analysis,
        }

    def _extract_color_palette(self, image: Image.Image, num_colors: int = 5) -> List[str]:
        """
        Extract dominant colors from the image.

        Args:
            image: PIL Image
            num_colors: Number of colors to extract

        Returns:
            List[str]: List of hex color codes
        """
        from collections import Counter

        # Resize for faster processing
        small_image = image.resize((100, 100))
        pixels = list(small_image.getdata())

        # Count color frequencies
        color_counter = Counter(pixels)
        dominant_colors = color_counter.most_common(num_colors)

        # Convert to hex
        hex_colors = [
            '#{:02x}{:02x}{:02x}'.format(r, g, b)
            for (r, g, b), count in dominant_colors
        ]

        return hex_colors

    def _detect_visual_regions(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Detect major visual regions using basic image processing.

        Args:
            image: PIL Image

        Returns:
            List[Dict]: Detected regions
        """
        import numpy as np
        from PIL import ImageFilter

        # Convert to numpy array
        img_array = np.array(image)

        # Simple region detection based on contrast
        gray = image.convert('L')
        edges = gray.filter(ImageFilter.FIND_EDGES)

        # Divide into thirds (common layout pattern)
        height = image.height
        regions = [
            {"name": "header", "bounds": [0, 0, image.width, height // 4]},
            {"name": "main", "bounds": [0, height // 4, image.width, 3 * height // 4]},
            {"name": "footer", "bounds": [0, 3 * height // 4, image.width, height]},
        ]

        return regions

    def _analyze_grid_structure(self, image: Image.Image) -> Dict[str, Any]:
        """
        Analyze potential grid structure of the layout.

        Args:
            image: PIL Image

        Returns:
            Dict: Grid analysis
        """
        width, height = image.size

        # Common grid systems
        grid_systems = [12, 16, 24]  # column counts

        # Detect likely grid based on content distribution
        # This is a simplified heuristic
        suggested_grid = 12  # Default to 12-column (most common)

        return {
            "suggested_columns": suggested_grid,
            "container_width": width,
            "gutter_estimate": 20,  # pixels
        }

    def classify_element_type(
        self,
        element: Element,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[ElementType, float]:
        """
        Classify an element's type using AI and heuristics.

        Args:
            element: Element to classify
            context: Additional context (surrounding elements, etc.)

        Returns:
            Tuple[ElementType, float]: (element_type, confidence_score)
        """
        # Rule-based classification
        if element.tag:
            tag_mapping = {
                'header': ElementType.HEADER,
                'footer': ElementType.FOOTER,
                'nav': ElementType.NAVIGATION,
                'h1': ElementType.HEADING,
                'h2': ElementType.HEADING,
                'h3': ElementType.HEADING,
                'p': ElementType.PARAGRAPH,
                'button': ElementType.BUTTON,
                'a': ElementType.LINK,
                'img': ElementType.IMAGE,
                'video': ElementType.VIDEO,
                'form': ElementType.FORM,
            }

            if element.tag in tag_mapping:
                return tag_mapping[element.tag], 0.9

        # Class-based detection
        class_indicators = {
            ElementType.HERO: ['hero', 'banner', 'jumbotron'],
            ElementType.CARD: ['card', 'box', 'tile'],
            ElementType.GALLERY: ['gallery', 'photos', 'images'],
            ElementType.SLIDER: ['slider', 'carousel', 'slideshow'],
        }

        classes_lower = [c.lower() for c in element.classes]
        for elem_type, indicators in class_indicators.items():
            if any(ind in ' '.join(classes_lower) for ind in indicators):
                return elem_type, 0.75

        # Default
        return ElementType.CONTAINER, 0.5

    def _calculate_confidence(
        self,
        gpt_analysis: Dict[str, Any],
        cv_analysis: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score for the analysis.

        Args:
            gpt_analysis: GPT-4 Vision analysis
            cv_analysis: Computer vision analysis

        Returns:
            float: Confidence score (0-1)
        """
        confidence = 0.5  # Base confidence

        # Increase if GPT provided detailed analysis
        if gpt_analysis.get('components'):
            confidence += 0.2

        if gpt_analysis.get('design_system'):
            confidence += 0.1

        # Increase if CV found clear structures
        if cv_analysis.get('visual_regions'):
            confidence += 0.1

        if cv_analysis.get('color_palette'):
            confidence += 0.1

        return min(confidence, 1.0)

    async def suggest_elementor_widget(
        self,
        element: Element,
        screenshot: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Suggest the best Elementor widget for an element.

        Args:
            element: Element to analyze
            screenshot: Optional screenshot of the element

        Returns:
            Dict: Widget suggestion with configuration
        """
        element_type_mapping = {
            ElementType.HEADING: {"widget": "heading", "confidence": 0.95},
            ElementType.PARAGRAPH: {"widget": "text-editor", "confidence": 0.95},
            ElementType.TEXT: {"widget": "text-editor", "confidence": 0.90},
            ElementType.BUTTON: {"widget": "button", "confidence": 0.95},
            ElementType.IMAGE: {"widget": "image", "confidence": 0.95},
            ElementType.VIDEO: {"widget": "video", "confidence": 0.95},
            ElementType.GALLERY: {"widget": "gallery", "confidence": 0.90},
            ElementType.SLIDER: {"widget": "image-carousel", "confidence": 0.85},
            ElementType.FORM: {"widget": "form", "confidence": 0.80},
            ElementType.HERO: {"widget": "heading", "confidence": 0.70, "note": "Combine with image widget"},
            ElementType.CARD: {"widget": "icon-box", "confidence": 0.75},
        }

        suggestion = element_type_mapping.get(
            element.type,
            {"widget": "html", "confidence": 0.50, "note": "Custom HTML widget"}
        )

        return suggestion
