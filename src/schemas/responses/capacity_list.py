from pydantic import BaseModel

from schemas.responses import CapacityResponse


class CapacityListResponse(BaseModel):
    count: int
    capacities: list[CapacityResponse]

