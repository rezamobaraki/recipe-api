import pytest

from src.domains.aircraft import Aircraft
from src.core.exceptions import DataFileNotFoundError
from src.services.file_service import FileService


class TestReadCsv:
    def test_reads_semicolon_csv(self, settings):
        service = FileService()
        rows = list(service.read_csv(settings.FLIGHT_EVENTS_DIR / "2022-10-03.csv"))
        assert len(rows) == 6
        assert rows[0]["flight_id"] == "100001"

    def test_raises_on_missing_file(self, tmp_path):
        service = FileService()
        with pytest.raises(DataFileNotFoundError):
            list(service.read_csv(tmp_path / "nonexistent.csv"))


class TestReadNdjson:
    def test_reads_valid_ndjson(self, settings):
        service = FileService()
        records = list(service.read_ndjson(settings.AIRCRAFT_FILE))
        assert len(records) == 2
        assert records[0]["code_icao"] == "A388"

    def test_skips_malformed_lines(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text('{"a": 1}\n{broken\n{"b": 2}\n')
        service = FileService()
        records = list(service.read_ndjson(path))
        assert len(records) == 2

    def test_raises_on_missing_file(self, tmp_path):
        service = FileService()
        with pytest.raises(DataFileNotFoundError):
            list(service.read_ndjson(tmp_path / "nonexistent.json"))


class TestListFiles:
    def test_lists_csv_files(self, settings):
        service = FileService()
        files = service.list_files(settings.FLIGHT_EVENTS_DIR)
        assert len(files) == 1
        assert files[0].name == "2022-10-03.csv"

    def test_raises_on_missing_dir(self, tmp_path):
        service = FileService()
        with pytest.raises(DataFileNotFoundError):
            service.list_files(tmp_path / "nonexistent")

    def test_raises_on_empty_dir(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        service = FileService()
        with pytest.raises(DataFileNotFoundError):
            service.list_files(empty)


class TestLoadAircraft:
    def test_loads_valid_aircraft(self, settings):
        service = FileService()
        aircraft = service.load_aircraft(settings.AIRCRAFT_FILE)
        assert len(aircraft) == 2
        assert all(isinstance(a, Aircraft) for a in aircraft)

    def test_parses_fields_correctly(self, settings):
        service = FileService()
        aircraft = service.load_aircraft(settings.AIRCRAFT_FILE)
        a380 = next(a for a in aircraft if a.code_icao == "A388")
        assert a380.full_name == "Airbus A380-800"
        assert a380.volume == 86.74

    def test_skips_invalid_records(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text('{"code_iata":"388"}\n')
        service = FileService()
        result = service.load_aircraft(path)
        assert len(result) == 0

    def test_raises_on_missing_file(self, tmp_path):
        service = FileService()
        with pytest.raises(DataFileNotFoundError):
            service.load_aircraft(tmp_path / "nonexistent.json")


class TestStreamEvents:
    def test_streams_from_file(self, settings):
        service = FileService()
        file_path = settings.FLIGHT_EVENTS_DIR / "2022-10-03.csv"
        events = list(service.stream_events_from_file(file_path))
        assert len(events) == 6

    def test_parses_fields_correctly(self, settings):
        service = FileService()
        file_path = settings.FLIGHT_EVENTS_DIR / "2022-10-03.csv"
        events = list(service.stream_events_from_file(file_path))
        first = events[0]
        assert first.flight_id == "100001"
        assert first.altitude == 37850
        assert first.equipment == "B789"

    def test_handles_empty_fields(self, settings):
        service = FileService()
        file_path = settings.FLIGHT_EVENTS_DIR / "2022-10-03.csv"
        events = list(service.stream_events_from_file(file_path))
        no_equip = [e for e in events if e.flight_id == "100003"]
        assert len(no_equip) == 1
        assert no_equip[0].equipment == ""

    def test_is_lazy(self, settings):
        service = FileService()
        file_path = settings.FLIGHT_EVENTS_DIR / "2022-10-03.csv"
        gen = service.stream_events_from_file(file_path)
        first = next(gen)
        assert first.flight_id == "100001"


class TestCopyToProcessed:
    def test_copies_file_successfully(self, tmp_path):
        service = FileService()
        source_dir = tmp_path / "source"
        processed_dir = tmp_path / "processed"
        source_dir.mkdir()

        file_path = source_dir / "test.csv"
        file_path.write_text("content")

        service.copy_to_processed(file_path, processed_dir)

        assert file_path.exists()
        assert (processed_dir / "test.csv").exists()
        assert (processed_dir / "test.csv").read_text() == "content"

    def test_creates_processed_dir_if_missing(self, tmp_path):
        service = FileService()
        source_dir = tmp_path / "source"
        processed_dir = tmp_path / "processed"  # Not created yet
        source_dir.mkdir()

        file_path = source_dir / "test.csv"
        file_path.write_text("content")

        service.copy_to_processed(file_path, processed_dir)

        assert processed_dir.exists()
        assert (processed_dir / "test.csv").exists()
