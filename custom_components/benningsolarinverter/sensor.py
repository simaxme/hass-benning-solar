from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .benning_entity import BenningEntity
from .benning_client import BenningClient

from homeassistant.helpers.storage import Store

from .benning_coordinator import BenningCoordinator
from .const import DOMAIN

import logging

_LOGGER = logging.getLogger(__name__)

class ConfigMissing(HomeAssistantError):
    pass

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """
    Will setup the sensor entries for the integration.
    """

    _LOGGER.debug("Loading benning config with available entries...")
    
    # First we will load the stored entities and config using the store API
    store = Store(hass, 1, "benning_config")
    benning_config: dict | None = await store.async_load()

    if benning_config == None:
        _LOGGER.error("Error while trying to load config with available entries for benning!")
        raise ConfigMissing

    _LOGGER.debug("Successfully load config with available entries!")

    available_entries = benning_config["available_entries"]

    _LOGGER.debug("Available entries are: " + (",".join(str(entry["oid"]) for entry in available_entries)))

    client = BenningClient(hass, benning_config["host"], benning_config["username"], benning_config["password"])

    # Then we need to extract the oids such that the coordinator knows which exact oids he needs to fetch.
    oids: list[int] = [bentry["oid"] for bentry in available_entries]

    coordinator = BenningCoordinator(hass, entry, client, oids)

    _LOGGER.debug("Fetching all entries first time...")

    fetched_entries = await client.get_entries(oids)

    _LOGGER.debug("Successfully fetched all entries on startup!")
    _LOGGER.debug("Setting up entities...")

    # Setting up the entities
    result_entities: list[BenningEntity] = []
    for bentry in fetched_entries:
        id = "benning_" + str(bentry["oid"]) + "_".join(str(bentry["label"]).split("."))
        entity = BenningEntity(hass, entry, coordinator, id, bentry)
        result_entities.append(entity)
    async_add_entities(result_entities)

    _LOGGER.debug("Successfully setup all entities")

