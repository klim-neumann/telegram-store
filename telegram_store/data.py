import json

with open('telegram_store/data/cities.json', encoding='utf-8') as file:
	cities = sorted(json.load(file), key=lambda x: x['name'])

with open('telegram_store/data/products.json', encoding='utf-8') as file:
	products = sorted(json.load(file), key=lambda x: x['name'])

with open('telegram_store/data/payments.json', encoding='utf-8') as file:
	payments = json.load(file)
