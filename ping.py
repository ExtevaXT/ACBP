import requests
import platform
import ctypes
from config import *
import time
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
if platform.system() == 'Windows': ctypes.windll.kernel32.SetConsoleTitleW("Ping Pong")
print('Ping Pong')
while True:
    try:
        response = requests.get("https://steamcommunity.com/pointssummary/ajaxgetasyncconfig", 
                                headers={'Cookie': f'steamLoginSecure={steam_cookie};'})
        if response.json()["success"]:
            token = response.json()["data"]["webapi_token"]
            logging.info(token)
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
