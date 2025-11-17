"""
Java Response Decorator - Automatically converts Java objects in API responses.
Only applies to specific endpoints that need Java object conversion.
"""

import logging
from functools import wraps
from typing import Any, Callable
from fastapi import Response
from fastapi.responses import JSONResponse
import json

logger = logging.getLogger(__name__)


def convert_java_objects_deep(obj: Any) -> Any:
    """
    Recursively convert all Java objects in a data structure to Python objects.
    This is the most aggressive approach - it will find and convert ANY Java object.
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
                logger.debug(f"Converting unknown Java type {class_name} to string")
                return str(obj)
        except Exception as e:
            logger.warning(f"Failed to convert Java object {class_name}: {e}")
            return str(obj)
    
    # Handle Python collections recursively
    elif isinstance(obj, dict):
        return {
            convert_java_objects_deep(k): convert_java_objects_deep(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, (list, tuple)):
        converted = [convert_java_objects_deep(item) for item in obj]
        return converted if isinstance(obj, list) else tuple(converted)
    elif isinstance(obj, set):
        return {convert_java_objects_deep(item) for item in obj}
    
    # Return as-is for other Python objects
    return obj


def java_safe_response(func: Callable) -> Callable:
    """
    Decorator that ensures all Java objects in the response are converted to Python objects.
    Use this on any endpoint that might return Java objects from JDBC.
    """
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Call the original function
            result = await func(*args, **kwargs)
            
            # Convert any Java objects in the result
            converted_result = convert_java_objects_deep(result)
            
            # Return as JSONResponse to ensure proper serialization
            return JSONResponse(content=converted_result)
            
        except Exception as e:
            logger.error(f"Error in java_safe_response wrapper for {func.__name__}: {e}")
            # If conversion fails, try to return the original result
            # This ensures the endpoint doesn't break completely
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as original_error:
                logger.error(f"Original function also failed: {original_error}")
                raise original_error
    
    return wrapper


class JavaSafeJSONResponse(JSONResponse):
    """
    Custom JSONResponse that automatically converts Java objects.
    Use this as response_class for endpoints that return Java objects.
    """
    
    def render(self, content: Any) -> bytes:
        # Convert all Java objects to Python objects
        converted_content = convert_java_objects_deep(content)
        
        # Use standard JSON encoding
        return json.dumps(
            converted_content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")
