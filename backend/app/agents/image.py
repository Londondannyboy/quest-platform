"""
Quest Platform v2.3 - ImageAgent
Generates themed images with H2 overlays using Ideogram V3 Turbo + Cloudinary CDN
"""

import asyncio
import re
from decimal import Decimal
from typing import Dict, Optional, List

import replicate
import cloudinary
import cloudinary.uploader
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class ImageAgent:
    """
    Image Agent: Generate themed images with H2 text overlays

    Strategy:
    - Hero: 3:1 ultra-wide banner with article title overlay
    - Content 1-3: 16:9 images with H2 section headings as overlay text
    - Neon aesthetic: Consistent branded look across all images

    Model: Ideogram V3 Turbo (better text rendering than FLUX)
    Cost: $0.003-$0.005 per image
    Quality: Photorealistic with clean neon text overlays
    Latency: 7-10 seconds per image
    """

    # Negative prompt: Allow REQUESTED text overlays, block unwanted text
    NEGATIVE_PROMPT = "unwanted text, random words, watermark, logo, unrelated typography, low quality, blurry, distorted, amateur, cartoon, illustration, drawing, 3d render, unrealistic"

    # Image specifications by type
    IMAGE_SPECS = {
        "hero": {
            "aspect_ratio": "3:1",  # Ultra-wide banner (1344x448 or similar)
            "description": "Hero banner with article title overlay"
        },
        "content_1": {
            "aspect_ratio": "16:9",  # Standard article image
            "description": "First content section with H2 overlay"
        },
        "content_2": {
            "aspect_ratio": "16:9",
            "description": "Second content section with H2 overlay"
        },
        "content_3": {
            "aspect_ratio": "16:9",
            "description": "Third content section with H2 overlay"
        }
    }

    # Time of day variations for visual diversity
    TIMES_OF_DAY = ["golden hour", "dusk", "sunset", "twilight"]

    # Text overlay styles by article type (for CTR optimization)
    TEXT_OVERLAY_STYLES = {
        "guide": {
            "placement": "center",
            "style": "bold blocky neon text, large font, centered, authoritative",
            "description": "Central, bold, authoritative (default for guides)"
        },
        "listicle": {
            "placement": "top-left",
            "style": "edgy clickbait neon text, smaller font, corner placement, provocative",
            "description": "Corner, edgy, clickbait-style"
        },
        "how_to": {
            "placement": "top",
            "style": "clean instructional neon text, medium font, top banner, professional",
            "description": "Top banner, clean, instructional"
        },
        "comparison": {
            "placement": "center-split",
            "style": "versus-style neon text, bold, centered with divider, competitive",
            "description": "Center split, competitive vs-style"
        },
        "news": {
            "placement": "bottom-banner",
            "style": "breaking news ticker neon text, urgent font, bottom banner, dynamic",
            "description": "Bottom banner, urgent, breaking news"
        }
    }

    def __init__(self):
        # Configure Replicate with token
        import os
        os.environ["REPLICATE_API_TOKEN"] = settings.REPLICATE_API_KEY
        self.replicate_model = settings.REPLICATE_MODEL

        # Configure Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
        )

        # Site-specific image styles with neon outline aesthetic
        self.style_guides = {
            "relocation": "modern professional international cityscape with subtle neon outline glow accents, photorealistic with futuristic edge lighting",
            "placement": "professional office data visualization with neon outline highlighting key elements, clean aesthetic with glowing borders",
            "rainmaker": "entrepreneurial dynamic aspirational scene with premium neon outline accents, glowing edge highlights",
        }

        # Neon aesthetic guidance (applied to all images)
        self.neon_aesthetic = "subtle neon outline glow on key subjects, glowing edges, cyberpunk-inspired lighting accents, modern futuristic aesthetic, vibrant rim lighting"

    def _detect_article_type(self, title: str) -> str:
        """
        Detect article type from title for text overlay styling

        Simple keyword-based detection for CTR optimization

        Args:
            title: Article title

        Returns:
            Article type: "guide", "listicle", "how_to", "comparison", "news"
        """
        title_lower = title.lower()

        # Priority order matters
        if "vs" in title_lower or "versus" in title_lower or " v " in title_lower:
            return "comparison"
        elif any(word in title_lower for word in ["top ", "best ", "worst ", "cheapest ", "most expensive"]):
            return "listicle"
        elif title_lower.startswith("how to") or "step by step" in title_lower:
            return "how_to"
        elif "breaking" in title_lower or "news" in title_lower or "update" in title_lower:
            return "news"
        else:
            return "guide"  # Default

    def _extract_h2_sections(self, content: str) -> List[str]:
        """
        Extract H2 headings from markdown content for image overlays

        Args:
            content: Article markdown content

        Returns:
            List of H2 headings (excluding "Further Reading & Sources")
        """
        h2_pattern = r'^## (.+)$'
        h2_matches = re.findall(h2_pattern, content, re.MULTILINE)

        # Filter out common footer sections
        excluded = [
            "Further Reading & Sources",
            "References",
            "Sources",
            "Conclusion",
            "Summary"
        ]
        h2_sections = [h2 for h2 in h2_matches if h2 not in excluded]

        logger.info(
            "image_agent.h2_extraction",
            total_h2=len(h2_matches),
            usable_h2=len(h2_sections),
            sections=h2_sections[:3]  # Log first 3 for debugging
        )

        return h2_sections

    async def generate(
        self, article: Dict, target_site: str, slug: str
    ) -> Dict:
        """
        Generate hero + 3 content images for article

        Args:
            article: Article data with title and excerpt
            target_site: Target site (relocation/placement/rainmaker)
            slug: Article slug for CDN storage

        Returns:
            Dict with all image URLs and cost
        """
        logger.info("image_agent.start", slug=slug, target_site=target_site)

        # Skip if disabled
        if not settings.ENABLE_IMAGE_GENERATION:
            logger.info("image_agent.skipped", reason="disabled")
            return {
                "hero_image_url": None,
                "content_image_1_url": None,
                "content_image_2_url": None,
                "content_image_3_url": None,
                "cost": Decimal("0.00"),
            }

        try:
            # Step 1: Craft prompts for all 4 images (with H2 overlays)
            prompts = self._create_all_prompts(article, target_site)

            # Step 2: Generate all 4 images in parallel (~7 seconds each)
            # Hero: 3:1 ultra-wide banner, Content: 16:9 standard
            image_tasks = [
                self._generate_via_ideogram(prompts["hero"], aspect_ratio="3:1"),
                self._generate_via_ideogram(prompts["content_1"], aspect_ratio="16:9"),
                self._generate_via_ideogram(prompts["content_2"], aspect_ratio="16:9"),
                self._generate_via_ideogram(prompts["content_3"], aspect_ratio="16:9"),
            ]
            generated_urls = await asyncio.gather(*image_tasks, return_exceptions=True)

            # Step 3: Upload all to Cloudinary in parallel
            upload_tasks = []
            suffixes = ["hero", "content-1", "content-2", "content-3"]
            for i, url in enumerate(generated_urls):
                if isinstance(url, Exception):
                    upload_tasks.append(asyncio.create_task(asyncio.sleep(0)))  # Placeholder
                else:
                    upload_tasks.append(
                        self._upload_to_cloudinary(url, target_site, f"{slug}-{suffixes[i]}")
                    )

            cdn_urls = await asyncio.gather(*upload_tasks, return_exceptions=True)

            # Parse results with fallback
            result = {
                "hero_image_url": cdn_urls[0] if not isinstance(cdn_urls[0], Exception) else None,
                "content_image_1_url": cdn_urls[1] if not isinstance(cdn_urls[1], Exception) else None,
                "content_image_2_url": cdn_urls[2] if not isinstance(cdn_urls[2], Exception) else None,
                "content_image_3_url": cdn_urls[3] if not isinstance(cdn_urls[3], Exception) else None,
                "cost": Decimal("0.016"),  # 4 images × $0.004 (Ideogram V2 Turbo)
            }

            logger.info(
                "image_agent.complete",
                slug=slug,
                hero=bool(result["hero_image_url"]),
                content_images=sum([
                    bool(result["content_image_1_url"]),
                    bool(result["content_image_2_url"]),
                    bool(result["content_image_3_url"]),
                ])
            )

            return result

        except Exception as e:
            logger.error(
                "image_agent.generation_failed",
                slug=slug,
                error=str(e),
                exc_info=e,
            )

            # Graceful degradation: Article succeeds without images
            return {
                "hero_image_url": None,
                "content_image_1_url": None,
                "content_image_2_url": None,
                "content_image_3_url": None,
                "cost": Decimal("0.00"),
                "error": str(e),
            }

    def _create_prompt(self, article: Dict, target_site: str) -> str:
        """
        Craft FLUX prompt from article data

        Args:
            article: Article with title and excerpt
            target_site: Site for style guide

        Returns:
            Image generation prompt
        """
        title = article.get("title", "")
        excerpt = article.get("excerpt", "")[:100]  # Truncate
        style = self.style_guides.get(target_site, self.style_guides["relocation"])

        # Extract main subject from title (remove filler words)
        filler_words = [
            "a",
            "an",
            "the",
            "guide",
            "to",
            "how",
            "why",
            "what",
            "complete",
        ]
        subject_words = [
            w for w in title.lower().split() if w not in filler_words
        ]
        subject = " ".join(subject_words[:5])  # First 5 meaningful words

        prompt = f"""Professional editorial photograph: {subject}. {excerpt}

Style: {style}
Format: 16:9 aspect ratio, high quality, photorealistic, editorial photography, magazine cover quality
Lighting: Natural, professional
Mood: Inspirational and informative"""

        logger.debug("image_agent.prompt_created", prompt=prompt[:100])
        return prompt

    def _create_all_prompts(self, article: Dict, target_site: str) -> Dict[str, str]:
        """
        Create themed prompts with H2 overlays for all 4 images

        Strategy:
        - Hero: Article title as neon overlay on iconic landmark
        - Content 1-3: H2 section headings as neon overlays on sequential landmarks

        Magic Prompt will enhance simple prompts into detailed descriptions

        Args:
            article: Article with title and content
            target_site: Site for style guide

        Returns:
            Dict with keys: hero, content_1, content_2, content_3
        """
        title = article.get("title", "")
        content = article.get("content", "")

        # Extract location/country from title (for now, use generic descriptions)
        # TODO Phase 2: Replace with actual landmark detection via Perplexity
        topic = title.replace("Complete Guide", "").replace("2025", "").strip()

        # Detect article type for text overlay styling
        article_type = self._detect_article_type(title)
        text_style = self.TEXT_OVERLAY_STYLES[article_type]

        # Extract H2 sections for content image overlays
        h2_sections = self._extract_h2_sections(content)

        # Hero prompt: Ultra-wide banner with styled title overlay
        hero_prompt = f"""Scenic location related to {topic} at {self.TIMES_OF_DAY[0]} with {text_style['style']}: "{title}".

Text placement: {text_style['placement']}
Text should be clearly readable on both mobile and desktop.
Do not include any other text in the image."""

        # Content images: H2 overlays on sequential images
        prompts = {"hero": hero_prompt}

        for i in range(1, 4):
            # Use H2 if available, otherwise use generic description
            if i-1 < len(h2_sections):
                overlay_text = h2_sections[i-1]
            else:
                overlay_text = f"Section {i}"

            time_of_day = self.TIMES_OF_DAY[i % len(self.TIMES_OF_DAY)]

            prompts[f"content_{i}"] = f"""Scenic location related to {topic} at {time_of_day} with neon overlay text: "{overlay_text}".

Do not include any other text in the image."""

        logger.info(
            "image_agent.prompts_created",
            article_type=article_type,
            text_placement=text_style['placement'],
            hero_overlay=title[:50],
            content_overlays=[h2_sections[i][:30] if i < len(h2_sections) else f"Section {i+1}" for i in range(3)]
        )

        return prompts

    async def _generate_via_ideogram(
        self,
        prompt: str,
        aspect_ratio: str = "16:9"
    ) -> str:
        """
        Generate image via Replicate Ideogram V3 Turbo with magic prompt

        Ideogram V3 Turbo excels at:
        - Clean text rendering (neon overlays)
        - Photorealistic scenes
        - Fast generation (~7 seconds)

        Args:
            prompt: Simple image description (magic prompt will enhance)
            aspect_ratio: "3:1" (hero) or "16:9" (content)

        Returns:
            URL of generated image
        """
        try:
            output = await replicate.async_run(
                "ideogram-ai/ideogram-v2-turbo",  # Using V2 Turbo (V3 may not be available yet)
                input={
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "magic_prompt_option": "On",  # Let Replicate enhance our prompts
                    "style_type": "None",  # Photorealistic
                    "style_preset": "None",
                },
            )

            # Output is either a string URL or list
            image_url = output if isinstance(output, str) else output[0]

            logger.info(
                "image_agent.ideogram_generated",
                url=image_url[:50],
                aspect_ratio=aspect_ratio
            )
            return image_url

        except Exception as e:
            logger.error(
                "image_agent.ideogram_failed",
                error=str(e),
                aspect_ratio=aspect_ratio,
                exc_info=e
            )
            raise

    async def _upload_to_cloudinary(
        self, image_url: str, target_site: str, slug: str
    ) -> str:
        """
        Upload image to Cloudinary CDN with responsive transformations

        Preserves original aspect ratios (3:1 for hero, 16:9 for content)
        while optimizing quality and format

        Args:
            image_url: Source image URL from Replicate
            target_site: Target site (for folder organization)
            slug: Article slug (for public_id)

        Returns:
            Cloudinary CDN URL
        """
        try:
            # Determine if this is a hero image (3:1) based on slug suffix
            is_hero = slug.endswith("-hero")

            # Wrap synchronous Cloudinary upload in thread to prevent event loop blocking
            result = await asyncio.to_thread(
                cloudinary.uploader.upload,
                image_url,
                folder=f"quest/{target_site}",
                public_id=slug,
                transformation=[
                    # Preserve aspect ratio, set quality
                    {"width": 1920 if not is_hero else 1344, "crop": "limit"},
                    # Quality: Higher for hero, standard for content
                    {"quality": "auto:best" if is_hero else "auto:good"},
                    # Format optimization (WebP for modern browsers, JPG fallback)
                    {"fetch_format": "auto"},
                ],
                overwrite=True,
                timeout=10,  # Longer timeout for larger images
            )

            cdn_url = result["secure_url"]

            logger.info(
                "image_agent.cloudinary_uploaded",
                slug=slug,
                cdn_url=cdn_url,
                bytes=result.get("bytes"),
                is_hero=is_hero
            )

            return cdn_url

        except Exception as e:
            logger.error("image_agent.cloudinary_failed", error=str(e), slug=slug, exc_info=e)
            raise
