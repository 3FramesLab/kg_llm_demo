# MongoDB Reconciliation Storage Guide

## Overview

This guide explains how to use MongoDB for storing reconciliation execution results as JSON documents. When you execute reconciliation rules in **Direct Execution Mode**, the results are automatically stored in MongoDB for easy querying and analysis.

## Architecture

```
┌─────────────────┐
│  Source DB      │
│  (Oracle, etc.) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Reconciliation         │
│  Executor               │◄────── JDBC Connection
│                         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  MongoDB                │
│  (JSON Storage)         │
│  - matched_records      │
│  - unmatched_source     │
│  - unmatched_target     │
│  - execution_metadata   │
└─────────────────────────┘
```

## Features

- **Automatic Storage**: Reconciliation results are automatically stored as JSON documents
- **Query API**: RESTful API endpoints to query stored results
- **Statistics**: Get summary statistics across multiple executions
- **Pagination**: List results with pagination support
- **Time-based Tracking**: Each execution is timestamped for historical analysis

## Getting Started

### 1. Start MongoDB with Docker Compose

MongoDB is included in the docker-compose.yml configuration:

```bash
docker-compose up -d mongodb
```

This will start MongoDB on port 27017 with default credentials:
- Username: `admin`
- Password: `admin123`
- Database: `reconciliation`

### 2. Environment Variables

The following environment variables control MongoDB connection (already configured in docker-compose.yml):

```env
MONGODB_HOST=mongodb
MONGODB_PORT=27017
MONGODB_USERNAME=admin
MONGODB_PASSWORD=admin123
MONGODB_DATABASE=reconciliation
MONGODB_AUTH_SOURCE=admin
MONGODB_RESULTS_COLLECTION=reconciliation_results
```

### 3. Execute Reconciliation with MongoDB Storage

When executing reconciliation in **Direct Execution Mode**, set `store_in_mongodb` to `true`:

```python
import requests

request_data = {
    "ruleset_id": "RECON_ABC123",
    "limit": 100,
    "source_db_config": {
        "db_type": "oracle",
        "host": "localhost",
        "port": 1521,
        "database": "ORCL",
        "username": "user1",
        "password": "pass1"
    },
    "target_db_config": {
        "db_type": "oracle",
        "host": "localhost",
        "port": 1521,
        "database": "ORCL",
        "username": "user2",
        "password": "pass2"
    },
    "include_matched": True,
    "include_unmatched": True,
    "store_in_mongodb": True  # Enable MongoDB storage
}

response = requests.post(
    "http://localhost:8000/api/v1/reconciliation/execute",
    json=request_data
)

result = response.json()
print(f"MongoDB Document ID: {result['mongodb_document_id']}")
```

## API Endpoints

### 1. Execute Reconciliation with MongoDB Storage

**Endpoint**: `POST /api/v1/reconciliation/execute`

**Request Body**:
```json
{
  "ruleset_id": "RECON_ABC123",
  "limit": 100,
  "source_db_config": { ... },
  "target_db_config": { ... },
  "store_in_mongodb": true
}
```

**Response**:
```json
{
  "success": true,
  "matched_count": 150,
  "unmatched_source_count": 25,
  "unmatched_target_count": 30,
  "matched_records": [...],
  "unmatched_source": [...],
  "unmatched_target": [...],
  "execution_time_ms": 2456.78,
  "mongodb_document_id": "507f1f77bcf86cd799439011",
  "storage_location": "mongodb"
}
```

### 2. Retrieve a Specific Result

**Endpoint**: `GET /api/v1/reconciliation/results/{document_id}`

**Example**:
```bash
curl http://localhost:8000/api/v1/reconciliation/results/507f1f77bcf86cd799439011
```

**Response**:
```json
{
  "success": true,
  "result": {
    "_id": "507f1f77bcf86cd799439011",
    "ruleset_id": "RECON_ABC123",
    "execution_timestamp": "2025-10-22T10:30:45.123Z",
    "matched_count": 150,
    "unmatched_source_count": 25,
    "unmatched_target_count": 30,
    "matched_records": [...],
    "unmatched_source": [...],
    "unmatched_target": [...],
    "metadata": {
      "execution_time_ms": 2456.78,
      "source_db_type": "oracle",
      "target_db_type": "oracle"
    }
  }
}
```

### 3. List Reconciliation Results

**Endpoint**: `GET /api/v1/reconciliation/results`

**Query Parameters**:
- `ruleset_id` (optional): Filter by ruleset ID
- `limit` (optional): Maximum results to return (default: 100)
- `skip` (optional): Number of results to skip for pagination (default: 0)

**Example**:
```bash
curl "http://localhost:8000/api/v1/reconciliation/results?ruleset_id=RECON_ABC123&limit=10"
```

**Response**:
```json
{
  "success": true,
  "results": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "ruleset_id": "RECON_ABC123",
      "execution_timestamp": "2025-10-22T10:30:45.123Z",
      "matched_count": 150,
      "unmatched_source_count": 25,
      "unmatched_target_count": 30
    }
  ],
  "count": 1,
  "limit": 10,
  "skip": 0
}
```

### 4. Get Summary Statistics

**Endpoint**: `GET /api/v1/reconciliation/statistics`

**Query Parameters**:
- `ruleset_id` (optional): Filter by ruleset ID

**Example**:
```bash
curl "http://localhost:8000/api/v1/reconciliation/statistics?ruleset_id=RECON_ABC123"
```

**Response**:
```json
{
  "success": true,
  "statistics": {
    "total_executions": 5,
    "total_matched": 750,
    "total_unmatched_source": 125,
    "total_unmatched_target": 150,
    "avg_matched": 150.0,
    "avg_unmatched_source": 25.0,
    "avg_unmatched_target": 30.0
  }
}
```

### 5. Delete a Result

**Endpoint**: `DELETE /api/v1/reconciliation/results/{document_id}`

**Example**:
```bash
curl -X DELETE http://localhost:8000/api/v1/reconciliation/results/507f1f77bcf86cd799439011
```

**Response**:
```json
{
  "success": true,
  "message": "Reconciliation result '507f1f77bcf86cd799439011' deleted successfully"
}
```

## MongoDB Document Structure

Each reconciliation execution is stored as a MongoDB document with the following structure:

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "ruleset_id": "RECON_ABC123",
  "execution_timestamp": ISODate("2025-10-22T10:30:45.123Z"),
  "matched_count": 150,
  "unmatched_source_count": 25,
  "unmatched_target_count": 30,
  "matched_records": [
    {
      "source_record": { "id": 1, "name": "Product A" },
      "target_record": { "id": 101, "name": "Product A" },
      "match_confidence": 0.95,
      "rule_used": "RULE_001",
      "rule_name": "Match by Product Name"
    }
  ],
  "unmatched_source": [
    {
      "id": 2,
      "name": "Product B",
      "rule_id": "RULE_001",
      "rule_name": "Match by Product Name"
    }
  ],
  "unmatched_target": [
    {
      "id": 102,
      "name": "Product C",
      "rule_id": "RULE_001",
      "rule_name": "Match by Product Name"
    }
  ],
  "metadata": {
    "execution_time_ms": 2456.78,
    "limit": 100,
    "source_db_type": "oracle",
    "target_db_type": "oracle",
    "include_matched": true,
    "include_unmatched": true
  }
}
```

## Querying MongoDB Directly

You can also query MongoDB directly using the `mongosh` command-line tool:

```bash
# Connect to MongoDB
docker exec -it kg-builder-mongodb mongosh -u admin -p admin123 --authenticationDatabase admin

# Switch to reconciliation database
use reconciliation

# List all results
db.reconciliation_results.find().pretty()

# Find results by ruleset_id
db.reconciliation_results.find({"ruleset_id": "RECON_ABC123"}).pretty()

# Count total executions
db.reconciliation_results.countDocuments()

# Get latest execution
db.reconciliation_results.find().sort({"execution_timestamp": -1}).limit(1).pretty()

# Aggregate statistics
db.reconciliation_results.aggregate([
  {
    $group: {
      _id: "$ruleset_id",
      total_executions: { $sum: 1 },
      avg_matched: { $avg: "$matched_count" },
      total_matched: { $sum: "$matched_count" }
    }
  }
])
```

## Best Practices

1. **Periodic Cleanup**: Set up a scheduled job to delete old reconciliation results to manage storage
2. **Indexing**: Create indexes on frequently queried fields:
   ```javascript
   db.reconciliation_results.createIndex({"ruleset_id": 1})
   db.reconciliation_results.createIndex({"execution_timestamp": -1})
   ```
3. **Monitoring**: Monitor MongoDB storage usage and query performance
4. **Backups**: Regularly backup MongoDB data for disaster recovery

## Troubleshooting

### MongoDB Connection Issues

If you see connection errors:

1. Check if MongoDB is running:
   ```bash
   docker ps | grep mongodb
   ```

2. Check MongoDB logs:
   ```bash
   docker logs kg-builder-mongodb
   ```

3. Verify connection settings in `.env` file

### pymongo Not Installed

If you see "pymongo not installed" error:

```bash
pip install pymongo==4.6.1
```

### Storage Disabled

If `storage_location` is `"memory"` instead of `"mongodb"`:

1. Check if `store_in_mongodb` is set to `true` in the request
2. Verify MongoDB is running and accessible
3. Check application logs for MongoDB connection errors

## Next Steps

- Review the [Reconciliation Execution Guide](docs/RECONCILIATION_EXECUTION_GUIDE.md) for complete workflow
- Explore the [Web Application Guide](WEB_APP_GUIDE.md) for UI-based reconciliation
- Check [Docker Setup](docs/DOCKER_GUIDE.md) for deployment options
