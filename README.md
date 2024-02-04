# ACBP
 Python version of [that]("https://github.com/ExtevaXT/AntiCounterBot") garbage

## Features

- Cache inventory to not ban yourself
- No async
- Better code

## Usage
- Install python
- Fill up `config.py`

```python
key='...'
api='https://tf2.tm/api/v2'
threshold=4
step=1
keep_price=0
```

- Run `acb.py` or `mu.py` in console
- `acb.py {market_id} {default_price} {min_price} {step} {single_target}`
- You can use `-c` instead of `{market_id}` to use cached `inventory.json`