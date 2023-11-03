import aiohttp
import asyncio
import pickle

from loguru import logger
from utils.proxies import set_proxy
from utils.methods import type_trade_bybit


async def manager(conf_data: dict) -> dict:
    try:

        # запросы к биржам, для получения кол-ва страниц (тасков)
        tickets = conf_data['tickets']
        data = {'urls': ['https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search',
                         'https://api2.bybit.com/fiat/otc/item/online'],
                'headers': {'content-type': 'application/json'},
                'proxy': set_proxy(conf_data=conf_data)}

        tasks = list()
        thr = dict()
        thr['binance'], thr['bybit'], thr['paxful'], thr['okx'] = list(), list(), list(), list()
        for req in tickets:
            data_bin = {"page": 1, "rows": 10, "asset": req[0], "fiat": req[1], "tradeType": req[2]}
            data_byb = {"tokenId": req[0], "currencyId": req[1], "side": type_trade_bybit(req[2]), "page": "1"}
            data_pax = {"coin": req[0], "fiat": req[1], "trade_type": req[2]}
            data_okx = {"coin": req[0], "currency": req[1], "trade_type": req[2]}

            task_1 = asyncio.create_task(req_to_binance(data=data, info=data_bin, thr=thr))
            tasks.append(task_1)

            task_2 = asyncio.create_task(req_to_bybit(data=data, info=data_byb, thr=thr))
            tasks.append(task_2)
            #
            if not req[0] == 'ETH':
                task_3 = asyncio.create_task(req_to_paxful(info=data_pax, thr=thr))
                tasks.append(task_3)

            task_4 = asyncio.create_task(req_to_okx(info=data_okx, thr=thr))
            tasks.append(task_4)

        await asyncio.gather(*tasks)
        return thr

    except Exception as ex:
        logger.error(f'Task Manager - manager | {ex}')


async def req_to_binance(data: dict, info: dict, thr) -> list:
    try:
        async with aiohttp.ClientSession() as session:
            proxy_auth = aiohttp.BasicAuth(data['proxy'][0]['user'], data['proxy'][0]['pass'])
            async with session.post(url=data['urls'][0], headers=data['headers'], json=info,
                                    proxy_auth=proxy_auth, proxy=data['proxy'][0]['url'], ssl=False) as response:
                assert response.status == 200
                loader = await response.json()
                pagination = int(loader['total'])
                if pagination:
                    pagination = pagination // 10 + 1
                    thr['binance'].append({pagination: [info['asset'], info['fiat'], info['tradeType']]})

        return thr
    except Exception as ex:
        logger.error(f'req_to_binance | {ex}')


async def req_to_bybit(data: dict, info: dict, thr) -> list:
    try:
        async with aiohttp.ClientSession() as session:
            proxy_auth = aiohttp.BasicAuth(data['proxy'][0]['user'], data['proxy'][0]['pass'])
            async with session.post(url=data['urls'][1], headers=data['headers'], json=info,
                                    proxy_auth=proxy_auth, proxy=data['proxy'][0]['url'], ssl=False) as response:
                assert response.status == 200
                loader = await response.json()
                pagination = loader['result']['count']
                if pagination:
                    pagination = pagination // 10 + 1
                    thr['bybit'].append({pagination: [info['tokenId'], info['currencyId'],
                                                      type_trade_bybit(info['side'])]})

        return thr
    except Exception as ex:
        logger.error(f'req_to_bybit| {ex}')


async def req_to_paxful(info: dict, thr) -> list:
    try:
        thr['paxful'].append({1: [info['coin'], info['fiat'], (info['trade_type'])]})

        return thr
    except Exception as ex:
        logger.error(f'req_to_paxful | {ex}')


async def req_to_okx(info: dict, thr) -> list:
    try:
        thr['okx'].append({1: [info['coin'], info['currency'], (info['trade_type'])]})

        return thr
    except Exception as ex:
        logger.error(f'req_to_okx | {ex}')


async def distributor(conf_data: dict, counter_to_change: int) -> None:
    try:

        # проверка лимитов на количество запросов к бирже в треде
        limit_requests = conf_data['limit_requests']
        limit_exchange = conf_data['limit_exchange']
        _DEBUG = conf_data['DEBUG']

        # запуск менеджера для создания тред_даты
        data = await manager(conf_data=conf_data)

        result_bin = [[]]
        result_byb = [[]]
        result_pax = [[]]
        result_okx = [[]]

        # сортировка данных по тредам исходя из лимитов
        for exchange in data:
            counter = 0
            limit_r = limit_requests
            limit_e = limit_exchange
            for dicts in data[exchange]:
                for key, val in dicts.items():
                    if key > limit_r or not limit_e:
                        counter += 1
                        if exchange == 'binance':
                            result_bin.append(list())
                            result_bin[counter].append(val)
                        elif exchange == 'bybit':
                            result_byb.append(list())
                            result_byb[counter].append(val)
                        elif exchange == 'paxful':
                            result_pax.append(list())
                            result_pax[counter].append(val)
                        elif exchange == 'okx':
                            result_okx.append(list())
                            result_okx[counter].append(val)
                        limit_r = limit_requests - key
                        limit_e = limit_exchange - 1

                    elif key <= limit_r and limit_e:
                        if exchange == 'binance':
                            result_bin[counter].append(val)
                        elif exchange == 'bybit':
                            result_byb[counter].append(val)
                        elif exchange == 'paxful':
                            result_pax[counter].append(val)
                        elif exchange == 'okx':
                            result_okx[counter].append(val)
                        limit_r -= key
                        limit_e -= 1

        thr = [result_bin, result_byb, result_pax, result_okx]
        len_tasks = max(len(result_bin), len(result_byb), len(result_pax), len(result_okx))
        count_of_proxy = len(conf_data['proxies'])

        if _DEBUG:
            logger.debug(f'Count of threads: {len_tasks}.')
        if count_of_proxy >= len_tasks:
            for thread in thr:
                while len(thread) < len_tasks:
                    thread.append(list())

            # битовая запись конфигурации тредов
            with open('threads.data', 'wb') as file:
                pickle.dump(thr, file)

        # если тредов больше чем прокси, увеличивается лимит запросов и кол-во бирж в треде
        else:
            conf_data['limit_requests'] = limit_requests + 5

            if counter_to_change % 5 == 0:
                conf_data['limit_exchange'] = limit_exchange + 1

            counter_to_change += 1
            logger.info(f"The configuration of the threads has been changed | "
                        f"limit_requests: {conf_data['limit_requests']}, limit_exchange: {conf_data['limit_exchange']}")
            await distributor(conf_data=conf_data, counter_to_change=counter_to_change)

    except Exception as ex:
        logger.error(f'Task Manager - distributor | {ex}')
