"""
Test script to demonstrate LLM prompt and response logging.
This script sets up logging to show DEBUG level messages.
"""
import logging
import sys
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from kg_builder.services.schema_parser import SchemaParser

# Configure logging to show DEBUG messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

def main():
    """Test LLM logging with multi-schema KG generation."""
    
    print("\n" + "="*80)
    print("LLM Prompt and Response Logging Test")
    print("="*80 + "\n")
    
    try:
        # Generate multi-schema KG with LLM enhancement
        print("Generating multi-schema knowledge graph with LLM enhancement...")
        print("Watch for DEBUG logs showing prompts and responses...\n")
        
        kg = SchemaParser.build_merged_knowledge_graph(
            schema_names=["orderMgmt-catalog", "qinspect-designcode"],
            kg_name="test_kg_with_logging",
            use_llm=True
        )
        
        print("\n" + "="*80)
        print("Knowledge Graph Generated Successfully!")
        print("="*80)
        print(f"KG Name: {kg.name}")
        print(f"Nodes: {len(kg.nodes)}")
        print(f"Relationships: {len(kg.relationships)}")
        
        # Show sample relationships with LLM metadata
        print("\n" + "="*80)
        print("Sample Relationships with LLM Metadata:")
        print("="*80)
        
        for i, rel in enumerate(kg.relationships[:3]):
            print(f"\nRelationship {i+1}:")
            print(f"  Source: {rel.source_id}")
            print(f"  Target: {rel.target_id}")
            print(f"  Type: {rel.relationship_type}")
            
            if rel.properties:
                if "llm_confidence" in rel.properties:
                    print(f"  LLM Confidence: {rel.properties.get('llm_confidence')}")
                    print(f"  LLM Reasoning: {rel.properties.get('llm_reasoning')}")
                    print(f"  LLM Status: {rel.properties.get('llm_validation_status')}")
                    print(f"  LLM Description: {rel.properties.get('llm_description')}")
        
        print("\n" + "="*80)
        print("✅ Test completed! Check DEBUG logs above for prompts and responses.")
        print("="*80 + "\n")
        
    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

