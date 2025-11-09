from functools import cached_property
from typing import override
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
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

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, coordinator: DataUpdateCoordinator, id: str, data):
        SensorEntity.__init__(self)
        CoordinatorEntity.__init__(self, coordinator)

        self.hass = hass
        self.coordinator = coordinator
        self.entry = entry
        self._unique_id = id
        self._name = data["uitext"]
        self._unit = data["unit"]
        self._oid = data["oid"]
        self._attr_native_value = parse_number(data)

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
        if self._unit == "W/m^2":
            return "W/m²"

        return self._unit

    @cached_property
    @override
    def device_class(self) -> SensorDeviceClass | None:
        if self._unit in ["mWh", "Wh", "kWh", "MWh", "GWh", "TWh"]:
            return SensorDeviceClass.ENERGY

        if self._unit in ["mW", "W", "kW", "MW"]:
            return SensorDeviceClass.POWER

        if self._unit in ["°C"]:
            return SensorDeviceClass.TEMPERATURE

        if self._unit in ["A", "mA"]:
            return SensorDeviceClass.CURRENT

        if self._unit in ["V", "mV", "kV", "MV"]:
            return SensorDeviceClass.VOLTAGE

        if self._unit in ["VA", "mVA", "kVA"]:
            return SensorDeviceClass.APPARENT_POWER

        if self._unit in ["W/m²", "W/m^2"]:
            return SensorDeviceClass.IRRADIANCE

        if self._unit in ["h"]:
            return SensorDeviceClass.DURATION

        if self._unit in ["Hz"]:
            return SensorDeviceClass.FREQUENCY

        return None

    @cached_property
    def extra_state_attributes(self) -> dict:
        return {
            "oid": self._oid
        }

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
