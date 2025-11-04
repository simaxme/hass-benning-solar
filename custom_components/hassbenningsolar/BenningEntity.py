from functools import cached_property
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DOMAIN

from .benning_client import BenningClient

class BenningEntity(SensorEntity, CoordinatorEntity):
    hass: HomeAssistant
    coordinator: DataUpdateCoordinator
    benning_client: BenningClient
    _unique_id: str
    _name: str
    _unit: str
    _oid: int

    def __init__(self, hass: HomeAssistant, coordinator: DataUpdateCoordinator, benning_client: BenningClient, id: str, name: str, unit: str, oid: int):
        SensorEntity.__init__(self)
        CoordinatorEntity.__init__(self, coordinator)

        self.hass = hass
        self.benning_client = benning_client
        self.coordinator = coordinator
        self._unique_id = id
        self._name = name
        self._unit = unit
        self._oid = oid

    @cached_property
    def name(self):
        return "Benning " + self._name

    @cached_property
    def unique_id(self):
        return self._unique_id

    @cached_property
    def suggested_(self):
        return self._unique_id

    @cached_property
    def native_unit_of_measurement(self):
        return self._unit

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data[str(self._oid)]["val"]
        self.async_write_ha_state()
