# ACBP
 Python version of [this](https://github.com/ExtevaXT/AntiCounterBot)

## Features
- Destroy counterbots
- Use cached inventory
- No async
- Better code

## Usage
- Install python, dependencies or whatever, idk how they automake it 
- Fill up `config.py`

```python
key='...'
api='https://tf2.tm/api/v2'
threshold=4
step=1
single_target = 0
keep_price=0
steam_cookie = '...' # steamLoginSecure from steam cookies
```

- Run `acb.py` or `mu.py` in console
- `acb.py {market_id} {default_price} {min_price} {step} {single_target}`
- You can use `-c` instead of `{market_id}` to use cached inventory

## Notes
- All classic frontends are handled fine, tf2, cs, dota.
