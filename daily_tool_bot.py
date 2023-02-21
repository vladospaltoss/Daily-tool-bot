import asyncio
from aiogram import Bot, Dispatcher, types, executor
from db import Datebase
from config import BOT_TOKEN, API_KEY
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import requests 
import datetime
from bs4 import BeautifulSoup
import lxml
import random
from requests.auth import HTTPProxyAuth
import pytz

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

db = Datebase('database.db')

@dp.message_handler(commands=['start'])
async def start(msg: types.Message) -> None:
    if msg.chat.type == 'private':
        if not db.user_exists(msg.from_user.id):
            db.add_user(msg.from_user.id)
        await msg.answer('Добро пожаловать! Я <b>Daily Bot</b>, каждое утро я буду присылать тебе свежую информацию.\nДругие функции можно узнать с помощью комманды <b>/help</b> ', parse_mode='HTML')

@dp.message_handler(commands=['help'])
async def info(msg: types.Message) -> None:
    await msg.reply(
        '<strong>Комманды</strong>\n'\
        '\n'\
        'Комманда <b>/weather</b> - для получения информации о текущей погоде\n'\
        '\n'\
        'Комманда <b>/money</b> - для получения информации о текущем курсе валют\n'\
        '\n'\
        'Комманда <b>/quote</b> - для получения мотивирующей цитаты\n'\
        '\n'\
        'Если возникли вопросы/жалобы/предложения, то обращаться к <b>@VladossPaltos</b>', parse_mode="HTML"
    )


@dp.message_handler(commands=["quote"])
async def quote(msg: types.Message) -> None:
    try:
        proxies = {'http': 'http://ttNkVLRS:63cYXNdr@195.245.103.252:64534'}
        req = requests.get('https://wikiphile.ru/570-fraz-o-motivacii/?ysclid=le2s2e8ouu459711332', proxies=proxies)
        soup = BeautifulSoup(req.text, 'lxml')
        lst = soup.find('ol').find_all('li')
        random_index = random.randint(0, len(lst) - 1)

        await msg.answer(
            f'<strong>Рандомная цитата</strong>\n'\
            '\n'\
            f'{lst[random_index].text}', parse_mode="HTML"
            )

    except Exception as ex:
        print(ex)
        await msg.answer('Возникла ошибка...')


@dp.message_handler(commands=["weather"])
async def wether(msg: types.Message) -> None:
    try:
        URL= f'https://api.openweathermap.org/data/2.5/weather?lat=53.9&lon=27.5667&appid={API_KEY}&units=metric&lang=ru'
        proxies = {'http': 'http://ttNkVLRS:63cYXNdr@195.245.103.252:64534'}

        r = requests.get(url=URL, proxies=proxies)
        data = r.json()

        city = data['name']
        cur_weath = round(float(data['main']['temp']))
        feel_weth = round(float(data['main']['feels_like']))
        humidity = data['main']['humidity']
        wind = data['wind']['speed']
        description = data['weather'][0]['description']
        sunrise = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
        sunset = datetime.datetime.fromtimestamp(data['sys']['sunset'])
        mnsk_sunrise = sunrise + datetime.timedelta(hours=3)
        mnsk_sunset = sunset + datetime.timedelta(hours=3)
        mnsk_sunrise = mnsk_sunrise.strftime('%H:%M')
        mnsk_sunset = mnsk_sunset.strftime('%H:%M')

        await msg.answer(
            f'<strong>Погода на {datetime.datetime.now().strftime("%d.%m.%Y")}</strong>\n'\
            '\n'\
            f'<b>{city}</b>\n'\
            f'{str(description).title()}\n'\
            f'Температура   {cur_weath}°С\n'\
            f'Ощущается как   {feel_weth}°С\n'\
            f'Скорость ветра -   {wind} м/с\n'\
            f'Влажность   {humidity}%\n'\
            f'Рассвет:   {mnsk_sunrise}\n'
            f'Закат:   {mnsk_sunset}\n', parse_mode="HTML"
            )
    except Exception as ex:
        print(ex)
        await msg.answer('Возникла ошибка...')


@dp.message_handler(commands=['money'])
async def money(msg: types.Message) -> None:
    try:
        proxies = {'http': 'http://ttNkVLRS:63cYXNdr@195.245.103.252:64534'}
        rub = requests.get('https://www.nbrb.by/api/exrates/rates/RUB?parammode=2', proxies=proxies)
        data1 = rub.json()
        price_rub = round(float(data1['Cur_OfficialRate']), 2)

        usd = requests.get('https://www.nbrb.by/api/exrates/rates/USD?parammode=2', proxies=proxies)
        data2 = usd.json()
        price_usd = round(float(data2['Cur_OfficialRate']), 2)

        eur = requests.get('https://www.nbrb.by/api/exrates/rates/EUR?parammode=2', proxies=proxies)
        data3 = eur.json()
        price_eur = round(float(data3['Cur_OfficialRate']), 2)

        await msg.answer(
            f'<strong>Курсы валют на {datetime.datetime.now().strftime("%d.%m.%Y")}</strong>\n'\
            '\n'\
            f'<u>Доллар $</u>\n'\
            f'Курс по НБРБ:   {price_usd} BYN\n'\
            '\n'\
            f'<u>Евро €</u>\n'\
            f'Курс по НБРБ:   {price_eur} BYN\n'\
            '\n'\
            f'<u>Российский рубль(за 100р) ₽</u>\n'\
            f'Курс по НБРБ:   {price_rub} BYN\n', parse_mode="HTML"
            )

    except Exception as ex:
        await msg.answer('Возникла ошибка...')
        print(ex)



@dp.message_handler(commands=['onlyadmin'])
async def sms(msg: types.Message) -> None:
    users = db.get_users()
    for user in users:
        try:        
            URL= f'https://api.openweathermap.org/data/2.5/weather?lat=53.9&lon=27.5667&appid={API_KEY}&units=metric&lang=ru'
            headers = {
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.41',
                    'cookie': '__cf_bm=zRd.cB6QSqIji6uoJe468.oBemHDtsINpvgP_P5hrcs-1676488839-0-Ab38wTDsXh0HIHDRG2u2LsZAZl2Nn3F11BNIENISOI50fgHVL96EWpo6BkmtZ3Sp8D8u+Kmwdc6bQdyROhRXO7pdFfgt6B0DULBtYDhEPilzIr8PDfmMbBaNVCyw63TZw5UVKdVueQHgtOfKo9RsCak=',
                    'accept-language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
                    'accept-encoding': 'gzip, deflate, br',
                    'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Microsoft Edge";v="110"',
                    'upgrade-insecure-requests': '1',
                    'cache-control': 'max-age=0',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'none',
                    'sec-fetch-user': '?1',

                }
            # proxies = {'http': '194.158.203.14:80'}
            proxies = {'http': 'http://ttNkVLRS:63cYXNdr@195.245.103.252:64534'}
            # export HTTPS_PROXY="http://ttNkVLRS:63cYXNdr@195.245.103.252:64534"

            # response = requests.get('https://api64.ipify.org?format=json', proxies=proxies).json()
            # print(response["ip"])

            r = requests.get(url=URL, proxies=proxies)
            # print(r.status_code)
            data = r.json()

            city = data['name']
            cur_weath = round(float(data['main']['temp']))
            feel_weth = round(float(data['main']['feels_like']))
            humidity = data['main']['humidity']
            wind = data['wind']['speed']
            description = data['weather'][0]['description']
            sunrise = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
            sunset = datetime.datetime.fromtimestamp(data['sys']['sunset'])
            mnsk_sunrise = sunrise + datetime.timedelta(hours=3)
            mnsk_sunset = sunset + datetime.timedelta(hours=3)
            mnsk_sunrise = mnsk_sunrise.strftime('%H:%M')
            mnsk_sunset = mnsk_sunset.strftime('%H:%M')


            rub = requests.get('https://www.nbrb.by/api/exrates/rates/RUB?parammode=2', proxies=proxies)
            # print(rub.status_code)
            data1 = rub.json()
            price_rub = round(float(data1['Cur_OfficialRate']), 2)

            usd = requests.get('https://www.nbrb.by/api/exrates/rates/USD?parammode=2', proxies=proxies)
            # print(usd.status_code)
            data2 = usd.json()
            price_usd = round(float(data2['Cur_OfficialRate']), 2)

            eur = requests.get('https://www.nbrb.by/api/exrates/rates/EUR?parammode=2', proxies=proxies)
            # print(eur.status_code)
            data3 = eur.json()
            price_eur = round(float(data3['Cur_OfficialRate']), 2)

            req = requests.get('https://wikiphile.ru/570-fraz-o-motivacii/?ysclid=le2s2e8ouu459711332', proxies=proxies)
            # print(req.status_code)
            
            soup = BeautifulSoup(req.text, 'lxml')

            lst = soup.find('ol').find_all('li')
            random_index = random.randint(0, len(lst) - 1)

            await bot.send_message(user[0], text=
                f'<b>---{datetime.datetime.now().strftime("%d.%m.%Y")}---</b>\n'\
                '\n'\
                f'<strong>Погода</strong>\n'\
                '\n'\
                f'<b>{city}</b>\n'\
                f'{str(description).title()}\n'\
                f'Температура   {cur_weath}°С\n'\
                f'Ощущается как   {feel_weth}°С\n'\
                f'Скорость ветра -   {wind} м/с\n'\
                f'Влажность   {humidity}%\n'\
                f'Рассвет:   {mnsk_sunrise}\n'
                f'Закат:   {mnsk_sunset}\n'
                '\n'\
                f'<strong>Курсы валют</strong>\n'\
                '\n'\
                f'<u>Доллар $</u>\n'\
                f'Курс по НБРБ:   {price_usd} BYN\n'\
                f'<u>Евро €</u>\n'\
                f'Курс по НБРБ:   {price_eur} BYN\n'\
                f'<u>Российский рубль(за 100р) ₽</u>\n'\
                f'Курс по НБРБ:   {price_rub} BYN\n'
                '\n'\
                f'<strong>Рандомная цитата</strong>\n'\
                '\n'\
                f'{lst[random_index].text}'
                , parse_mode="HTML"
                )
            if int(user[1]) != 1:
                db.set_active(user[0], 1)
        except Exception as ex:
            print(ex)
            db.set_active(user[0], 0)



if __name__ == '__main__':
    scheduler = AsyncIOScheduler(timezone='Europe/Minsk')
    scheduler.add_job(sms, trigger='cron', hour=7, minute=00, start_date=datetime.datetime.now(), kwargs={'msg':types.Message, }, misfire_grace_time=3600) 
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)