from pydantic import BaseModel


class CapacityResponse(BaseModel):
    flight_id: str
    flight_number: str
    date: str
    origin_iata: str
    destination_iata: str
    equipment: str
    aircraft_name: str
    category: str
    volume_m3: float | None
    payload_kg: float | None
    operator: str

