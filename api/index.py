from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated
import multipart
import re
import traceback
from urllib.parse import unquote, urlparse
from api.functions import main, get_preparations, get_deal_preparations, set_preparations
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.post('/api/deal_in_stage')
async def deal_in_stage_handler(request: Request):
    try:
        form_data = await request.form()
        form_data = dict(form_data)
        print(form_data)
        deal_id = int(form_data["document_id[2]"][5:])
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
        print(form_data)
        print(form_data["data[FIELDS_AFTER][ID]"])
        #result = await collab_created_handler(form_data["data[FIELDS][ID]"])
        #return result
    except Exception as e:
        print(e)
        traceback.print_exc()
        return e

@app.get("/api/edit_preparations")
async def edit_preparations(request: Request):
  try:      
    deal_id = dict(request.query_params)["deal_id"]
    preparation_list = await get_preparations(1)
    deal_preparations = await get_deal_preparations(preparation_list, deal_id)
    preparation_list = [item.get("name") for item in preparation_list]
    context = {
        'preparation_list': preparation_list,
        'initial_list': deal_preparations
    }
    return templates.TemplateResponse(
        request=request, name="_index.html", context=context
    )
  except Exception as e:
        print(e)
        traceback.print_exc()
        return e 

@app.post("/api/update_preparations")
async def update_preparations(request: Request):
  try:
    data = await request.json()
    print(data)   
    preparation_list = await get_preparations(1)
    for preparation in data["orderItems"]:
      preparation["id"] = next((item for item in preparation_list if item.get("name") == preparation["product"]), None)["id"]
      preparation["name"] = preparation["product"]
      #preparation["price"] = next((item for item in preparation_list if item.get("name") == preparation["product"]), None)["price"]
    print(data)
    await set_preparations(preparation_list, data["orderItems"], int(data["deal_id"]), int(data["task_id"]))
  except Exception as e:
        print(e)
        traceback.print_exc()
        return e                            
