import logging
import sys

from src.core.container import container
from src.core.exceptions import AppError

logger = logging.getLogger(__name__)


def run_ingestion() -> None:
    logger.info("Starting ingestion command...")
    
    try:
        container.repository.initialize()
        container.pipeline.run()
        logger.info("Ingestion complete.")
    except AppError as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)

