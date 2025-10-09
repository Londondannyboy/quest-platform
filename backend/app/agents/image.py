"""
Quest Platform v2.2 - ImageAgent
Generates hero images using FLUX Schnell via Replicate + Cloudinary CDN
"""

import asyncio
from decimal import Decimal
from typing import Dict, Optional

import replicate
import cloudinary
import cloudinary.uploader
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class ImageAgent:
    """
    Image Agent: Generate hero images with FLUX Schnell

    Cost: $0.003 per image
    Quality: Photorealistic, suitable for hero images
    Latency: 30-60 seconds
    """

    # Negative prompt for quality control (what to avoid)
    NEGATIVE_PROMPT = "low quality, blurry, distorted, watermark, text overlay, amateur, cartoon, illustration, drawing, 3d render, unrealistic"

    # Image specifications by type
    IMAGE_SPECS = {
        "hero": {
            "aspect_ratio": "16:9",
            "description": "Wide hero image - vibrant, professional, business context"
        },
        "content_1": {
            "aspect_ratio": "16:9",
            "description": "Infographic or process diagram - clear visual hierarchy"
        },
        "content_2": {
            "aspect_ratio": "16:9",
            "description": "Business scene with people - modern office or location"
        },
        "content_3": {
            "aspect_ratio": "16:9",
            "description": "Visual metaphor - symbolic representation, clean composition"
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

        # Site-specific image styles
        self.style_guides = {
            "relocation": "modern, professional, international cityscape, photorealistic",
            "placement": "professional office, data visualization, business setting, clean aesthetic",
            "rainmaker": "entrepreneurial, dynamic, aspirational, premium aesthetic",
        }

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
            # Step 1: Craft prompts for all 4 images
            prompts = self._create_all_prompts(article, target_site)

            # Step 2: Generate all 4 images in parallel (60s total instead of 240s)
            image_tasks = [
                self._generate_via_flux(prompts["hero"]),
                self._generate_via_flux(prompts["content_1"]),
                self._generate_via_flux(prompts["content_2"]),
                self._generate_via_flux(prompts["content_3"]),
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
                "cost": Decimal("0.012"),  # 4 images × $0.003
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
        Create specialized prompts for all 4 images (hero + 3 content)

        Each image type has a specific purpose:
        - Hero: Wide, vibrant, attention-grabbing main image
        - Content 1: Infographic or diagram style
        - Content 2: People/scene oriented
        - Content 3: Conceptual/metaphor

        Args:
            article: Article with title and content
            target_site: Site for style guide

        Returns:
            Dict with keys: hero, content_1, content_2, content_3
        """
        title = article.get("title", "")
        content = article.get("content", "")
        style = self.style_guides.get(target_site, self.style_guides["relocation"])

        # Extract topic from title
        topic = title.replace("Complete Guide", "").replace("2025", "").strip()

        # Hero prompt (main topic) - Wide, vibrant, business context
        hero_prompt = f"""Professional editorial photograph about {topic}.
{self.IMAGE_SPECS['hero']['description']}

Style: {style}, vibrant colors, wide composition
Format: 16:9 aspect ratio, high quality, photorealistic, 4k resolution
Lighting: Natural, professional, golden hour
Mood: Inspirational and authoritative

AVOID: {self.NEGATIVE_PROMPT}"""

        # Content image 1: Infographic/diagram style - Clear visual hierarchy
        content_1_prompt = f"""Detailed infographic or diagram showing the process of {topic}.
{self.IMAGE_SPECS['content_1']['description']}

Style: {style}, clean layout, informative
Format: 16:9 aspect ratio, high quality, clear visual hierarchy
Visual elements: Charts, icons, step-by-step flow
Mood: Educational and professional

AVOID: {self.NEGATIVE_PROMPT}"""

        # Content image 2: Business scene with people - Modern office/location
        content_2_prompt = f"""Professional business scene related to {topic}.
{self.IMAGE_SPECS['content_2']['description']}

Style: {style}, people working together, modern setting
Format: 16:9 aspect ratio, high quality, photorealistic
Scene: Professional office environment or relevant location
Mood: Collaborative and productive

AVOID: {self.NEGATIVE_PROMPT}"""

        # Content image 3: Visual metaphor - Symbolic, clean composition
        content_3_prompt = f"""Visual metaphor or conceptual image representing {topic}.
{self.IMAGE_SPECS['content_3']['description']}

Style: {style}, symbolic, minimalist
Format: 16:9 aspect ratio, high quality, artistic photorealistic
Composition: Clean, focused, meaningful symbolism
Mood: Thoughtful and sophisticated

AVOID: {self.NEGATIVE_PROMPT}"""

        return {
            "hero": hero_prompt,
            "content_1": content_1_prompt,
            "content_2": content_2_prompt,
            "content_3": content_3_prompt,
        }

    async def _generate_via_flux(self, prompt: str) -> str:
        """
        Generate image via Replicate FLUX Schnell

        Args:
            prompt: Image generation prompt

        Returns:
            URL of generated image
        """
        try:
            output = await replicate.async_run(
                self.replicate_model,
                input={
                    "prompt": prompt,
                    "num_outputs": 1,
                    "aspect_ratio": "16:9",
                    "output_format": "jpg",
                    "output_quality": 90,
                },
            )

            # Output is a list of URLs
            image_url = output[0] if isinstance(output, list) else output

            logger.info("image_agent.flux_generated", url=image_url[:50])
            return image_url

        except Exception as e:
            logger.error("image_agent.flux_failed", error=str(e), exc_info=e)
            raise

    async def _upload_to_cloudinary(
        self, image_url: str, target_site: str, slug: str
    ) -> str:
        """
        Upload image to Cloudinary CDN with transformations

        Args:
            image_url: Source image URL from Replicate
            target_site: Target site (for folder organization)
            slug: Article slug (for public_id)

        Returns:
            Cloudinary CDN URL
        """
        try:
            # Wrap synchronous Cloudinary upload in thread to prevent event loop blocking
            # This prevents 100-500ms blocking for every concurrent request
            result = await asyncio.to_thread(
                cloudinary.uploader.upload,
                image_url,
                folder=f"quest/{target_site}",
                public_id=slug,
                transformation=[
                    # Resize and crop
                    {"width": 1200, "height": 675, "crop": "fill", "gravity": "auto"},
                    # Quality optimization
                    {"quality": "auto"},
                    # Format optimization
                    {"fetch_format": "auto"},
                ],
                overwrite=True,
                timeout=5,  # 5 second timeout to prevent hanging
            )

            cdn_url = result["secure_url"]

            logger.info(
                "image_agent.cloudinary_uploaded",
                slug=slug,
                cdn_url=cdn_url,
                bytes=result.get("bytes"),
            )

            return cdn_url

        except Exception as e:
            logger.error("image_agent.cloudinary_failed", error=str(e), exc_info=e)
            raise
