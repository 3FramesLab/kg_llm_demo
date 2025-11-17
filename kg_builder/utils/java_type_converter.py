"""
Java Type Converter - Centralized conversion of Java objects to Python types.
Handles serialization issues when JDBC returns Java objects that can't be JSON serialized.
"""

import logging
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)


def convert_java_types(value: Any) -> Any:
    """
    Convert Java types to Python types for JSON serialization.
    
    Args:
        value: Any value that might be a Java object
        
    Returns:
        Python-compatible value for JSON serialization
    """
    if value is None:
        return None
        
    # Check if it's a Java object
    if hasattr(value, '__class__') and 'java' in str(value.__class__):
        class_name = str(value.__class__)
        
        if 'BigInteger' in class_name:
            # Convert Java BigInteger to Python int via string
            return int(str(value))
        elif 'BigDecimal' in class_name:
            # Convert Java BigDecimal to Python float via string
            return float(str(value))
        elif 'String' in class_name:
            # Convert Java String to Python string
            return str(value)
        elif 'Timestamp' in class_name:
            # Convert Java Timestamp to Python string
            return str(value)
        elif 'Date' in class_name:
            # Convert Java Date to Python string
            return str(value)
        elif 'Boolean' in class_name:
            # Convert Java Boolean to Python bool
            return bool(value)
        elif 'Integer' in class_name:
            # Convert Java Integer to Python int
            return int(value)
        elif 'Long' in class_name:
            # Convert Java Long to Python int
            return int(value)
        elif 'Double' in class_name:
            # Convert Java Double to Python float
            return float(value)
        elif 'Float' in class_name:
            # Convert Java Float to Python float
            return float(value)
        else:
            # For any other Java type, convert to string as fallback
            logger.debug(f"Unknown Java type {class_name}, converting to string")
            return str(value)
    
    return value


def convert_java_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert all Java types in a dictionary to Python types.
    
    Args:
        data: Dictionary that may contain Java objects
        
    Returns:
        Dictionary with all Java objects converted to Python types
    """
    if not isinstance(data, dict):
        return convert_java_types(data)
    
    converted = {}
    for key, value in data.items():
        converted_key = convert_java_types(key)
        
        if isinstance(value, dict):
            converted[converted_key] = convert_java_dict(value)
        elif isinstance(value, list):
            converted[converted_key] = convert_java_list(value)
        else:
            converted[converted_key] = convert_java_types(value)
    
    return converted


def convert_java_list(data: List[Any]) -> List[Any]:
    """
    Convert all Java types in a list to Python types.
    
    Args:
        data: List that may contain Java objects
        
    Returns:
        List with all Java objects converted to Python types
    """
    if not isinstance(data, list):
        return convert_java_types(data)
    
    converted = []
    for item in data:
        if isinstance(item, dict):
            converted.append(convert_java_dict(item))
        elif isinstance(item, list):
            converted.append(convert_java_list(item))
        else:
            converted.append(convert_java_types(item))
    
    return converted


def convert_jdbc_row(row: tuple, columns: List[str]) -> Dict[str, Any]:
    """
    Convert a JDBC result row to a dictionary with Java type conversion.
    
    Args:
        row: JDBC result row (tuple of values)
        columns: Column names
        
    Returns:
        Dictionary with column names as keys and converted values
    """
    record = {}
    for i, value in enumerate(row):
        if i < len(columns):
            record[columns[i]] = convert_java_types(value)
    return record


def convert_jdbc_results(rows: List[tuple], columns: List[str]) -> List[Dict[str, Any]]:
    """
    Convert JDBC result set to list of dictionaries with Java type conversion.
    
    Args:
        rows: List of JDBC result rows
        columns: Column names
        
    Returns:
        List of dictionaries with converted values
    """
    return [convert_jdbc_row(row, columns) for row in rows]
