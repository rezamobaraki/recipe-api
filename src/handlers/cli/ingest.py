from src.services.ingest_service import IngestService


class IngestCommand:
    def __init__(self, ingest_service: IngestService) -> None:
        self._ingest_service = ingest_service

    def run(self) -> None:
        self._ingest_service.run()
        print("Ingest complete")
