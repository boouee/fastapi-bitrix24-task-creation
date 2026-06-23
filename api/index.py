from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
from api.functions import collab_created_handler, check_collabs
import multipart
import re
import traceback

#from api.handlers import set_time, update, clear_keys, hash_password
from urllib.parse import unquote, urlparse

app = FastAPI()

#templates = Jinja2Templates(directory="templates")

@app.post('/api/cartesia')
async def cartesia_handler(request: Request):
    try:
        body = await request.body()
        print(unquote(body))
        form_data = await request.form()
        form_data = dict(form_data)
        print(form_data)
    except Exception as e:
        print(e)
        traceback.print_exc()
        return e
        
@app.get('/api/update')
async def get_handler():
    try:
        result = await check_collabs()
        return result 
    except Exception as e:
        print(e)
        traceback.print_exc()
        return e
        
@app.post('/api/collab_added')
async def new_collab_handler(request: Request):
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
        
@app.get('/api/index', response_class=HTMLResponse)
async def read_index():
    return HTMLResponse(html)

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Запись на прием</title>
    <script src="https://ilabvr.infoclinica.ru/assets/javascripts/embedded/embedded.build.min.js"></script> 
</head>
<body>
    <button id="createAppointment">Запись</button>
    <div id="container"></div>
    <p>This page is rendered using Jinja2 template.</p>
    <script> 
        //window.widget = new WrEmbedded({container: document.getElementById("container")}); 
    </script> 
    <script> 
        button = document.getElementById("createAppointment");
        button.addEventListener("click", (e)=> {
           modalWidget = new WrEmbedded({path: "/schedule?filial=1&departments=1&doctors=524&modal=true", modal: true}) 
        })
    </script>
</body>
</html>
"""
