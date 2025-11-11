#!/usr/bin/env python3

import json
import os
from pathlib import Path
from datetime import datetime

def test_kg_listing_simple():
    """Test KG listing logic without dependencies."""
    
    storage_path = Path("data/graphiti_storage")
    print(f"Storage path: {storage_path}")
    print(f"Storage path exists: {storage_path.exists()}")
    
    if not storage_path.exists():
        print("Storage path doesn't exist!")
        return []
    
    graphs = []
    
    for d in storage_path.iterdir():
        if d.is_dir():
            metadata_file = d / "metadata.json"
            print(f"Checking directory: {d.name}")
            print(f"Metadata file: {metadata_file}")
            print(f"Metadata exists: {metadata_file.exists()}")
            
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        # Add backends information
                        metadata['backends'] = ['graphiti']
                        graphs.append(metadata)
                        print(f"  ✅ Loaded metadata for {d.name}")
                        print(f"     Name: {metadata.get('name', 'N/A')}")
                        print(f"     Created: {metadata.get('created_at', 'N/A')}")
                        print(f"     Tables with aliases: {len(metadata.get('table_aliases', {}))}")
                except Exception as e:
                    print(f"  ❌ Error reading metadata for {d.name}: {e}")
                    # Fallback: add basic info
                    graphs.append({
                        'name': d.name,
                        'backends': ['graphiti'],
                        'created_at': None
                    })
            else:
                # No metadata file, add basic info
                print(f"  ⚠️  No metadata file for {d.name}")
                graphs.append({
                    'name': d.name,
                    'backends': ['graphiti'],
                    'created_at': None
                })
    
    # Sort by created_at timestamp (latest first)
    def sort_key(graph):
        created_at = graph.get('created_at')
        if created_at is None:
            return datetime.min  # Put None values at the end
        try:
            # Parse ISO format timestamp
            return datetime.fromisoformat(created_at)
        except (ValueError, TypeError):
            return datetime.min  # Put invalid timestamps at the end

    graphs.sort(key=sort_key, reverse=True)
    
    print(f"\n📊 Final Results:")
    print(f"Found {len(graphs)} graphs:")
    for i, graph in enumerate(graphs, 1):
        print(f"{i}. {graph.get('name', 'Unknown')} (created: {graph.get('created_at', 'Unknown')})")
    
    # Simulate API response
    api_response = {
        "success": True,
        "data": graphs,
        "count": len(graphs)
    }
    
    print(f"\n🔗 API Response format:")
    print(json.dumps(api_response, indent=2, default=str))
    
    return graphs

if __name__ == "__main__":
    test_kg_listing_simple()
