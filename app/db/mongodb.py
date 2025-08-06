from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging
import traceback

from app.core.settings import settings


from app.models import MODELS  # Import here to avoid circular imports
# Configure logging
logger = logging.getLogger(__name__)

class MongoDB:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.is_connected = False

    async def connect(self):
        try:
            logger.info("Connecting to MongoDB...")
            self.client = AsyncIOMotorClient(
                settings.MONGO_URI,
                tz_aware=True,
                serverSelectionTimeoutMS=5000
            )
            
            # Test the connection
            await self.client.admin.command('ping')
            logger.info("MongoDB connection established")
            
            # Initialize models one by one for better error reporting
            await self._initialize_models()
            self.is_connected = True
            
        except Exception as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            traceback.print_exc()
            raise

    async def _initialize_models(self) -> None:
        """Initialise *all* Beanie models in one shot."""
        db = self.client[settings.MONGO_DB_NAME]

        try:
            logger.info("Initialising Beanie models: %s",
                        [m.__name__ for m in MODELS])

            # ONE call – pass the full tuple
            await init_beanie(
                database=db,
                document_models=MODELS,
                allow_index_dropping=True  # ← drop & rebuild any conflicting indexes
            )
            

            logger.info("Beanie initialised successfully")
        except Exception as e:
            logger.exception("Beanie initialisation failed")
            raise RuntimeError("Beanie initialisation error") from e

    async def disconnect(self):
        if self.client:
            logger.info("Closing MongoDB connection...")
            self.client.close()
            self.is_connected = False
            logger.info("MongoDB connection closed")

    async def check_connection(self):
        """Check if the connection is alive"""
        try:
            if self.client:
                await self.client.admin.command('ping')
                return True
            return False
        except Exception:
            return False

mongo = MongoDB()