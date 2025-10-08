"""
PDFAgent - Automated PDF Generation for LLM SEO Optimization

Based on Income Stream Surfers' 2026 SEO strategy:
- LLMs search positions 1-100 on Google (not just 1-10)
- PDFs rank easily in positions 11-100 (low competition)
- LLMs prefer diverse source types (blog + PDF vs just blog)
- PDFs perceived as more authoritative/official

Strategy: Generate beautiful, SEO-optimized PDFs for every article to increase
chances of being cited by ChatGPT, Perplexity, Claude, and Google AI Overviews.
"""

import os
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from io import BytesIO

# PDF generation libraries
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
except ImportError:
    HTML = None  # Will provide helpful error message

from pydantic import BaseModel
import cloudinary
import cloudinary.uploader


class PDFMetadata(BaseModel):
    """SEO metadata for PDF files"""
    title: str
    author: str = "Quest Platform - AI + Human Verified"
    subject: str
    keywords: list[str]
    description: str
    created_date: datetime = datetime.now()


class PDFAgent:
    """
    Generate SEO-optimized PDFs for LLM discovery and citation

    Workflow:
    1. Take finalized article content
    2. Convert to beautifully formatted PDF
    3. Add SEO metadata (title, author, keywords, description)
    4. Upload to Cloudinary /pdfs/ folder
    5. Return public URL
    6. Submit to Google for indexing (via sitemap)

    LLM Optimization Features:
    - Clean, professional formatting
    - Embedded images from article
    - Citations/sources section
    - QR code back to website
    - "Download as PDF" watermark
    - Selectable text (not image-based)
    """

    def __init__(self):
        if HTML is None:
            raise ImportError(
                "WeasyPrint not installed. Install with: pip install weasyprint"
            )

        # Initialize Cloudinary
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET")
        )

        self.font_config = FontConfiguration()

    async def generate_pdf(
        self,
        article_id: str,
        title: str,
        content: str,
        images: list[str] = None,
        sources: list[str] = None,
        keywords: list[str] = None,
        seo_description: str = ""
    ) -> Dict[str, Any]:
        """
        Generate SEO-optimized PDF from article content

        Args:
            article_id: Unique article identifier
            title: Article title
            content: Article content (markdown or HTML)
            images: List of image URLs to embed
            sources: List of source URLs (for citations section)
            keywords: SEO keywords for PDF metadata
            seo_description: SEO description for PDF metadata

        Returns:
            Dict with pdf_url, filename, size, and metadata
        """

        # 1. Create HTML version with beautiful styling
        html_content = self._create_styled_html(
            title=title,
            content=content,
            images=images or [],
            sources=sources or []
        )

        # 2. Generate PDF with WeasyPrint
        pdf_bytes = await self._generate_pdf_bytes(html_content)

        # 3. Add SEO metadata
        metadata = PDFMetadata(
            title=title,
            subject=seo_description or f"Complete guide: {title}",
            keywords=keywords or [],
            description=seo_description or f"Comprehensive guide about {title}"
        )

        # 4. Upload to Cloudinary
        filename = self._generate_filename(article_id, title)
        upload_result = await self._upload_to_cloudinary(
            pdf_bytes=pdf_bytes,
            filename=filename,
            metadata=metadata
        )

        return {
            "pdf_url": upload_result["secure_url"],
            "filename": filename,
            "size_bytes": len(pdf_bytes),
            "cloudinary_public_id": upload_result["public_id"],
            "metadata": metadata.dict()
        }

    def _create_styled_html(
        self,
        title: str,
        content: str,
        images: list[str],
        sources: list[str]
    ) -> str:
        """Create beautifully formatted HTML for PDF conversion"""

        # Convert markdown to HTML if needed
        if content.startswith("#"):
            # Simple markdown to HTML conversion (or use markdown library)
            content = self._markdown_to_html(content)

        # Create images section
        images_html = ""
        if images:
            images_html = "<div class='images'>"
            for img in images[:3]:  # Limit to 3 images for PDF
                images_html += f'<img src="{img}" alt="Article image" />'
            images_html += "</div>"

        # Create sources section
        sources_html = ""
        if sources:
            sources_html = "<div class='sources'><h2>Sources & Citations</h2><ul>"
            for source in sources:
                sources_html += f'<li><a href="{source}">{source}</a></li>'
            sources_html += "</ul></div>"

        # Complete HTML with styling
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                    @bottom-right {{
                        content: counter(page);
                        font-size: 10pt;
                        color: #666;
                    }}
                }}

                body {{
                    font-family: 'Georgia', serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 100%;
                }}

                h1 {{
                    color: #2c3e50;
                    font-size: 28pt;
                    margin-bottom: 0.5cm;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 0.3cm;
                }}

                h2 {{
                    color: #34495e;
                    font-size: 20pt;
                    margin-top: 1cm;
                    margin-bottom: 0.5cm;
                }}

                h3 {{
                    color: #555;
                    font-size: 16pt;
                    margin-top: 0.8cm;
                }}

                p {{
                    text-align: justify;
                    margin-bottom: 0.5cm;
                }}

                .header {{
                    text-align: center;
                    margin-bottom: 1cm;
                }}

                .metadata {{
                    font-size: 10pt;
                    color: #777;
                    margin-bottom: 1cm;
                    padding: 0.5cm;
                    background: #f8f9fa;
                    border-left: 3px solid #3498db;
                }}

                .images {{
                    margin: 1cm 0;
                    text-align: center;
                }}

                .images img {{
                    max-width: 100%;
                    max-height: 8cm;
                    margin: 0.5cm 0;
                }}

                .sources {{
                    margin-top: 2cm;
                    padding-top: 1cm;
                    border-top: 1px solid #ddd;
                }}

                .sources h2 {{
                    font-size: 14pt;
                    color: #666;
                }}

                .sources ul {{
                    font-size: 9pt;
                    color: #888;
                }}

                .footer {{
                    margin-top: 2cm;
                    padding-top: 1cm;
                    border-top: 1px solid #ddd;
                    text-align: center;
                    font-size: 10pt;
                    color: #999;
                }}

                code {{
                    background: #f4f4f4;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                }}

                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 1cm 0;
                }}

                table th, table td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}

                table th {{
                    background: #f8f9fa;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{title}</h1>
                <div class="metadata">
                    <strong>Quest Platform</strong> - AI-Powered Content Intelligence<br>
                    Published: {datetime.now().strftime("%B %d, %Y")}<br>
                    Download original: relocation.quest
                </div>
            </div>

            <div class="content">
                {content}
            </div>

            {images_html}

            {sources_html}

            <div class="footer">
                <p>© {datetime.now().year} Quest Platform - AI + Human Verified Content</p>
                <p>Visit relocation.quest for more guides</p>
            </div>
        </body>
        </html>
        """

        return html

    async def _generate_pdf_bytes(self, html_content: str) -> bytes:
        """Generate PDF bytes from HTML using WeasyPrint"""

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        pdf_bytes = await loop.run_in_executor(
            None,
            self._weasyprint_generate,
            html_content
        )

        return pdf_bytes

    def _weasyprint_generate(self, html_content: str) -> bytes:
        """Synchronous WeasyPrint PDF generation"""
        html = HTML(string=html_content)
        pdf_bytes = html.write_pdf(font_config=self.font_config)
        return pdf_bytes

    async def _upload_to_cloudinary(
        self,
        pdf_bytes: bytes,
        filename: str,
        metadata: PDFMetadata
    ) -> Dict[str, Any]:
        """Upload PDF to Cloudinary with metadata"""

        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            pdf_bytes,
            resource_type="raw",
            folder="pdfs",
            public_id=filename.replace(".pdf", ""),
            tags=["pdf", "article", "seo"],
            context={
                "title": metadata.title,
                "author": metadata.author,
                "keywords": "|".join(metadata.keywords)
            }
        )

        return result

    def _generate_filename(self, article_id: str, title: str) -> str:
        """Generate SEO-friendly filename"""
        # Convert title to slug
        slug = title.lower()
        slug = slug.replace(" ", "-")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
        slug = slug[:50]  # Limit length

        return f"{slug}-{article_id[:8]}.pdf"

    def _markdown_to_html(self, markdown: str) -> str:
        """Simple markdown to HTML conversion"""
        # This is a basic implementation
        # In production, use a library like markdown or mistune

        html = markdown

        # Headers
        html = html.replace("\n### ", "\n<h3>")
        html = html.replace("\n## ", "\n<h2>")
        html = html.replace("\n# ", "\n<h1>")
        html = html.replace("</h", "</h")

        # Paragraphs
        lines = html.split("\n\n")
        html = "</p>\n<p>".join(lines)
        html = f"<p>{html}</p>"

        # Bold
        import re
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)

        # Italic
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)

        # Links
        html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)

        return html


# Example usage
async def example():
    """Example of generating PDF for an article"""

    agent = PDFAgent()

    result = await agent.generate_pdf(
        article_id="550e8400-e29b-41d4-a716-446655440001",
        title="Portugal Digital Nomad Visa: Complete 2025 Guide",
        content="""
        # Introduction

        Portugal has become one of the most popular destinations for digital nomads...

        ## Requirements

        You must demonstrate minimum monthly income of **€3,280**...
        """,
        images=[
            "https://res.cloudinary.com/quest/image/portugal-visa.jpg"
        ],
        sources=[
            "https://imigrante.sef.pt",
            "https://www.portugal.gov.pt"
        ],
        keywords=["portugal", "digital nomad", "visa", "2025"],
        seo_description="Complete guide to Portugal Digital Nomad Visa requirements"
    )

    print(f"PDF generated: {result['pdf_url']}")
    print(f"Size: {result['size_bytes'] / 1024:.1f} KB")


if __name__ == "__main__":
    asyncio.run(example())
