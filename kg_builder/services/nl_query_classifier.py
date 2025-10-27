"""
Natural Language Query Classifier

Classifies NL definitions into different types:
- RELATIONSHIP: "Products are supplied by Vendors"
- DATA_QUERY: "Show me products not in OPS Excel"
- FILTER_QUERY: "Show me active products"
- COMPARISON_QUERY: "Compare RBP GPU with OPS Excel"
- AGGREGATION_QUERY: "Count products by category"
"""

import logging
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class DefinitionType(Enum):
    """Types of NL definitions."""
    RELATIONSHIP = "relationship"
    DATA_QUERY = "data_query"
    FILTER_QUERY = "filter_query"
    COMPARISON_QUERY = "comparison_query"
    AGGREGATION_QUERY = "aggregation_query"


class NLQueryClassifier:
    """Classify NL definitions into different types."""

    def __init__(self):
        """Initialize classifier with keyword patterns."""
        # Keywords for each type
        self.relationship_keywords = [
            "are", "is", "supplied by", "contains", "references",
            "belongs to", "has", "provides", "manages", "placed by",
            "related to", "associated with", "linked to"
        ]

        self.query_keywords = [
            "show me", "find", "list", "get", "which", "where",
            "display", "retrieve", "fetch", "select", "give me"
        ]

        self.filter_keywords = [
            "active", "inactive", "status", "where", "condition",
            "filter", "matching", "with", "having"
        ]

        self.comparison_keywords = [
            "compare", "difference", "not in", "missing", "mismatch",
            "unmatched", "unmatches", "except", "minus", "without",
            "vs", "versus", "between"
        ]

        self.aggregation_keywords = [
            "count", "sum", "average", "total", "group by",
            "aggregate", "statistics", "how many", "total count"
        ]

    def classify(self, definition: str) -> DefinitionType:
        """
        Classify a definition into one of the types.

        Args:
            definition: Natural language definition

        Returns:
            DefinitionType: Type of the definition
        """
        text_lower = definition.lower()

        # Check for comparison queries first (most specific)
        if self._has_keywords(text_lower, self.comparison_keywords):
            logger.debug(f"Classified as COMPARISON_QUERY: {definition}")
            return DefinitionType.COMPARISON_QUERY

        # Check for aggregation queries
        if self._has_keywords(text_lower, self.aggregation_keywords):
            logger.debug(f"Classified as AGGREGATION_QUERY: {definition}")
            return DefinitionType.AGGREGATION_QUERY

        # Check for data queries
        if self._has_keywords(text_lower, self.query_keywords):
            # If it also has filter keywords, it's a filter query
            if self._has_keywords(text_lower, self.filter_keywords):
                logger.debug(f"Classified as FILTER_QUERY: {definition}")
                return DefinitionType.FILTER_QUERY
            else:
                logger.debug(f"Classified as DATA_QUERY: {definition}")
                return DefinitionType.DATA_QUERY

        # Check for filter queries
        if self._has_keywords(text_lower, self.filter_keywords):
            logger.debug(f"Classified as FILTER_QUERY: {definition}")
            return DefinitionType.FILTER_QUERY

        # Default to relationship
        logger.debug(f"Classified as RELATIONSHIP: {definition}")
        return DefinitionType.RELATIONSHIP

    def get_operation_type(self, definition: str) -> Optional[str]:
        """
        Extract the operation type from a definition.

        Args:
            definition: Natural language definition

        Returns:
            str: Operation type (NOT_IN, IN, EQUALS, CONTAINS, etc.)
        """
        text_lower = definition.lower()

        # Check for set operations
        if any(kw in text_lower for kw in ["not in", "missing", "without", "except"]):
            return "NOT_IN"
        elif any(kw in text_lower for kw in ["in", "matching", "matched"]):
            return "IN"
        elif any(kw in text_lower for kw in ["equals", "equal to", "same as"]):
            return "EQUALS"
        elif any(kw in text_lower for kw in ["contains", "includes"]):
            return "CONTAINS"
        elif any(kw in text_lower for kw in ["count", "total", "sum"]):
            return "AGGREGATE"

        return None

    def _has_keywords(self, text: str, keywords: list) -> bool:
        """
        Check if text contains any of the keywords.

        Args:
            text: Text to check
            keywords: List of keywords

        Returns:
            bool: True if any keyword found
        """
        return any(keyword in text for keyword in keywords)


def get_nl_query_classifier() -> NLQueryClassifier:
    """Get or create NL query classifier instance."""
    return NLQueryClassifier()

