from src.domains.flight import Flight
import pytest


class TestCapacityRepository:
    def test_calculate_matches_flights_to_aircraft(self, repository, sample_aircraft):
        repository.bulk_insert_aircraft(sample_aircraft)
        flights = [
            Flight(
                flight_id="1",
                date="2022-10-03",
                equipment="B789",
                origin_iata="MEM",
                destination_iata="HNL",
            ),
            Flight(
                flight_id="2",
                date="2022-10-03",
                equipment="A388",
                origin_iata="PER",
                destination_iata="LHR",
            ),
        ]
        repository.bulk_insert_flights(flights)

        count = repository.calculate_capacity()

        assert count == 2
        capacities = list(repository.stream_capacities())
        assert len(capacities) == 2

        capacities.sort(key=lambda x: x.flight_id)

        c1 = next(c for c in capacities if c.equipment == "B789")
        assert c1.volume_m3 == 74.78
        assert c1.payload_kg == 40610.85
        assert c1.aircraft_name == "Boeing 787-9"

        c2 = next(c for c in capacities if c.equipment == "A388")
        assert c2.volume_m3 == 86.74
        assert c2.payload_kg == 83417.60
        assert c2.aircraft_name == "Airbus A380-800"

    def test_calculate_includes_unmatched_equipment(self, repository, sample_aircraft):
        repository.bulk_insert_aircraft(sample_aircraft)
        flights = [
            Flight(
                flight_id="1",
                date="2022-10-03",
                equipment="ZZZZ",
                origin_iata="AAA",
                destination_iata="BBB",
            ),
        ]
        repository.bulk_insert_flights(flights)

        count = repository.calculate_capacity()

        assert count == 1
        capacities = list(repository.stream_capacities())
        assert len(capacities) == 1

        c = capacities[0]
        assert c.equipment == "ZZZZ"
        assert c.aircraft_name == "Unknown Aircraft"
        assert c.category == "unknown_aircraft"
        assert c.volume_m3 is None
        assert c.payload_kg is None

    def test_calculate_preserves_flight_data(self, repository, sample_aircraft):
        repository.bulk_insert_aircraft(sample_aircraft)
        flights = [
            Flight(
                flight_id="1",
                flight_number="FX1",
                date="2022-10-03",
                equipment="B789",
                origin_iata="MEM",
                destination_iata="HNL",
                operator="FDX",
            ),
        ]
        repository.bulk_insert_flights(flights)

        repository.calculate_capacity()

        capacities = list(repository.stream_capacities())
        assert len(capacities) == 1
        c = capacities[0]

        assert c.flight_number == "FX1"
        assert c.operator == "FDX"
        assert c.aircraft_name == "Boeing 787-9"
        assert c.category == "B787"

    def test_calculate_updates_existing_records(self, repository, sample_aircraft):
        repository.bulk_insert_aircraft(sample_aircraft)
        flights = [
            Flight(
                flight_id="1",
                date="2022-10-03",
                equipment="B789",
                origin_iata="MEM",
                destination_iata="HNL",
            ),
        ]
        repository.bulk_insert_flights(flights)
        repository.calculate_capacity()

        updated_flight = Flight(
            flight_id="1",
            date="2022-10-03",
            equipment="A388",
            origin_iata="MEM",
            destination_iata="HNL",
        )
        repository.bulk_insert_flights([updated_flight])

        count = repository.calculate_capacity()

        capacities = list(repository.stream_capacities())
        assert len(capacities) == 1
        assert capacities[0].equipment == "A388"
        assert capacities[0].volume_m3 == 86.74

