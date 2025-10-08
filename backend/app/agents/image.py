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
        Create prompts for all 4 images (hero + 3 content)

        Args:
            article: Article with title and content
            target_site: Site for style guide

        Returns:
            Dict with keys: hero, content_1, content_2, content_3
        """
        title = article.get("title", "")
        content = article.get("content", "")
        style = self.style_guides.get(target_site, self.style_guides["relocation"])

        # Extract sections from content for varied images
        sections = content.split('\n\n')[:10] if content else []

        # Hero prompt (main topic)
        hero_prompt = self._create_prompt(article, target_site)

        # Content image 1: Focus on first major section
        content_1_context = sections[1] if len(sections) > 1 else title
        content_1_prompt = f"""Professional editorial photograph illustrating: {content_1_context[:150]}

Style: {style}
Format: 16:9 aspect ratio, high quality, photorealistic
Lighting: Natural, professional
Mood: Engaging and informative"""

        # Content image 2: Mid-article visual
        content_2_context = sections[3] if len(sections) > 3 else f"{title} - practical aspects"
        content_2_prompt = f"""Professional editorial photograph showing: {content_2_context[:150]}

Style: {style}
Format: 16:9 aspect ratio, high quality, photorealistic
Lighting: Natural, professional
Mood: Practical and helpful"""

        # Content image 3: Supporting visual
        content_3_context = sections[5] if len(sections) > 5 else f"{title} - key details"
        content_3_prompt = f"""Professional editorial photograph depicting: {content_3_context[:150]}

Style: {style}
Format: 16:9 aspect ratio, high quality, photorealistic
Lighting: Natural, professional
Mood: Detailed and informative"""

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
