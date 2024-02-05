import platform
import ctypes
import requests
from time import sleep, localtime, strftime
import json
import datetime
import sys

import flash
from config import *

# TODO Operate on second lowest when reached min_price, some of them do that shit
# TODO Fix item_on_sale bug (Adding existing offer)

single_target = 0
cooldown_delay = 60
default_delay = 15
short_delay = 5
cache = False

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

def load_inventory():
    global inventory
    index_path = 'index.txt'
    cache_path = 'inventory.json'
    if(cache == True):
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
        matches = list(filter(lambda x: x["id"] == steam_item_id, inventory))
        if matches:
            global inventory_item
            inventory_item = matches[0]
            name = inventory_item['market_hash_name']
            print(f"Selected: {name}")
            if platform.system() == 'Windows': ctypes.windll.kernel32.SetConsoleTitleW(f"ACBP | {name}")
            break
        else: print('Invalid ID')

# TODO Test it
def select_offer():
    response = requests.get(f'{api}/items/?key={key}')
    if response.status_code == 200:
        matches = list(filter(lambda x: x["item_id"] == market_item_id, 
                              response.json()['items']))
        if matches:
            global inventory_item, steam_item_id
            item = matches[0]
            # Retrieving asset ID directly from steam, market does not provide it
            response = requests.get(f'{api}/get-my-steam-id/?key={key}')
            if response.status_code == 200:
                steam_id = response.json()['steamid64']
                app_id = 440 if "tf2" in api else (710 if "cs" in api else (570 if "dota" in api else 0))
                response = requests.get(f'https://steamcommunity.com/inventory/{steam_id}/{app_id}/2?l=english&count=5000')
                if response.status_code == 200:
                    inventory = response.json()
                    steam_item = next(asset for asset in inventory.assets if asset['classid'] == item['classid'] and asset['instanceid'] == item['instanceid'])
                    # Pray for finding right one
                    steam_item_id = steam_item['assetid']
                    inventory_item = {
                        'market_hash_name': item['market_hash_name'],
                        'instanceid': item['instanceid'],
                        'classid': item['classid'],
                        'id': steam_item['assetid']
                    }

def set_prices(): 
    global default_price, min_price
    default_price = int(input("Enter default_price: "))
    min_price = int(input("Enter min_price: "))
    input("Check your input. Enter to continue")

def now(): return strftime("[%Y-%m-%d %H:%M:%S]", localtime())

def check_prices():
    global lowest_price, price
    response = requests.get(f'{api}/search-item-by-hash-name/?key={key}&hash_name={inventory_item["market_hash_name"]}')
    if response.status_code == 200:
        data = response.json()['data']
        # No other offers
        if len(data) == 0:
            lowest_price = default_price;
            return
        lowest_price = data[0]['price']
        # Single target (Targetting item with stacked offers)
        if single_target == 1:
            lowest_price = next(x['price'] for x in data if str(x['instance']) == inventory_item['instanceid'] and str(x['class']) == inventory_item['classid'])
        # Reached min_price
        if lowest_price < min_price: 
            price = default_price
        # Main step
        elif lowest_price != price: 
            price = lowest_price - step
        # Target second offer in item?
        if lowest_price == price and len(data) >= 2 and data[0]['count'] == 1:
            if default_price == 0: 
                price = data[1]['price'] - step
            
def process_item():
    global market_item_id, price, outranned
    check_prices()
    # Reached min_price
    if price <= min_price:
        if market_item_id is None and default_price != 0:
            price = default_price
        else:
            print(f'{now()} Reached min price, lowest: {lowest_price}')
            sleep(cooldown_delay)
            return
    
    if market_item_id is not None:
        # Advantage skip
        if price == lowest_price:
            sleep(short_delay)
            return
        # Re-add if enemy have advantage (If gap more than {threshold} iterations)
        if outranned >= threshold:
            response = requests.get(f"{api}/set-price?key={key}&item_id={market_item_id}&price=0&cur=RUB")
            if response.status_code == 200:
                print(f'{now()} Reached threshold, re-adding item')
                market_item_id = None
                # Let it cook
                sleep(cooldown_delay + short_delay)
                return
    # First iteration
    if market_item_id is None:
        print('Started first iteration')
        if default_price: price = default_price
        response = requests.get(f"{api}/add-to-sale?key={key}&id={inventory_item['id']}&price={price}&cur=RUB")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                market_item_id = data['item_id']
                print(f'{now()} Added item for {price}')
                # Here comes enemy
                # Let it cook
                sleep(default_delay)
                check_prices()
                outranned = 0
            else:
                print(f"{now()} {data['error']}")
                sleep(short_delay)
                return
    # Setting calculated price
    response = requests.get(f"{api}/set-price?key={key}&item_id={market_item_id}&price={price}&cur=RUB")
    if response.status_code == 200:    
        data = response.json()
        if data['success']:
            if price == default_price:
                print(f"Item has default {price}")
                sleep(default_delay * 2)
            else:
                if price != lowest_price: print(f"{now()} Anticountered {lowest_price} with {price}")
                else: print(f"{now()} Item has lowest price")
                sleep(default_delay)
        else:
            if data['error']:
                print(f"{now()} {data['error']}")
                # Market got ~60s cooldown for set-price
                # Spams 'too often' when enemy starting to find gap
                if data['error'] == 'too_often': outranned += 1
                sleep(short_delay)
            else:
                print(f"{now()} {inventory_item['market_hash_name']} has been bought for: {price}")
                flash.flash_console_icon()
                input()
    # Refresh outran
    outranned = 0            
    
# Parse args for market utility
if len(sys.argv) > 1: 
    if sys.argv[1] == '-c': cache = True
    else: market_item_id = int(sys.argv[1])
if len(sys.argv) > 2: default_price = int(sys.argv[2])
if len(sys.argv) > 3: min_price = int(sys.argv[3])
if len(sys.argv) > 4: step = int(sys.argv[4])
if len(sys.argv) > 5: single_target = int(sys.argv[5])

load_inventory()
select_item()
set_prices()
print('Starting main loop')
while True:
    process_item()
    sleep(default_delay)
