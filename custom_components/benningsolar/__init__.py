"""The HASS Benning Solar Inverter Integration integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    This will just forward the setup to the sensor file. 
    All devices of this plugins are sensors.
    """
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR])


    return True

async def async_unload_entry(hass: HomeAssistant, entry: New_NameConfigEntry) -> bool:
    """
    Currently not needed
    """
    return True
