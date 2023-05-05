import os

import requests


def test(base_url: str, api_key: str, uid: str):
    # Define the URL and headers
    url = f"{base_url}/status/{uid}"
    headers = {
        "Content-Type": "application/json",  # Example header
        "Authorization": f"Bearer {api_key}"   # Example header
    }

    response = requests.get(url, headers=headers)

    # Check the response status code
    if response.status_code == 200:
        print("GET request successful!")
        print("Response JSON:")
        print(response.json())
    else:
        print("GET request failed with status code:", response.status_code)


if __name__ == "__main__":
    base_url: str = os.environ["BASE_URL"]
    api_key = os.environ["API_KEY"]
    uid = os.environ["ORDER_UID"]
    test(base_url=base_url, api_key=api_key, uid=uid)
