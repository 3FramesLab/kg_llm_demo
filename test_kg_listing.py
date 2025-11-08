#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

from kg_builder.services.graphiti_backend import GraphitiBackend
from kg_builder.config import GRAPHITI_STORAGE_PATH

def test_kg_listing():
    print("Testing KG listing...")
    print(f"Storage path: {GRAPHITI_STORAGE_PATH}")
    print(f"Storage path exists: {GRAPHITI_STORAGE_PATH.exists()}")
    
    if GRAPHITI_STORAGE_PATH.exists():
        print(f"Contents: {list(GRAPHITI_STORAGE_PATH.iterdir())}")
    
    # Test the backend
    backend = GraphitiBackend()
    graphs = backend.list_graphs()
    
    print(f"\nFound {len(graphs)} graphs:")
    for i, graph in enumerate(graphs, 1):
        print(f"{i}. {graph}")
    
    return graphs

if __name__ == "__main__":
    graphs = test_kg_listing()
