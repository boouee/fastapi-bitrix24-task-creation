from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated
import multipart
import re
import traceback
from urllib.parse import unquote, urlparse

app = FastAPI()

@app.post('/api/cartesia')
async def cartesia_handler(request: Request):
    try:
        if request.headers.get("x-webhook-secret") != "secret":
            data = {"error": "unauthorized"}
            json_compatible_data = jsonable_encoder(data)
    
            # 2. Return JSONResponse with a custom status code
            return JSONResponse(
              status_code=status.HTTP_401_CREATED,
              content=json_compatible_data
            )
        body = await request.body()
        json = await request.json()
        print(unquote(body))
        data = unquote(body)
        if json["type"] == "post_call_analysis":
            await cartesia_call_handler(json["call_id"])
        form_data = await request.form()
        form_data = dict(form_data)
        print(form_data)
        
    except Exception as e:
        print(e)
        traceback.print_exc()
        return e
        
@app.post('/api/deal_in_stage')
async def deal_in_stage_handler():
    try:
        result = await check_collabs()
        return result 
    except Exception as e:
        print(e)
        traceback.print_exc()
        return e
        
@app.post('/api/task_complete')
async def task_complete_handler(request: Request):
    try:
        body = await request.body()
        print(unquote(body))
        form_data = await request.form()
        form_data = dict(form_data)
        result = await collab_created_handler(form_data["data[FIELDS][ID]"])
        return result
    except Exception as e:
        print(e)
        traceback.print_exc()
        return e

@app.post('/api/task_updated')
async def task_updated(request: Request):
    try:
        body = await request.body()
        print(unquote(body))
        form_data = await request.form()
        form_data = dict(form_data)
        #result = await collab_update_handler(form_data["data[FIELDS][ID]"])
        #return result
    except Exception as e:
        print(e)
        traceback.print_exc()
        return e
