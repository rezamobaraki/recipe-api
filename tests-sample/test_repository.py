from src.domains.aircraft import Aircraft
from src.domains.capacity import Capacity


class TestSQLiteRepository:
    def test_save_and_retrieve_aircraft(self, repository):
        repo = repository
        aircraft = [
            Aircraft(
                code_iata="388",
                code_icao="A388",
                full_name="Airbus A380-800",
                category="A380",
                average_speed_mph=550.0,
                volume=86.74,
                payload=83417.60,
            ),
        ]
        count = repo.bulk_insert_aircraft(aircraft)
        assert count == 1
        amap = {a.code_icao: a for a in repo.stream_aircraft()}
        assert "A388" in amap
        assert amap["A388"].full_name == "Airbus A380-800"

    def test_save_and_retrieve_capacity(self, repository):
        repo = repository
        caps = [
            Capacity(
                flight_id="1",
                date="2022-10-03",
                origin_iata="MEM",
                destination_iata="HNL",
                equipment="B789",
                aircraft_name="Boeing 787-9",
                volume_m3=74.78,
                payload_kg=40610.85,
            ),
            Capacity(
                flight_id="2",
                date="2022-10-03",
                origin_iata="PER",
                destination_iata="LHR",
                equipment="A388",
                aircraft_name="Airbus A380-800",
                volume_m3=86.74,
                payload_kg=83417.60,
            ),
        ]
        repo.bulk_insert_capacity(caps)
        assert not repo.is_exists()

    def test_get_capacity_filters_by_origin(self, repository):
        repo = repository
        caps = [
            Capacity(
                flight_id="1",
                date="2022-10-03",
                origin_iata="MEM",
                destination_iata="HNL",
                equipment="B789",
                volume_m3=74.78,
                payload_kg=40610.85,
            ),
            Capacity(
                flight_id="2",
                date="2022-10-03",
                origin_iata="PER",
                destination_iata="LHR",
                equipment="A388",
                volume_m3=86.74,
                payload_kg=83417.60,
            ),
        ]
        repo.bulk_insert_capacity(caps)
        result = list(repo.stream_capacities(origin="MEM"))
        assert len(result) == 1
        assert result[0].flight_id == "1"

    def test_get_capacity_filters_by_date(self, repository):
        repo = repository
        caps = [
            Capacity(
                flight_id="1",
                date="2022-10-03",
                origin_iata="MEM",
                destination_iata="HNL",
                equipment="B789",
                volume_m3=74.78,
                payload_kg=40610.85,
            ),
            Capacity(
                flight_id="2",
                date="2022-10-04",
                origin_iata="MEM",
                destination_iata="HNL",
                equipment="B789",
                volume_m3=74.78,
                payload_kg=40610.85,
            ),
        ]
        repo.bulk_insert_capacity(caps)
        result = list(repo.stream_capacities(date="2022-10-03"))
        assert len(result) == 1

    def test_get_capacity_summary(self, repository):
        repo = repository
        caps = [
            Capacity(
                flight_id="1",
                date="2022-10-03",
                origin_iata="MEM",
                destination_iata="HNL",
                volume_m3=10.0,
                payload_kg=100.0,
            ),
            Capacity(
                flight_id="2",
                date="2022-10-03",
                origin_iata="MEM",
                destination_iata="HNL",
                volume_m3=20.0,
                payload_kg=200.0,
            ),
            Capacity(
                flight_id="3",
                date="2022-10-04",
                origin_iata="MEM",
                destination_iata="HNL",
                volume_m3=30.0,
                payload_kg=300.0,
            ),
        ]
        repo.bulk_insert_capacity(caps)

        result = list(repo.stream_capacity_summary(origin="MEM", destination="HNL"))
        assert len(result) == 2

        d1 = next(r for r in result if r.date == "2022-10-03")
        assert d1.total_flights == 2
        assert d1.total_volume_m3 == 30.0
        assert d1.total_payload_kg == 300.0

        d2 = next(r for r in result if r.date == "2022-10-04")
        assert d2.total_flights == 1
        assert d2.total_volume_m3 == 30.0
        assert d2.total_payload_kg == 300.0

        result_date = list(
            repo.stream_capacity_summary(origin="MEM", destination="HNL", date="2022-10-03")
        )
        assert len(result_date) == 1
        assert result_date[0].date == "2022-10-03"

    def test_is_empty_on_fresh_db(self, repository):
        assert repository.is_exists()
