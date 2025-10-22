# LLM Logging Guide

## Overview

The LLM-enhanced multi-schema knowledge graph feature now includes comprehensive logging of:
- **Prompts** sent to the LLM (before API calls)
- **Responses** received from the LLM (after API calls)
- **Info logs** for high-level operations

## Configuration

### Enable DEBUG Logging

To see the prompts and responses, set the log level to `DEBUG` in your `.env` file:

```env
LOG_LEVEL=DEBUG
```

### Log Levels

- **INFO**: High-level operations (e.g., "LLM inferred 3 additional relationships")
- **DEBUG**: Detailed prompts and responses (full LLM input/output)
- **WARNING**: Issues like disabled LLM service
- **ERROR**: Exceptions and failures

## What Gets Logged

### 1. Inference Prompt (DEBUG)
```
Inference Prompt:
Analyze these database schemas and already-detected relationships.
Infer additional relationships that might exist based on semantic meaning and business logic.

SCHEMAS:
{...full schema JSON...}

ALREADY DETECTED RELATIONSHIPS:
{...relationships JSON...}
```

### 2. Inference Response (DEBUG)
```
LLM Inference Response:
{
    "inferred_relationships": [
        {
            "source_table": "catalog",
            "target_table": "design_code_master",
            "relationship_type": "SEMANTIC_REFERENCE",
            "reasoning": "...",
            "confidence": 0.85
        }
    ]
}
```

### 3. Enhancement Prompt (DEBUG)
```
Enhancement Prompt:
Generate clear business descriptions for these database relationships.

SCHEMAS:
{...full schema JSON...}

RELATIONSHIPS:
{...relationships JSON...}
```

### 4. Enhancement Response (DEBUG)
```
LLM Enhancement Response:
{
    "enhanced_relationships": [
        {
            "source_table": "catalog",
            "target_table": "design_code_master",
            "description": "Each product in the catalog is supplied by a vendor..."
        }
    ]
}
```

### 5. Scoring Prompt (DEBUG)
```
Scoring Prompt:
Assess the confidence and validity of these database relationships.

SCHEMAS:
{...full schema JSON...}

RELATIONSHIPS:
{...relationships JSON...}
```

### 6. Scoring Response (DEBUG)
```
LLM Scoring Response:
{
    "scored_relationships": [
        {
            "source_table": "catalog",
            "target_table": "design_code_master",
            "confidence": 0.95,
            "reasoning": "Strong naming pattern and semantic alignment",
            "validation_status": "VALID"
        }
    ]
}
```

### 7. Info Logs (INFO)
```
LLM inferred 3 additional relationships
LLM enhanced 80 relationships with descriptions
LLM scored 80 relationships with confidence
LLM enhancement complete: 80 relationships (3 inferred)
```

## Testing Logging

Run the test script to see all logs:

```bash
python test_llm_logging.py
```

This will:
1. Load environment variables from `.env`
2. Set logging to DEBUG level
3. Generate a multi-schema KG with LLM enhancement
4. Display all prompts and responses

## Log Output Example

```
2025-10-20 18:09:53,820 - kg_builder.services.multi_schema_llm_service - DEBUG - Inference Prompt:
Analyze these database schemas...

2025-10-20 18:10:05,504 - openai._base_client - DEBUG - Sending HTTP Request: POST https://api.openai.com/v1/chat/completions

2025-10-20 18:10:09,893 - kg_builder.services.multi_schema_llm_service - DEBUG - LLM Inference Response:
{
    "inferred_relationships": [...]
}

2025-10-20 18:10:09,893 - kg_builder.services.multi_schema_llm_service - INFO - LLM inferred 3 additional relationships
```

## Implementation Details

### Files Modified

1. **kg_builder/services/multi_schema_llm_service.py**
   - Added `logger.debug(f"Inference Prompt:\n{prompt}")` before API call
   - Added `logger.debug(f"LLM Inference Response:\n{result_text}")` after API call
   - Same for enhancement and scoring methods

2. **.env**
   - Changed `LOG_LEVEL=INFO` to `LOG_LEVEL=DEBUG`

3. **test_llm_logging.py** (new)
   - Test script that loads `.env` and demonstrates logging

### Logging Configuration

The logging is configured in `kg_builder/main.py`:

```python
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Troubleshooting

### Logs Not Showing

1. Check `.env` file has `LOG_LEVEL=DEBUG`
2. Ensure `OPENAI_API_KEY` is set
3. Run with `python test_llm_logging.py` to verify

### Too Much Output

If logs are too verbose:
- Set `LOG_LEVEL=INFO` to see only high-level operations
- Filter logs by logger name: `kg_builder.services.multi_schema_llm_service`

### Performance Impact

Logging has minimal performance impact:
- DEBUG logs are only written if log level is DEBUG
- LLM API calls dominate execution time (~4-5 seconds)
- Logging adds <100ms overhead

## Best Practices

1. **Development**: Use `LOG_LEVEL=DEBUG` to see all details
2. **Production**: Use `LOG_LEVEL=INFO` for cleaner logs
3. **Debugging**: Use `LOG_LEVEL=DEBUG` when troubleshooting LLM issues
4. **Monitoring**: Parse INFO logs for metrics and monitoring

## Next Steps

- Monitor LLM response quality using the logged confidence scores
- Adjust prompts based on logged responses
- Use logging for debugging relationship inference issues
- Track LLM API usage through logs

