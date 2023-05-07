__author__ = "Richard Correro (richard@richardcorrero.com)"

from pydantic import BaseModel, Field

from .utils import generate_uid


geojson_str: str = '{"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": {"coordinates": [-122.166971, 37.427611], "type": "Point"}}]}'
default_bbox_threshold: float = 0.95

class TargetParams(BaseModel):
    start: str | None = Field(
        default="2023_01", title="Start Month", 
        description="Start month (inclusive) in `%Y_%m` format.", max_length=7, min_length=7
    )
    stop: str | None = Field(
        default="2023_02", title="Stop Month", 
        description="Stop month (exclusive) in `%Y_%m` format.", max_length=7, min_length=7
    )
    target_geojson: str = Field(
        default=geojson_str, title="GeoJSON", 
        description="GeoJSON (encoded as a string) demarcating the region for analysis."
    )
    bbox_threshold: float = Field(
        default=default_bbox_threshold, title="Bounding Box Score Threshold",
        description="Value used to determine whether to consider a predicted bounded box a positive. Value must lie in the range `[0,1]`."
    )
    process_uid: str = Field(
        default_factory=generate_uid, title="Process UID", 
        description="(Optional) UID which will be assigned to this analysis. Used to check its status via the `/status` endpoint."
    ) # User may provide a process UID
