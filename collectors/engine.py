import json
import asyncio
import aiohttp

from loguru import logger
from fake_useragent import UserAgent
from db_model.interface_db import db_insert
from utils.methods import pay_method_bybit, coin_paxful, type_trade_bybit


async def p2p_parser_binance(session: aiohttp.ClientSession, url: str, headers: dict,
                             json_data: dict, proxy: dict, proxy_auth, connect) -> None:
    try:
        async with session.post(url=url, headers=headers, json=json_data, ssl=False,
                                proxy_auth=proxy_auth, proxy=proxy['url']) as response_session:
            assert response_session.status == 200

            response = await response_session.read()
            loader = json.loads(response)
            cards = loader['data']

            data = dict()
            data['currency'] = json_data['fiat']
            data['coin'] = json_data['asset']
            data['trade_type'] = json_data['tradeType']
            data['exchange_id'] = 1

            for element in cards:

                data['price'] = float(element['adv']['price'])
                data['nick_name'] = element['advertiser']['nickName']
                data['orders'] = element['advertiser']['monthOrderCount']
                data['link'] = f"https://p2p.binance.com/en/advertiserDetail?advertiserNo=" \
                               f"{element['advertiser']['userNo']}"
                data['available'] = float(element['adv']['surplusAmount'])
                data['max_limit'] = float(element['adv']['maxSingleTransAmount'])
                data['min_limit'] = float(element['adv']['minSingleTransAmount'])
                data['rate'] = round(100 * float(element['advertiser']['monthFinishRate']), 2)
                data['pay_methods'] = []

                for method in element['adv']['tradeMethods']:
                    data['pay_methods'].append(method['identifier'])

                db_insert(connection=connect, data=data)

    except AssertionError:
        pass
    except ConnectionError as ex:
        logger.error(f'Parser-Binance | ConnectionError | {ex}')
    except TimeoutError:
        logger.error('Parser-Binance | TimeoutError')
    except aiohttp.client_exceptions.ClientOSError as ex:
        logger.error(f'Parser-Binance | ClientOSError | {ex}')
    except aiohttp.client_exceptions.ClientProxyConnectionError as ex:
        logger.error(f'Parser-Binance | ClientProxyConnectionError | {ex}')


async def p2p_parser_bybit(session: aiohttp.ClientSession, url: str, headers: dict,
                           json_data: dict, type_trade: str, proxy: dict, proxy_auth, connect) -> None:
    try:
        async with session.post(url=url, headers=headers, json=json_data, ssl=False,
                                proxy_auth=proxy_auth, proxy=proxy['url']) as response_session:
            assert response_session.status == 200

            response = await response_session.read()
            loader = json.loads(response)
            cards = loader['result']['items']

            data = dict()
            data['currency'] = json_data['currencyId']
            data['coin'] = json_data['tokenId']
            data['trade_type'] = type_trade
            data['exchange_id'] = 2

            for element in cards:
                data['price'] = element['price']
                data['nick_name'] = element['nickName']
                data['orders'] = element['recentOrderNum']
                data['available'] = element['lastQuantity']
                data['max_limit'] = element['maxAmount']
                data['min_limit'] = element['minAmount']
                data['rate'] = element['recentExecuteRate']
                data['link'] = f"https://www.bybit.com/fiat/trade/otc/profile/{element['userId']}/{data['coin']}/" \
                               f"{data['currency']}/item"
                data['pay_methods'] = []

                for method in element['payments']:
                    data['pay_methods'].append(pay_method_bybit(method))

                db_insert(connection=connect, data=data)

    except AssertionError:
        pass
    except ConnectionError as ex:
        logger.error(f'Parser-Bybit | ConnectionError | {ex}')
    except TimeoutError:
        logger.error('Parser-Bybit | TimeoutError')
    except aiohttp.client_exceptions.ClientOSError as ex:
        logger.error(f'Parser-Bybit | ClientOSError | {ex}')
    except aiohttp.client_exceptions.ClientProxyConnectionError as ex:
        logger.error(f'Parser-Bybit | ClientProxyConnectionError | {ex}')


async def p2p_parser_paxful(session: aiohttp.ClientSession, url: str, headers: dict,
                            json_data: dict, proxy: dict, connect) -> None:
    try:
        proxy_auth = aiohttp.BasicAuth(proxy['user'], proxy['pass'])
        async with session.get(url=url, headers=headers, ssl=False,
                               proxy_auth=proxy_auth, proxy=proxy['url']) as response_session:
            assert response_session.status == 200

            response = await response_session.read()
            loader = json.loads(response)
            cards = loader['data']

            data = json_data

            for element in cards:
                exchange_rate = element['fiatPricePerBtc']
                data['orders'] = 0

                data['price'] = round(element['fiatPricePerBtc'], 2)
                data['nick_name'] = element['username']
                data['rate'] = element['feedbackPositive']
                data['max_limit'] = element['fiatAmountRangeMax']
                data['min_limit'] = element['fiatAmountRangeMin']
                data['available'] = round((data['max_limit'] / exchange_rate), 8)
                data['pay_methods'] = element['paymentMethodName']
                data['link'] = f"https://paxful.com/en/offer/{element['idHashed']}"

                db_insert(connection=connect, data=data)

    except AssertionError:
        pass
    except ConnectionError as ex:
        logger.error('ConnectionError')
    except TimeoutError:
        logger.error('Parser-Paxful | TimeoutError')
    except aiohttp.client_exceptions.ClientOSError as ex:
        logger.error(f'Parser-Paxful | ClientOSError | {ex}')
    except aiohttp.client_exceptions.ClientProxyConnectionError as ex:
        logger.error(f'Parser-Paxful | ClientProxyConnectionError | {ex}')


async def distributor_binance(coin: str, currency: str, type_trade: str, proxy: dict, connect) -> None:
    try:
        url = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
        ua = UserAgent()
        headers = {'content-type': 'application/json', 'User-Agent': str(ua.random)}
        json_data = {
            "page": 1,
            "rows": 10,
            "asset": coin,
            "fiat": currency,
            "tradeType": type_trade,
            "payTypes": [],
        }
        connector = aiohttp.TCPConnector(limit=proxy['limit'])
        proxy_auth = aiohttp.BasicAuth(proxy['user'], proxy['pass'])
        async with aiohttp.ClientSession(connector=connector, trust_env=True) as session:
            async with session.post(url, headers=headers, json=json_data, ssl=False,
                                    proxy_auth=proxy_auth, proxy=proxy['url']) as response:
                assert response.status == 200

                loader = await response.json()

                pagination = int(loader['total']) // 10 + 1
                tasks = []

                pagination = 40 if pagination > 40 else pagination
                for page in range(1, pagination + 1):
                    json_data = {
                        "page": page,
                        "rows": 10,
                        "asset": coin,
                        "fiat": currency,
                        "tradeType": type_trade
                    }

                    task = asyncio.create_task(p2p_parser_binance(session, url=url, headers=headers,
                                                                  json_data=json_data, proxy=proxy,
                                                                  proxy_auth=proxy_auth, connect=connect))
                    tasks.append(task)
                await asyncio.gather(*tasks)

    except AssertionError:
        pass
    except (aiohttp.client_exceptions.ClientOSError, aiohttp.client_exceptions.ServerDisconnectedError,
            aiohttp.client_exceptions.ClientHttpProxyError) as ex:
        logger.error(f'Dist-Binance | {ex}')


async def distributor_bybit(coin: str, currency: str, type_trade: str, proxy: dict, connect) -> None:
    try:
        url = 'https://api2.bybit.com/fiat/otc/item/online'

        headers = {'content-type': 'application/json'}
        json_data = {
            "tokenId": coin,
            "currencyId": currency,
            "payment": [],
            "side": type_trade_bybit(type_trade),
            "size": "10",
            "page": "1",
        }

        connector = aiohttp.TCPConnector(limit=proxy['limit'])
        proxy_auth = aiohttp.BasicAuth(proxy['user'], proxy['pass'])
        async with aiohttp.ClientSession(connector=connector, trust_env=True) as session:
            async with session.post(url, headers=headers, json=json_data, ssl=False,
                                    proxy_auth=proxy_auth, proxy=proxy['url']) as response:
                assert response.status == 200

                loader = await response.json()
                pagination = loader['result']['count'] // 10 + 1

                tasks = []

                pagination = 40 if pagination > 40 else pagination
                for page in range(1, pagination + 1):
                    json_data = {
                        "tokenId": coin,
                        "currencyId": currency,
                        "payment": [],
                        "side": type_trade_bybit(type_trade),
                        "size": "10",
                        "page": str(page),
                    }

                    task = asyncio.create_task(
                        p2p_parser_bybit(session, url=url, headers=headers, json_data=json_data,
                                         type_trade=type_trade, proxy=proxy,
                                         proxy_auth=proxy_auth, connect=connect))
                    tasks.append(task)
                await asyncio.gather(*tasks)

    except AssertionError:
        pass
    except TimeoutError as ex:
        logger.error(f'Dist-Bybit | {ex}')
    except (aiohttp.client_exceptions.ClientOSError, aiohttp.client_exceptions.ServerDisconnectedError,
            aiohttp.client_exceptions.ClientHttpProxyError) as ex:
        logger.error(f'Dist-Bybit | {ex}')


async def distributor_paxful(coin: str, currency: str, type_trade: str, proxy: dict, connect) -> None:
    try:
        url = f'https://paxful.com/en/rest/v1/offers?transformResponse=camelCase&withFavorites=false&' \
              f'crypto_currency_id={coin_paxful(coin)}&is_payment_method_localized=0&visitor_country_has_changed=false&' \
              f'visitor_country_iso=US&currency={currency}&payment-method%5B0%5D=with-any-payment-method&type={type_trade}'

        ua = UserAgent()
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': str(ua.random)}

        data = dict()
        data['currency'] = currency
        data['coin'] = coin
        data['trade_type'] = type_trade
        data['exchange_id'] = 3

        connector = aiohttp.TCPConnector(limit=proxy['limit'])
        async with aiohttp.ClientSession(connector=connector, trust_env=True) as session:
            await p2p_parser_paxful(session, url=url, headers=headers, json_data=data, proxy=proxy, connect=connect)

    except Exception as ex:
        logger.error(f'Dist-Paxful | {ex}')
