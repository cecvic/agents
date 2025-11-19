"""
AI-Powered Similarity Checker

Compares source and migrated websites to ensure 90%+ fidelity in:
- Visual appearance
- Layout structure
- Content accuracy
- Functional elements
"""

import base64
from io import BytesIO
from typing import Dict, List, Optional, Tuple
import logging

from PIL import Image
import numpy as np
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error as mse
import openai

from ..idf.schema import IDF, Page, Element


logger = logging.getLogger(__name__)


class SimilarityChecker:
    """
    Multi-dimensional similarity checker for website migrations.

    Evaluates:
    1. Visual Similarity (screenshot comparison)
    2. Structural Similarity (DOM/element tree comparison)
    3. Content Similarity (text and asset matching)
    4. Functional Similarity (interaction elements)

    Target: 90%+ overall similarity score
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the similarity checker.

        Args:
            api_key: OpenAI API key for AI-powered comparison
        """
        self.api_key = api_key
        if api_key:
            openai.api_key = api_key

    async def check_similarity(
        self,
        source_screenshot: bytes,
        target_screenshot: bytes,
        source_idf: IDF,
        target_idf: IDF,
    ) -> Dict[str, Any]:
        """
        Comprehensive similarity check between source and target.

        Args:
            source_screenshot: Screenshot of original site
            target_screenshot: Screenshot of migrated site
            source_idf: IDF of source site
            target_idf: IDF of target site

        Returns:
            Dict: Detailed similarity report with scores
        """
        logger.info("Starting comprehensive similarity check")

        # 1. Visual Similarity
        visual_score = await self._check_visual_similarity(
            source_screenshot,
            target_screenshot
        )

        # 2. Structural Similarity
        structural_score = self._check_structural_similarity(
            source_idf,
            target_idf
        )

        # 3. Content Similarity
        content_score = self._check_content_similarity(
            source_idf,
            target_idf
        )

        # 4. Asset Similarity
        asset_score = self._check_asset_similarity(
            source_idf,
            target_idf
        )

        # 5. AI-Powered Semantic Similarity
        semantic_score = await self._check_semantic_similarity(
            source_screenshot,
            target_screenshot,
            source_idf,
            target_idf
        )

        # Calculate weighted overall score
        overall_score = self._calculate_overall_score({
            'visual': visual_score,
            'structural': structural_score,
            'content': content_score,
            'asset': asset_score,
            'semantic': semantic_score,
        })

        report = {
            "overall_score": overall_score,
            "meets_target": overall_score >= 0.90,
            "target_score": 0.90,
            "scores": {
                "visual": visual_score,
                "structural": structural_score,
                "content": content_score,
                "asset": asset_score,
                "semantic": semantic_score,
            },
            "details": {
                "visual_details": visual_score.get('details', {}),
                "structural_details": structural_score.get('details', {}),
                "content_details": content_score.get('details', {}),
            },
            "recommendations": self._generate_recommendations(
                overall_score,
                {
                    'visual': visual_score,
                    'structural': structural_score,
                    'content': content_score,
                    'asset': asset_score,
                }
            ),
        }

        logger.info(f"Similarity check complete. Overall score: {overall_score:.2%}")
        return report

    async def _check_visual_similarity(
        self,
        source_screenshot: bytes,
        target_screenshot: bytes
    ) -> Dict[str, Any]:
        """
        Compare visual appearance using image similarity metrics.

        Args:
            source_screenshot: Source screenshot bytes
            target_screenshot: Target screenshot bytes

        Returns:
            Dict: Visual similarity score and details
        """
        logger.info("Checking visual similarity...")

        try:
            # Load images
            source_img = Image.open(BytesIO(source_screenshot))
            target_img = Image.open(BytesIO(target_screenshot))

            # Resize to same dimensions for comparison
            target_size = (1920, max(source_img.height, target_img.height))
            source_resized = source_img.resize(target_size)
            target_resized = target_img.resize(target_size)

            # Convert to grayscale numpy arrays
            source_array = np.array(source_resized.convert('L'))
            target_array = np.array(target_resized.convert('L'))

            # Calculate SSIM (Structural Similarity Index)
            ssim_score = ssim(source_array, target_array)

            # Calculate MSE (Mean Squared Error)
            mse_score = mse(source_array, target_array)

            # Normalize MSE to 0-1 scale (lower is better, so invert)
            max_mse = 255 ** 2
            normalized_mse = 1 - (mse_score / max_mse)

            # Color histogram similarity
            color_similarity = self._compare_color_histograms(source_img, target_img)

            # Weighted average
            visual_score = (
                ssim_score * 0.5 +
                normalized_mse * 0.3 +
                color_similarity * 0.2
            )

            return {
                "score": visual_score,
                "details": {
                    "ssim": ssim_score,
                    "mse": mse_score,
                    "normalized_mse": normalized_mse,
                    "color_similarity": color_similarity,
                },
            }

        except Exception as e:
            logger.error(f"Error in visual similarity check: {str(e)}")
            return {"score": 0.0, "error": str(e)}

    def _compare_color_histograms(
        self,
        img1: Image.Image,
        img2: Image.Image
    ) -> float:
        """
        Compare color histograms of two images.

        Args:
            img1: First image
            img2: Second image

        Returns:
            float: Similarity score (0-1)
        """
        # Calculate histograms
        hist1 = img1.histogram()
        hist2 = img2.histogram()

        # Calculate correlation
        sum_squares = sum((h1 - h2) ** 2 for h1, h2 in zip(hist1, hist2))
        norm = sum(h ** 2 for h in hist1) + sum(h ** 2 for h in hist2)

        if norm == 0:
            return 0.0

        similarity = 1 - (sum_squares / norm)
        return max(0, similarity)

    def _check_structural_similarity(
        self,
        source_idf: IDF,
        target_idf: IDF
    ) -> Dict[str, Any]:
        """
        Compare structural similarity of element trees.

        Args:
            source_idf: Source IDF
            target_idf: Target IDF

        Returns:
            Dict: Structural similarity score and details
        """
        logger.info("Checking structural similarity...")

        # Compare number of pages
        page_count_similarity = min(
            len(source_idf.pages),
            len(target_idf.pages)
        ) / max(len(source_idf.pages), len(target_idf.pages))

        # Compare element counts per page
        element_similarities = []
        for i, source_page in enumerate(source_idf.pages):
            if i < len(target_idf.pages):
                target_page = target_idf.pages[i]
                source_elem_count = len(self._get_all_elements(source_page.elements))
                target_elem_count = len(self._get_all_elements(target_page.elements))

                elem_similarity = min(source_elem_count, target_elem_count) / max(
                    source_elem_count, target_elem_count
                )
                element_similarities.append(elem_similarity)

        avg_element_similarity = (
            sum(element_similarities) / len(element_similarities)
            if element_similarities else 0
        )

        # Compare element type distributions
        type_similarity = self._compare_element_type_distributions(
            source_idf,
            target_idf
        )

        # Calculate overall structural score
        structural_score = (
            page_count_similarity * 0.2 +
            avg_element_similarity * 0.4 +
            type_similarity * 0.4
        )

        return {
            "score": structural_score,
            "details": {
                "page_count_similarity": page_count_similarity,
                "element_count_similarity": avg_element_similarity,
                "element_type_similarity": type_similarity,
                "source_pages": len(source_idf.pages),
                "target_pages": len(target_idf.pages),
            },
        }

    def _compare_element_type_distributions(
        self,
        source_idf: IDF,
        target_idf: IDF
    ) -> float:
        """
        Compare the distribution of element types.

        Args:
            source_idf: Source IDF
            target_idf: Target IDF

        Returns:
            float: Type distribution similarity (0-1)
        """
        from collections import Counter

        # Get all element types from both
        source_types = []
        target_types = []

        for page in source_idf.pages:
            for elem in self._get_all_elements(page.elements):
                source_types.append(elem.type)

        for page in target_idf.pages:
            for elem in self._get_all_elements(page.elements):
                target_types.append(elem.type)

        # Count frequencies
        source_counts = Counter(source_types)
        target_counts = Counter(target_types)

        # Calculate similarity using cosine similarity
        all_types = set(source_counts.keys()) | set(target_counts.keys())

        if not all_types:
            return 1.0

        dot_product = sum(
            source_counts.get(t, 0) * target_counts.get(t, 0)
            for t in all_types
        )

        source_magnitude = sum(c ** 2 for c in source_counts.values()) ** 0.5
        target_magnitude = sum(c ** 2 for c in target_counts.values()) ** 0.5

        if source_magnitude == 0 or target_magnitude == 0:
            return 0.0

        similarity = dot_product / (source_magnitude * target_magnitude)
        return similarity

    def _check_content_similarity(
        self,
        source_idf: IDF,
        target_idf: IDF
    ) -> Dict[str, Any]:
        """
        Compare text content similarity.

        Args:
            source_idf: Source IDF
            target_idf: Target IDF

        Returns:
            Dict: Content similarity score and details
        """
        logger.info("Checking content similarity...")

        # Extract all text content
        source_texts = self._extract_all_text(source_idf)
        target_texts = self._extract_all_text(target_idf)

        # Calculate text similarity
        text_similarity = self._calculate_text_similarity(
            ' '.join(source_texts),
            ' '.join(target_texts)
        )

        # Compare text lengths
        source_length = sum(len(t) for t in source_texts)
        target_length = sum(len(t) for t in target_texts)

        length_similarity = min(source_length, target_length) / max(
            source_length, target_length, 1
        )

        # Overall content score
        content_score = (
            text_similarity * 0.7 +
            length_similarity * 0.3
        )

        return {
            "score": content_score,
            "details": {
                "text_similarity": text_similarity,
                "length_similarity": length_similarity,
                "source_text_length": source_length,
                "target_text_length": target_length,
            },
        }

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            float: Similarity score (0-1)
        """
        from difflib import SequenceMatcher

        # Use SequenceMatcher for simple similarity
        similarity = SequenceMatcher(None, text1, text2).ratio()

        return similarity

    def _check_asset_similarity(
        self,
        source_idf: IDF,
        target_idf: IDF
    ) -> Dict[str, Any]:
        """
        Compare assets (images, videos, etc.).

        Args:
            source_idf: Source IDF
            target_idf: Target IDF

        Returns:
            Dict: Asset similarity score
        """
        logger.info("Checking asset similarity...")

        source_assets = source_idf.get_all_assets()
        target_assets = target_idf.get_all_assets()

        # Compare counts
        asset_count_similarity = min(
            len(source_assets),
            len(target_assets)
        ) / max(len(source_assets), len(target_assets), 1)

        # Compare types
        source_types = [a.type for a in source_assets]
        target_types = [a.type for a in target_assets]

        type_matches = sum(
            1 for st in source_types if st in target_types
        )
        type_similarity = type_matches / max(len(source_types), 1)

        asset_score = (
            asset_count_similarity * 0.5 +
            type_similarity * 0.5
        )

        return {
            "score": asset_score,
            "details": {
                "count_similarity": asset_count_similarity,
                "type_similarity": type_similarity,
                "source_asset_count": len(source_assets),
                "target_asset_count": len(target_assets),
            },
        }

    async def _check_semantic_similarity(
        self,
        source_screenshot: bytes,
        target_screenshot: bytes,
        source_idf: IDF,
        target_idf: IDF
    ) -> Dict[str, Any]:
        """
        Use GPT-4 Vision for semantic similarity comparison.

        Args:
            source_screenshot: Source screenshot
            target_screenshot: Target screenshot
            source_idf: Source IDF
            target_idf: Target IDF

        Returns:
            Dict: Semantic similarity score
        """
        logger.info("Checking semantic similarity with AI...")

        try:
            # Encode screenshots
            source_b64 = base64.b64encode(source_screenshot).decode('utf-8')
            target_b64 = base64.b64encode(target_screenshot).decode('utf-8')

            # Create comparison prompt
            prompt = f"""Compare these two website screenshots and evaluate their similarity.

The first image is the ORIGINAL website, and the second is the MIGRATED version.

Evaluate similarity in these areas (scale 0-10 for each):
1. **Layout Similarity**: Are sections arranged similarly?
2. **Visual Hierarchy**: Is the importance of elements preserved?
3. **Color Scheme**: Do colors match?
4. **Typography**: Are fonts and text styles similar?
5. **Spacing**: Is whitespace and padding similar?
6. **Component Placement**: Are key components (nav, hero, footer, etc.) in similar positions?

Provide scores and brief explanation for each area.

Respond in JSON format:
{{
  "layout_similarity": 0-10,
  "visual_hierarchy": 0-10,
  "color_scheme": 0-10,
  "typography": 0-10,
  "spacing": 0-10,
  "component_placement": 0-10,
  "overall_impression": "brief description",
  "notable_differences": ["difference 1", "difference 2", ...]
}}
"""

            response = await openai.ChatCompletion.acreate(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{source_b64}",
                                    "detail": "high"
                                }
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{target_b64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.2,
            )

            result_text = response.choices[0].message.content

            # Parse JSON response
            import json
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())

                # Calculate average score (normalized to 0-1)
                scores = [
                    result.get('layout_similarity', 0),
                    result.get('visual_hierarchy', 0),
                    result.get('color_scheme', 0),
                    result.get('typography', 0),
                    result.get('spacing', 0),
                    result.get('component_placement', 0),
                ]

                avg_score = sum(scores) / (len(scores) * 10)  # Normalize to 0-1

                return {
                    "score": avg_score,
                    "details": result,
                }

            return {"score": 0.5, "details": {"raw_response": result_text}}

        except Exception as e:
            logger.error(f"Error in semantic similarity check: {str(e)}")
            return {"score": 0.5, "error": str(e)}

    def _calculate_overall_score(self, scores: Dict[str, Any]) -> float:
        """
        Calculate weighted overall similarity score.

        Args:
            scores: Individual category scores

        Returns:
            float: Overall score (0-1)
        """
        # Weights for each category
        weights = {
            'visual': 0.35,      # Most important - how it looks
            'structural': 0.20,   # Element hierarchy
            'content': 0.20,      # Text content
            'asset': 0.10,        # Images/media
            'semantic': 0.15,     # AI understanding
        }

        overall = sum(
            scores[category].get('score', 0) * weight
            for category, weight in weights.items()
        )

        return overall

    def _generate_recommendations(
        self,
        overall_score: float,
        category_scores: Dict[str, Any]
    ) -> List[str]:
        """
        Generate recommendations for improvement.

        Args:
            overall_score: Overall similarity score
            category_scores: Individual category scores

        Returns:
            List[str]: Recommendations
        """
        recommendations = []

        if overall_score >= 0.90:
            recommendations.append("✅ Excellent migration! Target similarity achieved.")
        elif overall_score >= 0.80:
            recommendations.append("⚠️ Good migration, but some improvements needed.")
        else:
            recommendations.append("❌ Significant differences detected. Manual review required.")

        # Category-specific recommendations
        for category, data in category_scores.items():
            score = data.get('score', 0)
            if score < 0.70:
                recommendations.append(
                    f"• {category.capitalize()}: Score {score:.2%} - Needs improvement"
                )

        return recommendations

    def _get_all_elements(self, elements: List[Element]) -> List[Element]:
        """Recursively get all elements"""
        all_elements = []
        for elem in elements:
            all_elements.append(elem)
            if elem.children:
                all_elements.extend(self._get_all_elements(elem.children))
        return all_elements

    def _extract_all_text(self, idf: IDF) -> List[str]:
        """Extract all text content from IDF"""
        texts = []
        for page in idf.pages:
            for elem in self._get_all_elements(page.elements):
                if elem.content:
                    texts.append(elem.content)
        return texts
