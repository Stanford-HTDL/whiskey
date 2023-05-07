__author__ = "Richard Correro (richard@richardcorrero.com)"

import os
from datetime import datetime
from typing import Any, Dict, List

from celery.result import AsyncResult
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from starlette.responses import RedirectResponse

from .celery_config.celery import celery_app
from .models import TargetParams
from .utils import get_api_keys, get_datetime

API_KEYS_PATH: str = os.environ["API_KEYS_PATH"]
APP_TITLE: str = os.environ["APP_TITLE"]
APP_DESCRIPTION: str = os.environ["APP_DESCRIPTION"]
APP_VERSION: str = os.environ["APP_VERSION"]

valid_api_keys: List[str] = get_api_keys(api_keys_path=API_KEYS_PATH)

app = FastAPI(title=APP_TITLE, description=APP_DESCRIPTION, version=APP_VERSION)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # use token authentication

task_uids: Dict = dict() # O(1) lookup time


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
    # if params.process_uid is None:
    #     # Generate a UID for the task
    #     uid: str = generate_uid()
    #     params.process_uid = uid
    # else:
    #     uid = params.process_uid    
    uid = params.process_uid

    start: str = params.start
    stop: str = params.stop

    # Validate dates are in correct format (`%Y_%m`)

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

    # target_geojson_dict: dict = json.loads(params.target_geojson)

    # kwargs: dict = {**params.dict(), "target_geojson_dict": target_geojson_dict}
    
    celery_app.send_task(name="analyze", kwargs=params.dict(), task_id=uid)
    # # Create a Celery task and pass the parameters to it
    # task.apply_async(
    #     kwargs=params.dict(), task_id=uid
    # )
    
    # Generate the URL for the second endpoint
    result_url = f"/status/{uid}"

    task_uids[uid] = "running"
    
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
    # Check if the task is completed
    task: AsyncResult = celery_app.AsyncResult(uid)
    if task.ready():
        # Task is completed, return the result(s)
        if task.successful():
            result: Any = task.result
            task_uids[uid] = "completed"
            return {"status": "completed", "result": result}
        else:
            task_uids[uid] = "failed"
            return {"status": "failed"}
    elif uid in task_uids:
        return {"status": "running"}
    else:
        return {"status": f"unknown uid: {uid}"}
