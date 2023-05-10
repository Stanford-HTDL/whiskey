__author__ = "Richard Correro (richard@richardcorrero.com)"

import hashlib
import json
import random
import string
from datetime import datetime
from typing import List, Optional

from celery.app.control import Inspect

from .exceptions import MalformedDateStringError


def is_task_known(task_uid: str, inspect_obj: Inspect) -> bool:
    task_dicts: dict = inspect_obj.query_task(task_uid)
    if task_dicts is not None:
        for _, task_dict in task_dicts.items():
            if bool(task_dict) and task_uid in task_dict.keys():
                return True
    return False


def is_json(json_str: str) -> bool:
  try:
    json.loads(json_str)
  except ValueError:
    return False
  return True


def hash_string(string: str) -> str:
    """Hash a string using the SHA-256 algorithm."""
    # Encode the string to bytes
    string_bytes = string.encode("utf-8")

    # Create a hash object using the SHA-256 algorithm
    hash_object = hashlib.sha256()

    # Update the hash object with the bytes of the string
    hash_object.update(string_bytes)

    # Get the hashed value as a hexadecimal string
    hashed_string = hash_object.hexdigest()

    return hashed_string


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


def get_datetime(time_str: str) -> datetime:
    try: 
        dt: datetime = datetime.strptime(time_str[:7], '%Y_%m')
    except:
        raise MalformedDateStringError(
            f"Time string must be in %Y_%m format. Received string {time_str}."
        )
    return dt
