__author__ = "Richard Correro (richard@richardcorrero.com)"

import json
import random
import string
from typing import List, Optional


def get_api_keys(api_keys_path: str) -> List[str]:
    # Open the .json file in read mode
    with open(api_keys_path, 'r') as file:
        # Load the JSON data from the file into a Python dictionary
        keys_dict: dict = json.load(file)
    return list(keys_dict.values())


def generate_uid(uid_len: Optional[int] = 64) -> str:
    uid: str = ''.join(
        random.SystemRandom().choice(
            string.ascii_lowercase + string.digits
        ) for _ in range(uid_len)
    )

    return uid
