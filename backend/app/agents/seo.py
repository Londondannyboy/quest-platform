"""
SEOEnhancer - LLM-Optimized JSON Schema Generation

Based on Income Stream Surfers' 2026 SEO strategy:
- LLMs read JSON schema FIRST (in <head> tag) before body content
- Google stopped caring about verbose schema, but LLMs still prioritize it
- More aggressive schema = better LLM understanding = higher citation chance

Strategy: Create verbose, LLM-first JSON schema that includes FAQs, mentions,
citations, and rich metadata to help ChatGPT, Perplexity, and Claude understand
article context immediately.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class EntityMention(BaseModel):
    """Entity mentioned in article (person, place, organization)"""
    type: str  # Person, Place, Organization, Event, etc.
    name: str
    same_as: Optional[str] = None  # Wikipedia or authoritative URL


class FAQItem(BaseModel):
    """FAQ question-answer pair"""
    question: str
    answer: str


class SEOEnhancer:
    """
    Generate LLM-optimized JSON schema for articles

    Key Differences from Google-Safe Schema:
    1. More verbose descriptions (LLMs don't penalize verbosity)
    2. Include FAQ section (LLMs love Q&A format)
    3. Rich entity mentions (helps LLMs understand context)
    4. All source citations (LLMs prefer cited content)
    5. Detailed about/mentions fields

    LLMs read this schema BEFORE the article body, so it's critical
    for helping them understand what the article is about.
    """

    def generate_article_schema(
        self,
        title: str,
        description: str,
        content: str,
        author: str = "Quest Platform",
        published_date: datetime = None,
        modified_date: datetime = None,
        url: str = "",
        image_url: str = "",
        keywords: List[str] = None,
        entities: List[EntityMention] = None,
        faqs: List[FAQItem] = None,
        citations: List[str] = None,
        word_count: int = 0
    ) -> str:
        """
        Generate comprehensive JSON-LD schema for LLM optimization

        Args:
            title: Article title
            description: SEO description (be verbose for LLMs)
            content: Article content (first 500 chars for description)
            author: Author name or organization
            published_date: Publication date
            modified_date: Last modified date
            url: Canonical URL
            image_url: Featured image URL
            keywords: List of keywords/topics
            entities: List of entities mentioned (people, places, orgs)
            faqs: List of FAQ items
            citations: List of source URLs cited
            word_count: Article word count

        Returns:
            JSON-LD schema as string (ready to embed in <head>)
        """

        published_date = published_date or datetime.now()
        modified_date = modified_date or published_date

        # Build base article schema
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": description,
            "articleBody": content[:500] + "...",  # Preview for LLMs
            "url": url,
            "datePublished": published_date.isoformat(),
            "dateModified": modified_date.isoformat(),
            "wordCount": word_count,

            # Author information
            "author": {
                "@type": "Organization",
                "name": author,
                "description": "AI-powered content intelligence platform with human verification and quality gates",
                "url": "https://relocation.quest"
            },

            # Publisher information
            "publisher": {
                "@type": "Organization",
                "name": "Quest Platform",
                "description": "Premium content intelligence platform combining AI generation with human editorial oversight",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://relocation.quest/logo.png"
                }
            },

            # Image
            "image": {
                "@type": "ImageObject",
                "url": image_url,
                "width": 1200,
                "height": 630
            } if image_url else None,

            # Keywords
            "keywords": ", ".join(keywords) if keywords else None,

            # About (help LLMs understand topic)
            "about": {
                "@type": "Thing",
                "name": title,
                "description": description
            },

            # Article section/category
            "articleSection": keywords[0] if keywords else "Guides",

            # Is part of series
            "isPartOf": {
                "@type": "WebSite",
                "name": "Quest Platform",
                "url": "https://relocation.quest"
            }
        }

        # Add entity mentions (CRITICAL for LLM understanding)
        if entities:
            schema["mentions"] = [
                {
                    "@type": entity.type,
                    "name": entity.name,
                    "sameAs": entity.same_as
                }
                for entity in entities
            ]

        # Add citations (LLMs prefer cited content)
        if citations:
            schema["citation"] = [
                {
                    "@type": "WebPage",
                    "url": url_cite
                }
                for url_cite in citations
            ]

        # Add FAQ section (LLMs LOVE Q&A format)
        if faqs:
            faq_schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": faq.question,
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": faq.answer
                        }
                    }
                    for faq in faqs
                ]
            }
            # Return both schemas
            return self._format_schema([schema, faq_schema])

        return self._format_schema([schema])

    def generate_organization_schema(
        self,
        site: str = "relocation",
        name: str = "Quest Platform",
        aggregate_rating: float = 4.8,
        review_count: int = 127
    ) -> str:
        """
        Generate Organization schema for brand trust and NAP consistency

        Critical for AI SEO (Matt Diggity + Nathan Gotch):
        - NAP (Name, Address, Phone) consistency
        - Brand trust signals
        - Review/rating schema
        - Social proof for LLMs

        Args:
            site: Target site (relocation/placement/rainmaker)
            name: Organization name
            aggregate_rating: Average rating (1-5)
            review_count: Number of reviews

        Returns:
            JSON-LD schema as string
        """

        site_urls = {
            "relocation": "https://relocation.quest",
            "placement": "https://placement.quest",
            "rainmaker": "https://rainmaker.quest"
        }

        base_url = site_urls.get(site, "https://relocation.quest")

        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": name,
            "description": "AI-powered content intelligence platform combining AI generation with human editorial oversight for relocation, career, and business content",
            "url": base_url,
            "logo": {
                "@type": "ImageObject",
                "url": f"{base_url}/logo.png",
                "width": 200,
                "height": 200
            },
            "sameAs": [
                "https://linkedin.com/company/quest-platform",
                "https://twitter.com/questplatform",
                "https://github.com/quest-platform"
            ],
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": aggregate_rating,
                "reviewCount": review_count,
                "bestRating": 5,
                "worstRating": 1
            },
            "founder": {
                "@type": "Person",
                "name": "Quest Platform Team"
            }
        }

        return self._format_schema([schema])

    def generate_guide_schema(
        self,
        title: str,
        description: str,
        steps: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        Generate HowTo schema for step-by-step guides

        Args:
            title: Guide title
            description: Guide description
            steps: List of {"name": "Step name", "text": "Step description"}
            **kwargs: Same as generate_article_schema

        Returns:
            JSON-LD schema as string
        """

        schema = {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": title,
            "description": description,
            "step": [
                {
                    "@type": "HowToStep",
                    "name": step["name"],
                    "text": step["text"],
                    "position": idx + 1
                }
                for idx, step in enumerate(steps)
            ]
        }

        # Also include article schema
        article_schema = self.generate_article_schema(title, description, "", **kwargs)

        return self._format_schema([json.loads(article_schema), schema])

    def extract_entities_from_content(self, content: str, title: str) -> List[EntityMention]:
        """
        Extract entity mentions from content (basic implementation)

        In production, use NER (Named Entity Recognition) or LLM extraction
        For now, extracts from common patterns
        """

        entities = []

        # Extract countries (basic pattern matching)
        countries = [
            "Portugal", "Spain", "Germany", "France", "Italy", "Netherlands",
            "United States", "Canada", "Mexico", "Brazil", "Argentina",
            "Japan", "South Korea", "Singapore", "Thailand", "Vietnam"
        ]

        for country in countries:
            if country in content or country in title:
                entities.append(EntityMention(
                    type="Place",
                    name=country,
                    same_as=f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
                ))

        # Extract organizations (basic pattern matching)
        orgs = ["Google", "Amazon", "Microsoft", "Apple", "Meta", "Netflix"]
        for org in orgs:
            if org in content or org in title:
                entities.append(EntityMention(
                    type="Organization",
                    name=org,
                    same_as=f"https://en.wikipedia.org/wiki/{org}"
                ))

        return entities

    def generate_faqs_from_content(self, content: str) -> List[FAQItem]:
        """
        Generate FAQ items from content (basic implementation)

        In production, use LLM to extract common questions from content
        For now, returns empty list (manually add FAQs)
        """

        # TODO: Use LLM to extract Q&A pairs from content
        # For now, return empty - FAQs should be manually curated or AI-generated

        return []

    def _format_schema(self, schemas: List[Dict]) -> str:
        """Format schema(s) as JSON-LD string ready for <head> tag"""

        if len(schemas) == 1:
            return json.dumps(schemas[0], indent=2, ensure_ascii=False)
        else:
            # Multiple schemas - wrap in array
            return json.dumps(schemas, indent=2, ensure_ascii=False)


# Example usage
def example():
    """Example of generating LLM-optimized schema"""

    enhancer = SEOEnhancer()

    schema = enhancer.generate_article_schema(
        title="Portugal Digital Nomad Visa: Complete 2025 Guide",
        description="Comprehensive guide to Portugal Digital Nomad Visa requirements, application process, costs, tax benefits, and best cities for remote workers in 2025",
        content="Portugal has become one of the most popular destinations...",
        url="https://relocation.quest/portugal-digital-nomad-visa",
        image_url="https://res.cloudinary.com/quest/image/portugal-visa.jpg",
        keywords=["portugal", "digital nomad", "visa", "remote work", "2025"],
        entities=[
            EntityMention(
                type="Place",
                name="Portugal",
                same_as="https://en.wikipedia.org/wiki/Portugal"
            ),
            EntityMention(
                type="GovernmentOrganization",
                name="SEF - Portuguese Immigration Service",
                same_as="https://imigrante.sef.pt"
            )
        ],
        faqs=[
            FAQItem(
                question="How much income do I need for Portugal Digital Nomad Visa?",
                answer="You must demonstrate minimum monthly income of €3,280 (approximately $3,500 USD) from remote work."
            ),
            FAQItem(
                question="Can I bring my family?",
                answer="Yes, your spouse and dependent children can apply for family reunification once you have the visa."
            )
        ],
        citations=[
            "https://imigrante.sef.pt",
            "https://www.portugal.gov.pt",
            "https://www.portugalist.com/portugal-digital-nomad-visa"
        ],
        word_count=2847
    )

    print("LLM-Optimized JSON-LD Schema:")
    print(schema)


if __name__ == "__main__":
    example()
