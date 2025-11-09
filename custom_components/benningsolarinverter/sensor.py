from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .benning_entity import BenningEntity
from .benning_client import BenningClient

from homeassistant.helpers.storage import Store

from .benning_coordinator import BenningCoordinator
from .const import DOMAIN

class ConfigMissing(HomeAssistantError):
    pass

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """
    Will setup the sensor entries for the integration.
    """


    # First we will load the stored entities and config using the store API
    store = Store(hass, 1, "benning_config")
    benning_config: dict | None = await store.async_load()

    if benning_config == None:
        raise ConfigMissing

    available_entries = benning_config["available_entries"]
    client = BenningClient(hass, benning_config["host"], benning_config["username"], benning_config["password"])

    # Then we need to extract the oids such that the coordinator knows which exact oids he needs to fetch.
    oids: list[int] = []
    for bentry in available_entries:
        oids.append(bentry["oid"])
    coordinator = BenningCoordinator(hass, entry, client, oids)

    fetched_entries = await client.get_entries(oids)

    # Setting up the entities
    result_entities: list[BenningEntity] = []
    for bentry in fetched_entries:
        id = "benning_" + str(bentry["oid"]) + "_".join(str(bentry["label"]).split("."))
        entity = BenningEntity(hass, entry, coordinator, id, bentry)
        result_entities.append(entity)
    async_add_entities(result_entities)

