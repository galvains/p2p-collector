import aiohttp
import asyncio
from utils.proxies import set_proxy
from utils.methods import type_trade_bybit


async def manager(data: list):
    tickets = [
        ['USDT', 'USD', 'BUY'],
        ['USDT', 'USD', 'SELL'],
        ['USDT', 'EUR', 'BUY'],
        ['USDT', 'EUR', 'SELL'],
        ['BTC', 'USD', 'BUY'],
        ['BTC', 'USD', 'SELL'],
        ['BTC', 'EUR', 'BUY'],
        ['BTC', 'EUR', 'SELL'],
        ['USDC', 'USD', 'BUY'],
        ['USDC', 'USD', 'SELL'],
        ['USDC', 'EUR', 'BUY'],
        ['USDC', 'EUR', 'SELL'],
        ['ETH', 'USD', 'BUY'],
        ['ETH', 'USD', 'SELL'],
        ['ETH', 'EUR', 'BUY'],
        ['ETH', 'EUR', 'SELL'],
    ]

    async with aiohttp.ClientSession() as session:
        tasks = dict()
        tasks['binance'], tasks['bybit'] = list(), list()
        headers = {'content-type': 'application/json'}
        proxy = set_proxy()
        proxy_auth = aiohttp.BasicAuth(proxy[0]['user'], proxy[0]['pass'])

        for req in tickets:
            data_bin = {"page": 1, "rows": 10, "asset": req[0], "fiat": req[1], "tradeType": req[2]}
            data_byb = {"tokenId": req[0], "currencyId": req[1], "payment": [], "side": type_trade_bybit(req[2]),
                        "size": "10", "page": "1"}

            # print(data_bin)
            async with session.post(url=data[0], headers=headers, json=data_bin,
                                    proxy_auth=proxy_auth, proxy=proxy[0]['url'], ssl=False) as r_bin:
                assert r_bin.status == 200
                loader = await r_bin.json()
                pagination = int(loader['total']) // 10 + 1
                tasks['binance'].append({pagination: req})

            async with session.post(url=data[1], headers=headers, json=data_byb,
                                    proxy_auth=proxy_auth, proxy=proxy[0]['url'], ssl=False) as r_byb:
                assert r_byb.status == 200
                loader = await r_byb.json()
                pagination = loader['result']['count'] // 10 + 1
                tasks['bybit'].append({pagination: req})

    print(tasks)


async def main():
    data = ['https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search',
            'https://api2.bybit.com/fiat/otc/item/online']

    await manager(data=data)


if __name__ == '__main__':
    asyncio.run(main())
