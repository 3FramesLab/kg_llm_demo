"""
LLM service for multi-schema relationship analysis and enhancement.
Provides intelligent relationship inference, descriptions, and confidence scoring.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI
from kg_builder.config import (
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS
)

logger = logging.getLogger(__name__)


class MultiSchemaLLMService:
    """Service for LLM-based multi-schema relationship analysis."""
    
    def __init__(self):
        """Initialize the LLM service."""
        self.enabled = bool(OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.temperature = OPENAI_TEMPERATURE
        self.max_tokens = OPENAI_MAX_TOKENS
        
        if self.enabled:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info(f"MultiSchemaLLMService initialized with model: {self.model}")
        else:
            logger.warning("MultiSchemaLLMService disabled: OPENAI_API_KEY not set")
    
    def is_enabled(self) -> bool:
        """Check if LLM service is enabled."""
        return self.enabled
    
    def infer_relationships(
        self,
        schemas_info: Dict[str, Any],
        detected_relationships: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to infer additional relationships beyond pattern matching.
        
        Args:
            schemas_info: Information about all schemas
            detected_relationships: Relationships already detected by pattern matching
            
        Returns:
            Enhanced relationships with inferred ones added
        """
        if not self.enabled:
            logger.warning("LLM service disabled, returning original relationships")
            return detected_relationships
        
        try:
            prompt = self._build_inference_prompt(schemas_info, detected_relationships)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert database analyst. Analyze database schemas and infer relationships between tables across different schemas based on semantic meaning and naming conventions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            result_text = response.content[0].text
            inferred = self._parse_inferred_relationships(result_text)
            
            # Combine detected and inferred relationships
            all_relationships = detected_relationships + inferred
            
            logger.info(f"LLM inferred {len(inferred)} additional relationships")
            return all_relationships
            
        except Exception as e:
            logger.error(f"Error in relationship inference: {e}")
            return detected_relationships
    
    def enhance_relationships(
        self,
        relationships: List[Dict[str, Any]],
        schemas_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to generate meaningful descriptions for relationships.
        
        Args:
            relationships: List of relationships to enhance
            schemas_info: Information about schemas
            
        Returns:
            Relationships with enhanced descriptions
        """
        if not self.enabled:
            logger.warning("LLM service disabled, returning original relationships")
            return relationships
        
        try:
            prompt = self._build_enhancement_prompt(relationships, schemas_info)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert database analyst. Generate clear, concise business descriptions for database relationships."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            result_text = response.content[0].text
            enhanced = self._parse_enhanced_relationships(result_text)
            
            logger.info(f"LLM enhanced {len(enhanced)} relationships with descriptions")
            return enhanced
            
        except Exception as e:
            logger.error(f"Error in relationship enhancement: {e}")
            return relationships
    
    def score_relationships(
        self,
        relationships: List[Dict[str, Any]],
        schemas_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to assess confidence in detected relationships.
        
        Args:
            relationships: List of relationships to score
            schemas_info: Information about schemas
            
        Returns:
            Relationships with confidence scores
        """
        if not self.enabled:
            logger.warning("LLM service disabled, returning original relationships")
            return relationships
        
        try:
            prompt = self._build_scoring_prompt(relationships, schemas_info)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert database analyst. Assess the confidence and validity of database relationships."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            result_text = response.content[0].text
            scored = self._parse_scored_relationships(result_text)
            
            logger.info(f"LLM scored {len(scored)} relationships with confidence")
            return scored
            
        except Exception as e:
            logger.error(f"Error in relationship scoring: {e}")
            return relationships
    
    def _build_inference_prompt(
        self,
        schemas_info: Dict[str, Any],
        detected_relationships: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for relationship inference."""
        schemas_str = json.dumps(schemas_info, indent=2)
        detected_str = json.dumps(detected_relationships, indent=2)
        
        return f"""Analyze these database schemas and already-detected relationships.
Infer additional relationships that might exist based on semantic meaning and business logic.

SCHEMAS:
{schemas_str}

ALREADY DETECTED RELATIONSHIPS:
{detected_str}

For each inferred relationship, provide:
1. source_table
2. target_table
3. relationship_type (e.g., "SEMANTIC_REFERENCE", "BUSINESS_LOGIC")
4. reasoning (why this relationship likely exists)
5. confidence (0.0-1.0)

Return as JSON array with this structure:
{{
    "inferred_relationships": [
        {{
            "source_table": "table1",
            "target_table": "table2",
            "relationship_type": "SEMANTIC_REFERENCE",
            "reasoning": "explanation",
            "confidence": 0.85
        }}
    ]
}}

Only include relationships with confidence >= 0.7."""
    
    def _build_enhancement_prompt(
        self,
        relationships: List[Dict[str, Any]],
        schemas_info: Dict[str, Any]
    ) -> str:
        """Build prompt for relationship description enhancement."""
        rels_str = json.dumps(relationships, indent=2)
        schemas_str = json.dumps(schemas_info, indent=2)
        
        return f"""Generate clear business descriptions for these database relationships.

SCHEMAS:
{schemas_str}

RELATIONSHIPS:
{rels_str}

For each relationship, provide a clear, concise business description explaining:
- What the relationship represents
- Why it exists
- How data flows through it

Return as JSON array with this structure:
{{
    "enhanced_relationships": [
        {{
            "source_table": "table1",
            "target_table": "table2",
            "description": "Clear business description of the relationship"
        }}
    ]
}}"""
    
    def _build_scoring_prompt(
        self,
        relationships: List[Dict[str, Any]],
        schemas_info: Dict[str, Any]
    ) -> str:
        """Build prompt for relationship confidence scoring."""
        rels_str = json.dumps(relationships, indent=2)
        schemas_str = json.dumps(schemas_info, indent=2)
        
        return f"""Assess the confidence and validity of these database relationships.

SCHEMAS:
{schemas_str}

RELATIONSHIPS:
{rels_str}

For each relationship, provide:
1. confidence (0.0-1.0) - How confident you are this relationship is valid
2. reasoning - Why you assigned this confidence level
3. validation_status - "VALID", "LIKELY", "UNCERTAIN", or "QUESTIONABLE"

Return as JSON array with this structure:
{{
    "scored_relationships": [
        {{
            "source_table": "table1",
            "target_table": "table2",
            "confidence": 0.95,
            "reasoning": "Strong naming pattern and semantic alignment",
            "validation_status": "VALID"
        }}
    ]
}}"""
    
    def _parse_inferred_relationships(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse inferred relationships from LLM response."""
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)
            
            relationships = []
            for rel in data.get('inferred_relationships', []):
                relationships.append({
                    'source_table': rel.get('source_table'),
                    'target_table': rel.get('target_table'),
                    'relationship_type': rel.get('relationship_type'),
                    'reasoning': rel.get('reasoning'),
                    'confidence': rel.get('confidence', 0.0),
                    'inferred_by_llm': True
                })
            
            return relationships
        except Exception as e:
            logger.error(f"Error parsing inferred relationships: {e}")
            return []
    
    def _parse_enhanced_relationships(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse enhanced relationships from LLM response."""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)
            
            relationships = []
            for rel in data.get('enhanced_relationships', []):
                relationships.append({
                    'source_table': rel.get('source_table'),
                    'target_table': rel.get('target_table'),
                    'description': rel.get('description')
                })
            
            return relationships
        except Exception as e:
            logger.error(f"Error parsing enhanced relationships: {e}")
            return []
    
    def _parse_scored_relationships(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse scored relationships from LLM response."""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)
            
            relationships = []
            for rel in data.get('scored_relationships', []):
                relationships.append({
                    'source_table': rel.get('source_table'),
                    'target_table': rel.get('target_table'),
                    'confidence': rel.get('confidence', 0.0),
                    'reasoning': rel.get('reasoning'),
                    'validation_status': rel.get('validation_status')
                })
            
            return relationships
        except Exception as e:
            logger.error(f"Error parsing scored relationships: {e}")
            return []


# Singleton instance
_multi_schema_llm_service = None


def get_multi_schema_llm_service() -> MultiSchemaLLMService:
    """Get or create the multi-schema LLM service singleton."""
    global _multi_schema_llm_service
    if _multi_schema_llm_service is None:
        _multi_schema_llm_service = MultiSchemaLLMService()
    return _multi_schema_llm_service

