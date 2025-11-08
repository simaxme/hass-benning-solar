from functools import cached_property
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .utils import parse_number
from .const import DOMAIN

from .benning_client import BenningClient

class BenningEntity(SensorEntity, CoordinatorEntity):
    """
    A entity representing one specific entry / oid of the inverter.
    """
 
    hass: HomeAssistant
    """
    The HomeAssistance Instance
    """

    coordinator: DataUpdateCoordinator
    """
    The coordinator for receiving update events
    """

    entry: ConfigEntry
    """
    The config entry instance.
    Used for access the specific entry id for uniquiely identifying the entitie's device.
    """

    _unique_id: str
    """
    The unique id of this entity
    """

    _name: str
    """
    The name of this entity
    """

    _unit: str
    """
    The unit of this value.
    """

    _oid: int
    """
    The oid of this value
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, coordinator: DataUpdateCoordinator, id: str, name: str, unit: str, oid: int):
        SensorEntity.__init__(self)
        CoordinatorEntity.__init__(self, coordinator)

        self.hass = hass
        self.coordinator = coordinator
        self.entry = entry
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

    @cached_property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={
                (DOMAIN, self.entry.entry_id)
            },
            name="Benning Solar Inverter",
            manufacturer="Benning Solar"
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """
        Handle the coordinator update, will just extract the data.
        """

        data = self.coordinator.data[str(self._oid)]

        if data == None:
            return

        self._attr_native_value = parse_number(data)
        self.async_write_ha_state()
