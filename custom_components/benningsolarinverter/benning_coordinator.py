from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .benning_client import BenningClient
import logging

_LOGGER = logging.getLogger(__name__)

class BenningCoordinator(DataUpdateCoordinator):
    """
    The coordinator that manages the automatic update of all values.
    """

    hass: HomeAssistant
    client: BenningClient
    oids: list[int]

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, client: BenningClient, oids: list[int]):
        super().__init__(
            hass,
            _LOGGER,
            name = "Benning Inverter",
            config_entry=config_entry,
            update_interval=timedelta(seconds=30),
            always_update=True

        )

        self.hass = hass
        self.client = client
        self.oids = oids

    async def _async_update_data(self):
        """
        Update event
        """

        _LOGGER.debug("Updating entry data...")

        available_entries = await self.client.get_entries(self.oids)
        mapping = {}
        for entry in available_entries:
            mapping[str(entry["oid"])] = entry

        _LOGGER.debug("Updated entry data!")

        return mapping

