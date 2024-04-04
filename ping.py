import requests
import platform
import ctypes
from config import *
import time

if platform.system() == 'Windows': ctypes.windll.kernel32.SetConsoleTitleW("Ping Pong")
print('Ping Pong')
while True:
    try:
        response = requests.get(f"{api}/ping?key={key}&v=2")
        print(response.json())
        if response.json()["success"]:
            time.sleep(180)
        else: time.sleep(60)
    except:
        time.sleep(60)
