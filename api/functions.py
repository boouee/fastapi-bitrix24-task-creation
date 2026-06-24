from urllib.parse import unquote
from datetime import datetime, timedelta
import httpx
import re
import math
import numbers
import time
import os
import redis
import secrets
import string
import random 
import hashlib
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")
redis_url = os.getenv("REDIS_URL")
bitrix24_url = os.getenv("BITRIX24_URL")
cartesia_headers = {
  "Content-Type": "application/json",
  "X-API-Key": "sk_car_F8fhNz7AKebsimYgU6wCiF",
  "Cartesia-Version": "2026-03-01"
}
template_list = [1, 2, 3]

async def cartesia_call_handler(data):
  ...

async def create_lead(client, data):
  url = bitrix24_url + "crm.item.add"
  body = {"entityTypeId": 1, "fields": {"title": title} }
  response = await client.post(url, json=body)
  response = response.json()
  return response["result"]

async def get_metric(client, metric_id, call_id):
  url = cartesia_url + "
  ...
async def collab_created_handler(id):
  print(redis_url)
  r = redis.Redis.from_url(redis_url, decode_responses=True)
  collab_list = r.lrange("b24_collabs", 0, -1)
  print(collab_list)
  async with httpx.AsyncClient() as client:
    collab_data = await get_collab_data(client, id)
    print(collab_data["TYPE"] == "collab", collab_data["ORDINARY_MEMBERS"], id not in collab_list)
    if collab_data["TYPE"] == "collab":
      r.rpush("b24_collabs", id)

async def check_collabs():
  r = redis.Redis.from_url(redis_url, decode_responses=True)
  collab_list = r.lrange("b24_collabs", 0, -1)
  print(collab_list)
  async with httpx.AsyncClient() as client:
    users = await get_users(client)
    for collab in collab_list:
      success = await process(client, users, collab)
      if success:
        r.lrem("b24_collabs", 0, collab)
        
async def process(client, users, id):
  collab_data = await get_collab_data(client, id)
  extranet_users = await get_users(client)
  collab_guests = [user for user in extranet_users if int(user["ID"]) in collab_data["MEMBERS"]]
  if collab_guests:
    crm_object_id = await create_crm_object(client)
    await create_tasks(client, id, crm_object_id, collab_data["OWNER_ID"], collab_guests[0]["ID"], template_list)
    return True
  return False
  
#Получить данные коллаборации по id
async def get_collab_data(client, id):
  url = bitrix24_url + "socialnetwork.api.workgroup.get"
  body = {"params": {"groupId": id} }
  response = await client.post(url, json=body)
  response = response.json()
  return response["result"]
  
#def check_users(collab_user_list, user_list):
  
async def get_users(client):
  url = bitrix24_url + "user.get"
  body = {
    "filter": {
      "user_type": "extranet"
    }
  }
  response = await client.post(url, json=body)
  response = response.json()
  return response["result"]
  
#Создать объект CRM
async def create_crm_object(client):
  url = bitrix24_url + "crm.item.add"
  body = {
    "entityTypeId": 2,
    "fields": {
      
    } 
  }
  response = await client.post(url, json=body)
  response = response.json()
  return response["result"]["item"]["id"]

async def create_tasks(client, group_id, crm_object_id, creator_id, responsible_id, template_list):
  task_list = []
  for template_id in template_list:
    task_id = await create_task(client, group_id, crm_object_id, creator_id, responsible_id, template_id)
    task_list.append(task_id)
  for i in range(0, len(task_list), 2):
    await create_task_connection(client, task_list[i - 1], task_list[i])

#Создать задачу
async def create_task(client, group_id, crm_object_id, creator_id, responsible_id, template_id):
  url = bitrix24_url + "tasks.task.add"
  body = {
    "fields": {
      "TITLE": f"Задача по шаблону {template_id}", 
      "CREATED_BY": creator_id,
      "RESPONSIBLE_ID": responsible_id, 
      "GROUP_ID": group_id,
      "UF_AUTO_710940755509": crm_object_id,
      "FORKED_BY_TEMPLATE_ID": template_id
    } 
  }
  response = await client.post(url, json=body)
  response = response.json()
  print(response)
  return response["result"]["task"]["id"]

async def create_task_connection(client, task_id_from, task_id_to):
  url = bitrix24_url + "task.dependence.add"
  body = {
    "taskIdFrom": task_id_from,
    "taskIdTo": task_id_to,
    "linkType": 3
  }
  print(body)
  response = await client.post(url, json=body)
  response = response.json()
  print(response)
  return response["result"]
#async def batch_create_tasks(client, task_list):
  
#Изменить стадию обьекта CRM по выполнении задачи
async def update_crm_object_stage(client, id, stage):
  url = bitrix24_url + "crm.item.update"
  body = {"entityTypeId": 2, "id": id, "fields": {"stageId": stage} }
  response = await client.post(url, json=body)
  response = response.json()
  return response["result"]
