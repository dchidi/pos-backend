from app.core.logger import logger  # This ensures setup_logger is invoked

def setup_logging():
    # This function triggers the logger to initialize, no need for basicConfig anymore
    logger.info("Logging is configured.")
