from sanic_session.base import SessionDict, BaseSessionInterface
from sanic_session import RedisSessionInterface
from sanic_session.utils import *

import ujson
import uuid

from typing import Callable

'''
Based off of sanic_session
https://github.com/subyraman/sanic_session/
I just made some changes to it
'''

class MyRedisInterface(RedisSessionInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def save(self, request, response) -> None:
        """Saves the session into Redis and returns appropriate cookies.
        Args:
            request (sanic.request.Request):
                The sanic request which has an attached session.
            response (sanic.response.Response):
                The Sanic response. Cookies with the appropriate expiration
                will be added onto this response.
        Returns:
            None
        """
        if 'session' not in request:
            return

        redis_connection = await self.redis_getter()
        key = self.prefix + request['session'].sid
        if not request['session']:
            #await redis_connection.delete([key])
            await redis_connection.delete(key)

            if request['session'].modified:
                self._delete_cookie(request, response)

            return

        val = ujson.dumps(dict(request['session']))

        await redis_connection.set(key,val,expire=self.expiry)

        self._set_cookie_expiration(request, response)

    