from datetime import timedelta
import aiohttp
from homeassistant.config_entries import ConfigEntry
import homeassistant.helpers.aiohttp_client as aiohttp_client
from homeassistant.core import HomeAssistant

from custom_components.hassbenningsolar.exceptions.cannot_connect import CannotConnect
from custom_components.hassbenningsolar.exceptions.entry_not_available import EntryNotAvailable
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

import json
from .exceptions.invalid_auth import InvalidAuth
import logging
import async_timeout

_LOGGER = logging.getLogger(__name__)

class BenningClient:
    hass: HomeAssistant
    host_url: str
    username: str
    password: str
    token: str

    def __init__(self, hass: HomeAssistant, host_url: str, username: str, password: str):
        self.hass = hass
        self.host_url = host_url
        self.username = username
        self.password = password

        print("Benning hub initialized!")

    def get_base_url(self) -> str:
        return "http://" + self.host_url

    async def authenticate(self):
        session = aiohttp_client.async_get_clientsession(self.hass)

        params = {
            "name": self.username,
            "pass": self.password
        }

        try:
            async with async_timeout.timeout(15):
                async with session.get(self.get_base_url() + "/login.cgi", params=params) as response:
                    if response.status != 200:
                        raise InvalidAuth

                    content = await response.text()

                    if content == "-1":
                        raise InvalidAuth
        except TimeoutError:
            raise CannotConnect


    async def get_entry(self, oid: int):
        session = aiohttp_client.async_get_clientsession(self.hass)

        params = {
            "oid": oid
        }

        async with session.get(self.get_base_url() + "/getentry.cgi", params=params) as response:
            if response.status != 200:
                raise InvalidAuth

            content = await response.text()

            if content == "-1":
                raise EntryNotAvailable

            return await response.json()

    async def get_entries(self, oids: list[int]) -> list:
        session = aiohttp_client.async_get_clientsession(self.hass)

        params = {
            "oids": ",".join(str(x) for x in oids)
        }

        async with session.get(self.get_base_url() + "/getentries.cgi", params=params) as response:
            if response.status != 200:
                raise InvalidAuth

            content = await response.text()

            if content == "-1":
                raise EntryNotAvailable

            content = "".join(content.split("\n"))
            content = "".join(content.split("\r"))

            mapped = ",".join([a for a in content.split(",") if a != ""])

            if mapped.endswith(",]"):
                mapped = mapped.replace(",]", "]")

            return json.loads(mapped)


    async def get_available_entries(self) -> list:
        res: list[int] = []

        for i in range(0, 100):
            temp_ids = []
            for x in range(i*1000, i*1000+1000):
                temp_ids.append(x)
            entries = await self.get_entries(temp_ids)
            res.extend(entries)
            print("Loading entries " + str(i) + "%")

        return res

