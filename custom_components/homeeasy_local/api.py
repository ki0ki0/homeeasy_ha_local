"""Sample API Client."""
import logging
import asyncio
import socket
from typing import Optional
import aiohttp
import async_timeout

TIMEOUT = 10

from homeeasy.DeviceState import DeviceState
from homeeasy.HomeEasyLibLocal import HomeEasyLibLocal

_LOGGER: logging.Logger = logging.getLogger(__package__)


class ApiClient(HomeEasyLibLocal):
    def __init__(self, ip: str, session: aiohttp.ClientSession) -> None:
        """Sample API Client."""
        self._ip = ip
        self._session = session

    async def async_get_data(self) -> dict:
        """Get data from the API."""
        await self.connect(self._ip)
        self.state = await self.request_status_async()
        return self.state

    async def ensure_connected(self) -> dict:
        """Get data from the API."""
        await self.connect(self._ip)
        await self.request_status_async()
