#!/usr/bin/env python3
""" web cache"""
import requests
import redis


r = redis.Redis()


def get_page(url: str) -> str:
    '''implements the cache'''
    key = "count:{}".format(url)
    '''
    gives the count of how many times a URL has been visited
    '''
    r.incr(key)
    cached_data = r.get(url)
    '''
    checks for the  data associated with url in cache
    '''
    if cached_data is not None:
        return cached_data.decode('utf-8')
    '''
    if there is no data, query the url and add in cache for 10 seconds
    '''
    resp = requests.get(url)
    info = resp.text
    r.setex(url, 10, info)

    return info
