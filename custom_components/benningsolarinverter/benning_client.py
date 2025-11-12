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

        _LOGGER.info("Trying to authenticate with Benning server...")

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
                        _LOGGER.error("Received '-1', meaning the authentication credentials are wrong!")
                        raise InvalidAuth
        except TimeoutError:
            _LOGGER.error("Was unable to authenticate: a timeout occured after 15 seconds!")
            raise CannotConnect


        _LOGGER.info("Successfully authenticated with Benning Server!")


    async def get_entry(self, oid: int):
        """
        Will return a specific entry from the API.
        Please consider using get_entries(oids) if wanting to get multiple entries at once.
        """

        _LOGGER.debug("Fetching entry with oid " + str(oid) + "...")

        session = aiohttp_client.async_get_clientsession(self.hass)

        params = {
            "oid": oid
        }

        async with session.get(self.get_base_url() + "/getentry.cgi", params=params) as response:
            if response.status != 200:
                _LOGGER.error("The server returned a response status != 200 while trying to fetch oid " + str(oid) + "!")
                raise InvalidAuth

            content = await response.text()

            if content == "-1":
                _LOGGER.error("Error while parsing content from data for oid " + str(oid) + ", the server returned '-1', meaning the entry does not exist!")
                raise EntryNotAvailable

            _LOGGER.debug("Successfully received content from backend for oid " + str(oid) + ": " + str(content))

            return await response.json()

    async def get_entries(self, oids: list[int]) -> list:
        """
        Will return a list of specified entries from the API
        Note this will ignore unkown oids and will return an empty array if no oids match.
        """
        _LOGGER.debug("Fetching the following entries: " + ",".join(str(oid) for oid in oids))

        session = aiohttp_client.async_get_clientsession(self.hass)

        params = {
            "oids": ",".join(str(x) for x in oids)
        }

        async with session.get(self.get_base_url() + "/getentries.cgi", params=params) as response:
            if response.status != 200:
                _LOGGER.error("The server returned a response status != 200 while trying to fetch multiple oids: " + (",".join(str(oid) for oid in oids)) + "!")
                raise InvalidAuth

            content = await response.text()

            if content == "-1":
                _LOGGER.error("Error while parsing content from data for oids " + (",".join(str(oid) for oid in oids)) + ", the server returned '-1', meaning the entries do not exist!")
                raise EntryNotAvailable

            _LOGGER.debug("Successfully received the following response while trying to fetch oids " + (",".join(str(oid) for oid in oids)) + ": " + content)

            # Do some parsing stuff, the returned json is not completly valid
            content = "".join(content.split("\n"))
            content = "".join(content.split("\r"))
            mapped = ",".join([a for a in content.split(",") if a != ""])
            if mapped.endswith(",]"):
                mapped = mapped.replace(",]", "]")

            _LOGGER.debug("Mapped response while trying to fetch oids " +  (",".join(str(oid) for oid in oids)) + " to: " + mapped)

            return json.loads(mapped)


    async def get_available_entries(self) -> list:
        """
        Will try to gather all entries that can be accessed through the API
        Note this is basically bruteforcing the oids and therefore may take a while.
        (yes, there is no endpoint to gather a list of all endpoints :/)
        """
        _LOGGER.info("Trying to obtain available entries from benning server...")

        res: list[int] = []

        for i in range(0, 100):
            temp_ids = []
            for x in range(i*1000, i*1000+1000):
                temp_ids.append(x)
            entries = await self.get_entries(temp_ids)
            res.extend(entries)

            if i % 10 == 0:
                _LOGGER.info("Progress while loading entries: " + str(i) + "%")

        _LOGGER.info("Obtained " + str(len(res)) + " entries from benning server.")

        return res

