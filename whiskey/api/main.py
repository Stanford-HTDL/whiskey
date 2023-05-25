__author__ = "Richard Correro (richard@richardcorrero.com)"

import json
import os
from datetime import datetime
from typing import Any, List, Tuple, Union

import redis
from celery.result import AsyncResult
from celery.utils import gen_unique_id
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import RedirectResponse

from .celery_config.celery import celery_app
from .models import TargetParams, MediaParams
from .utils import get_api_keys, get_datetime, hash_string, is_json

API_KEYS_PATH: str = os.environ["API_KEYS_PATH"]
APP_TITLE: str = os.environ["APP_TITLE"]
APP_DESCRIPTION: str = os.environ["APP_DESCRIPTION"]
APP_VERSION: str = os.environ["APP_VERSION"]

REDIS_HOST: str = os.environ["REDIS_HOST"]
REDIS_PORT: int = int(os.environ["REDIS_PORT"])
REDIS_STORE_DB_INDEX: int = int(os.environ["REDIS_STORE_DB_INDEX"])

valid_api_keys: List[str] = get_api_keys(api_keys_path=API_KEYS_PATH)

app = FastAPI(title=APP_TITLE, description=APP_DESCRIPTION, version=APP_VERSION)

redis_client: redis.Redis = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_STORE_DB_INDEX
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # use token authentication


def api_key_auth(api_key: str = Depends(oauth2_scheme)) -> None:
    if api_key not in valid_api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )


@app.get("/")
async def redirect() -> RedirectResponse:
    return RedirectResponse(url=f"/redoc", status_code=303)


@app.post(
    "/analyze", 
    dependencies=[Depends(api_key_auth)]
)
async def run_analysis(
    params: TargetParams, api_key: str = Depends(oauth2_scheme)
) -> dict:
    # if not is_json(json_str=params.target_geojson):
    #     raise HTTPException(
    #         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #         detail=f"target_geojson must be valid json."
    #     )
    for geojson_str in params.target_geojsons:
        if not is_json(json_str=geojson_str):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"target_geojson must be valid json. Received {geojson_str}."
            )
        
    geojson_strs: str = json.dumps(params.target_geojsons)

    geojson_str_hash : str = hash_string(geojson_strs)

    # geojson_str_hash : str = hash_string(params.target_geojson)

    user_active_tasks_json: List[Union[str, None]] = redis_client.lrange(api_key, 0, -1)
    user_active_tasks: List[Union[None, Tuple[str, str]]] = [
        json.loads(json_data) for json_data in user_active_tasks_json
    ]

    for _, task_geojson_str_hash in user_active_tasks:
        if geojson_str_hash == task_geojson_str_hash:
            # Prevent duplicate execution of the same task resubmitted multiple times
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=("A task has already been submitted using this target_geojson, "
                f"which has an SHA256 hash of {geojson_str_hash}. Please wait until "
                "this task has completed before resubmitting.")
            )
    uid: str = gen_unique_id()
    task_info: Tuple[str, str] = (uid, geojson_str_hash)
    task_info_json: str = json.dumps(task_info)
    redis_client.lpush(api_key, task_info_json)

    start: str = params.start
    stop: str = params.stop

    try:
        start_datetime: datetime = get_datetime(start)
        start_formatted: str = start_datetime.strftime('%Y_%m')
    except:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"start must be in %Y_%m format. Received value of {params.start}."
        )
    try:
        stop_datetime: datetime = get_datetime(stop)
        stop_formatted: str = stop_datetime.strftime('%Y_%m')
    except:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"stop must be in %Y_%m format. Received value of {params.stop}."
        )

    params.start = start_formatted
    params.stop = stop_formatted

    # Verify bbox_threshold lies in range `[0,1]`
    if params.bbox_threshold > 1.0 or params.bbox_threshold < 0.0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"bbox_threshold must lie in range [0,1]. Received value of {params.bbox_threshold}."
        )
    
    kwargs = {**params.dict(), "process_uid": uid}
    
    celery_app.send_task(name="analyze", kwargs=kwargs, task_id=uid)
    
    # Generate the URL for the second endpoint
    result_url = f"/status/{uid}"
    
    return {"url": result_url, "uid": uid}


@app.post(
    "/media", 
    dependencies=[Depends(api_key_auth)]
)
async def make_media(
    params: MediaParams, api_key: str = Depends(oauth2_scheme)
) -> dict:
    for geojson_str in params.target_geojsons:
        if not is_json(json_str=geojson_str):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"target_geojson must be valid json. Received {geojson_str}."
            )
        
    geojson_strs: str = json.dumps(params.target_geojsons)

    geojson_str_hash : str = hash_string(geojson_strs)

    user_active_tasks_json: List[Union[str, None]] = redis_client.lrange(api_key, 0, -1)
    user_active_tasks: List[Union[None, Tuple[str, str]]] = [
        json.loads(json_data) for json_data in user_active_tasks_json
    ]

    for _, task_geojson_str_hash in user_active_tasks:
        if geojson_str_hash == task_geojson_str_hash:
            # Prevent duplicate execution of the same task resubmitted multiple times
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=("A task has already been submitted using this target_geojson, "
                f"which has an SHA256 hash of {geojson_str_hash}. Please wait until "
                "this task has completed before resubmitting.")
            )
    uid: str = gen_unique_id()
    task_info: Tuple[str, str] = (uid, geojson_str_hash)
    task_info_json: str = json.dumps(task_info)
    redis_client.lpush(api_key, task_info_json)

    start: str = params.start
    stop: str = params.stop

    try:
        start_datetime: datetime = get_datetime(start)
        start_formatted: str = start_datetime.strftime('%Y_%m')
    except:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"start must be in %Y_%m format. Received value of {params.start}."
        )
    try:
        stop_datetime: datetime = get_datetime(stop)
        stop_formatted: str = stop_datetime.strftime('%Y_%m')
    except:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"stop must be in %Y_%m format. Received value of {params.stop}."
        )

    params.start = start_formatted
    params.stop = stop_formatted
    
    kwargs = {**params.dict(), "process_uid": uid}
    
    celery_app.send_task(name="media", kwargs=kwargs, task_id=uid)
    
    # Generate the URL for the second endpoint
    result_url = f"/status/{uid}"
    
    return {"url": result_url, "uid": uid}


@app.get("/status/{uid}", dependencies=[Depends(api_key_auth)])
async def get_status(uid: str, api_key: str = Depends(oauth2_scheme)) -> dict:
    """
    Parameters
    ----------
    uid : `str`
        Process UID received in response to requests sent to the `/analyze`
        endpoint.

    Returns
    -------
    `dict`
    """
    user_active_tasks_json: List[Union[str, None]] = redis_client.lrange(api_key, 0, -1)
    # Check if the task is completed
    task: AsyncResult = celery_app.AsyncResult(uid)
    if task.ready():
        # Task is completed, return the result(s)
        for task_str in user_active_tasks_json:
            task_uid, _ = json.loads(task_str)
            if uid == task_uid:
                redis_client.lrem(api_key, 0, task_str) # Removes all matching instances
        if task.successful():
            result: Any = task.result
            return {"status": "completed", "result": result}
        else:
            return {"status": "failed"}
    elif len(user_active_tasks_json) > 0:
        for task_str in user_active_tasks_json:
            task_uid, _ = json.loads(task_str)
            if uid == task_uid:
                return {"status": "running"}
    else:
        return {"status": f"unknown uid: {uid}"}
