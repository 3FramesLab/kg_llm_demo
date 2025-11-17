"""
Java-aware JSON encoder for FastAPI responses.
Automatically converts Java objects to Python objects during JSON serialization.
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class JavaAwareJSONEncoder(json.JSONEncoder):
    """JSON encoder that automatically converts Java objects to Python objects."""
    
    def default(self, obj: Any) -> Any:
        """Convert Java objects to JSON-serializable Python objects."""
        
        # Check if it's a Java object
        if hasattr(obj, '__class__') and 'java' in str(obj.__class__):
            class_name = str(obj.__class__)
            
            try:
                if 'BigInteger' in class_name:
                    return int(str(obj))
                elif 'BigDecimal' in class_name:
                    return float(str(obj))
                elif 'String' in class_name:
                    return str(obj)
                elif 'Timestamp' in class_name:
                    return str(obj)
                elif 'Date' in class_name:
                    return str(obj)
                elif 'Boolean' in class_name:
                    return bool(obj)
                elif 'Integer' in class_name:
                    return int(str(obj))
                elif 'Long' in class_name:
                    return int(str(obj))
                elif 'Double' in class_name:
                    return float(str(obj))
                elif 'Float' in class_name:
                    return float(str(obj))
                else:
                    # For any other Java type, convert to string as fallback
                    logger.debug(f"Converting unknown Java type {class_name} to string")
                    return str(obj)
            except Exception as e:
                logger.warning(f"Failed to convert Java object {class_name}: {e}")
                return str(obj)
        
        # For non-Java objects, use the default behavior
        return super().default(obj)


def convert_java_objects_recursive(obj: Any) -> Any:
    """
    Recursively convert all Java objects in a data structure to Python objects.
    This is a more aggressive approach that traverses the entire object tree.
    """
    
    if obj is None:
        return None
    
    # Handle Java objects
    if hasattr(obj, '__class__') and 'java' in str(obj.__class__):
        class_name = str(obj.__class__)
        
        try:
            if 'BigInteger' in class_name:
                return int(str(obj))
            elif 'BigDecimal' in class_name:
                return float(str(obj))
            elif 'String' in class_name:
                return str(obj)
            elif 'Timestamp' in class_name:
                return str(obj)
            elif 'Date' in class_name:
                return str(obj)
            elif 'Boolean' in class_name:
                return bool(obj)
            elif 'Integer' in class_name:
                return int(str(obj))
            elif 'Long' in class_name:
                return int(str(obj))
            elif 'Double' in class_name:
                return float(str(obj))
            elif 'Float' in class_name:
                return float(str(obj))
            else:
                return str(obj)
        except Exception as e:
            logger.warning(f"Failed to convert Java object {class_name}: {e}")
            return str(obj)
    
    # Handle Python collections recursively
    elif isinstance(obj, dict):
        return {
            convert_java_objects_recursive(k): convert_java_objects_recursive(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, (list, tuple)):
        converted = [convert_java_objects_recursive(item) for item in obj]
        return converted if isinstance(obj, list) else tuple(converted)
    elif isinstance(obj, set):
        return {convert_java_objects_recursive(item) for item in obj}
    
    # Return as-is for other Python objects
    return obj
