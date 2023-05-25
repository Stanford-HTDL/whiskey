import os
import json

from typing import Dict

import requests


def test(base_url: str, api_key: str, geojson_path: str):
    url = f"{base_url}/media"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    with open(geojson_path) as f:
        geometry: Dict = json.load(f)
    geometry_str: str = json.dumps(geometry)

    # Define the data to be sent in the request body
    data = {
        "start": "2018_04",
        "stop": "2023_05",
        "target_geojsons": [geometry_str],
    }

    # Send the POST request with headers and data
    response = requests.post(url, headers=headers, json=data)

    # Check the response status code
    if response.status_code == 200:
        print("POST request successful!")
        print("Response JSON:")
        print(response.json())
    else:
        print("POST request failed with status code:", response.status_code)
        # print(response.json())


if __name__ == "__main__":
    base_url: str = os.environ["BASE_URL"]
    api_key: str = os.environ["API_KEY"]
    geojson_path: str = os.environ["GEOJSON_PATH"]
    test(base_url=base_url, api_key=api_key, geojson_path=geojson_path)
