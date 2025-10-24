"""
LLM Service for intelligent entity and relationship extraction using OpenAI.
"""
import json
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI, APIError

from kg_builder.config import (
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, 
    OPENAI_MAX_TOKENS, ENABLE_LLM_EXTRACTION
)

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-based intelligent extraction."""
    
    def __init__(self):
        """Initialize LLM service with OpenAI client."""
        self.enabled = ENABLE_LLM_EXTRACTION and bool(OPENAI_API_KEY)
        self.client = None
        self.model = OPENAI_MODEL
        self.temperature = OPENAI_TEMPERATURE
        self.max_tokens = OPENAI_MAX_TOKENS
        
        if self.enabled:
            try:
                self.client = OpenAI(api_key=OPENAI_API_KEY)
                logger.info(f"LLM Service initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.enabled = False
        else:
            logger.warning("LLM Service disabled: OPENAI_API_KEY not set or LLM extraction disabled")
    
    def is_enabled(self) -> bool:
        """Check if LLM service is enabled and available."""
        return self.enabled
    
    def extract_entities(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to intelligently extract entities from schema.
        
        Args:
            schema: Database schema dictionary
            
        Returns:
            Dictionary with extracted entities and their descriptions
        """
        if not self.enabled:
            logger.warning("LLM extraction disabled, returning empty result")
            return {"entities": [], "descriptions": {}}
        
        try:
            schema_str = json.dumps(schema, indent=2)
            
            prompt = f"""Analyze this database schema and extract key entities with their business purposes.

Schema:
{schema_str}

For each table/entity, provide:
1. Entity name
2. Business purpose (what it represents)
3. Key attributes (important columns)
4. Entity type (e.g., "Master Data", "Transaction", "Reference")

Return as JSON with this structure:
{{
    "entities": [
        {{
            "name": "entity_name",
            "purpose": "business purpose",
            "type": "entity_type",
            "key_attributes": ["attr1", "attr2"],
            "description": "detailed description"
        }}
    ]
}}"""

            logger.debug(f"Entity Extraction Prompt:\n{prompt}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a database schema analyst. Extract entities and their business purposes from database schemas. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            result_text = response.choices[0].message.content
            logger.debug(f"LLM Entity Extraction Response:\n{result_text}")

            result = json.loads(result_text)

            logger.info(f"LLM extracted {len(result.get('entities', []))} entities")
            return result
            
        except APIError as e:
            logger.error(f"OpenAI API error during entity extraction: {e}")
            return {"entities": [], "descriptions": {}, "error": str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return {"entities": [], "descriptions": {}, "error": "Invalid JSON response"}
        except Exception as e:
            logger.error(f"Error during LLM entity extraction: {e}")
            return {"entities": [], "descriptions": {}, "error": str(e)}
    
    def extract_relationships(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to intelligently extract relationships from schema.
        
        Args:
            schema: Database schema dictionary
            
        Returns:
            Dictionary with extracted relationships
        """
        if not self.enabled:
            logger.warning("LLM extraction disabled, returning empty result")
            return {"relationships": []}
        
        try:
            schema_str = json.dumps(schema, indent=2)
            
            prompt = f"""Analyze this database schema and extract all relationships between entities.

Schema:
{schema_str}

For each relationship, identify:
1. Source entity
2. Target entity
3. Relationship type (e.g., "HAS", "BELONGS_TO", "REFERENCES", "CONTAINS")
4. Cardinality (1:1, 1:N, N:N)
5. Business meaning

Return as JSON with this structure:
{{
    "relationships": [
        {{
            "source": "source_entity",
            "target": "target_entity",
            "type": "relationship_type",
            "cardinality": "1:N",
            "description": "business meaning of relationship",
            "foreign_key": "column_name or null"
        }}
    ]
}}"""

            logger.debug(f"Relationship Extraction Prompt:\n{prompt}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a database schema analyst. Extract relationships between entities from database schemas. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            result_text = response.choices[0].message.content
            logger.debug(f"LLM Relationship Extraction Response:\n{result_text}")

            result = json.loads(result_text)

            logger.info(f"LLM extracted {len(result.get('relationships', []))} relationships")
            return result
            
        except APIError as e:
            logger.error(f"OpenAI API error during relationship extraction: {e}")
            return {"relationships": [], "error": str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return {"relationships": [], "error": "Invalid JSON response"}
        except Exception as e:
            logger.error(f"Error during LLM relationship extraction: {e}")
            return {"relationships": [], "error": str(e)}
    
    def analyze_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to provide comprehensive schema analysis.
        
        Args:
            schema: Database schema dictionary
            
        Returns:
            Dictionary with schema analysis
        """
        if not self.enabled:
            logger.warning("LLM analysis disabled, returning empty result")
            return {"analysis": {}}
        
        try:
            schema_str = json.dumps(schema, indent=2)
            
            prompt = f"""Provide a comprehensive analysis of this database schema.

Schema:
{schema_str}

Analyze:
1. Overall purpose and domain
2. Data model patterns
3. Key entities and their roles
4. Data relationships and dependencies
5. Potential business logic
6. Data quality considerations

Return as JSON with this structure:
{{
    "domain": "business domain",
    "purpose": "overall purpose",
    "patterns": ["pattern1", "pattern2"],
    "key_entities": ["entity1", "entity2"],
    "data_flow": "description of data flow",
    "business_logic": "inferred business logic",
    "quality_notes": "data quality considerations"
}}"""

            logger.debug(f"Schema Analysis Prompt:\n{prompt}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a database architect. Analyze database schemas and provide insights about their structure, purpose, and business logic. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            result_text = response.choices[0].message.content
            logger.debug(f"LLM Schema Analysis Response:\n{result_text}")

            result = json.loads(result_text)

            logger.info("LLM schema analysis completed")
            return result
            
        except APIError as e:
            logger.error(f"OpenAI API error during schema analysis: {e}")
            return {"analysis": {}, "error": str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return {"analysis": {}, "error": "Invalid JSON response"}
        except Exception as e:
            logger.error(f"Error during LLM schema analysis: {e}")
            return {"analysis": {}, "error": str(e)}


# Global LLM service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

