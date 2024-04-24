import requests
import platform
import ctypes
from config import *
import time
import logging
from steampy.login import LoginExecutor

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
if platform.system() == 'Windows': ctypes.windll.kernel32.SetConsoleTitleW("Ping Pong")
print('Ping Pong')
def login():
    return LoginExecutor(login, password, shared_secret, requests.Session()).login()

session = login()
while True:
    try:
        response = session.get("https://steamcommunity.com/pointssummary/ajaxgetasyncconfig")
        if response.json()["success"]:
            token = response.json()["data"]["webapi_token"]
            logging.info(token)
            time.sleep(500)
            response = requests.post(f"{api}/ping-new?key={key}", json={"access_token": token})
            logging.info(response.json())
            if response.json()["success"]:
                time.sleep(24*60*60)
            else: time.sleep(60)
        else: 
            logging.info(response.json())
            time.sleep(60)
    except Exception as e: 
        logging.info(e)
        time.sleep(60)
