#!/usr/bin/env python3
"""
DQ-POC Environment Setup Script
Manages unified environment configuration across all components
"""

import os
import shutil
import argparse
from pathlib import Path

def setup_environment(environment='development'):
    """
    Setup unified environment configuration for DQ-POC project
    
    Args:
        environment: 'development', 'docker', or 'production'
    """
    
    project_root = Path(__file__).parent.parent
    config_dir = project_root / 'config'
    unified_env = config_dir / 'unified.env'
    
    print(f"🔧 Setting up {environment} environment...")
    print(f"📁 Project root: {project_root}")
    
    # Check if unified.env exists
    if not unified_env.exists():
        print(f"❌ Unified environment file not found: {unified_env}")
        return False
    
    # Copy unified.env to root .env
    root_env = project_root / '.env'
    print(f"📋 Copying {unified_env} → {root_env}")
    shutil.copy2(unified_env, root_env)
    
    # Create web-app .env with appropriate API URL
    web_app_dir = project_root / 'web-app'
    web_app_env = web_app_dir / '.env'
    
    api_urls = {
        'development': 'http://localhost:8000/v1',
        'docker': 'http://localhost:8000/v1',
        'production': 'https://api.company.com/v1'  # Update for your production URL
    }
    
    web_app_content = f"# API Configuration\nREACT_APP_API_URL={api_urls[environment]}\n"
    
    print(f"🌐 Creating web-app environment: {web_app_env}")
    with open(web_app_env, 'w') as f:
        f.write(web_app_content)
    
    # Apply environment-specific modifications
    if environment == 'docker':
        apply_docker_overrides(root_env)
    elif environment == 'production':
        apply_production_overrides(root_env)
    
    print(f"✅ Environment setup complete for {environment}")
    print("\n📝 Next steps:")
    print("1. Review and customize the .env file with your specific settings")
    print("2. Update database credentials and connection details")
    print("3. Set your OpenAI API key if using LLM features")
    print("4. Configure email settings for Airflow notifications")
    print("5. Run: python scripts/setup-environment.py --validate")
    
    return True

def apply_docker_overrides(env_file):
    """Apply Docker-specific environment overrides"""
    print("🐳 Applying Docker environment overrides...")
    
    overrides = {
        'FALKORDB_HOST': 'falkordb',
        'MONGODB_HOST': 'mongodb',
        'JDBC_DRIVERS_PATH': '/app/jdbc_drivers',
        'SOURCE_DB_HOST': 'host.docker.internal',
        'TARGET_DB_HOST': 'host.docker.internal',
        'KPI_DB_HOST': 'host.docker.internal'
    }
    
    apply_overrides(env_file, overrides)

def apply_production_overrides(env_file):
    """Apply production-specific environment overrides"""
    print("🏭 Applying production environment overrides...")
    
    overrides = {
        'LOG_LEVEL': 'WARNING',
        'API_RELOAD': 'false',
        'ENABLE_LLM_EXTRACTION': 'false',  # Disable for production unless needed
        'AIRFLOW_LOGGING_LEVEL': 'WARNING'
    }
    
    apply_overrides(env_file, overrides)

def apply_overrides(env_file, overrides):
    """Apply environment variable overrides to .env file"""
    
    # Read current content
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Apply overrides
    for key, value in overrides.items():
        updated = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                updated = True
                print(f"  ✏️  Updated {key}={value}")
                break
        
        if not updated:
            lines.append(f"{key}={value}\n")
            print(f"  ➕ Added {key}={value}")
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.writelines(lines)

def validate_environment():
    """Validate that environment is properly configured"""
    print("🔍 Validating environment configuration...")
    
    project_root = Path(__file__).parent.parent
    required_files = [
        project_root / '.env',
        project_root / 'web-app' / '.env'
    ]
    
    all_valid = True
    for file_path in required_files:
        if file_path.exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_valid = False
    
    return all_valid

def main():
    parser = argparse.ArgumentParser(description='Setup DQ-POC environment configuration')
    parser.add_argument(
        'environment',
        choices=['development', 'docker', 'production'],
        help='Environment type to setup'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate environment configuration'
    )
    
    args = parser.parse_args()
    
    if args.validate:
        if validate_environment():
            print("🎉 Environment validation passed!")
        else:
            print("❌ Environment validation failed!")
            return 1
    else:
        if setup_environment(args.environment):
            print("🎉 Environment setup completed successfully!")
        else:
            print("❌ Environment setup failed!")
            return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
