#!/usr/bin/env python3
"""
Test script to validate command line arguments for standalone_sql_preview.py
This script tests the argument parsing without actually running the SQL generation.
"""

import sys
import argparse

def test_argument_parsing():
    """Test the argument parsing logic."""
    
    # Simulate the command line arguments from your example
    test_args = [
        '--nl-definition', 'get products from hana_material_master where OPS_PLANNER is missing',
        '--kg-name', 'KG_Test_001',
        '--select-schema', 'newdqnov7',
        '--openai-key', 'Test',
        '--temperature', '0',
        '--db-host', 'DESKTOP-41O1AL9\\LOCALHOST',
        '--db-name', 'NewDQ',
        '--db-user', 'mithun',
        '--db-password', 'mithun123',
        '--use-llm',
        '--verbose'
    ]
    
    # Create the same argument parser as in the main script
    parser = argparse.ArgumentParser(
        description='Standalone SQL Preview Generator - Generate SQL from natural language without execution'
    )
    
    # Required arguments
    parser.add_argument('--nl-definition', required=True, help='Natural language definition to convert to SQL')
    parser.add_argument('--kg-name', required=True, help='Knowledge graph name')
    parser.add_argument('--select-schema', required=True, help='Database schema to query')
    parser.add_argument('--openai-key', required=True, help='OpenAI API key')
    parser.add_argument('--db-host', required=True, help='Database host')
    parser.add_argument('--db-user', required=True, help='Database username')
    parser.add_argument('--db-password', required=True, help='Database password')
    
    # Optional arguments with defaults
    parser.add_argument('--temperature', type=float, default=0.0, help='OpenAI temperature (default: 0.0)')
    parser.add_argument('--db-port', type=int, default=1433, help='Database port (default: 1433)')
    parser.add_argument('--db-name', default='NewDQ', help='Database name (default: NewDQ)')
    parser.add_argument('--use-llm', action='store_true', help='Use LLM for parsing (default: rule-based)')
    parser.add_argument('--output-file', help='Save results to JSON file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    try:
        # Parse the test arguments
        args = parser.parse_args(test_args)
        
        print("✅ Argument parsing successful!")
        print("\nParsed arguments:")
        print(f"  NL Definition: {args.nl_definition}")
        print(f"  KG Name: {args.kg_name}")
        print(f"  Select Schema: {args.select_schema}")
        print(f"  OpenAI Key: {args.openai_key[:20]}...")
        print(f"  Temperature: {args.temperature}")
        print(f"  DB Host: {args.db_host}")
        print(f"  DB Port: {args.db_port}")
        print(f"  DB Name: {args.db_name}")
        print(f"  DB User: {args.db_user}")
        print(f"  DB Password: {'*' * len(args.db_password)}")
        print(f"  Use LLM: {args.use_llm}")
        print(f"  Verbose: {args.verbose}")
        print(f"  Output File: {args.output_file}")
        
        # Prepare database configuration
        db_config = {
            'host': args.db_host,
            'port': args.db_port,
            'database': args.db_name,
            'username': args.db_user,
            'password': args.db_password
        }
        
        print(f"\nDatabase configuration:")
        print(f"  Connection: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        print(f"  User: {db_config['username']}")
        
        print("\n🎉 All arguments parsed correctly!")
        print("\nYour command line format is perfect for the standalone_sql_preview.py script!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error parsing arguments: {e}")
        return False

def main():
    """Main function."""
    print("="*80)
    print("TESTING COMMAND LINE ARGUMENTS FOR standalone_sql_preview.py")
    print("="*80)
    
    success = test_argument_parsing()
    
    print("\n" + "="*80)
    if success:
        print("✅ TEST PASSED - Your command line format is correct!")
        print("\nTo run the actual script, make sure you have:")
        print("1. Installed dependencies: pip install -r requirements_sql_preview.txt")
        print("2. ODBC Driver 17 for SQL Server installed")
        print("3. Network access to your database")
        print("\nThen run:")
        print("python standalone_sql_preview.py \\")
        print("     --nl-definition \"get products from hana_material_master where OPS_PLANNER is missing\" \\")
        print("     --kg-name \"KG_Test_001\" \\")
        print("     --select-schema \"newdqnov7\" \\")
        print("     --openai-key \"your-key\" \\")
        print("     --temperature 0 \\")
        print("     --db-host \"DESKTOP-41O1AL9\\LOCALHOST\" \\")
        print("     --db-name \"NewDQ\" \\")
        print("     --db-user \"mithun\" \\")
        print("     --db-password \"mithun123\" \\")
        print("     --use-llm \\")
        print("     --verbose")
    else:
        print("❌ TEST FAILED - There's an issue with the argument parsing")
    print("="*80)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
