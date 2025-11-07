#!/usr/bin/env python3
"""Test server startup with new routes"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_server_startup():
    """Test if the server can start with new routes."""
    try:
        print("🧪 Testing server startup...")
        
        # Import the main app
        from kg_builder.main import app
        print("✅ FastAPI app imported successfully")
        
        # Check routes
        kpi_routes = []
        for route in app.routes:
            if hasattr(route, 'path') and 'landing-kpi-mssql' in route.path:
                methods = list(getattr(route, 'methods', ['GET']))
                kpi_routes.append(f"  {methods} {route.path}")
        
        print(f"\n📊 Enhanced KPI routes found: {len(kpi_routes)}")
        if kpi_routes:
            print("✅ Enhanced KPI Analytics routes:")
            for route in sorted(kpi_routes):
                print(route)
        else:
            print("❌ No enhanced KPI routes found")
            return False
        
        print(f"\n📈 Total routes: {len(app.routes)}")
        print("✅ Server startup test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_server_startup()
    sys.exit(0 if success else 1)
