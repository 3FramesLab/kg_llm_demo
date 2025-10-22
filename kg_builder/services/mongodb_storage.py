"""
MongoDB storage service for reconciliation results.

This service stores reconciliation execution results as JSON documents in MongoDB.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from bson import ObjectId

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, PyMongoError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    logging.warning("pymongo not installed. MongoDB storage will not be available.")

from kg_builder.config import (
    get_mongodb_connection_string,
    MONGODB_DATABASE,
    MONGODB_RESULTS_COLLECTION
)

logger = logging.getLogger(__name__)


class MongoDBStorage:
    """MongoDB storage for reconciliation results."""

    def __init__(self):
        """Initialize MongoDB connection."""
        if not PYMONGO_AVAILABLE:
            raise RuntimeError(
                "pymongo is not installed. "
                "Please install it with: pip install pymongo"
            )

        self.client: Optional[MongoClient] = None
        self.db = None
        self.collection = None
        self._connect()

    def _connect(self):
        """Establish connection to MongoDB."""
        try:
            connection_string = get_mongodb_connection_string()
            logger.info(f"Connecting to MongoDB at {connection_string.split('@')[1] if '@' in connection_string else connection_string}")

            self.client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000
            )

            # Test connection
            self.client.admin.command('ping')

            self.db = self.client[MONGODB_DATABASE]
            self.collection = self.db[MONGODB_RESULTS_COLLECTION]

            logger.info(f"Connected to MongoDB database: {MONGODB_DATABASE}")

        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Error initializing MongoDB: {e}")
            raise

    def is_connected(self) -> bool:
        """Check if MongoDB connection is active."""
        if not self.client:
            return False

        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            return False

    def store_reconciliation_result(
        self,
        ruleset_id: str,
        matched_records: List[Dict[str, Any]],
        unmatched_source: List[Dict[str, Any]],
        unmatched_target: List[Dict[str, Any]],
        execution_metadata: Dict[str, Any]
    ) -> str:
        """
        Store reconciliation execution results in MongoDB.

        Args:
            ruleset_id: ID of the ruleset that was executed
            matched_records: List of matched records
            unmatched_source: List of unmatched source records
            unmatched_target: List of unmatched target records
            execution_metadata: Metadata about the execution (time, config, etc.)

        Returns:
            MongoDB document ID as a string
        """
        try:
            # Prepare document
            document = {
                "ruleset_id": ruleset_id,
                "execution_timestamp": datetime.utcnow(),
                "matched_count": len(matched_records),
                "unmatched_source_count": len(unmatched_source),
                "unmatched_target_count": len(unmatched_target),
                "matched_records": matched_records,
                "unmatched_source": unmatched_source,
                "unmatched_target": unmatched_target,
                "metadata": execution_metadata
            }

            # Insert document
            result = self.collection.insert_one(document)
            doc_id = str(result.inserted_id)

            logger.info(
                f"Stored reconciliation result in MongoDB: "
                f"document_id={doc_id}, "
                f"matched={len(matched_records)}, "
                f"unmatched_source={len(unmatched_source)}, "
                f"unmatched_target={len(unmatched_target)}"
            )

            return doc_id

        except PyMongoError as e:
            logger.error(f"Error storing reconciliation result: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error storing reconciliation result: {e}")
            raise

    def get_reconciliation_result(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a reconciliation result by document ID.

        Args:
            document_id: MongoDB document ID

        Returns:
            Document as dictionary, or None if not found
        """
        try:
            result = self.collection.find_one({"_id": ObjectId(document_id)})

            if result:
                # Convert ObjectId to string for JSON serialization
                result["_id"] = str(result["_id"])
                result["execution_timestamp"] = result["execution_timestamp"].isoformat()

            return result

        except Exception as e:
            logger.error(f"Error retrieving reconciliation result: {e}")
            return None

    def list_reconciliation_results(
        self,
        ruleset_id: Optional[str] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List reconciliation results.

        Args:
            ruleset_id: Optional filter by ruleset ID
            limit: Maximum number of results to return
            skip: Number of results to skip (for pagination)

        Returns:
            List of reconciliation result documents
        """
        try:
            query = {}
            if ruleset_id:
                query["ruleset_id"] = ruleset_id

            cursor = self.collection.find(query).sort("execution_timestamp", -1).skip(skip).limit(limit)

            results = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                doc["execution_timestamp"] = doc["execution_timestamp"].isoformat()
                results.append(doc)

            return results

        except Exception as e:
            logger.error(f"Error listing reconciliation results: {e}")
            return []

    def delete_reconciliation_result(self, document_id: str) -> bool:
        """
        Delete a reconciliation result by document ID.

        Args:
            document_id: MongoDB document ID

        Returns:
            True if deleted, False otherwise
        """
        try:
            result = self.collection.delete_one({"_id": ObjectId(document_id)})
            return result.deleted_count > 0

        except Exception as e:
            logger.error(f"Error deleting reconciliation result: {e}")
            return False

    def get_summary_statistics(self, ruleset_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get summary statistics for reconciliation results.

        Args:
            ruleset_id: Optional filter by ruleset ID

        Returns:
            Dictionary with summary statistics
        """
        try:
            match_stage = {}
            if ruleset_id:
                match_stage = {"$match": {"ruleset_id": ruleset_id}}

            pipeline = []
            if match_stage:
                pipeline.append(match_stage)

            pipeline.extend([
                {
                    "$group": {
                        "_id": None,
                        "total_executions": {"$sum": 1},
                        "total_matched": {"$sum": "$matched_count"},
                        "total_unmatched_source": {"$sum": "$unmatched_source_count"},
                        "total_unmatched_target": {"$sum": "$unmatched_target_count"},
                        "avg_matched": {"$avg": "$matched_count"},
                        "avg_unmatched_source": {"$avg": "$unmatched_source_count"},
                        "avg_unmatched_target": {"$avg": "$unmatched_target_count"}
                    }
                }
            ])

            result = list(self.collection.aggregate(pipeline))

            if result:
                stats = result[0]
                stats.pop("_id", None)
                return stats
            else:
                return {
                    "total_executions": 0,
                    "total_matched": 0,
                    "total_unmatched_source": 0,
                    "total_unmatched_target": 0,
                    "avg_matched": 0,
                    "avg_unmatched_source": 0,
                    "avg_unmatched_target": 0
                }

        except Exception as e:
            logger.error(f"Error getting summary statistics: {e}")
            return {}

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Singleton instance
_mongodb_storage: Optional[MongoDBStorage] = None


def get_mongodb_storage() -> MongoDBStorage:
    """Get or create the singleton MongoDB storage instance."""
    global _mongodb_storage
    if _mongodb_storage is None:
        _mongodb_storage = MongoDBStorage()
    return _mongodb_storage
