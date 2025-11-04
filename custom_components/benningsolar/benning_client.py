import homeassistant.helpers.aiohttp_client as aiohttp_client
from homeassistant.core import HomeAssistant

from .exceptions.cannot_connect import CannotConnect
from .exceptions.entry_not_available import EntryNotAvailable

import json
from .exceptions.invalid_auth import InvalidAuth
import logging
import async_timeout

_LOGGER = logging.getLogger(__name__)

class BenningClient:
    """
    A client that will interact with the API of the inverter.
    """

    hass: HomeAssistant
    """
    The hass instance to create a client session
    """

    host: str
    """
    The ip of the host.
    """

    username: str
    """
    The username to authenticate with the host.
    """
    
    password: str
    """
    The password to authenticate with the password
    """


    def __init__(self, hass: HomeAssistant, host: str, username: str, password: str):
        self.hass = hass
        self.host = host
        self.username = username
        self.password = password

    def get_base_url(self) -> str:
        """
        Returns the base url to which requests are made.
        """
        return "http://" + self.host

    async def authenticate(self):
        """
        Will try to authenticate with the inverter's API with the given host and credentials parameter.
        Currently only used to validate that the connection works properly.
        """
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
        """
        Will return a specific entry from the API.
        Please consider using get_entries(oids) if wanting to get multiple entries at once.
        """
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
        """
        Will return a list of specified entries from the API
        Note this will ignore unkown oids and will return an empty array if no oids match.
        """
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
        """
        Will try to gather all entries that can be accessed through the API
        Note this is basically bruteforcing the oids and therefore may take a while.
        (yes, there is no endpoint to gather a list of all endpoints :/)
        """
        res: list[int] = []

        for i in range(0, 100):
            temp_ids = []
            for x in range(i*1000, i*1000+1000):
                temp_ids.append(x)
            entries = await self.get_entries(temp_ids)
            res.extend(entries)
            print("Loading entries " + str(i) + "%")

        return res

