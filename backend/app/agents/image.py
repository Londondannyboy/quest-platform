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

    def __init__(self):
        # Configure Replicate
        self.replicate_token = settings.REPLICATE_API_KEY
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
        Generate hero image for article

        Args:
            article: Article data with title and excerpt
            target_site: Target site (relocation/placement/rainmaker)
            slug: Article slug for CDN storage

        Returns:
            Dict with image URL and cost
        """
        logger.info("image_agent.start", slug=slug, target_site=target_site)

        # Skip if disabled
        if not settings.ENABLE_IMAGE_GENERATION:
            logger.info("image_agent.skipped", reason="disabled")
            return {
                "hero_image_url": None,
                "cost": Decimal("0.00"),
            }

        try:
            # Step 1: Craft image prompt
            prompt = self._create_prompt(article, target_site)

            # Step 2: Generate via FLUX
            image_url = await self._generate_via_flux(prompt)

            # Step 3: Upload to Cloudinary
            cdn_url = await self._upload_to_cloudinary(
                image_url, target_site, slug
            )

            logger.info(
                "image_agent.complete",
                slug=slug,
                cdn_url=cdn_url,
            )

            return {
                "hero_image_url": cdn_url,
                "cost": Decimal("0.003"),  # Replicate FLUX cost
            }

        except Exception as e:
            logger.error(
                "image_agent.generation_failed",
                slug=slug,
                error=str(e),
                exc_info=e,
            )

            # Graceful degradation: Article succeeds without image
            return {
                "hero_image_url": None,
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
