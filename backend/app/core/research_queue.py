"""
Research Queue Governance Module
Enforces topic prioritization and deduplication from QUEST_RELOCATION_RESEARCH.md
"""
import os
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import structlog
from app.core.database import get_db

logger = structlog.get_logger()

class ResearchGovernance:
    """
    Manages research topic prioritization and deduplication
    Enforces QUEST_RELOCATION_RESEARCH.md requirements
    """

    # High-value topics from research document
    HIGH_PRIORITY_TOPICS = {
        # Golden visa programs ($15-30 CPC)
        "golden_visa": [
            "Portugal Golden Visa 2025",
            "Spain Golden Visa Requirements",
            "Greece Golden Visa Program",
            "Malta Golden Visa Investment",
            "Cyprus Investment Program",
            "Caribbean Golden Visa Options",
            "EU Golden Visa Comparison",
            "Golden Visa Tax Benefits",
            "Best Golden Visa Programs 2025",
            "Golden Visa Property Investment"
        ],
        # Tax strategies ($20-40 CPC)
        "tax_strategies": [
            "Digital Nomad Tax Strategies",
            "Offshore Tax Planning Guide",
            "Portugal NHR Tax Regime",
            "Spain Beckham Law Tax",
            "Cyprus Tax Residency Benefits",
            "Dubai Zero Tax Guide",
            "Malta Tax Residency Program",
            "Crypto Tax Optimization Strategies",
            "International Tax Planning 2025",
            "Expat Tax Filing Guide"
        ],
        # Business setup ($18-35 CPC)
        "business_setup": [
            "Estonia e-Residency Business Setup",
            "Dubai Free Zone Company Formation",
            "Singapore Business Registration Guide",
            "Hong Kong Company Formation",
            "Delaware LLC for Non-Residents",
            "UK Ltd Company Remote Setup",
            "Cyprus Company Formation Benefits",
            "Malta Gaming License Guide",
            "Offshore Company Formation 2025",
            "Best Countries for Online Business"
        ],
        # Digital nomad visas (high search volume)
        "digital_nomad_visas": [
            "Thailand Digital Nomad Visa",
            "Bali Digital Nomad Visa",
            "Mexico Digital Nomad Visa",
            "Croatia Digital Nomad Visa",
            "Germany Freelance Visa",
            "Netherlands DAFT Visa",
            "Czech Republic Freelance Visa",
            "Estonia Digital Nomad Visa",
            "Barbados Welcome Stamp",
            "Dubai Virtual Working Program"
        ]
    }

    def __init__(self):
        """Initialize research governance"""
        self.completed_topics = set()
        # Note: load_completed_topics() must be called with await from async context

    async def load_completed_topics(self):
        """Load already completed topics from database"""
        try:
            pool = get_db()
            async with pool.acquire() as conn:
                articles = await conn.fetch(
                    "SELECT title, slug FROM articles WHERE status != 'failed'"
                )
                for article in articles:
                    self.completed_topics.add(article['title'].lower())
                    self.completed_topics.add(article['slug'].lower())

            logger.info(
                "research_governance.loaded_completed",
                count=len(self.completed_topics)
            )
        except Exception as e:
            logger.warning(
                "research_governance.load_failed",
                error=str(e)
            )

    def is_duplicate(self, topic: str) -> bool:
        """
        Check if topic has already been covered

        Args:
            topic: Proposed topic

        Returns:
            True if duplicate, False otherwise
        """
        normalized_topic = self._normalize_topic(topic)

        # Check exact matches
        if normalized_topic in self.completed_topics:
            logger.info(
                "research_governance.duplicate_found",
                topic=topic
            )
            return True

        # Check for similar topics (80% word overlap)
        topic_words = set(normalized_topic.split())
        for completed in self.completed_topics:
            completed_words = set(completed.split())
            overlap = len(topic_words & completed_words)
            if len(topic_words) > 0 and overlap / len(topic_words) > 0.8:
                logger.info(
                    "research_governance.similar_found",
                    topic=topic,
                    similar_to=completed,
                    overlap_ratio=overlap/len(topic_words)
                )
                return True

        return False

    def get_priority_score(self, topic: str) -> Tuple[int, str]:
        """
        Calculate priority score for a topic based on SEO value

        Args:
            topic: Proposed topic

        Returns:
            Tuple of (priority_score, category)
            Higher score = higher priority
        """
        normalized_topic = topic.lower()

        # Check high-priority categories
        for category, topics in self.HIGH_PRIORITY_TOPICS.items():
            for high_value_topic in topics:
                if self._topics_match(normalized_topic, high_value_topic.lower()):
                    if category == "golden_visa":
                        return (100, category)  # Highest priority - untapped
                    elif category == "tax_strategies":
                        return (95, category)   # Very high priority
                    elif category == "business_setup":
                        return (90, category)   # High priority
                    elif category == "digital_nomad_visas":
                        return (85, category)   # Good volume

        # Check for general keyword matches
        if "golden visa" in normalized_topic:
            return (100, "golden_visa")
        elif "tax" in normalized_topic or "offshore" in normalized_topic:
            return (95, "tax_strategies")
        elif "company" in normalized_topic or "business" in normalized_topic or "llc" in normalized_topic:
            return (90, "business_setup")
        elif "visa" in normalized_topic or "nomad" in normalized_topic:
            return (85, "digital_nomad_visas")
        elif "citizenship" in normalized_topic or "passport" in normalized_topic:
            return (75, "citizenship_programs")
        elif "cost of living" in normalized_topic or "budget" in normalized_topic:
            return (60, "cost_of_living")
        elif "healthcare" in normalized_topic or "education" in normalized_topic:
            return (40, "healthcare_education")
        elif "property" in normalized_topic or "real estate" in normalized_topic:
            return (45, "property_investment")
        elif "banking" in normalized_topic or "finance" in normalized_topic:
            return (50, "banking_finance")
        else:
            return (30, "general")  # Low priority

    def suggest_next_topic(self) -> Optional[str]:
        """
        Suggest the next high-priority topic to research

        Returns:
            Topic string or None if all covered
        """
        # Prioritize by category value
        for category in ["golden_visa", "tax_strategies", "business_setup", "digital_nomad_visas"]:
            topics = self.HIGH_PRIORITY_TOPICS.get(category, [])
            for topic in topics:
                if not self.is_duplicate(topic):
                    logger.info(
                        "research_governance.suggested_topic",
                        topic=topic,
                        category=category
                    )
                    return topic

        logger.warning("research_governance.no_topics_available")
        return None

    def validate_research_request(self, topic: str) -> Dict:
        """
        Validate if a research request should proceed

        Args:
            topic: Requested research topic

        Returns:
            Dict with validation results
        """
        result = {
            "approved": True,
            "is_duplicate": False,
            "priority_score": 0,
            "category": "",
            "suggested_alternative": None,
            "reason": ""
        }

        # Check for duplicates
        if self.is_duplicate(topic):
            result["approved"] = False
            result["is_duplicate"] = True
            result["reason"] = f"Topic already covered: {topic}"
            result["suggested_alternative"] = self.suggest_next_topic()
            return result

        # Calculate priority
        priority_score, category = self.get_priority_score(topic)
        result["priority_score"] = priority_score
        result["category"] = category

        # Warn if low priority
        if priority_score < 50:
            result["reason"] = f"Low priority topic (score: {priority_score}). Consider high-value topics like Golden Visa or Tax Strategies."
            result["suggested_alternative"] = self.suggest_next_topic()
        else:
            result["reason"] = f"Approved: {category} topic with priority {priority_score}"

        logger.info(
            "research_governance.validation_complete",
            topic=topic,
            approved=result["approved"],
            priority=priority_score,
            category=category
        )

        return result

    def record_completion(self, topic: str):
        """
        Record a topic as completed

        Args:
            topic: Completed topic
        """
        normalized = self._normalize_topic(topic)
        self.completed_topics.add(normalized)
        logger.info(
            "research_governance.topic_completed",
            topic=topic,
            total_completed=len(self.completed_topics)
        )

    def _normalize_topic(self, topic: str) -> str:
        """Normalize topic for comparison"""
        # Remove special characters and extra spaces
        normalized = re.sub(r'[^\w\s]', ' ', topic.lower())
        normalized = ' '.join(normalized.split())
        return normalized

    def _topics_match(self, topic1: str, topic2: str) -> bool:
        """Check if two topics are essentially the same"""
        # Remove years and numbers for comparison
        clean1 = re.sub(r'\b\d{4}\b|\b\d+\b', '', topic1)
        clean2 = re.sub(r'\b\d{4}\b|\b\d+\b', '', topic2)

        # Check for high word overlap
        words1 = set(clean1.split())
        words2 = set(clean2.split())

        if len(words1) == 0 or len(words2) == 0:
            return False

        overlap = len(words1 & words2)
        min_len = min(len(words1), len(words2))

        return overlap / min_len > 0.7

    def get_category_progress(self) -> Dict:
        """
        Get progress report by category

        Returns:
            Dict with category progress stats
        """
        progress = {}

        for category, topics in self.HIGH_PRIORITY_TOPICS.items():
            completed = sum(1 for topic in topics if self.is_duplicate(topic))
            total = len(topics)
            progress[category] = {
                "completed": completed,
                "total": total,
                "percentage": (completed / total * 100) if total > 0 else 0
            }

        return progress