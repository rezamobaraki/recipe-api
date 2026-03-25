from pydantic import BaseModel, Field, field_validator


class CapacityRequest(BaseModel):
    origin: str | None = Field(
        default=None,
        min_length=3,
        max_length=4,
        description="Origin airport code (IATA or ICAO)"
    )
    destination: str | None = Field(
        default=None,
        min_length=3,
        max_length=4,
        description="Destination airport code (IATA or ICAO)"
    )
    date: str | None = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Filter by date (YYYY-MM-DD)"
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Number of records to return"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Offset for pagination"
    )

    @field_validator("origin", "destination")
    @classmethod
    def to_upper(cls, value: str | None) -> str | None:
        return value.upper() if value else value
