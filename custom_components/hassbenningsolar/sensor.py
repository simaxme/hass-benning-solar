from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from custom_components.hassbenningsolar.BenningEntity import BenningEntity
from custom_components.hassbenningsolar.benning_client import BenningClient

from homeassistant.helpers.storage import Store

from .benning_coordinator import BenningCoordinator
from .const import DOMAIN

class ConfigMissing(HomeAssistantError):
    pass

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    store = Store(hass, 1, "benning_config")

    benning_config: dict | None = await store.async_load()

    if benning_config == None:
        raise ConfigMissing

    available_entries = benning_config["available_entries"]


    client = BenningClient(hass, benning_config["host"], benning_config["username"], benning_config["password"])

    oids: list[int] = []
    for bentry in available_entries:
        oids.append(bentry["oid"])

    coordinator = BenningCoordinator(hass, entry, client, oids)

    result_entities: list[BenningEntity] = []

    for bentry in available_entries:
        id = "benning_" + str(bentry["oid"]) + "_".join(str(bentry["label"]).split("."))
        entity = BenningEntity(hass, coordinator, client, id, bentry["uitext"], bentry["unit"], bentry["oid"])
        result_entities.append(entity)

    async_add_entities(result_entities)

    # async_add_entities([BenningEntity(hass, entry, client)])

