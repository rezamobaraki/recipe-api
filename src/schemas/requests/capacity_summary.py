from pydantic import BaseModel, Field, field_validator


class CapacitySummaryRequest(BaseModel):
    origin: str = Field(
        ..., 
        min_length=3, 
        max_length=4, 
        description="Origin airport code (IATA or ICAO)"
    )
    destination: str = Field(
        ..., 
        min_length=3, 
        max_length=4, 
        description="Destination airport code (IATA or ICAO)"
    )
    date: str | None = Field(
        default=None, 
        pattern=r"^\d{4}-\d{2}-\d{2}$", 
        description="Filter by date (YYYY-MM-DD)"
    )

    @field_validator("origin", "destination")
    @classmethod
    def to_upper(cls, value: str | None) -> str | None:
        return value.upper() if value else value
