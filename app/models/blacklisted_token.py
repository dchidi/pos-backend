from datetime import datetime, timezone
from beanie import Document
from pymongo import ASCENDING, IndexModel

class BlacklistedToken(Document):
  token: str
  expires_at: datetime  # Same expiry as JWT
  created_at: datetime = datetime.now(timezone.utc)  # For cleanup monitoring

  class Settings:
    name = "blacklisted_tokens"
    indexes = [
      IndexModel(
          [("token", ASCENDING), ("expires_at", ASCENDING)],
          name="blacklistedtoken_model_token_expires_at"
          ),
      IndexModel(
          [("expires_at", ASCENDING)],
          name="blacklistedtoken_model_expires_at"
          ),  # For TTL index
      IndexModel(
          [("token", ASCENDING)],
          name="blacklistedtoken_model_token"
          ),  # For fast lookup
      IndexModel(
          [("created_at", ASCENDING)],
          name="blacklistedtoken_model_created_at"
      )
    ]