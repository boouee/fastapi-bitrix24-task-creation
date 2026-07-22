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
  deal_fields = await get_deal_fields(deal_id)
  if deal_fields["UF_CRM_1784660003816"] == "1":
    print("A task has already been created.")
    return
  preparation_list = await get_preparations(1)
  deal_preparations = await get_deal_preparations(preparation_list, deal_id)
  deal_services = await get_deal_services(preparation_list, deal_id)
  deal_services = list(map(lambda preparation: preparation["name"], deal_services))
  contact_data = await get_contact_data(deal_fields["CONTACT_ID"])
  task_preparations = list(map(lambda preparation: preparation["name"], deal_preparations))
  task_preparations = "\n".join(task_preparations)
  
  fields = {
	  "TITLE": (", ".join(deal_services) or "Задача"),
	  "RESPONSIBLE_ID": deal_fields["UF_CRM_1782853296"],
	  "DEADLINE": deal_fields["UF_CRM_1782801843799"],
	  "UF_CRM_TASK": [f"D_{deal_id}"],
	  "TASK_CONTROL": "Y"
  }
  task_id = await create_task(fields)
  task_description = f"""
  Адрес:
  {(deal_fields["UF_CRM_1782801963621"] or "")}

  Имя: {(contact_data["NAME"] or "") + " " + (contact_data["SECOND_NAME"] or "") + " " + (contact_data["LAST_NAME"] or "") }
  Телефон: {contact_data["PHONE"][0]["VALUE"]}

  Препараты (изменить: https://fastapi-bitrix24-task-creation-one.vercel.app/api/edit_preparations?deal_id={deal_id}&task_id={task_id}):
  {task_preparations}
  """
  await update_task_description(task_id, task_description)
  await update_deal(deal_id)
	
async def get_deal_fields(deal_id):
  bitrix_response = client.crm.deal.get(bitrix_id=deal_id).response
  result = bitrix_response.result
  print(result)
  return result

async def get_contact_data(contact_id):
  fields = { "ID": contact_id }
  response = bitrix_token.call_method(api_method="crm.contact.get", params=fields)
  return response["result"]
	
async def create_task(fields):  
  bitrix_response = client.tasks.task.add(fields=fields).response
  result = bitrix_response.result
  print(result)
  return result["task"]["id"]
	
async def send_notification(client, deal):
  ...

async def update_deal(deal_id):
  fields = {
	  "entityTypeId": 2,
	  "id": deal_id,
	  "useOriginalUfNames": "Y", 
	  "fields": {
		  "UF_CRM_1784660003816": "1"
	  }
  }
  response = bitrix_token.call_method(api_method="crm.item.update", params=fields)

async def set_task_preparations(preparation_list, deal_id, task_id):
  deal_preparations = await get_deal_preparations(preparation_list, deal_id)
  task_preparations = list(map(lambda preparation: preparation["name"], deal_preparations))
  task_preparations = "\n".join(task_preparations)
  task_data = await get_task(task_id)
  task_description = task_data["description"]
  print(task_description)
  task_description = re.search(r".*Препараты.*?\n", task_description, re.S).group()
  print(task_description)
  task_description = task_description + task_preparations
  await update_task_description(task_id, task_description)

async def set_deal_preparations(preparation_list, preparations, deal_id, task_id):
  deal_services = await get_deal_services(preparation_list, deal_id)
  rows = []
  preparations = preparations + deal_services
  for service in deal_services:
	  rows.append({
	      "PRODUCT_ID": service["productId"],
	      "QUANTITY": service["quantity"],
	      "PRICE": 0
	  })
  for preparation in preparations:
	  rows.append({
	      "PRODUCT_ID": preparation["productId"],
	      "QUANTITY": preparation["quantity"],
	      "PRICE": 0
	  })
  fields = {
	"id": deal_id,
	"rows": rows	  
  }
  response = bitrix_token.call_method(api_method="crm.deal.productrows.set", params=fields)

async def get_preparations(start): 
  fields = {
	"start": start,
	"select": [
		"id",
		"iblockId",
		"name",
		"quantity",
		"price"
	],
	"filter": {
		"active": "Y",
		"iblockId": 14,
		"iblockSectionId": 2
	}
  }
  response = bitrix_token.call_method(api_method="catalog.product.list", params=fields)
  products = response["result"]["products"]
  if response["total"] == 50:
	  next_page_products = await get_preparations(start + 1)
	  products = products + next_page_products
  #products = list(map(lambda product: product["name"], products)
      
  print(products)
  return products
	
async def get_deal_preparations(preparation_list, deal_id):
  fields = {
	"filter": {
	  "=ownerType": "D",
	  "=ownerId": deal_id
	}
  }
  response = bitrix_token.call_method(api_method="crm.item.productrow.list", params=fields)
  products = response["result"]["productRows"]
  preparation_list = [item.get("name") for item in preparation_list]
  products = list(filter(lambda product: product["productName"] in preparation_list, products))
  for product in products:
	  product["name"] = product["productName"]
	  
  print(products)
  return products

async def get_deal_services(preparation_list, deal_id):
  fields = {
	"filter": {
	  "=ownerType": "D",
	  "=ownerId": deal_id
	}
  }
  response = bitrix_token.call_method(api_method="crm.item.productrow.list", params=fields)
  products = response["result"]["productRows"]
  preparation_list = [item.get("name") for item in preparation_list]
  products = list(filter(lambda product: product["productName"] not in preparation_list, products))
  for product in products:
	  product["name"] = product["productName"]
  print(products)
  return products

async def check_task(task_id):
  fields = {"taskId": task_id}
  response = bitrix_token.call_method(api_method="tasks.task.result.list", params=fields)
  if response["result"]["text"] and response["result"]["files"]:
	  return True
  else:
	  return False 

async def return_task_to_work(task_id):
  fields = {"taskId": task_id}
  response = bitrix_token.call_method(api_method="tasks.task.disapprove", params=fields)

async def update_task_description(preparations, task_id):
  task_data = await get_task(task_id)
  task_description = task_data["description"]
  task
  fields = {"taskId": task_id, "fields": { "description": description } }
  response = bitrix_token.call_method(api_method="tasks.task.update", params=fields)

async def get_task(task_id):
  fields = {"taskId": task_id}
  response = bitrix_token.call_method(api_method="tasks.task.get", params=fields)
  return response["result"]["task"]

async def update_task_description(task_id, description):
  fields = {"id": task_id, "fields": { "DESCRIPTION": description } }
  response = bitrix_token.call_method(api_method="tasks.task.update", params=fields)
	  
