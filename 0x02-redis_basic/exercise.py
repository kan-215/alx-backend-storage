#!/usr/bin/env python3

from typing import Callable, Optional, Union
from uuid import uuid4
import redis
from functools import wraps

'''
    Redis string operations.
'''

def track_calls(func: Callable) -> Callable:
    '''
        Track how many times a function is invoked.
    '''

    @wraps(func)
    def inner(self, *args, **kwargs):
        '''
            Inner function for tracking.
        '''
        identifier = func.__qualname__
        self._redis.incr(identifier)
        return func(self, *args, **kwargs)
    return inner


def log_history(func: Callable) -> Callable:
    """ Decorator that saves the inputs and outputs 
    of a specific function.
    """
    identifier = func.__qualname__
    input_log = identifier + ":inputs"
    output_log = identifier + ":outputs"

    @wraps(func)
    def inner(self, *args, **kwargs):  # sourcery skip: avoid-builtin-shadow
        """ Inner function to handle logging """
        self._redis.rpush(input_log, str(args))
        result = func(self, *args, **kwargs)
        self._redis.rpush(output_log, str(result))
        return result

    return inner


def display_history(func: Callable) -> None:
    # sourcery skip: use-fstring-for-concatenation, use-fstring-for-formatting
    """
    Displays the call history of a function.
    Args:
        func: The target function to show the history.
    Returns:
        None
    """
    identifier = func.__qualname__
    cache_instance = redis.Redis()
    call_count = cache_instance.get(identifier).decode("utf-8")
    print("{} was called {} times:".format(identifier, call_count))
    inputs = cache_instance.lrange(identifier + ":inputs", 0, -1)
    outputs = cache_instance.lrange(identifier + ":outputs", 0, -1)
    for inp, out in zip(inputs, outputs):
        print("{}(*{}) -> {}".format(identifier, inp.decode('utf-8'),
                                     out.decode('utf-8')))


class RedisCache:
    '''
        RedisCache class.
    '''
    def __init__(self):
        '''
            Initialize the Redis cache.
        '''
        self._redis = redis.Redis()
        self._redis.flushdb()

    @track_calls
    @log_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''
            Store a piece of data in the Redis cache.
        '''
        unique_key = str(uuid4())
        self._redis.set(unique_key, data)
        return unique_key

    def retrieve(self, key: str,
                 transform: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        '''
            Retrieve data from Redis cache.
        '''
        stored_value = self._redis.get(key)
        if transform:
            stored_value = transform(stored_value)
        return stored_value

    def retrieve_str(self, key: str) -> str:
        '''
            Retrieve a string from the cache.
        '''
        stored_value = self._redis.get(key)
        return stored_value.decode('utf-8')

    def retrieve_int(self, key: str) -> int:
        '''
            Retrieve an integer from the cache.
        '''
        stored_value = self._redis.get(key)
        try:
            stored_value = int(stored_value.decode('utf-8'))
        except Exception:
            stored_value = 0
        return stored_value
