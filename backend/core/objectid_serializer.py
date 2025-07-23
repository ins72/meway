"""
ObjectId Serialization Utility
Handles MongoDB ObjectId serialization for FastAPI responses
"""

from bson import ObjectId
from typing import Any, Dict, List, Union

def serialize_objectid(obj: Any) -> Any:
    """Convert ObjectId objects to strings for JSON serialization"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: serialize_objectid(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_objectid(item) for item in obj]
    else:
        return obj

def prepare_response_data(data: Union[Dict, List]) -> Union[Dict, List]:
    """Prepare data for FastAPI response by serializing ObjectIds"""
    return serialize_objectid(data)

def safe_document_return(doc: Dict) -> Dict:
    """Safely return a MongoDB document with ObjectId converted to string"""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

def safe_documents_return(docs: List[Dict]) -> List[Dict]:
    """Safely return MongoDB documents with ObjectIds converted to strings"""
    for doc in docs:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
    return docs
