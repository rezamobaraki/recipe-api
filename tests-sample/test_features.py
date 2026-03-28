import pytest
import shutil
from src.domains.flight_event import FlightEvent
from src.domains.flight import Flight
from src.domains.capacity import Capacity
from src.services.file_service import FileService
from src.services.pipeline_service import PipelineService
from pathlib import Path
import json

class TestFeatures:
    
    def test_deterministic_aggregation(self, repository):
        # Insert multiple events for same flight with different data
        # Event 1: earlier date, equipment A
        # Event 2: later date, equipment B
        # Should pick B
        
        events = [
            FlightEvent(
                flight_id="F1",
                date="2022-10-01",
                time="10:00:00",
                equipment="EQ1",
                flight_number="FN1",
                origin_iata="AAA",
                origin_icao="AAAA",
                destination_iata="BBB",
                destination_icao="BBBB",
                operator="OP1",
                registration="REG1",
                address="ADDR1",
                event="E1"
            ),
            FlightEvent(
                flight_id="F1",
                date="2022-10-02",
                time="10:00:00",
                equipment="EQ2",
                flight_number="FN2",
                origin_iata="CCC",
                origin_icao="CCCC",
                destination_iata="DDD",
                destination_icao="DDDD",
                operator="OP2",
                registration="REG2",
                address="ADDR2",
                event="E2"
            )
        ]
        
        repository.bulk_insert_events(events)
        repository.aggregate_flights()
        
        flights = list(repository.stream_flights())
        assert len(flights) == 1
        f = flights[0]
        assert f.equipment == "EQ2"
        assert f.date == "2022-10-02"
        assert f.origin_iata == "CCC"

    def test_iata_vs_icao_filtering(self, repository, sample_aircraft):
        repository.bulk_insert_aircraft(sample_aircraft)
        # Create flights with distinct IATA and ICAO codes
        flights = [
            Flight(
                flight_id="1",
                date="2022-10-03",
                equipment="B789",
                origin_iata="MEM",
                origin_icao="KMEM",
                destination_iata="HNL",
                destination_icao="PHNL",
            )
        ]
        repository.bulk_insert_flights(flights)
        repository.calculate_capacity()
        
        # Test IATA
        res_iata = list(repository.stream_capacities(origin="MEM"))
        assert len(res_iata) == 1
        
        res_iata_miss = list(repository.stream_capacities(origin="XXX"))
        assert len(res_iata_miss) == 0

        # Test ICAO
        res_icao = list(repository.stream_capacities(origin="KMEM"))
        assert len(res_icao) == 1

        res_icao_miss = list(repository.stream_capacities(origin="XXXX"))
        assert len(res_icao_miss) == 0
        
        # Test mixing
        res_mixed = list(repository.stream_capacities(origin="KMEM", destination="HNL"))
        assert len(res_mixed) == 1

    def test_duplicate_ingestion(self, repository, tmp_data_dir, pipeline):
        # We need a fresh pipeline instance? We can use the fixture `pipeline`
        # But we need to control files.
        
        # Setup: Create a file in events dir
        events_dir = tmp_data_dir / "flight_events"
        processed_dir = tmp_data_dir / "processed"
        
        csv_path = events_dir / "test.csv"
        csv_path.write_text("header\nvalues") # Content doesn't matter much if we mock, but using real pipeline is better
        
        # We need valid CSV content
        csv_content = """address;altitude;callsign;date;destination_iata;destination_icao;equipment;event;flight;flight_id;latitude;longitude;operator;origin_iata;origin_icao;registration;time
A;0;C;2022-01-01;DST;DDDD;EQ;event;FL;1;0;0;OP;ORG;OOOO;REG;00:00:00
"""
        csv_path.write_text(csv_content)
        
        # First run
        pipeline.run()
        
        # Check raw events count
        # conftest.py adds 1 file with 6 events initially.
        # We added test.csv with 1 event.
        # Total = 7
        cursor = repository.connection.execute("SELECT COUNT(*) FROM events")
        count_1 = cursor.fetchone()[0]
        assert count_1 == 7
        
        # Check file is processed
        assert (processed_dir / "test.csv").exists()
        assert repository.is_file_processed("test.csv")
        
        # Restore file to events dir to simulate re-run
        shutil.copy(processed_dir / "test.csv", events_dir / "test.csv")
        
        # Run again
        pipeline.run()
        
        # Check raw events count - SHOULD BE SAME
        cursor = repository.connection.execute("SELECT COUNT(*) FROM events")
        count_2 = cursor.fetchone()[0]
        assert count_2 == 7





