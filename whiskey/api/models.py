__author__ = "Richard Correro (richard@richardcorrero.com)"

from typing import List

from pydantic import BaseModel, Field

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
    # target_geojson: str = Field(
    #     default=geojson_str, title="GeoJSON", 
    #     description="GeoJSON (encoded as a string) demarcating the region for analysis."
    # )
    target_geojsons: List[str] | None = Field(
        default=[geojson_str], title="List of GeoJSONs", 
        description="List of GeoJSONs (encoded as strings) demarcating the region for which media will be created."
    )
    bbox_threshold: float = Field(
        default=default_bbox_threshold, title="Bounding Box Score Threshold",
        description="Value used to determine whether to consider a predicted bounded box a positive. Value must lie in the range `[0,1]`."
    )


class MediaParams(BaseModel):
    start: str | None = Field(
        default="2022_01", title="Start Month", 
        description="Start month (inclusive) in `%Y_%m` format.", max_length=7, min_length=7
    )
    stop: str | None = Field(
        default="2023_01", title="Stop Month", 
        description="Stop month (exclusive) in `%Y_%m` format.", max_length=7, min_length=7
    )
    target_geojsons: List[str] | None = Field(
        default=[geojson_str], title="List of GeoJSONs", 
        description="List of GeoJSONs (encoded as strings) demarcating the region for which media will be created."
    )
