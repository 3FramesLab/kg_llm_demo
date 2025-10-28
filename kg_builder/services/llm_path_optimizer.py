"""
LLM-based JOIN Path Optimizer (Phase 3)

Uses LLM to intelligently score and select optimal join paths between tables.
Replaces the BFS algorithm with LLM-powered semantic understanding.
"""

import json
import logging
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from kg_builder.services.llm_service import get_llm_service

if TYPE_CHECKING:
    from kg_builder.models import KnowledgeGraph

logger = logging.getLogger(__name__)


class LLMPathOptimizer:
    """Use LLM to optimize join paths between tables."""

    def __init__(self, kg: Optional["KnowledgeGraph"] = None):
        """
        Initialize path optimizer.

        Args:
            kg: Knowledge Graph for relationship context
        """
        self.kg = kg
        self.llm_service = get_llm_service()

    def score_paths(self, source: str, target: str, paths: List[List[str]]) -> List[str]:
        """
        Score and rank join paths using LLM.

        Args:
            source: Source table name
            target: Target table name
            paths: List of possible paths (each path is a list of table names)

        Returns:
            List[str]: Best path (list of table names)
        """
        if not paths:
            logger.warning(f"No paths provided to score between {source} and {target}")
            return []

        # If only one path, return it
        if len(paths) == 1:
            logger.info(f"Only one path available: {paths[0]}")
            return paths[0]

        # If LLM not available, fallback to shortest path (BFS-style)
        if not self.llm_service.is_enabled():
            logger.info("LLM not available, using shortest path heuristic")
            return min(paths, key=len)

        try:
            logger.info(f"Scoring {len(paths)} paths from {source} to {target} using LLM")

            # Build prompt with path context
            prompt = self._build_path_scoring_prompt(source, target, paths)

            # Call LLM
            response = self.llm_service.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a database join optimization expert. Analyze join paths and select the most efficient one based on relationship semantics, cardinality, and query performance."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.2  # Low temperature for consistent scoring
            )

            # Parse response
            result_text = response.choices[0].message.content.strip()
            logger.debug(f"LLM path scoring response:\n{result_text}")

            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                if "best_path" in result:
                    best_path = result["best_path"]
                    score = result.get("score", 0)
                    reasoning = result.get("reasoning", "")
                    logger.info(f"✓ LLM selected path: {best_path} (score: {score})")
                    logger.info(f"  Reasoning: {reasoning}")
                    return best_path
                elif "scored_paths" in result and result["scored_paths"]:
                    # Sort by score and return best
                    sorted_paths = sorted(result["scored_paths"], key=lambda x: x.get("score", 0), reverse=True)
                    best = sorted_paths[0]
                    logger.info(f"✓ LLM selected path: {best['path']} (score: {best.get('score', 0)})")
                    return best["path"]

            # Fallback if parsing failed
            logger.warning("Failed to parse LLM path scoring response, using shortest path")
            return min(paths, key=len)

        except Exception as e:
            logger.error(f"Error during LLM path scoring: {e}")
            # Fallback to shortest path
            return min(paths, key=len)

    def _build_path_scoring_prompt(self, source: str, target: str, paths: List[List[str]]) -> str:
        """
        Build prompt for path scoring.

        Args:
            source: Source table name
            target: Target table name
            paths: List of possible paths

        Returns:
            str: Prompt for LLM
        """
        # Format paths with details from KG
        paths_with_context = []
        for i, path in enumerate(paths):
            path_details = {
                "path_id": i + 1,
                "tables": path,
                "length": len(path),
                "relationships": self._get_path_relationships(path)
            }
            paths_with_context.append(path_details)

        prompt = f"""Analyze these join paths from '{source}' to '{target}' and select the best one.

SOURCE TABLE: {source}
TARGET TABLE: {target}

AVAILABLE PATHS:
{json.dumps(paths_with_context, indent=2)}

SCORING CRITERIA:
1. **Path Length**: Shorter paths are generally better (fewer joins = better performance)
2. **Relationship Strength**: Strong relationships (REFERENCES, HAS, BELONGS_TO) are better than weak ones
3. **Cardinality**: 1:N or N:1 relationships are better than N:N (avoid cross joins)
4. **Semantic Correctness**: Path should make logical sense in the business domain
5. **Performance**: Consider foreign keys, indexes, and data volume

KNOWLEDGE GRAPH CONTEXT:
{self._format_kg_relationships()}

Return your analysis in this JSON format:
{{
    "best_path": ["table1", "table2", "table3"],
    "score": 85,
    "reasoning": "This path is optimal because it uses direct foreign key relationships with 1:N cardinality, avoiding intermediate junction tables. The path length is minimal (2 hops) and follows natural business logic."
}}

Return ONLY valid JSON, no additional text."""

        return prompt

    def _get_path_relationships(self, path: List[str]) -> List[Dict[str, Any]]:
        """
        Get relationship details for each step in the path.

        Args:
            path: List of table names

        Returns:
            List of relationship details
        """
        if not self.kg or len(path) < 2:
            return []

        relationships = []
        for i in range(len(path) - 1):
            table1 = path[i].lower()
            table2 = path[i + 1].lower()

            # Find relationship in KG
            for rel in self.kg.relationships:
                source_id = rel.source_id.lower() if rel.source_id else ""
                target_id = rel.target_id.lower() if rel.target_id else ""

                if (table1 in source_id and table2 in target_id) or \
                   (table2 in source_id and table1 in target_id):
                    relationships.append({
                        "from": table1,
                        "to": table2,
                        "type": rel.relationship_type,
                        "source_column": rel.source_column or rel.properties.get("source_column") if rel.properties else None,
                        "target_column": rel.target_column or rel.properties.get("target_column") if rel.properties else None
                    })
                    break

        return relationships

    def _format_kg_relationships(self) -> str:
        """Format KG relationships for the prompt."""
        if not self.kg:
            return "No Knowledge Graph available"

        relationships = []
        for rel in self.kg.relationships[:20]:  # Limit to first 20 to avoid token limits
            relationships.append({
                "source": rel.source_id,
                "target": rel.target_id,
                "type": rel.relationship_type,
                "source_column": rel.source_column or rel.properties.get("source_column") if rel.properties else None,
                "target_column": rel.target_column or rel.properties.get("target_column") if rel.properties else None
            })

        if len(self.kg.relationships) > 20:
            relationships.append({"note": f"... and {len(self.kg.relationships) - 20} more relationships"})

        return json.dumps(relationships, indent=2)


def get_llm_path_optimizer(kg: Optional["KnowledgeGraph"] = None) -> LLMPathOptimizer:
    """Get or create LLM path optimizer instance."""
    return LLMPathOptimizer(kg=kg)
