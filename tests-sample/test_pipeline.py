import pytest
from src.services.pipeline_service import PipelineService
from src.services.file_service import FileService
import csv

class TestPipeline:
    def test_pipeline_copies_files_to_processed(self, pipeline, settings):
        # Given: Source files exist relative to tmp_data_dir fixture
        source_event = settings.FLIGHT_EVENTS_DIR / "2022-10-03.csv"
        source_aircraft = settings.AIRCRAFT_FILE
        assert source_event.exists()
        assert source_aircraft.exists()
        
        # When: Pipeline runs
        pipeline.run()
        
        # Then: Source files should still exist
        assert source_event.exists()
        assert source_aircraft.exists()
        
        # And: Processed copies should exist
        processed_event = settings.PROCESSED_DIR / "2022-10-03.csv"
        processed_aircraft = settings.PROCESSED_DIR / "airplane_details_original.json"
        
        assert processed_event.exists()
        assert processed_aircraft.exists()

    def test_pipeline_exports_capacity_csv(self, pipeline, settings):
        # When: Pipeline runs
        pipeline.run()

        # Then: Capacity CSV should be created
        csv_file = settings.CAPACITY_OUTPUT_FILE
        assert csv_file.exists()

        # And structure should be correct
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) > 0
            assert "flight_id" in rows[0]
            assert "volume_m3" in rows[0]
            
            # Check content match
            row1 = next(r for r in rows if r["flight_id"] == "100001")
            assert row1["equipment"] == "B789"
            assert float(row1["volume_m3"]) > 0
