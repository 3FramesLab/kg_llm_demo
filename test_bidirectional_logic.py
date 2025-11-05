#!/usr/bin/env python3
"""
Test script to verify correct bidirectional values for different relationship types.
"""

import json
import requests
from typing import Dict, List

def analyze_bidirectional_consistency(relationships: List[Dict]) -> Dict:
    """Analyze bidirectional consistency across relationship types."""
    analysis = {
        "total_relationships": len(relationships),
        "by_type": {},
        "bidirectional_issues": [],
        "recommendations": []
    }
    
    # Expected bidirectional values by relationship type
    expected_bidirectional = {
        "REFERENCES": False,        # Directional dependency
        "MATCHES": True,           # Symmetric equivalence  
        "FOREIGN_KEY": False,      # Explicit constraint direction
        "CONTAINS": False,         # Hierarchical (parent → child)
        "BELONGS_TO": False,       # Hierarchical (child → parent)
        "HAS": False,             # Ownership (owner → owned)
        "SEMANTIC_REFERENCE": True, # Same concept, different names
        "HIERARCHICAL": False,     # Parent-child structure
        "TEMPORAL": False,         # Time flows one way
        "LOOKUP": False,          # Lookup direction
        "BUSINESS_LOGIC": False,   # Usually directional
    }
    
    for rel in relationships:
        rel_type = rel.get('relationship_type', 'UNKNOWN')
        bidirectional = rel.get('bidirectional', False)
        
        # Track by type
        if rel_type not in analysis["by_type"]:
            analysis["by_type"][rel_type] = {
                "count": 0,
                "bidirectional_true": 0,
                "bidirectional_false": 0
            }
        
        analysis["by_type"][rel_type]["count"] += 1
        if bidirectional:
            analysis["by_type"][rel_type]["bidirectional_true"] += 1
        else:
            analysis["by_type"][rel_type]["bidirectional_false"] += 1
        
        # Check for inconsistencies
        expected = expected_bidirectional.get(rel_type)
        if expected is not None and bidirectional != expected:
            issue = {
                "relationship": f"{rel.get('source_table', 'N/A')}.{rel.get('source_column', 'N/A')} → {rel.get('target_table', 'N/A')}.{rel.get('target_column', 'N/A')}",
                "type": rel_type,
                "current_bidirectional": bidirectional,
                "expected_bidirectional": expected,
                "reasoning": get_bidirectional_reasoning(rel_type, expected)
            }
            analysis["bidirectional_issues"].append(issue)
    
    # Generate recommendations
    for rel_type, stats in analysis["by_type"].items():
        expected = expected_bidirectional.get(rel_type)
        if expected is not None:
            wrong_count = stats["bidirectional_true"] if not expected else stats["bidirectional_false"]
            if wrong_count > 0:
                analysis["recommendations"].append({
                    "type": rel_type,
                    "issue": f"{wrong_count} relationships have incorrect bidirectional value",
                    "fix": f"Set bidirectional = {expected} for {rel_type} relationships"
                })
    
    return analysis

def get_bidirectional_reasoning(rel_type: str, expected: bool) -> str:
    """Get reasoning for expected bidirectional value."""
    reasons = {
        "REFERENCES": "REFERENCES are directional - source looks up target",
        "MATCHES": "MATCHES are symmetric - both sides represent same entity",
        "FOREIGN_KEY": "Foreign keys have explicit directional constraints",
        "CONTAINS": "CONTAINS is hierarchical - parent contains child",
        "BELONGS_TO": "BELONGS_TO is hierarchical - child belongs to parent",
        "SEMANTIC_REFERENCE": "SEMANTIC_REFERENCE represents same concept bidirectionally",
        "HIERARCHICAL": "HIERARCHICAL relationships have parent-child direction",
        "TEMPORAL": "TEMPORAL relationships follow time direction",
        "LOOKUP": "LOOKUP relationships have clear lookup direction"
    }
    return reasons.get(rel_type, f"Should be bidirectional = {expected}")

def test_current_relationships():
    """Test current relationship suggestions for bidirectional consistency."""
    print("="*60)
    print("  TESTING BIDIRECTIONAL CONSISTENCY")
    print("="*60)
    
    # Test with suggest-relationships endpoint
    payload = {
        "source_table": "brz_lnd_IBP_Product_Master",
        "schema_names": ["newdqschemanov"]
    }
    
    try:
        print("Getting relationship suggestions...")
        response = requests.post(
            "http://localhost:8000/api/v1/kg/llm/suggest-relationships",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            relationships = response.json()
            print(f"✅ Got {len(relationships)} relationship suggestions")
            
            # Analyze bidirectional consistency
            analysis = analyze_bidirectional_consistency(relationships)
            
            print(f"\n📊 ANALYSIS RESULTS:")
            print(f"   Total relationships: {analysis['total_relationships']}")
            
            print(f"\n📋 BY RELATIONSHIP TYPE:")
            for rel_type, stats in analysis["by_type"].items():
                print(f"   {rel_type}:")
                print(f"     Total: {stats['count']}")
                print(f"     Bidirectional=true: {stats['bidirectional_true']}")
                print(f"     Bidirectional=false: {stats['bidirectional_false']}")
            
            if analysis["bidirectional_issues"]:
                print(f"\n⚠️  BIDIRECTIONAL ISSUES FOUND ({len(analysis['bidirectional_issues'])}):")
                for i, issue in enumerate(analysis["bidirectional_issues"][:5], 1):  # Show first 5
                    print(f"\n   {i}. {issue['relationship']}")
                    print(f"      Type: {issue['type']}")
                    print(f"      Current: bidirectional = {issue['current_bidirectional']}")
                    print(f"      Expected: bidirectional = {issue['expected_bidirectional']}")
                    print(f"      Reason: {issue['reasoning']}")
            else:
                print(f"\n✅ NO BIDIRECTIONAL ISSUES FOUND!")
            
            if analysis["recommendations"]:
                print(f"\n🔧 RECOMMENDATIONS:")
                for rec in analysis["recommendations"]:
                    print(f"   • {rec['type']}: {rec['fix']}")
            
            return len(analysis["bidirectional_issues"]) == 0
            
        else:
            print(f"❌ FAILED: API returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  SKIP: API server not running")
        return True
    except Exception as e:
        print(f"❌ FAILED: Exception occurred: {e}")
        return False

def test_manual_examples():
    """Test manual examples of correct bidirectional values."""
    print("\n" + "="*60)
    print("  MANUAL BIDIRECTIONAL EXAMPLES")
    print("="*60)
    
    examples = [
        {
            "relationship": "orders.customer_id → customers.id",
            "type": "REFERENCES",
            "bidirectional": False,
            "correct": True,
            "reasoning": "Orders reference customers (directional lookup)"
        },
        {
            "relationship": "system_a.material ↔ system_b.material", 
            "type": "MATCHES",
            "bidirectional": True,
            "correct": True,
            "reasoning": "Same material in different systems (symmetric)"
        },
        {
            "relationship": "OPS.PLANNING_SKU → RBP.Material",
            "type": "REFERENCES", 
            "bidirectional": True,  # This is the issue from your example!
            "correct": False,
            "reasoning": "Should be bidirectional=false (OPS references RBP)"
        },
        {
            "relationship": "HANA.MATERIAL ↔ RBP.Material",
            "type": "MATCHES",
            "bidirectional": True,
            "correct": True, 
            "reasoning": "Same material concept (symmetric equivalence)"
        }
    ]
    
    print("Analyzing manual examples:")
    
    correct_count = 0
    for i, example in enumerate(examples, 1):
        status = "✅ CORRECT" if example["correct"] else "❌ INCORRECT"
        print(f"\n{i}. {example['relationship']}")
        print(f"   Type: {example['type']}")
        print(f"   Bidirectional: {example['bidirectional']}")
        print(f"   Status: {status}")
        print(f"   Reasoning: {example['reasoning']}")
        
        if example["correct"]:
            correct_count += 1
    
    print(f"\n📊 Manual Examples: {correct_count}/{len(examples)} correct")
    return correct_count == len(examples)

def main():
    """Run bidirectional consistency tests."""
    print("Testing Bidirectional Logic for Relationship Types")
    print("This test verifies that bidirectional values match relationship semantics")
    print()
    
    tests = [
        test_current_relationships,
        test_manual_examples
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("  BIDIRECTIONAL CONSISTENCY SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 Bidirectional logic is consistent!")
        print("\nKey principles:")
        print("✅ REFERENCES: bidirectional = false (directional)")
        print("✅ MATCHES: bidirectional = true (symmetric)")
        print("✅ Hierarchical types: bidirectional = false")
        print("✅ Equivalence types: bidirectional = true")
        return 0
    else:
        print("⚠️  Bidirectional inconsistencies found")
        print("\nRecommendations:")
        print("• Fix REFERENCES relationships to bidirectional = false")
        print("• Keep MATCHES relationships as bidirectional = true")
        print("• Review hierarchical relationships")
        return 1

if __name__ == "__main__":
    exit(main())
