from datetime import datetime
import re
import os

from dotenv import load_dotenv
load_dotenv()

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient, errors


class User:
    def __init__(self, first_name, last_name, birth_date, birth_place, phone):
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.birth_place = birth_place
        self.phone = phone

    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birth_date": self.birth_date,
            "birth_place": self.birth_place,
            "phone": self.phone,
        }


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Lazy connection: connect only when first needed
_client = None
_users_collection = None
_connection_error = None


def _init_db():
    """Initialize MongoDB connection on first use (lazy)."""
    global _client, _users_collection, _connection_error
    
    if _users_collection is not None:
        return  # Already initialized
    
    try:
        # Use longer timeout for Atlas clusters (they can be slow)
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=15000, connectTimeoutMS=15000)
        _client.server_info()  # Test connection
        db = _client["user_management"]
        _users_collection = db["users"]
        _users_collection.create_index("phone", unique=True)
        print("✓ Connected to MongoDB")
    except Exception as e:
        _connection_error = str(e)
        print(f"⚠ MongoDB connection failed (will retry on next request): {type(e).__name__}")
        _users_collection = None
        _client = None


def _require_collection():
    global _connection_error
    _init_db()
    if _users_collection is None:
        msg = f"MongoDB is not available: {_connection_error}" if _connection_error else "MongoDB is not available."
        raise RuntimeError(msg)
    return _users_collection


def _serialize_user(document):
    if not document:
        return None
    document["_id"] = str(document["_id"])
    return document


def validate(data):
    data = data or {}
    for field in ["first_name", "last_name", "birth_date", "birth_place", "phone"]:
        if not str(data.get(field, "")).strip():
            return f"Field '{field}' is required."
    try:
        datetime.strptime(str(data["birth_date"]).strip(), "%Y-%m-%d")
    except ValueError:
        return "Birth date must be in YYYY-MM-DD format."
    if not re.match(r"^\+?[0-9]{7,15}$", str(data["phone"]).strip()):
        return "Invalid phone number format."
    return None


def list_users(query_text=""):
    collection = _require_collection()
    query_text = str(query_text or "").strip()
    query = {}
    if query_text:
        query = {
            "$or": [
                {"first_name": {"$regex": query_text, "$options": "i"}},
                {"last_name": {"$regex": query_text, "$options": "i"}},
                {"birth_place": {"$regex": query_text, "$options": "i"}},
                {"phone": {"$regex": query_text, "$options": "i"}},
                {"birth_date": {"$regex": query_text, "$options": "i"}},
            ]
        }
    return [_serialize_user(user) for user in collection.find(query)]


def create_user(data):
    collection = _require_collection()
    err = validate(data)
    if err:
        raise ValueError(err)

    result = collection.insert_one(
        {
            "first_name": str(data["first_name"]).strip(),
            "last_name": str(data["last_name"]).strip(),
            "birth_date": str(data["birth_date"]).strip(),
            "birth_place": str(data["birth_place"]).strip(),
            "phone": str(data["phone"]).strip(),
        }
    )
    return str(result.inserted_id)


def get_user(user_id):
    collection = _require_collection()
    try:
        object_id = ObjectId(user_id)
    except (InvalidId, TypeError):
        raise ValueError("Invalid user id.")
    return _serialize_user(collection.find_one({"_id": object_id}))


def update_user(user_id, data):
    collection = _require_collection()
    err = validate(data)
    if err:
        raise ValueError(err)

    try:
        object_id = ObjectId(user_id)
    except (InvalidId, TypeError):
        raise ValueError("Invalid user id.")

    result = collection.update_one(
        {"_id": object_id},
        {
            "$set": {
                "first_name": str(data["first_name"]).strip(),
                "last_name": str(data["last_name"]).strip(),
                "birth_date": str(data["birth_date"]).strip(),
                "birth_place": str(data["birth_place"]).strip(),
                "phone": str(data["phone"]).strip(),
            }
        },
    )
    return result.matched_count > 0


def delete_user(user_id):
    collection = _require_collection()
    try:
        object_id = ObjectId(user_id)
    except (InvalidId, TypeError):
        raise ValueError("Invalid user id.")

    result = collection.delete_one({"_id": object_id})
    return result.deleted_count > 0
