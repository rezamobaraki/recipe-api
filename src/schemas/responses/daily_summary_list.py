from pydantic import BaseModel

from schemas.responses import DailySummaryResponse


class DailySummaryListResponse(BaseModel):
    count: int
    summaries: list[DailySummaryResponse]
