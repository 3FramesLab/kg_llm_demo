#!/usr/bin/env python3
"""
Run KPI cache fields migration using the existing JDBC connection.
This uses the same connection method as the KPI service.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_migration():
    """Run the KPI cache fields migration."""
    try:
        from kg_builder.services.landing_kpi_service_jdbc import LandingKPIServiceJDBC
        
        print("🔧 Running KPI Cache Fields Migration...")
        print("=" * 50)
        
        # Use the same service that's already working
        service = LandingKPIServiceJDBC()
        conn = service._get_connection()
        cursor = conn.cursor()
        
        try:
            # Check current table structure
            print("📋 Checking current table structure...")
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'kpi_definitions'
                ORDER BY ORDINAL_POSITION
            """)
            current_columns = [row[0] for row in cursor.fetchall()]
            print(f"   Current columns: {', '.join(current_columns)}")
            
            # Add isAccept field
            if 'isAccept' not in current_columns:
                print("➕ Adding isAccept field...")
                cursor.execute("ALTER TABLE kpi_definitions ADD isAccept BIT DEFAULT 0")
                print("   ✅ Added isAccept field")
            else:
                print("   ⚠️ isAccept field already exists")
            
            # Add isSQLCached field
            if 'isSQLCached' not in current_columns:
                print("➕ Adding isSQLCached field...")
                cursor.execute("ALTER TABLE kpi_definitions ADD isSQLCached BIT DEFAULT 0")
                print("   ✅ Added isSQLCached field")
            else:
                print("   ⚠️ isSQLCached field already exists")
            
            # Add cached_sql field
            if 'cached_sql' not in current_columns:
                print("➕ Adding cached_sql field...")
                cursor.execute("ALTER TABLE kpi_definitions ADD cached_sql NVARCHAR(MAX) NULL")
                print("   ✅ Added cached_sql field")
            else:
                print("   ⚠️ cached_sql field already exists")
            
            # Commit changes
            conn.commit()
            
            # Verify new structure
            print("\n📋 Verifying updated table structure...")
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'kpi_definitions'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = cursor.fetchall()
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                default = f" DEFAULT {col[3]}" if col[3] else ""
                print(f"   {col[0]} ({col[1]}) {nullable}{default}")
            
            print("\n🎉 Migration completed successfully!")
            print("\n📋 Next Steps:")
            print("1. Restart your backend server")
            print("2. Navigate to KPI Management page")
            print("3. Test the cache toggle buttons (✓ and 🔄)")
            print("4. Try the clear cache button (💫)")
            
            return True
            
        finally:
            cursor.close()
            conn.close()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the project root directory.")
        return False
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("\n📋 Manual Steps:")
        print("1. Open SQL Server Management Studio")
        print("2. Connect to your database server")
        print("3. Select database: newdqschemanov")
        print("4. Run the SQL from quick_migration.sql")
        return False

if __name__ == "__main__":
    success = run_migration()
    
    if not success:
        print("\n💡 Alternative: Run quick_migration.sql manually in SSMS")
    
    input("\nPress Enter to continue...")
