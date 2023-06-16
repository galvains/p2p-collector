import requests
import json
import asyncio
import time

from fake_useragent import UserAgent


async def p2p_parser_binance(url: str, headers: dict, json_data: dict) -> None:
    response = requests.post(url=url, headers=headers, json=json_data)
    loader = json.loads(response.text)
    cards = loader['data']

    for element in cards:

        price = element['adv']['price']
        nick_name = element['advertiser']['nickName']
        orders = element['advertiser']['monthOrderCount']
        coins_available = element['adv']['surplusAmount']
        max_limit = element['adv']['maxSingleTransAmount']
        min_limit = element['adv']['minSingleTransAmount']
        finish_rate = round(100 * float(element['advertiser']['monthFinishRate']), 2)
        payment_methods = []

        for method in element['adv']['tradeMethods']:
            payment_methods.append(method['identifier'])

        print(
            f'BINANCE > {nick_name} | Orders: {orders} | Rate: {finish_rate}%\nAvailable: {coins_available} | Price: {price}\n'
            f'Max: {max_limit} | Min: {min_limit}\nMethod: {payment_methods}\n----------')


async def p2p_parser_bybit(url: str, headers: dict, json_data: dict) -> None:
    response = requests.post(url=url, headers=headers, json=json_data)
    loader = json.loads(response.text)
    cards = loader['result']['items']

    for element in cards:
        price = element['price']
        nick_name = element['nickName']
        orders = element['recentOrderNum']
        coins_available = element['quantity']
        max_limit = element['maxAmount']
        min_limit = element['minAmount']
        finish_rate = element['recentExecuteRate']
        payment_methods = []

        for method in element['payments']:
            payment_methods.append(ref_method(int(method)))

        print(
            f'BYBIT > {nick_name} | Orders: {orders} | Rate: {finish_rate}%\nAvailable: {coins_available} | Price: {price}\n'
            f'Max: {max_limit} | Min: {min_limit}\nMethod: {payment_methods}\n----------')


async def p2p_parser_paxful(url: str, headers: dict) -> None:
    response = requests.get(url=url, headers=headers)
    loader = json.loads(response.text)
    cards = loader['data']
    # print(cards)

    for element in cards:
        price = round(element['fiatPricePerBtc'], 2)
        nick_name = element['username']
        orders = element['feedbackPositive']
        max_limit = element['fiatAmountRangeMax']
        min_limit = element['fiatAmountRangeMin']
        exchange_rate = element['fiatPricePerBtc']
        coins_available = round((max_limit / exchange_rate), 8)
        payment_methods = element['paymentMethodName']
        # finish_rate = element['feedbackPositive']

    #
    #     for method in element['paymentMethodName']:
    #         payment_methods.append(method)

        print(f'PAXFUL > {nick_name} | Orders: {orders}\nAvailable: {coins_available} | Price: '
              f'{price}\nMax: {max_limit} | Min: {min_limit}\nMethod: {payment_methods}\n----------')


async def distributor_binance() -> None:
    url = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
    page = 1
    ua = UserAgent()
    headers = {'content-type': 'application/json', 'User-Agent': str(ua.random)}
    json_data = {
        "page": page,
        "rows": 10,
        "asset": "BTC",
        "fiat": "USD",
        "tradeType": "BUY",
        "payTypes": [],
    }
    response = requests.post(url, headers=headers, json=json_data)
    loader = json.loads(response.text)
    pagination = int(loader['total']) // 10 + 1

    for page in range(1, pagination + 1):
        json_data = {
            "page": page,
            "rows": 10,
            "asset": "BTC",
            "fiat": "USD",
            "tradeType": "BUY"
        }
        await p2p_parser_binance(url=url, headers=headers, json_data=json_data)


async def distributor_bybit() -> None:
    url = 'https://api2.bybit.com/fiat/otc/item/online'
    ua = UserAgent()
    headers = {'content-type': 'application/json', 'User-Agent': str(ua.random)}
    # headers = {'content-type': 'application/json'}

    json_data = {
        # "userId": 70467739,
        "tokenId": "BTC",
        "currencyId": "USD",
        "payment": [],
        "side": "1",
        "size": "10",
        "page": "1",
    }

    response = requests.post(url, headers=headers, json=json_data)
    loader = json.loads(response.text)
    pagination = int(loader['result']['count']) // 10 + 1
    # print(pagination)

    for page in range(1, pagination + 1):
        json_data = {
            # "userId": 70467739,
            "tokenId": "BTC",
            "currencyId": "USD",
            "payment": [],
            "side": "1",
            "size": "10",
            "page": str(page),
        }
        await p2p_parser_bybit(url=url, headers=headers, json_data=json_data)


async def distributor_paxful() -> None:
    coin = 1
    url = f'https://paxful.com/ru/rest/v1/offers?transformResponse=camelCase&withFavorites=false&' \
          f'crypto_currency_id={coin}&is_payment_method_localized=0&visitor_country_has_changed=false&' \
          f'visitor_country_iso=DE&currency=USD&payment-method%5B0%5D=with-any-payment-method&type=buy'

    ua = UserAgent()
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': str(ua.random)}

    await p2p_parser_paxful(url=url, headers=headers)


def ref_method(method) -> str:
    if method == 5: return 'Advcash'
    if method == 51: return 'Payeer'
    if method == 185: return 'Rosbank'
    if method == 75: return 'Tinkoff'
    if method == 14: return 'Bank Transfer'
    if method == 64: return 'Raiffeisenbank'
    if method == 49: return 'OTP Bank'
    if method == 90: return 'Cash in Person'
    if method == 1: return 'A - Bank'

    return str(method)


async def main():
    start_time = time.time()

    task_1 = asyncio.create_task(distributor_binance())
    task_2 = asyncio.create_task(distributor_bybit())
    task_3 = asyncio.create_task(distributor_paxful())

    await asyncio.gather(task_1, task_3, task_2)

    print(time.time() - start_time)

if __name__ == '__main__':
    asyncio.run(main())
