# LLM Quick Start - 5 Minutes

Get OpenAI LLM integration working in 5 minutes!

## Step 1: Get OpenAI API Key (2 minutes)

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

## Step 2: Set Environment Variable (1 minute)

### Option A: Create `.env` file
```bash
# Create .env in project root
OPENAI_API_KEY=sk-your-key-here
```

### Option B: Set environment variable
```bash
# Linux/Mac
export OPENAI_API_KEY=sk-your-key-here

# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key-here"

# Windows CMD
set OPENAI_API_KEY=sk-your-key-here
```

## Step 3: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

## Step 4: Start Server (30 seconds)

```bash
python -m kg_builder.main
```

## Step 5: Test LLM (30 seconds)

### Check Status
```bash
curl http://localhost:8000/api/v1/llm/status
```

Expected response:
```json
{
  "enabled": true,
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

### Extract Entities
```bash
curl -X POST http://localhost:8000/api/v1/llm/extract/orderMgmt-catalog
```

### Analyze Schema
```bash
curl -X POST http://localhost:8000/api/v1/llm/analyze/orderMgmt-catalog
```

## Done! 🎉

Your LLM integration is working!

## Next Steps

### Python Example
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Extract entities and relationships
response = requests.post(
    f"{BASE_URL}/llm/extract/orderMgmt-catalog"
)
result = response.json()

print(f"Entities: {len(result['entities'])}")
print(f"Relationships: {len(result['relationships'])}")

for entity in result['entities']:
    print(f"\n{entity['name']}")
    print(f"  Purpose: {entity['purpose']}")
    print(f"  Type: {entity['type']}")
```

### Swagger UI
Visit: http://localhost:8000/docs

Look for:
- `POST /api/v1/llm/extract/{schema_name}`
- `POST /api/v1/llm/analyze/{schema_name}`
- `GET /api/v1/llm/status`

## Troubleshooting

### "LLM service is not enabled"
- Check that `OPENAI_API_KEY` is set
- Restart the server
- Verify key is correct

### "Invalid API key"
- Go to https://platform.openai.com/api-keys
- Verify your key is correct
- Check for extra spaces

### "Rate limit exceeded"
- Wait a moment and retry
- Check your OpenAI usage at https://platform.openai.com/account/usage

### "Timeout"
- Schema might be too large
- Try with a smaller schema first

## Configuration

### Change Model
Edit `.env`:
```bash
OPENAI_MODEL=gpt-4
```

Options:
- `gpt-3.5-turbo` (fast, cheap) ← recommended
- `gpt-4` (powerful, expensive)
- `gpt-4-turbo-preview` (balanced)

### Adjust Creativity
Edit `.env`:
```bash
OPENAI_TEMPERATURE=0.3
```

Range: 0 (consistent) to 2 (creative)

### Limit Response Length
Edit `.env`:
```bash
OPENAI_MAX_TOKENS=1000
```

## Cost Estimate

- Entity extraction: ~$0.0001-0.0005 per schema
- Relationship extraction: ~$0.0001-0.0008 per schema
- Schema analysis: ~$0.0002-0.0010 per schema

**Total for 100 schemas: ~$0.10-0.50**

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/llm/status` | GET | Check if LLM is enabled |
| `/llm/extract/{schema}` | POST | Extract entities & relationships |
| `/llm/analyze/{schema}` | POST | Analyze schema |

## Documentation

- **Full Setup**: [LLM_INTEGRATION.md](LLM_INTEGRATION.md)
- **All Prompts**: [LLM_PROMPTS_REFERENCE.md](LLM_PROMPTS_REFERENCE.md)
- **Code Examples**: [LLM_EXAMPLES.md](LLM_EXAMPLES.md)
- **Implementation**: [LLM_IMPLEMENTATION_SUMMARY.md](LLM_IMPLEMENTATION_SUMMARY.md)

## What's Happening

When you call the LLM endpoints:

1. **Schema is loaded** from JSON file
2. **Prompt is created** with schema data
3. **OpenAI API is called** with the prompt
4. **Response is parsed** as JSON
5. **Results are returned** to you

The LLM understands:
- What each table represents
- Why relationships exist
- Business logic in the schema
- Data quality patterns

## Next: Use Results

The extracted entities and relationships can be used to:
- Create richer knowledge graphs
- Generate documentation
- Understand data models
- Identify business logic
- Improve data quality

See [LLM_EXAMPLES.md](LLM_EXAMPLES.md) for integration examples.

---

**You're all set!** Start exploring the LLM features! 🚀

