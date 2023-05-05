__author__ = "Richard Correro (richard@richardcorrero.com)"

from pydantic import BaseModel, Field

from .utils import generate_uid


class TargetParams(BaseModel):
    start: str | None = Field(
        default="2023_01", title="Start Month", 
        description="Start month in `%Y_%m` format.", max_length=7, min_length=7
    )
    stop: str | None = Field(
        default="2023_02", title="Stop Month", 
        description="Stop month in `%Y_%m` format.", max_length=7, min_length=7
    )
    target_geojson: str = Field(
        title="GeoJSON", 
        description="GeoJSON (encoded as a string) demarcating the region for analysis."
    )
    process_uid: str = Field(
        default_factory=generate_uid, title="Process UID", 
        description="UID which will be assigned to this analysis. Used to check its status via the `/status` endpoint."
    ) # User may provide a process UID
