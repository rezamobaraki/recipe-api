import json
import tempfile
from pathlib import Path

import pytest

from src.core.settings import Settings
from src.domains.aircraft import Aircraft
from src.domains.flight import Flight
from src.repositories.sqlite_repository import SQLiteRepository
from src.services.file_service import FileService

from src.services.pipeline_service import PipelineService

SAMPLE_AIRCRAFT = [
    {
        "code_iata": "388",
        "code_icao": "A388",
        "full_name": "Airbus A380-800",
        "category": "A380",
        "average_speed_mph": 550.0,
        "volume": 86.74,
        "payload": 83417.60,
    },
    {
        "code_iata": "789",
        "code_icao": "B789",
        "full_name": "Boeing 787-9",
        "category": "B787",
        "average_speed_mph": 570.0,
        "volume": 74.78,
        "payload": 40610.85,
    },
]

SAMPLE_EVENTS_CSV = """address;altitude;callsign;date;destination_iata;destination_icao;equipment;event;flight;flight_id;latitude;longitude;operator;origin_iata;origin_icao;registration;time
ABAF47;37850;FDX197;2022-10-03;HNL;PHNL;B789;descent;FX197;100001;21.88;-156.09;FDX;MEM;KMEM;N852FD;02:50:10
ABAF47;0;FDX197;2022-10-03;HNL;PHNL;B789;landed;FX197;100001;21.32;-157.92;FDX;MEM;KMEM;N852FD;03:16:57
ABAF47;0;FDX197;2022-10-03;HNL;PHNL;B789;gate_arrival;FX197;100001;21.32;-157.92;FDX;MEM;KMEM;N852FD;03:17:12
CC0011;35000;QFA7;2022-10-03;LHR;EGLL;A388;cruising;QF7;100002;30.0;50.0;QFA;PER;YPPH;VH-OQA;04:00:00
CC0011;10000;QFA7;2022-10-03;LHR;EGLL;A388;descent;QF7;100002;51.0;-0.5;QFA;PER;YPPH;VH-OQA;05:30:00
DD0022;0;NOEQUIP;2022-10-03;JFK;KJFK;;landed;;100003;40.63;-73.77;;;;N999XX;06:00:00
"""


@pytest.fixture
def tmp_data_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        events_dir = base / "flight_events"
        events_dir.mkdir()

        aircraft_file = base / "airplane_details_original.json"
        with open(aircraft_file, "w") as f:
            for a in SAMPLE_AIRCRAFT:
                f.write(json.dumps(a) + "\n")

        csv_file = events_dir / "2022-10-03.csv"
        csv_file.write_text(SAMPLE_EVENTS_CSV.strip())

        (base / "processed").mkdir()
        (base / "warehouse").mkdir()

        yield base


@pytest.fixture
def settings(tmp_data_dir):
    s = Settings()
    s.DATA_DIR = tmp_data_dir
    s.RAW_DIR = tmp_data_dir
    s.FLIGHT_EVENTS_DIR = tmp_data_dir / "flight_events"
    s.PROCESSED_DIR = tmp_data_dir / "processed"
    s.WAREHOUSE_DIR = tmp_data_dir / "warehouse"
    s.AIRCRAFT_FILE = tmp_data_dir / "airplane_details_original.json"
    s.DATABASE_PATH = s.WAREHOUSE_DIR / "flight_capacity_test.db"
    s.CAPACITY_OUTPUT_FILE = s.WAREHOUSE_DIR / "capacity_table.csv"
    return s


@pytest.fixture
def repository(settings):
    repo = SQLiteRepository(settings.DATABASE_PATH)
    repo.initialize()
    yield repo
    repo.close()


@pytest.fixture
def pipeline(settings, repository):
    file_service = FileService()

    return PipelineService(
        file_service=file_service,
        repository=repository,
        aircraft_path=settings.AIRCRAFT_FILE,
        events_dir=settings.FLIGHT_EVENTS_DIR,
        processed_dir=settings.PROCESSED_DIR,
        capacity_output_path=settings.CAPACITY_OUTPUT_FILE,
    )


@pytest.fixture
def sample_aircraft():
    return [Aircraft(**a) for a in SAMPLE_AIRCRAFT]


@pytest.fixture
def sample_flights():
    return [
        Flight(
            flight_id="100001",
            flight_number="FX197",
            date="2022-10-03",
            origin_iata="MEM",
            origin_icao="KMEM",
            destination_iata="HNL",
            destination_icao="PHNL",
            equipment="B789",
            operator="FDX",
            registration="N852FD",
        ),
        Flight(
            flight_id="100002",
            flight_number="QF7",
            date="2022-10-03",
            origin_iata="PER",
            origin_icao="YPPH",
            destination_iata="LHR",
            destination_icao="EGLL",
            equipment="A388",
            operator="QFA",
            registration="VH-OQA",
        ),
    ]
