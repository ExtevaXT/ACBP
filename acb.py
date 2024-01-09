import platform
import ctypes
import requests
from time import sleep, localtime, strftime
import json
import datetime

import flash
from config import *

single_target = 0
cooldown_delay = 60000
default_delay = 15000
short_delay = 5000

inventory = None
inventory_item = None
market_item_id = None

price = 0
lowest_price = 0
outranned = 0

min_price = 0
default_price = 0

if platform.system() == 'Windows': ctypes.windll.kernel32.SetConsoleTitleW("ACBP")
print('AntiCounterBot | Python Version')

def load_inventory(cached=False):
    global inventory
    index_path = 'index.txt'
    cache_path = 'inventory.json'
    if(cached == True):
        with open(cache_path, "r") as file:
            inventory = json.load(file)
    else:
        response = requests.get(f'{api}/my-inventory/?key={key}')
        if response.status_code == 200:
            inventory = response.json()['items']
            with open('inventory.json', 'w', encoding='utf-8') as file:
                json.dump(inventory, file, ensure_ascii=False, indent=4)
            with open(index_path, 'w', encoding="utf-8") as file:
                for item in inventory:
                    text = f"{item['id']}: {item['market_hash_name']}"
                    file.write(text + '\n')
            print(f'IDs written to {index_path}')

def select_item():
    while True:
        steam_item_id = input("Enter steam item id: ")
        matches = list(filter(lambda x: x["id"]==steam_item_id, inventory))
        if matches:
            global inventory_item
            inventory_item = matches[0]
            name = inventory_item['market_hash_name']
            print(f"Valid ID: {name}")
            if platform.system() == 'Windows': ctypes.windll.kernel32.SetConsoleTitleW(f"ACBP | {name}")
            break
        else: print('Invalid ID')

def set_prices():
    global default_price, min_price
    default_price = input("Enter default_price: ")
    min_price = input("Enter min_price: ")
    input("Check your input. Enter to continue")

def now(): return strftime("[%Y-%m-%d %H:%M:%S]", localtime())

def check_prices():
    global inventory_item, lowest_price, min_price, price
    response = requests.get(f'{api}/search-item-by-hash-name/?key={key}&hash_name={inventory_item["market_hash_name"]}')
    if response.status_code == 200:
        if len(response['data']) == 0:
            lowest_price = default_price;
            return
        lowest_price = response['data'][0].price
        if single_target == 1:
            # lowest_price = list(filter(lambda x: str(x["instance"]) == inventory_item['instanceid'] and str(x["class"]) == inventory_item['classid'], response['data']))[0]['price']
            lowest_price = next(x['price'] for x in response['data'] if str(x['instance']) == inventory_item['instanceid'] and str(x['class']) == inventory_item['classid'])
        if lowest_price < min_price: price = default_price
        elif lowest_price != min_price: price = lowest_price - step
        if lowest_price == price and len(response['data']) >= 2 and response['data'][0]['count'] == 1:
            if default_price == 0: price = response['data'][1]['price'] - step
            
def process_item():
    global inventory_item, market_item_id, lowest_price, min_price, price, threshold, outranned
    check_prices()
    if price <= min_price:
        if market_item_id is None and default_price != 0:
            price = default_price
        else:
            print(f'{now()} Reached min price, lowest: {lowest_price}')
            sleep(cooldown_delay)
            return
    # If we are first skip
    if market_item_id and price == lowest_price:
        sleep(short_delay)
        return
    # Restart if they are banging us
    # If gap more than {threshold} iterations
    if market_item_id and outranned >= threshold:
        response = requests.get(f"{api}/set-price?key={key}&item_id={market_item_id}&price=0&cur=RUB")
        if response.status_code == 200:
            print(f'{now()} Reached threshold, re-adding item')
            market_item_id = None
            # Let it cook
            sleep(cooldown_delay + short_delay)
            return
    # First iteration
    if market_item_id is None:
        if default_price: price = default_price
        response = requests.get(f"{api}/add-to-sale?key={key}&id={inventory_item['id']}&price={price}&cur=RUB")
        if response.status_code == 200:
            if response['success']:
                market_item_id = response['item_id']
                print(f'{now()} Added item for {price}')
                # Here comes enemy
                # Let it cook
                sleep(default_delay)
                check_prices()
                outranned = 0
            else:
                print(f"{now()} {response['error']}")
                sleep(short_delay)
                return
    
    response = requests.get(f"{api}/set-price?key={key}&item_id={market_item_id}&price={price}&cur=RUB")
    if response.status_code == 200:       
        if response['success']:
            if price == default_price:
                print(f"Item has default {price}")
                sleep(default_delay * 2)
            else:
                if price != lowest_price: print(f"{now()} Anticountered {lowest_price} with {price}")
                else: print(f"{now()} Item has lowest price")
                sleep(default_delay)
        else:
            if response['error']:
                print(f"{now()} {response['error']}")
                # Market got ~60s cooldown for set-price
                # Spams 'too often' when enemy starting to find gap
                if response['error'] == 'too_often': outranned += 1
                sleep(short_delay)
            else:
                print(f"{now()} {inventory_item['market_hash_name']} has been bought for: {price}")
                flash.flash_console_icon()
                input()
    outranned = 0            
    
# flash.flash_console_icon()

# load_inventory(cached=True)
# time.sleep(1)
# select_item()
# set_prices()