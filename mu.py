import subprocess
import requests
import tabulate
import platform
import ctypes
from config import *

if platform.system() == 'Windows': ctypes.windll.kernel32.SetConsoleTitleW("Market Utility")
print('Market Utility | Python Version')

def acb(args):
    subprocess.Popen(['python', 'acb.py', args], creationflags=subprocess.CREATE_NEW_CONSOLE)
def inventory():
    ''
def offers():
    ''
# Passed
def update():
    response = requests.get(f'{api}/update-inventory/?key={key}')
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print('Requested market inventory update')
            # It actually will update after 5s-10min
def add(args):
    response = requests.get(f'{api}/add-to-sale?key={key}&id={args[0]}&price={args[1]}&cur=RUB')
    if response.status_code == 200:
        if response['success']:
            print(f'Added {args[0]} for {args[1]} -> {response["item_id"]}')
        else:
            print(response["error"])
def set(args):
    response = requests.get(f'{api}/set-price?key={key}&item_id={args[0]}&price={args[1]}&cur=RUB')
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f'Setted price {args[1]} for {args[0]}')
        else:
            print(data["error"])
def check():
    ''
    

while(True):
    query = input('>  ').split()
    literal = query[0]
    args = query[1:]
    match literal:
        case "acb":
            acb(args)
        case "inventory":
            inventory()
        case "offers":
            offers()
        case "update":
            update()
        case "add":
            add(args)
        case "check":
            check()
        case "set":
            set(args)
        case "reload":
            print('no')
        case "help":
            print('https://github.com/ExtevaXT/ACBP')