"""
JDBC Connection Manager - Centralized JVM and JDBC driver management.
Ensures JVM is initialized once with all JDBC drivers in classpath.
"""

import logging
import os
import glob
from typing import Optional, Any
import threading

logger = logging.getLogger(__name__)

# Global lock for JVM initialization
_jvm_lock = threading.Lock()
_jvm_initialized = False

def ensure_jvm_initialized():
    """
    Ensure JVM is initialized with all JDBC drivers.
    Thread-safe and idempotent - can be called multiple times safely.
    """
    global _jvm_initialized
    
    with _jvm_lock:
        if _jvm_initialized:
            return True
            
        try:
            import jpype
            from kg_builder.config import JDBC_DRIVERS_PATH
            
            # Check if JVM is already started by another process
            if jpype.isJVMStarted():
                logger.info("JVM already started by external process")
                _jvm_initialized = True
                return True
            
            logger.info("🚀 Initializing JVM with all JDBC drivers...")
            
            # Find all JDBC driver JAR files
            jdbc_patterns = [
                "mssql-jdbc*.jar",      # SQL Server
                "mysql-connector-j*.jar", # MySQL
                "postgresql-*.jar",     # PostgreSQL
                "ojdbc*.jar"           # Oracle
            ]
            
            all_jars = []
            for pattern in jdbc_patterns:
                jar_pattern = os.path.join(JDBC_DRIVERS_PATH, pattern)
                jars = glob.glob(jar_pattern)
                all_jars.extend(jars)
            
            if not all_jars:
                logger.warning(f"No JDBC drivers found in {JDBC_DRIVERS_PATH}")
                return False
            
            logger.info(f"Found {len(all_jars)} JDBC drivers:")
            for jar in all_jars:
                logger.info(f"  - {os.path.basename(jar)}")
            
            # Start JVM with all JDBC drivers in classpath
            classpath = os.pathsep.join(all_jars)
            jpype.startJVM(jpype.getDefaultJVMPath(), f"-Djava.class.path={classpath}")
            
            logger.info("✅ JVM initialized successfully with all JDBC drivers")
            _jvm_initialized = True
            return True
            
        except ImportError:
            logger.warning("JPype not available - JDBC functionality will be limited")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize JVM with JDBC drivers: {e}")
            return False


def get_jdbc_connection(driver_class: str, jdbc_url: str, username: str, password: str) -> Optional[Any]:
    """
    Get JDBC connection using centralized JVM management.
    
    Args:
        driver_class: JDBC driver class name
        jdbc_url: JDBC connection URL
        username: Database username
        password: Database password
        
    Returns:
        Database connection or None if failed
    """
    try:
        import jaydebeapi
        
        # Ensure JVM is initialized with all drivers
        if not ensure_jvm_initialized():
            raise Exception("Failed to initialize JVM with JDBC drivers")
        
        # Connect without specifying JAR (drivers already in classpath)
        conn = jaydebeapi.connect(
            driver_class,
            jdbc_url,
            [username, password]
        )
        
        return conn
        
    except ImportError:
        logger.error("jaydebeapi not available - cannot create JDBC connection")
        return None
    except Exception as e:
        logger.error(f"Failed to create JDBC connection: {e}")
        return None
