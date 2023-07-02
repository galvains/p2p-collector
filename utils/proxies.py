import random


def set_proxy() -> list:
    limit = random.randint(27, 32)
    proxies = [
        {'name': 'NED', 'user': 'KmwLCK', 'pass': 'DQL35V', 'url': 'http://168.80.203.214:8000', 'limit': limit},
        {'name': 'JP', 'user': '25EsGn', 'pass': 'U3pJVn', 'url': 'http://45.146.181.148:8000', 'limit': limit},
        {'name': 'FR', 'user': 'gwXRtN', 'pass': 'NBPaGz', 'url': 'http://45.86.14.175:8000', 'limit': limit},
        {'name': 'DE', 'user': 'r9zpqD', 'pass': 'uwCo6q', 'url': 'http://196.19.11.234:8000', 'limit': limit},
        {'name': 'USA', 'user': 'UL4N9P', 'pass': 'Y6AztT', 'url': 'http://196.16.110.238:8000', 'limit': limit},
    ]

    random.shuffle(proxies)
    return proxies
