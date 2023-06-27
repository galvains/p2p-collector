import random


def set_proxy() -> list:
    proxies = [
        {'name': 'NED', 'user': 'KmwLCK', 'pass': 'DQL35V', 'url': 'http://168.80.203.214:8000'},
        {'name': 'JP', 'user': '25EsGn', 'pass': 'U3pJVn', 'url': 'http://45.146.181.148:8000'},
        {'name': 'FR', 'user': 'gwXRtN', 'pass': 'NBPaGz', 'url': 'http://45.86.14.175:8000'},
        {'name': 'DE', 'user': 'r9zpqD', 'pass': 'uwCo6q', 'url': 'http://196.19.11.234:8000'},
    ]

    random.shuffle(proxies)
    return proxies
