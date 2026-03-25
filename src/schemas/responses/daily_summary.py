from pydantic import BaseModel


class DailySummaryResponse(BaseModel):
    date: str
    origin_iata: str
    destination_iata: str
    total_flights: int
    total_volume_m3: float
    total_payload_kg: float
