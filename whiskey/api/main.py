__author__ = "Richard Correro (richard@richardcorrero.com)"

import os
from datetime import datetime
from typing import Any, List

from celery.app.control import Inspect
from celery.result import AsyncResult
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import RedirectResponse

from .celery_config.celery import celery_app
from .models import TargetParams
from .utils import (get_api_keys, get_datetime, hash_string, is_json,
                    is_task_known)

API_KEYS_PATH: str = os.environ["API_KEYS_PATH"]
APP_TITLE: str = os.environ["APP_TITLE"]
APP_DESCRIPTION: str = os.environ["APP_DESCRIPTION"]
APP_VERSION: str = os.environ["APP_VERSION"]

valid_api_keys: List[str] = get_api_keys(api_keys_path=API_KEYS_PATH)

app = FastAPI(title=APP_TITLE, description=APP_DESCRIPTION, version=APP_VERSION)

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


@app.post("/analyze", dependencies=[Depends(api_key_auth)])
async def run_analysis(params: TargetParams) -> dict:
    if not is_json(json_str=params.target_geojson):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"target_geojson must be valid json."
        )

    # uid = params.process_uid
    uid: str = hash_string(params.target_geojson)

    inspect_obj: Inspect = celery_app.control.inspect()
    task_known: bool = is_task_known(task_uid=uid, inspect_obj=inspect_obj)
    if task_known:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A task has already been submitted using this target_geojson with uid {uid}. Please wait until this task has completed before resubmitting."
        )

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

    # task_uids[uid] = "running"
    
    return {"url": result_url, "uid": uid}


@app.get("/status/{uid}", dependencies=[Depends(api_key_auth)])
async def get_status(uid: str) -> dict:
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
    inspect_obj: Inspect = celery_app.control.inspect()
    task_known: bool = is_task_known(task_uid=uid, inspect_obj=inspect_obj)

    # Check if the task is completed
    task: AsyncResult = celery_app.AsyncResult(uid)
    if task.ready():
        # Task is completed, return the result(s)
        if task.successful():
            result: Any = task.result
            return {"status": "completed", "result": result}
        else:
            return {"status": "failed"}
    elif task_known:
        return {"status": "running"}
    else:
        return {"status": f"unknown uid: {uid}"}
