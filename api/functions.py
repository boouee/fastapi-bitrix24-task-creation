from urllib.parse import unquote
from datetime import datetime, timedelta
import httpx
import time
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
from b24pysdk import BitrixWebhook, Client

load_dotenv(dotenv_path=".env.local")
domain = os.getenv("domain")
webhook_token = os.getenv("webhook_token")
bitrix_token = BitrixWebhook(
    domain=domain,
    webhook_token=webhook_token,
)

client = Client(bitrix_token)

async def main(deal_id):
  fields = await get_deal_fields(client, deal_id)
  await create_task(client, fields)
  
async def get_deal_fields(client, deal_id):
  bitrix_response = client.crm.deal.get(bitrix_id=deal_id).response
  result = bitrix_response.result
  print(result)
  return {"TITLE": "TITLE", "RESPONSIBLE_ID":1}
  
async def create_task(client, fields):
  
  bitrix_response = client.tasks.task.add(fields=fields).response
  result = bitrix_response.result
  print(result)

async def send_notification(client, deal):
  ...

async def update_deal(client, deal_id):
  ...

async def check_task(client, task_id):
  ...

async def return_task_to_work(client, task_id):
  ...

