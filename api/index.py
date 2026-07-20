from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated
import multipart
import re
import traceback
from urllib.parse import unquote, urlparse
from api.functions import main

app = FastAPI()

@app.post('/api/deal_in_stage')
async def deal_in_stage_handler(request: Request):
    try:
        form_data = await request.form()
        form_data = dict(form_data)
        print(form_data)
        deal_id = form_data["document_id[2]"][5:]
        await main(deal_id)
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
        #result = await collab_created_handler(form_data["data[FIELDS][ID]"])
        #return result
    except Exception as e:
        print(e)
        traceback.print_exc()
        return e
