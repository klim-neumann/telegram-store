import asyncio
from asyncio import sleep
from random import randrange

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, PicklePersistence, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from aiohttp import ClientSession

import data
import messages
from env import TOKEN

session = ClientSession()


async def cities(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
	keyboard = [[InlineKeyboardButton(x['name'], callback_data=f'city_{x["id"]}')] for x in data.cities]
	reply_markup = InlineKeyboardMarkup(keyboard)

	if update.callback_query is None:
		await update.message.reply_text(messages.CITIES, reply_markup=reply_markup)
	else:
		await update.callback_query.answer()
		await update.callback_query.edit_message_text(messages.CITIES, reply_markup=reply_markup)


async def products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	context.user_data['city_id'] = int(update.callback_query.data.replace('city_', ''))

	keyboard = [[InlineKeyboardButton(f'{x["name"]} ({x["price"]}тг)', callback_data=f'product_{x["id"]}')] for x in data.products]
	keyboard += [[InlineKeyboardButton('Назад', callback_data='start')]]
	reply_markup = InlineKeyboardMarkup(keyboard)

	await update.callback_query.answer()
	await update.callback_query.edit_message_text(messages.PRODUCTS, reply_markup=reply_markup)


async def payments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	context.user_data['product_id'] = int(update.callback_query.data.replace('product_', ''))

	keyboard = [[InlineKeyboardButton('Криптовалюта', callback_data='cryptocurrencies')]]
	keyboard += [[InlineKeyboardButton(x['name'], callback_data=f'bank_{x["id"]}') for x in data.payments['banks']]]
	keyboard += [[InlineKeyboardButton('Назад', callback_data=f'city_{context.user_data["city_id"]}')]]
	reply_markup = InlineKeyboardMarkup(keyboard)

	await update.callback_query.answer()
	await update.callback_query.edit_message_text(messages.PAYMENTS, reply_markup=reply_markup)


async def cryptocurrencies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	keyboard = [[InlineKeyboardButton(x['name'], callback_data=f'cryptocurrency_{x["id"]}')] for x in data.payments['cryptocurrencies']]
	keyboard += [[InlineKeyboardButton('Назад', callback_data=f'product_{context.user_data["product_id"]}')]]
	reply_markup = InlineKeyboardMarkup(keyboard)

	await update.callback_query.answer()
	await update.callback_query.edit_message_text(messages.PAYMENTS, reply_markup=reply_markup)


async def cryptocurrency(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	if context.bot_data.get('deal_number') is None:
		context.bot_data['deal_number'] = 0
	else:
		context.bot_data['deal_number'] += 1

	context.user_data['cryptocurrency_id'] = int(update.callback_query.data.replace('cryptocurrency_', ''))
	city = next(x for x in data.cities if x['id'] == context.user_data['city_id'])
	product = next(x for x in data.products if x['id'] == context.user_data['product_id'])
	cryptocurrency = next(x for x in data.payments['cryptocurrencies'] if x['id'] == context.user_data['cryptocurrency_id'])

	match cryptocurrency['name']:
		case 'BTC':
			cryptocurrency_id = 'bitcoin'
		case 'USDT':
			cryptocurrency_id = 'tether'
		case 'TON':
			cryptocurrency_id = 'the-open-network'

	async with session.get(
		'https://api.coingecko.com/api/v3/simple/price',
		params={'ids': cryptocurrency_id, 'vs_currencies': 'usd'},
	) as res:
		json = await res.json()
		cryptocurrency_price = json[cryptocurrency_id]['usd']

	async with session.get('https://api.exchangerate-api.com/v4/latest/USD') as res:
		json = await res.json()
		rate = json['rates']['KZT']

	cryptocurrency_price = cryptocurrency_price * rate
	product_price = round(product['price'] / cryptocurrency_price, 9)

	keyboard = [[InlineKeyboardButton('Я оплатил(а)', callback_data='confirm')]]
	keyboard += [[InlineKeyboardButton('Отменить', callback_data='cryptocurrencies')]]
	reply_markup = InlineKeyboardMarkup(keyboard)

	await update.callback_query.answer()
	await update.callback_query.edit_message_text(
		messages.CRYPTOCURRENCY.format(
			deal_number=context.bot_data['deal_number'],
			city_name=city['name'],
			product_name=product['name'],
			total_price=product_price,
			cryptocurrency_name=cryptocurrency['name'],
			cryptocurrency_network=cryptocurrency['network'],
			cryptocurrency_standard=cryptocurrency['standard'],
			cryptocurrency_address=cryptocurrency['address']
		),
		reply_markup=reply_markup,
		parse_mode=ParseMode.HTML,
	)


async def bank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	if context.bot_data.get('deal_number') is None:
		context.bot_data['deal_number'] = 0
	else:
		context.bot_data['deal_number'] += 1

	context.user_data['bank_id'] = int(update.callback_query.data.replace('bank_', ''))
	city = next(x for x in data.cities if x['id'] == context.user_data['city_id'])
	product = next(x for x in data.products if x['id'] == context.user_data['product_id'])
	bank = next(x for x in data.payments['banks'] if x['id'] == context.user_data['bank_id'])

	keyboard = [[InlineKeyboardButton('Я оплатил(а)', callback_data='confirm')]]
	keyboard += [[InlineKeyboardButton('Отменить', callback_data=f'product_{context.user_data["product_id"]}')]]
	reply_markup = InlineKeyboardMarkup(keyboard)

	await update.callback_query.answer()
	await update.callback_query.edit_message_text(
		messages.BANK.format(
			deal_number=context.bot_data['deal_number'],
			city_name=city['name'],
			product_name=product['name'],
			total_price=product['price'],
			bank_details=bank['details']
		),
		reply_markup=reply_markup,
		parse_mode=ParseMode.HTML,
	)


async def confirm(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
	keyboard = [[InlineKeyboardButton('Назад', callback_data='start')]]
	reply_markup = InlineKeyboardMarkup(keyboard)

	await update.callback_query.answer()
	await update.callback_query.edit_message_text('Подтверждение оплаты...')
	await sleep(randrange(3, 7))
	await update.callback_query.edit_message_text(messages.CONFIRM, reply_markup=reply_markup)


persistence = PicklePersistence(filepath="telegram_store/data/callbackdata")
application = Application.builder().token(TOKEN).persistence(persistence).build()
application.add_handlers([
	CommandHandler('start', cities),
	CallbackQueryHandler(cities, pattern='^start$'),
	CallbackQueryHandler(products, pattern='^city_'),
	CallbackQueryHandler(payments, pattern='^product_'),
	CallbackQueryHandler(cryptocurrencies, pattern='^cryptocurrencies$'),
	CallbackQueryHandler(cryptocurrency, pattern='^cryptocurrency_'),
	CallbackQueryHandler(bank, pattern='^bank_'),
	CallbackQueryHandler(confirm, pattern='^confirm$'),
])
application.run_polling()
asyncio.run(session.close())
