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

load_dotenv(dotenv_path=".env.local")
redis_url = os.getenv("REDIS_URL")
#cartesia_api_key = os.getenv("CARTESIA_API_KEY")
bitrix24_url = os.getenv("B24_WEBHOOK")

async def get_deal_fields(client, deal_id):
  ...

async def create_task(client, fields):
  ...

async def send_notification(client, deal):
  ...

async def update_deal(client, deal_id):
  ...

async def check_task(client, task_id):
  ...

async def return_task_to_work(client, task_id):
  ...

