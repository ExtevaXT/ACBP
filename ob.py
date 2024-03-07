import requests
from time import sleep

from config import *

# https://tf2.tm/item/101785959-11040578

# We are checking orders and sticking to the last + 0.01 before max_price

print('Orders | ACB')

def check_orders():
    response = requests.post(f'{api.replace("/v2", "")}/MassInfo/0/1/0/0?key={key}', 
                             data={list: '101785959_11040578'})
    
    

item = input('Enter classid_instanceid: ')
default_price = input('Enter default_price: ')
max_price = input('Enter max_price: ')

while True:
    check_orders()
    sleep(1)
