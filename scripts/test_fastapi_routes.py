#!/usr/bin/env python3
"""Test FastAPI routes loading"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from kg_builder.main import app
    print('✅ FastAPI app loaded successfully')
    
    print('\n📋 Available KPI routes:')
    kpi_routes = []
    for route in app.routes:
        if hasattr(route, 'path') and 'kpi' in route.path.lower():
            methods = getattr(route, 'methods', ['GET'])
            kpi_routes.append(f"  {list(methods)} {route.path}")
    
    if kpi_routes:
        for route in sorted(kpi_routes):
            print(route)
    else:
        print("  No KPI routes found")
    
    print(f'\n📊 Total routes: {len(app.routes)}')
    print(f'📊 KPI routes: {len(kpi_routes)}')
    
except Exception as e:
    print(f'❌ Error loading FastAPI app: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
