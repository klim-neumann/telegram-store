CITIES = 'Выберите город:'
PRODUCTS = 'Выберите товар:'
PAYMENTS = 'Выберите способ оплаты:'

CRYPTOCURRENCY = '''
📄 <strong>Сделка</strong> #{deal_number}

<strong>Город:</strong> {city_name}
<strong>Товар:</strong> {product_name}
<strong>К оплате:</strong> {total_price} {cryptocurrency_name}

Используйте адрес ниже для оплаты

Монета: {cryptocurrency_name}
Сеть: {cryptocurrency_network} – {cryptocurrency_standard} ‼️

<code>{cryptocurrency_address}</code>

⚠️ Отправляйте только {cryptocurrency_name} через сеть {cryptocurrency_network}, иначе монеты будут утеряны.
'''

BANK = '''
📄 <strong>Сделка</strong> #{deal_number}

<strong>Город:</strong> {city_name}
<strong>Товар:</strong> {product_name}
<strong>К оплате:</strong> {total_price} KZT

Используйте номер карты ниже для оплаты

<code>{bank_details}</code>
'''

CONFIRM = '''
Платеж не найдет, обратитесь в поддержку с чеком
@MegaMarket_support
'''
