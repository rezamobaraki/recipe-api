import csv
import json
import logging
import shutil
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.core.exceptions import DataFileNotFoundError
from src.domains.aircraft import Aircraft
from src.domains.flight_event import FlightEvent

logger = logging.getLogger(__name__)


class FileService:
    def _ensure_exists(self, path: str | Path) -> Path:
        p = Path(path)
        if not p.exists():
            raise DataFileNotFoundError(str(p))
        return p

    @staticmethod
    def _strip_row(row: dict[str, str | None]) -> dict[str, str]:
        return {k: v.strip() for k, v in row.items() if k and v is not None}

    def read_csv(
        self,
        path: str | Path,
        delimiter: str = ";",
    ) -> Iterator[dict[str, str]]:
        path = self._ensure_exists(path)

        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=delimiter)

                if not reader.fieldnames:
                    raise ValueError(f"CSV has no header row: {path}")

                for row in reader:
                    cleaned_row = self._strip_row(row)
                    if cleaned_row:
                        yield cleaned_row
        except UnicodeDecodeError as e:
            raise ValueError(f"Cannot decode {path} as UTF-8") from e

    def read_ndjson(
        self,
        path: str | Path,
    ) -> Iterator[dict[str, Any]]:
        path = self._ensure_exists(path)

        with open(path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    logger.warning(
                        "Skipped malformed JSON at line %d in %s: %s",
                        line_num,
                        path,
                        e,
                    )

    def list_files(self, directory: str | Path, pattern: str = "*.csv") -> list[Path]:
        directory = self._ensure_exists(directory)
        files = sorted(directory.glob(pattern))
        if not files:
            raise DataFileNotFoundError(f"No {pattern} files in {directory}")
        return files

    def load_aircraft(self, path: str | Path) -> list[Aircraft]:
        loaded = 0
        skipped = 0
        aircraft: list[Aircraft] = []
        for raw in self.read_ndjson(path):
            try:
                aircraft.append(Aircraft.model_validate(raw))
                loaded += 1
            except ValidationError as e:
                skipped += 1
                logger.warning("Skipped invalid aircraft record: %s", e)

        logger.info("Aircraft loading complete: %d loaded, %d skipped", loaded, skipped)
        return aircraft

    def stream_events_from_file(self, csv_file: Path) -> Iterator[FlightEvent]:
        for row in self.read_csv(csv_file):
            try:
                yield FlightEvent.model_validate(row)
            except ValidationError as e:
                logger.warning("Skipped invalid event row in %s: %s", csv_file.name, e)

    def copy_to_processed(self, file_path: Path, processed_dir: Path) -> None:
        processed_dir.mkdir(parents=True, exist_ok=True)
        destination = processed_dir / file_path.name
        try:
            shutil.copy2(str(file_path), str(destination))
            logger.info("Copied processed file %s to %s", file_path.name, processed_dir)
        except Exception as e:
            logger.error("Failed to copy file %s: %s", file_path, e)

    def write_csv(
        self,
        path: Path,
        rows: Iterator[dict[str, Any]],
        fieldnames: list[str],
        delimiter: str = ",",
    ) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(rows)
            logger.info("Successfully wrote CSV to %s", path)
        except Exception as e:
            logger.error("Failed to write CSV to %s: %s", path, e)
            raise
